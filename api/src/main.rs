use actix_web::{web, App, HttpServer};
use listenfd::ListenFd;
use sqlx::postgres::PgPool;
use std::env;

mod api;

pub struct AppState {
    database: PgPool,
}

#[actix_rt::main]
async fn main() -> std::io::Result<()> {
    let mut listenfd = ListenFd::from_env();
    let max_size: u32 = 5;
    let database = PgPool::builder()
        .max_size(max_size)
        .build(match &env::var("DATABASE_URL") {
            Ok(url) => url,
            Err(_) => "",
        })
        .await
        .unwrap();
    let mut server = HttpServer::new(move || {
        App::new()
            .data(AppState {
                database: database.clone(),
            })
            .route("/", web::get().to(api::index))
            .route("/health", web::get().to(api::health::index))
    });

    server = if let Some(l) = listenfd.take_tcp_listener(0).unwrap() {
        server.listen(l)?
    } else {
        server.bind("127.0.0.1:8000")?
    };

    server.run().await
}
