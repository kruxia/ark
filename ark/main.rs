use axum::{http::StatusCode, response::Json, routing::get, Router};
use diesel_async::{pooled_connection::AsyncDieselConnectionManager, AsyncPgConnection};
use routes::accounts;
use serde::Serialize;
use tokio::net::TcpListener;
// use tower_http::trace::TraceLayer;

mod db;
mod errors;
mod models;
mod routes;
mod schema;

#[tokio::main]
async fn main() {
    // tracing
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::DEBUG)
        .init();

    tracing::debug!("Initialized tracing");

    // database
    let db_url: String = env!("DATABASE_URL").to_string();
    let db_config: AsyncDieselConnectionManager<AsyncPgConnection> =
        AsyncDieselConnectionManager::<AsyncPgConnection>::new(db_url);
    let pool: db::Pool = db::Pool::builder()
        // .max_size(4)
        // .min_idle(1)
        .build(db_config)
        .await
        .unwrap();

    // build our application with a route
    let app: Router = Router::new()
        .route("/", get(home))
        .route("/accounts", get(accounts::search).post(accounts::create))
        // .layer(TraceLayer::new_for_http())
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
