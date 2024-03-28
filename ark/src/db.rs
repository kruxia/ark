use crate::{
    errors::{error_response, ArkError, ArkErrorKind, ErrorResponse},
    AppState,
};
use axum::{
    async_trait,
    extract::{FromRef, FromRequestParts},
    http::{request, StatusCode},
    response::Json,
};
use diesel::result::DatabaseErrorKind;
use diesel_async::{pooled_connection::AsyncDieselConnectionManager, AsyncPgConnection};

/// Pool - convenient shorthand
pub type Pool = bb8::Pool<AsyncDieselConnectionManager<AsyncPgConnection>>;

// Connection - represent a database connection
pub struct Connection(
    pub bb8::PooledConnection<'static, AsyncDieselConnectionManager<AsyncPgConnection>>,
);

/// Extract Connection from Request
#[async_trait]
impl<S> FromRequestParts<S> for Connection
where
    S: Send + Sync,
    AppState: FromRef<S>,
{
    type Rejection = (StatusCode, Json<ErrorResponse>);

    async fn from_request_parts(
        _parts: &mut request::Parts,
        state: &S,
    ) -> Result<Self, Self::Rejection> {
        let app_state: AppState = AppState::from_ref(state);

        let conn: bb8::PooledConnection<'_, AsyncDieselConnectionManager<AsyncPgConnection>> =
            app_state
                .pool
                .get_owned()
                .await
                .map_err(pool_error_response)?;

        Ok(Self(conn))
    }
}

// Pool Errors

pub fn pool_error_response<E: std::fmt::Debug>(
    err: bb8::RunError<E>,
) -> (StatusCode, Json<ErrorResponse>) {
    error_response(ArkError {
        kind: ArkErrorKind::SystemError,
        error: format!("{:?}", err),
    })
}

// Database Errors

impl core::convert::From<diesel::result::Error> for ArkError {
    fn from(err: diesel::result::Error) -> ArkError {
        diesel_result_error(err)
    }
}

pub fn diesel_result_error_response(
    err: diesel::result::Error,
) -> (StatusCode, Json<ErrorResponse>) {
    error_response(diesel_result_error(err))
}

pub fn diesel_result_error(err: diesel::result::Error) -> ArkError {
    ArkError {
        kind: diesel_ark_error_kind(&err),
        error: format!("{:?}", err),
    }
}

fn diesel_ark_error_kind(err: &diesel::result::Error) -> ArkErrorKind {
    match err {
        diesel::result::Error::DatabaseError(dberr, _) => match dberr {
            // value errors
            DatabaseErrorKind::CheckViolation => ArkErrorKind::ValueError,
            DatabaseErrorKind::NotNullViolation => ArkErrorKind::ValueError,
            // key errors
            DatabaseErrorKind::ForeignKeyViolation => ArkErrorKind::ValueError,
            DatabaseErrorKind::UniqueViolation => ArkErrorKind::ValueError,
            // system errors
            _ => ArkErrorKind::SystemError,
        },
        diesel::result::Error::NotFound => ArkErrorKind::KeyError,
        _ => ArkErrorKind::SystemError,
    }
}
