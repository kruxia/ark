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
    errors::{ark_error, error_response, ArkError, ErrorResponse},
    models::file::{self, FileVersion, NewFileVersion, NewVersion, NewVersionRequest, Version},
    schema, AppState,
};
use axum::{
    extract::{Path, Query, Request, State},
    http::StatusCode,
    response::Json,
};
use chrono::DateTime;
use diesel::prelude::*;
use diesel_async::scoped_futures::ScopedFutureExt;
use diesel_async::AsyncConnection;
use diesel_async::RunQueryDsl;
use regex::Regex;
use uuid::Uuid;

const MAX_FILE_SIZE: usize = 100_000_000;

pub async fn create_version(
    State(state): State<AppState>,
    Json(new_version_request): Json<NewVersionRequest>,
) -> Result<(StatusCode, Json<Version>), (StatusCode, Json<ErrorResponse>)> {
    let mut conn = state.pool.get().await.map_err(db::pool_error_response)?;

    let version = conn
        .transaction::<Version, ArkError, _>(|mut conn| {
            async move {
                let new_version = NewVersion {
                    account_id: new_version_request.account_id,
                    meta: new_version_request.meta,
                };
                let version = diesel::insert_into(schema::version::table)
                    .values(new_version)
                    .returning(Version::as_returning())
                    .get_result(&mut conn)
                    .await
                    .map_err(db::diesel_result_error)?;

                Ok(version)
            }
            .scope_boxed()
        })
        .await
        .map_err(error_response)?;

    Ok((StatusCode::CREATED, Json(version)))
}

pub async fn upload_file(
    State(state): State<AppState>,
    Path((account_id, filepath)): Path<(Uuid, String)>,
    Query(query): Query<serde_json::Value>,
    request: Request,
) -> Result<(StatusCode, Json<FileVersion>), (StatusCode, Json<ErrorResponse>)> {
    let mut conn = state.pool.get().await.map_err(db::pool_error_response)?;
    let file_version = conn
        .transaction::<FileVersion, ArkError, _>(|mut conn| {
            async move {
                // create a version for this file
                let new_version = NewVersion {
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
                    .select(file::ExtMimetype::as_select())
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

                ark_s3::upload::upload_object_stream(
                    &state.s3,
                    &account_id.to_string(),
                    body.into(),
                    &filepath,
                    Some(&mimetype),
                )
                .await
                .map_err(ark_error)?;

                // create a file_version for this file
                let new_file_version = NewFileVersion {
                    account_id: account_id,
                    version_id: version.id,
                    filepath: filepath,
                    filesize: filesize,
                    mimetype: mimetype,
                    meta: Some(query),
                };
                let file_version = diesel::insert_into(schema::file_version::table)
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
