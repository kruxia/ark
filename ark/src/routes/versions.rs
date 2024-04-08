/*
A version contains zero or more files.
*/
use crate::{
    db,
    errors::{error_response, ArkError, ErrorResponse},
    models::version::{NewVersion, Version},
    schema, AppState,
};
use axum::{extract::State, http::StatusCode, response::Json};
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

// ## TODO ##
// Search for and list versions with the given parameters.

// ## TODO ##
// Get the metadata and files that were modified in the given version.
