use axum::{
    http::StatusCode,
    response::Json,
    routing::{get, post, put},
    Router,
};
use diesel_async::{pooled_connection::AsyncDieselConnectionManager, AsyncPgConnection};
use routes::{accounts, files, versions};
use serde::Serialize;
use std::env;
use tokio::net::TcpListener;
use tower_http::trace::TraceLayer;

mod db;
mod errors;
mod models;
mod routes;
mod schema;

#[derive(Clone)]
struct AppState {
    pool: db::Pool,
    s3: aws_sdk_s3::Client,
    settings: Settings,
}

#[derive(Clone)]
struct Settings {
    s3_bucket_name: String,
}

#[tokio::main]
async fn main() {
    // tracing
    let tracing_level = match env::var("TRACING_LEVEL")
        .unwrap_or(String::from("INFO"))
        .as_str()
    {
        "TRACE" => tracing::Level::TRACE,
        "DEBUG" => tracing::Level::DEBUG,
        "INFO" => tracing::Level::INFO,
        "WARN" => tracing::Level::WARN,
        "ERROR" => tracing::Level::ERROR,
        _ => tracing::Level::INFO,
    };
    tracing_subscriber::fmt()
        .with_max_level(tracing_level)
        .init();
    tracing::debug!("Initialized tracing");

    // database pool
    let db_url: String = env::var("DATABASE_URL").unwrap();
    let db_config: AsyncDieselConnectionManager<AsyncPgConnection> =
        AsyncDieselConnectionManager::<AsyncPgConnection>::new(db_url);
    let pool_max_size: u32 = env::var("POOL_MAX_SIZE")
        .unwrap_or(String::from("4"))
        .parse()
        .unwrap();
    let pool_min_idle: u32 = env::var("POOL_MIN_IDLE")
        .unwrap_or(String::from("1"))
        .parse()
        .unwrap();
    let pool: db::Pool = db::Pool::builder()
        .max_size(pool_max_size)
        .min_idle(pool_min_idle)
        .build(db_config)
        .await
        .unwrap();

    let s3_client = ark_s3::client::new_client();

    let settings = Settings {
        s3_bucket_name: env::var("S3_BUCKET_NAME").unwrap(),
    };

    // make sure the s3 bucket exists
    if !ark_s3::bucket::exists(&s3_client, &settings.s3_bucket_name).await {
        ark_s3::bucket::create(&s3_client, &settings.s3_bucket_name)
            .await
            .unwrap();
        tracing::info!("Created storage bucket: {}", &settings.s3_bucket_name);
    }

    let state = AppState {
        pool,
        s3: s3_client,
        settings,
    };

    // build our application with a route
    let app: Router = Router::new()
        .route("/", get(home))
        .route("/accounts", post(accounts::upsert).get(accounts::search))
        .route("/accounts/:account_id/files", get(files::search))
        .route(
            "/accounts/:account_id/files/*filepath",
            put(files::upload_file).get(files::get_file_data),
        )
        .route(
            "/accounts/:account_id/history/*filepath",
            get(files::get_history),
        )
        // .route("/versions", post(versions::create_version))
        .route("/versions/:version_id", get(versions::get_version))
        .layer(TraceLayer::new_for_http())
        .with_state(state);

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
