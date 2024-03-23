use crate::{
    db, errors,
    models::account::{Account, NewAccount},
    schema,
};
use axum::{http::StatusCode, response::Json};
use diesel::prelude::*;
use diesel_async::RunQueryDsl;

pub async fn create(
    db::Connection(mut conn): db::Connection,
    Json(new_account): Json<NewAccount>,
) -> Result<Json<Account>, (StatusCode, Json<errors::ErrorResponse>)> {
    let record = diesel::insert_into(schema::account::table)
        .values(new_account)
        .returning(Account::as_returning())
        .get_result(&mut conn)
        .await
        .map_err(errors::internal_error)?;
    tracing::debug!("{record:?}");

    // create a bucket for the account
    // - (TODO: inside a block wrapping the db tx)
    // - (TODO: with a static client for greater efficiency)
    let _ = ark_s3::create_bucket(&ark_s3::new_client(), record.id.to_string())
        .await
        .map_err(errors::internal_error)?;

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
        .map_err(errors::internal_error)?;

    // this will be converted into a JSON response
    // with a status code of `200 OK`
    tracing::debug!("{data:?}");
    Ok(Json(data))
}
