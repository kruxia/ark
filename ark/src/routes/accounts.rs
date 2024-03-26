use crate::{
    db, errors,
    models::account::{Account, NewAccount},
    schema, AppState,
};
use axum::{extract::State, http::StatusCode, response::Json};
use diesel::prelude::*;
use diesel_async::scoped_futures::ScopedFutureExt;
use diesel_async::AsyncConnection;
use diesel_async::RunQueryDsl;

pub async fn create(
    State(state): State<AppState>,
    Json(new_account): Json<NewAccount>,
) -> Result<Json<Account>, (StatusCode, Json<errors::ErrorResponse>)> {
    // get a connection to the pool
    let mut conn = state.pool.get().await.map_err(errors::error_response)?;

    let record = conn
        .transaction::<Account, errors::ArkError, _>(|mut conn| {
            async move {
                let record = diesel::insert_into(schema::account::table)
                    .values(new_account)
                    .returning(Account::as_returning())
                    .get_result(&mut conn)
                    .await?;

                // create a bucket for the account
                let _ = ark_s3::create_bucket(&state.s3, record.id.to_string())
                    .await
                    .map_err(errors::ark_error)?;

                Ok(record)
            }
            .scope_boxed()
        })
        .await
        .map_err(errors::error_response)?;

    Ok(Json(record))
}

pub async fn search(
    // Parse the request body as JSON into a `SearchAccount` type Json(payload):
    // Json<SearchAccount>,
    db::Connection(mut conn): db::Connection,
) -> Result<Json<Vec<Account>>, (StatusCode, Json<errors::ErrorResponse>)> {
    let data: Vec<Account> = crate::schema::account::table
        .select(Account::as_select())
        .load(&mut conn)
        .await
        .map_err(errors::error_response)?;

    // this will be converted into a JSON response
    // with a status code of `200 OK`
    tracing::debug!("{data:?}");
    Ok(Json(data))
}
