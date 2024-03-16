use axum::{http::StatusCode, routing::get, Json, Router};
// use diesel::sql_types::{Jsonb, Uuid};
use serde::{Deserialize, Serialize};
use serde_json::{Map, Value};
use tokio::net::TcpListener;
use uuid::Uuid;

#[tokio::main]
async fn main() {
    // initialize tracing
    tracing_subscriber::fmt::init();

    // build our application with a route
    let app: Router = Router::new()
        .route("/", get(home))
        .route("/accounts", get(search_accounts));

    // run our app with hyper, listening globally on port 8000
    let listener: TcpListener = TcpListener::bind("0.0.0.0:8000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

// basic handler that responds with a static string
async fn home() -> &'static str {
    "Hello, World!"
}

async fn search_accounts(// this argument tells axum to parse the request body
    // as JSON into a `SearchAccount` type
    // Json(payload): Json<SearchAccount>,
) -> (StatusCode, Json<Account>) {
    // insert your application logic here
    let mut meta: Map<String, Value> = Map::new();
    meta.insert("foo".to_string(), 3.into());
    meta.insert("βαρ".to_string(), "τηιρτυ".into());
    meta.insert("user_id".to_string(), Uuid::new_v4().to_string().into());
    let account: Account = Account {
        id: Uuid::new_v4(), // random id
        title: "Foo Bar".to_string(),
        meta: Some(meta),
    };

    // this will be converted into a JSON response
    // with a status code of `201 Created`
    (StatusCode::OK, Json(account))
}

// the input to our `account` handler
#[derive(Deserialize, Serialize)]
struct Account {
    id: Uuid,
    title: String,
    meta: Option<Map<String, Value>>,
}
