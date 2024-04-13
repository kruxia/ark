/*
A version contains zero or more files.
Each file is identified by its filepath and has one or more versions.

1. PUT a single file to a particular account and filepath: creates a new version
    containing that file.
2. POST one or more files to a particular account and directory path: creates a new
    version containing those files
*/
use crate::{
    db,
    errors::{ark_error, ark_error_response, error_response, ArkError, ErrorResponse},
    models::{
        file::{ExtMimetype, FileHistory, FileVersion, NewFileVersion},
        version::{NewVersion, Version},
    },
    schema, AppState,
};
use axum::{
    body::Body,
    extract::{Path, Query, Request, State},
    http::{header, StatusCode},
    response::{IntoResponse, Json},
};
use diesel::prelude::*;
use diesel_async::scoped_futures::ScopedFutureExt;
use diesel_async::AsyncConnection;
use diesel_async::RunQueryDsl;
use regex::Regex;
use schema::file_version;
use serde::Deserialize;
use uuid::Uuid;

const MAX_FILE_SIZE: usize = 100_000_000;

/// Upload a single file with a new version.
pub async fn upload_file(
    State(state): State<AppState>,
    Path((account_id, filepath)): Path<(Uuid, String)>,
    Query(meta): Query<serde_json::Value>,
    request: Request,
) -> Result<(StatusCode, Json<FileVersion>), (StatusCode, Json<ErrorResponse>)> {
    let mut conn = state.pool.get().await.map_err(db::pool_error_response)?;
    let file_version = conn
        .transaction::<FileVersion, ArkError, _>(|mut conn| {
            async move {
                // create a version for this file
                let new_version = NewVersion {
                    id: Some(Uuid::now_v7()),
                    account_id: account_id,
                    meta: None,
                };
                let version = diesel::insert_into(schema::version::table)
                    .values(new_version)
                    .returning(Version::as_returning())
                    .get_result(&mut conn)
                    .await
                    .map_err(db::diesel_result_error)?;

                // determine the mimetype from the file extension
                let ext_pattern = Regex::new(r"\.(?<ext>\w+)$").unwrap();
                let ext = ext_pattern
                    .captures(&filepath)
                    .map_or_else(|| String::from(""), |cap| String::from(&cap["ext"]));
                let ext_mimetype = schema::ext_mimetype::table
                    .filter(schema::ext_mimetype::ext.eq(ext))
                    .select(ExtMimetype::as_select())
                    .first(&mut conn)
                    .await;
                let mimetype = match ext_mimetype {
                    Ok(record) => record.name,
                    _ => String::from("application/octet-stream"),
                };

                // stream the request body to S3
                // ## TODO: axum BodyDataStream into aws ByteStream.
                // See <https://imfeld.dev/writing/process_streaming_uploads_with_axum>
                // For now, just get the whole body up to MAX_FILE_SIZE as bytes.

                let body = axum::body::to_bytes(request.into_body(), MAX_FILE_SIZE)
                    .await
                    .map_err(ark_error)?;

                // let body = request.into_body().into_data_stream();

                // get the files attributes: filesize
                let filesize = body.len() as i64;

                // TODO: What if this file content has been prevously uploaded?

                ark_s3::upload::upload_object_stream(
                    &state.s3,
                    &state.settings.s3_bucket_name,
                    body.into(),
                    format!("{}/{}/{}", &account_id, &filepath, version.id).as_str(),
                    Some(&mimetype),
                )
                .await
                .map_err(ark_error)?;

                // create a file_version for this file
                let new_file_version = NewFileVersion {
                    account_id,
                    version_id: version.id,
                    filepath,
                    filesize,
                    mimetype,
                    meta: Some(meta),
                };
                let file_version = diesel::insert_into(file_version::table)
                    .values(new_file_version)
                    .returning(FileVersion::as_returning())
                    .get_result(&mut conn)
                    .await
                    .map_err(db::diesel_result_error)?;

                Ok(file_version)
            }
            .scope_boxed()
        })
        .await
        .map_err(error_response)?;

    Ok((StatusCode::OK, Json(file_version)))
}

// ## TODO ##
// Upload one or more files in a new version.

#[derive(Deserialize, Debug)]
pub struct FileQuery {
    pub _version: Option<Uuid>,
}

// Get the content of the given file, optionally at the given version (default=latest).
pub async fn get_file_data(
    State(state): State<AppState>,
    Path((account_id, filepath)): Path<(Uuid, String)>,
    Query(file_query): Query<FileQuery>,
    _request: Request,
) -> Result<impl IntoResponse, (StatusCode, Json<ErrorResponse>)> {
    let mut conn = state.pool.get().await.map_err(db::pool_error_response)?;

    // get the given or latest file_version
    let file_version = match file_query._version {
        Some(version_id) => {
            file_version::table
                .filter(file_version::account_id.eq(account_id))
                .filter(file_version::filepath.eq(&filepath))
                .filter(file_version::version_id.eq(&version_id))
                .select(FileVersion::as_select())
                .first(&mut conn)
                .await
        }
        _ => {
            file_version::table
                .filter(file_version::account_id.eq(account_id))
                .filter(file_version::filepath.eq(&filepath))
                .select(FileVersion::as_select())
                .order_by(file_version::version_id.desc())
                .first(&mut conn)
                .await
        }
    }
    .map_err(db::diesel_result_error_response)?;

    let file_key = format!("{}/{}/{}", &account_id, &filepath, &file_version.version_id);

    let object_result =
        ark_s3::object::get_object(&state.s3, &state.settings.s3_bucket_name, &file_key)
            .await
            .map_err(ark_error_response)?;

    // TODO: Stream the ByteStream to the client directly without reading into bytes
    let body_data = object_result
        .body
        .collect()
        .await
        .map_err(ark_error_response)?;

    let body = Body::from(body_data.into_bytes());

    let headers = [(header::CONTENT_TYPE, file_version.mimetype)];

    Ok((headers, body))
}

// Get the history of the given file.
pub async fn get_history(
    db::Connection(mut conn): db::Connection,
    Path((account_id, filepath)): Path<(Uuid, String)>,
) -> Result<(StatusCode, Json<FileHistory>), (StatusCode, Json<ErrorResponse>)> {
    let versions: Vec<FileVersion> = file_version::table
        .filter(file_version::account_id.eq(account_id))
        .filter(file_version::filepath.eq(&filepath))
        .select(FileVersion::as_select())
        .load(&mut conn)
        .await
        .map_err(db::diesel_result_error_response)?;

    if versions.len() == 0 {
        Err((
            StatusCode::NOT_FOUND,
            Json(ErrorResponse {
                error: format!(
                    "No file versions found: account_id={}, filepath={}",
                    account_id, filepath
                ),
            }),
        ))
    } else {
        Ok((
            StatusCode::OK,
            Json(FileHistory {
                account_id,
                filepath,
                versions,
            }),
        ))
    }
}

// ## TODO ##
// Search for and list files with the given parameters.

// ## TODO ##
// Delete the given file (= mark it as deleted).

/* --------------------------------------------------------------------
/// Upload one or more files (multipart form with streaming upload)
/// - The `account` parameter is the account to store the file in
/// - The `path` parameter is the location for the files in the account's storage
/// - Insert the file_version for these files
/// - For each file,
///     - Stream the file data into object storage
///     - Insert a file_item
pub async fn create_file_version(
    State(state): State<AppState>,
    Json(new_file_item): Json<NewFileItem>,
) -> Result<(StatusCode, Json<FileItem>), (StatusCode, Json<ErrorResponse>)> {
    // get a connection to the pool
    let mut conn = state.pool.get().await.map_err(db::pool_error_response)?;
    let file_version = NewFileVersion {
        id: Some(Uuid::now_v7()),
        account_id: new_file_item.account_id,
        created: None,
        meta: None,
    };
    let file_item = FileItem {
        account_id: new_file_item.account_id,
        version_id: file_version.id.unwrap(),
        filepath: new_file_item.filepath,
        created: new_file_item
            .created
            .unwrap_or_else(|| chrono::offset::Utc::now()),
        mimetype: new_file_item.mimetype,
        meta: new_file_item.meta,
    };
    Ok((StatusCode::CREATED, Json(file_item)))
}

pub async fn search(
    db::Connection(mut conn): db::Connection,
    // Parse the request body as JSON into a `SearchFile` type Json(payload):
    // Json<SearchFile>,
) -> Result<Json<Vec<File>>, (StatusCode, Json<ErrorResponse>)> {
    let data: Vec<File> = crate::schema::account::table
        .select(File::as_select())
        .load(&mut conn)
        .await
        .map_err(db::diesel_result_error_response)?;

    // this will be converted into a JSON response
    // with a status code of `200 OK`
    tracing::debug!("{data:?}");
    Ok(Json(data))
}
-------------------------------------------------------------------- */