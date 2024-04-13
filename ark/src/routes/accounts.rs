use crate::{
    db, errors,
    models::account::{Account, NewAccount},
    schema::account,
    AppState,
};
use axum::{extract::State, http::StatusCode, response::Json};
use diesel::prelude::*;
use diesel_async::scoped_futures::ScopedFutureExt;
use diesel_async::AsyncConnection;
use diesel_async::RunQueryDsl;

/// Create a new account or update an existing one.
pub async fn upsert(
    State(state): State<AppState>,
    Json(new_account): Json<NewAccount>,
) -> Result<(StatusCode, Json<Account>), (StatusCode, Json<errors::ErrorResponse>)> {
    // get a connection to the pool
    let mut conn = state.pool.get().await.map_err(db::pool_error_response)?;

    // Create or update the account database record.
    let record = conn
        .transaction::<Account, errors::ArkError, _>(|mut conn| {
            async move {
                // create or update the database record
                let record = diesel::insert_into(account::table)
                    .values(&new_account)
                    .on_conflict(account::id)
                    .do_update()
                    .set(&new_account)
                    .returning(Account::as_returning())
                    .get_result(&mut conn)
                    .await
                    .map_err(db::diesel_result_error)?;

                Ok(record)
            }
            .scope_boxed()
        })
        .await
        .map_err(errors::error_response)?;

    Ok((StatusCode::CREATED, Json(record)))
}

/// Search for accounts (**TODO**: with the given parameters).
pub async fn search(
    db::Connection(mut conn): db::Connection,
    // Parse the request body as JSON into a `SearchAccount` type Json(payload):
    // Json<SearchAccount>,
) -> Result<Json<Vec<Account>>, (StatusCode, Json<errors::ErrorResponse>)> {
    let data: Vec<Account> = account::table
        .select(Account::as_select())
        .load(&mut conn)
        .await
        .map_err(db::diesel_result_error_response)?;

    // this will be converted into a JSON responses
    // with a status code of `200 OK`
    tracing::debug!("{data:?}");
    Ok(Json(data))
}
