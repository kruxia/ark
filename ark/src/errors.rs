use axum::{http::StatusCode, response::Json};
use serde::Serialize;

/// Return ErrorResponse struct with details of any error that occurs
#[derive(Serialize)]
pub struct ErrorResponse {
    error: String,
}

/// Any internal_error maps to a `500 Internal Server Error` response.
pub fn internal_error<E>(err: E) -> (StatusCode, Json<ErrorResponse>)
where
    E: std::error::Error,
{
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(ErrorResponse {
            error: err.to_string(),
        }),
    )
}
