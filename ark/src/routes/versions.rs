/*
A version contains zero or more files.
*/
use crate::{
    db,
    errors::{error_response, ArkError, ErrorResponse},
    models::file::FileVersion,
    models::version::{NewVersion, Version, VersionData},
    schema, AppState,
};
use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::Json,
};
use diesel::prelude::*;
use diesel_async::scoped_futures::ScopedFutureExt;
use diesel_async::AsyncConnection;
use diesel_async::RunQueryDsl;
use uuid::Uuid;

/// Create a new version without any files.
pub async fn create_version(
    State(state): State<AppState>,
    Json(mut new_version): Json<NewVersion>,
) -> Result<(StatusCode, Json<Version>), (StatusCode, Json<ErrorResponse>)> {
    let mut conn = state.pool.get().await.map_err(db::pool_error_response)?;

    let version = conn
        .transaction::<Version, ArkError, _>(|mut conn| {
            async move {
                new_version.id = Some(Uuid::now_v7());
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

/// Get the metadata and files that were modified in the given version.
pub async fn get_version(
    db::Connection(mut conn): db::Connection,
    Path(version_id): Path<Uuid>,
) -> Result<(StatusCode, Json<VersionData>), (StatusCode, Json<ErrorResponse>)> {
    let version = schema::version::table
        .filter(schema::version::id.eq(version_id))
        .select(Version::as_select())
        .first(&mut conn)
        .await
        .map_err(db::diesel_result_error_response)?;
    let files: Vec<FileVersion> = schema::file_version::table
        .filter(schema::file_version::version_id.eq(version_id))
        .select(FileVersion::as_select())
        .load(&mut conn)
        .await
        .map_err(db::diesel_result_error_response)?;

    Ok((
        StatusCode::OK,
        Json(VersionData {
            id: version.id,
            account_id: version.account_id,
            created: version.created,
            meta: version.meta,
            files: files,
        }),
    ))
}

// ## TODO ##
// Search for and list versions with the given parameters.
