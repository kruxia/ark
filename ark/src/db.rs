use crate::errors::{error_response, ErrorResponse};
use axum::{
    async_trait,
    extract::{FromRef, FromRequestParts},
    http::{request, StatusCode},
    response::Json,
};
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
    Pool: FromRef<S>,
{
    type Rejection = (StatusCode, Json<ErrorResponse>);

    async fn from_request_parts(
        _parts: &mut request::Parts,
        state: &S,
    ) -> Result<Self, Self::Rejection> {
        let pool: Pool = Pool::from_ref(state);

        let conn: bb8::PooledConnection<'_, AsyncDieselConnectionManager<AsyncPgConnection>> =
            pool.get_owned().await.map_err(error_response)?;

        Ok(Self(conn))
    }
}
