use actix_web::{HttpResponse, Responder};

pub async fn index() -> impl Responder {
    HttpResponse::Ok().body("{\"status\": 200, \"message\": \"Welcome to the Ark API\"}")
}
