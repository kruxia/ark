use axum::{http::StatusCode, response::Json};
use serde::Serialize;
use std::fmt::Display;

/// Return ErrorResponse struct with details of any error that occurs
#[derive(Serialize)]
pub struct ErrorResponse {
    pub error: String,
}

/// Any error_response maps to a `500 Internal Server Error` response.
pub fn error_response(err: ArkError) -> (StatusCode, Json<ErrorResponse>) {
    let status_code = match err.kind {
        ArkErrorKind::KeyError => StatusCode::NOT_FOUND,
        ArkErrorKind::ValueError => StatusCode::CONFLICT,
        ArkErrorKind::SystemError => StatusCode::INTERNAL_SERVER_ERROR,
    };
    (
        status_code,
        Json(ErrorResponse {
            error: err.to_string(),
        }),
    )
}

/// Generalized system error
pub fn ark_error<E>(err: E) -> ArkError
where
    E: std::error::Error,
{
    ArkError {
        kind: ArkErrorKind::SystemError,
        error: format!("{:?}", err),
    }
}

#[derive(Debug)]
pub struct ArkError {
    pub kind: ArkErrorKind,
    pub error: String,
}

#[derive(Debug)]
pub enum ArkErrorKind {
    ValueError,
    KeyError,
    SystemError,
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
