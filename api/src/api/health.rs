use crate::api;
use crate::AppData;
use actix_web::{web, HttpRequest, HttpResponse, Result};
use futures;
use reqwest;
use serde::{Deserialize, Serialize};
use serde_json;
use sqlx;
use std::{env, fs};

#[derive(Deserialize, Serialize)]
struct HealthStatus {
    files: api::StatusMessage,
    archive: api::StatusMessage,
    database: api::StatusMessage,
}

pub async fn index(_req: HttpRequest, app_state: web::Data<AppData>) -> Result<HttpResponse> {
    // query the health of services in parallel (by using join!)
    let (archive_files_status, archive_server_status, database_status) = futures::join!(
        archive_files_health(),
        archive_server_health(),
        database_health(app_state),
    );

    // return HealthStatus with the status of each service
    Ok(HttpResponse::Ok().json(HealthStatus {
        files: archive_files_status,
        archive: archive_server_status,
        database: database_status,
    }))
}

async fn archive_files_health() -> api::StatusMessage {
    match env::var("ARCHIVE_FILES") {
        Err(err) => api::StatusMessage {
            status: 404,
            message: err.to_string(),
        },
        Ok(archive_files) => match fs::metadata(&archive_files) {
            Err(err) => api::StatusMessage {
                status: 502,
                message: err.to_string(),
            },
            Ok(_) => api::StatusMessage {
                status: 200,
                message: "Ok".to_string(),
            },
        },
    }
}

async fn archive_server_health() -> api::StatusMessage {
    match env::var("ARCHIVE_SERVER") {
        Err(err) => api::StatusMessage {
            status: 404,
            message: err.to_string(),
        },
        Ok(archive_server) => match reqwest::get(&archive_server).await {
            Err(err) => api::StatusMessage {
                status: 502,
                message: err.to_string(),
            },
            Ok(_) => api::StatusMessage {
                status: 200,
                message: "Ok".to_string(),
            },
        },
    }
}

async fn database_health(app_state: web::Data<AppData>) -> api::StatusMessage {
    match sqlx::query("SELECT true")
        .execute(&app_state.database)
        .await
    {
        Err(err) => api::StatusMessage {
            status: 502,
            message: err.to_string(),
        },
        Ok(_) => api::StatusMessage {
            status: 200,
            message: "Ok".to_string(),
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::get_database_pool;
    use actix_web::test;

    // index returns 200 Ok (whether the underlying services are available or not)
    #[actix_rt::test]
    async fn test_index_ok() {
        let req = test::TestRequest::default().to_http_request();
        let app_data = web::Data::new(AppData { database: get_database_pool(1).await });
        let resp = index(req, app_data).await.unwrap();
        assert_eq!(resp.status(), 200);
    }
    
    // ---------------------------------------------------------------------------------

    // when ARCHIVE_FILES is set and the folder exists, returns
    // {"files": {"status": 200, "message": "Ok"}, ...}
    #[actix_rt::test]
    async fn test_archive_files_ok() {
        env::set_var("ARCHIVE_FILES", "/"); // root folder always exists
        let req = test::TestRequest::default().to_http_request();
        let app_data = web::Data::new(AppData { database: get_database_pool(1).await });
        let mut resp = index(req, app_data).await.unwrap();
        let bytes = test::load_stream(resp.take_body()).await.unwrap();
        let health_data = serde_json::from_slice::<HealthStatus>(&bytes).unwrap();
        assert_eq!(health_data.files.status, 200);
        assert_eq!(health_data.files.message, "Ok");
    }

    // when ARCHIVE_FILES is not set, returns
    // {"files": {"status": 404, "message": "...ARCHIVE_FILES is not set"}, ...}
    #[actix_rt::test]
    async fn test_archive_files_unset() {
        env::remove_var("ARCHIVE_FILES");
        let req = test::TestRequest::default().to_http_request();
        let app_data = web::Data::new(AppData { database: get_database_pool(1).await });
        let mut resp = index(req, app_data).await.unwrap();
        let bytes = test::load_stream(resp.take_body()).await.unwrap();
        let health_data = serde_json::from_slice::<HealthStatus>(&bytes).unwrap();
        assert_eq!(health_data.files.status, 404);
        assert_eq!(health_data.files.message, "environment variable not found");
    }

    // when ARCHIVE_FILES is set but does not exist, returns
    // {"files": {"status": 502, "message": "ARCHIVE_FILES NOT FOUND..."}, ...}
    #[actix_rt::test]
    async fn test_archive_files_non_existent() {
        env::set_var("ARCHIVE_FILES", ""); // empty folder does not exist
        let req = test::TestRequest::default().to_http_request();
        let app_data = web::Data::new(AppData { database: get_database_pool(1).await });
        let mut resp = index(req, app_data).await.unwrap();
        let bytes = test::load_stream(resp.take_body()).await.unwrap();
        let health_data = serde_json::from_slice::<HealthStatus>(&bytes).unwrap();
        assert_eq!(health_data.files.status, 502);
        assert!(health_data.files.message.contains("No such file or directory"));
    }

    // ---------------------------------------------------------------------------------
    
    // when ARCHIVE_SERVER is set and reachable, returns 
    // {"archive": {"status": 200, "message": "Ok"}, ...}

    // when ARCHIVE_SERVER is not set, returns
    // {"archive": {"status": 404, "message": "...ARCHIVE_SERVER is not set"}, ...}

    // when ARCHIVE_SERVER is set but not reachable, returns
    // {"archive": {"status": 502, "message": "..."}, ...}

    // ---------------------------------------------------------------------------------
    
    // when DATABASE_URL is set and reachable, returns
    // {"database": {"status": 200, "message": "Ok"}, ...}

    // when DATABASE_URL is not set, returns
    // {"archive": {"status": 404, "message": "...DATABASE_URL is not set"}, ...}

    // when DATABASE_URL is set but not reachable, returns
    // {"archive": {"status": 502, "message": "..."}, ...}

}