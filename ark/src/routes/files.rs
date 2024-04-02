use crate::{
    db, errors,
    models::file::{FileItem, FileVersion, NewFileItem, NewFileVersion},
    schema, AppState,
};
use axum::{extract::State, http::StatusCode, response::Json};
use diesel::prelude::*;
use diesel_async::scoped_futures::ScopedFutureExt;
use diesel_async::AsyncConnection;
use diesel_async::RunQueryDsl;
use uuid::Uuid;

/// Upload one or more files (multipart form with streaming upload)
/// - Insert the file_version for these files
/// - For each file,
///     - Stream the file data into object storage
///     - Insert a file_item
pub async fn create(
    State(state): State<AppState>,
    Json(new_file_item): Json<NewFileItem>,
) -> Result<(StatusCode, Json<FileItem>), (StatusCode, Json<errors::ErrorResponse>)> {
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
) -> Result<Json<Vec<File>>, (StatusCode, Json<errors::ErrorResponse>)> {
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
