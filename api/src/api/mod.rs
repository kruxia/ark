use actix_web::{HttpRequest, HttpResponse, Result};
use serde::Serialize;

pub mod health;

#[derive(Serialize)]
struct StatusMessage {
    status: u16,
    message: String,
}

pub async fn index(_req: HttpRequest) -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(StatusMessage {
        status: 200,
        message: "Welcome to the Ark API".to_string(),
    }))
}

#[cfg(test)]
mod tests {
    use super::*;
    use actix_web::test;

    #[actix_rt::test]
    async fn test_index_ok() {
        let req = test::TestRequest::default().to_http_request();
        let resp = index(req).await.unwrap();
        assert_eq!(resp.status(), 200);
    }
}