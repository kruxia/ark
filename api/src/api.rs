use actix_web::{HttpResponse, Result};
use serde::{Serialize};

pub mod health;

#[derive(Serialize)]
struct Message {
    status: u16,
    message: String,
}

pub async fn index() -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(Message {
        status: 200,
        message: "Welcome to the Ark API".to_string(),
    }))
}
