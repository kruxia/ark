use axum::{http::StatusCode, response::Json};
use serde::Serialize;
use std::fmt::Display;

/// Return ErrorResponse struct with details of any error that occurs
#[derive(Serialize)]
pub struct ErrorResponse {
    error: String,
    // message: String
}

// pub enum InternalError {
//     DieselResultError(diesel::result::Error),
//     S3CreateBucketError(aws_sdk_s3::operation::create_bucket::CreateBucketError),
//     S3ListBucketsError(aws_sdk_s3::operation::list_buckets::ListBucketsError),
// }

/// Any error_response maps to a `500 Internal Server Error` response.
pub fn error_response<E>(err: E) -> (StatusCode, Json<ErrorResponse>)
where
    E: std::error::Error,
{
    let status_code = StatusCode::INTERNAL_SERVER_ERROR;
    (
        status_code,
        Json(ErrorResponse {
            error: err.to_string(),
        }),
    )
}

// pub enum ErrorLevel {
//     Notice,
//     Warn,
//     Error,
//     Critical,
// }

// pub fn ark_error<E>(err: E, message: &str) -> ArkError
pub fn ark_error<E>(err: E) -> ArkError
where
    E: std::error::Error,
{
    ArkError {
        error: err.to_string(),
        // message: message.to_string(),
    }
}

#[derive(Debug)]
pub struct ArkError {
    error: String,
    // message: String,
}

impl Display for ArkError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        // write!(f, "{}: {}", self.error, self.message)
        write!(f, "{}", self.error)
    }
}

impl std::error::Error for ArkError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        None
    }
}

impl core::convert::From<diesel::result::Error> for ArkError {
    fn from(err: diesel::result::Error) -> ArkError {
        let message = err.to_string();
        ArkError {
            error: format!("Diesel result error: {message}"),
        }
    }
}
