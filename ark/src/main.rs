use axum::{
    async_trait,
    extract::{FromRef, FromRequestParts},
    http::{request, StatusCode},
    response::Json,
    routing::{get, post},
    Router,
};
use chrono::{DateTime, Utc};
use diesel::prelude::*;
use diesel_async::{
    pooled_connection::AsyncDieselConnectionManager, AsyncPgConnection, RunQueryDsl,
};
use serde::{Deserialize, Serialize};
use tokio::net::TcpListener;
use tower_http::trace::TraceLayer;
use uuid::Uuid;

type Pool = bb8::Pool<AsyncDieselConnectionManager<AsyncPgConnection>>;
struct DatabaseConnection(
    bb8::PooledConnection<'static, AsyncDieselConnectionManager<AsyncPgConnection>>,
);

#[tokio::main]
async fn main() {
    // tracing
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .init();

    tracing::debug!("Initialized tracing");

    // database
    let db_url: String = env!("DATABASE_URL").to_string();
    let db_config: AsyncDieselConnectionManager<AsyncPgConnection> =
        AsyncDieselConnectionManager::<AsyncPgConnection>::new(db_url);
    let pool: Pool = Pool::builder()
        // .max_size(4)
        // .min_idle(1)
        .build(db_config)
        .await
        .unwrap();

    // build our application with a route
    let app: Router = Router::new()
        .route("/", get(home))
        .route("/accounts", get(search_accounts))
        .route("/accounts", post(create_account))
        .layer(TraceLayer::new_for_http())
        .with_state(pool);

    // run our app with hyper, listening globally on port 8000
    let addr: &str = "0.0.0.0:8000";
    let listener: TcpListener = TcpListener::bind(addr).await.unwrap();
    tracing::info!("Listening on {addr}");
    axum::serve(listener, app).await.unwrap();
}

#[derive(Serialize, Debug)]
struct Home {
    message: String,
    version: String,
}

async fn home() -> (StatusCode, Json<Home>) {
    let data: Home = Home {
        message: "Welcome to Ark".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
    };
    tracing::debug!("{data:?}");
    (StatusCode::OK, Json(data))
}

// the input to our `account` handler
#[derive(Serialize, Selectable, Queryable, Debug)]
#[diesel(table_name = ark::schema::account)]
#[diesel(check_for_backend(diesel::pg::Pg))]
struct Account {
    id: Uuid,
    created: DateTime<Utc>,
    title: Option<String>,
    meta: Option<serde_json::Value>,
}

#[derive(Deserialize, Insertable, Debug)]
#[diesel(table_name = ark::schema::account)]
#[diesel(check_for_backend(diesel::pg::Pg))]
struct NewAccount {
    id: Option<Uuid>,
    created: Option<DateTime<Utc>>,
    title: Option<String>,
    meta: Option<serde_json::Value>,
}

async fn create_account(
    DatabaseConnection(mut conn): DatabaseConnection,
    Json(new_account): Json<NewAccount>,
) -> Result<Json<Account>, (StatusCode, Json<ErrorResponse>)> {
    let record = diesel::insert_into(ark::schema::account::table)
        .values(new_account)
        .returning(Account::as_returning())
        .get_result(&mut conn)
        .await
        .map_err(internal_error)?;
    tracing::debug!("{record:?}");
    Ok(Json(record))
}

async fn search_accounts(
    // Parse the request body as JSON into a `SearchAccount` type Json(payload):
    // Json<SearchAccount>,
    DatabaseConnection(mut conn): DatabaseConnection,
) -> Result<Json<Vec<Account>>, (StatusCode, Json<ErrorResponse>)> {
    let data: Vec<Account> = ark::schema::account::table
        .select(Account::as_select())
        .load(&mut conn)
        .await
        .map_err(internal_error)?;

    // this will be converted into a JSON response
    // with a status code of `200 OK`
    tracing::debug!("{data:?}");
    Ok(Json(data))
}

/// Extract DatabaseConnection from Request
#[async_trait]
impl<S> FromRequestParts<S> for DatabaseConnection
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
            pool.get_owned().await.map_err(internal_error)?;

        Ok(Self(conn))
    }
}

// -- Errors --

/// Return ErrorResponse struct with details of any error that occurs
#[derive(Serialize)]
struct ErrorResponse {
    detail: String,
}

/// Any internal_error maps to a `500 Internal Server Error` response.
fn internal_error<E>(err: E) -> (StatusCode, Json<ErrorResponse>)
where
    E: std::error::Error,
{
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(ErrorResponse {
            detail: err.to_string(),
        }),
    )
}
