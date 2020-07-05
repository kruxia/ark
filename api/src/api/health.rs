use crate::api;
use crate::AppData;
use actix_web::{web, HttpRequest, HttpResponse, Result};
use futures;
use reqwest;
use serde::{Deserialize, Serialize};
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
                message: "OK".to_string(),
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
            Ok(resp) => api::StatusMessage {
                status: resp.status().as_u16(),
                message: resp.status().canonical_reason().unwrap().to_string(),
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
            message: "OK".to_string(),
        },
    }
}

#[cfg(test)]
mod tests {
    use actix_web::test;
    use serde_json;
    use std::format;
    use crate::get_database_pool;
    use super::*;

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
    // {"files": {"status": 200, "message": "OK"}, ...}
    #[actix_rt::test]
    async fn test_archive_files_ok() {
        env::set_var("ARCHIVE_FILES", "/"); // root folder always exists
        let req = test::TestRequest::default().to_http_request();
        let app_data = web::Data::new(AppData { database: get_database_pool(1).await });
        let mut resp = index(req, app_data).await.unwrap();
        let bytes = test::load_stream(resp.take_body()).await.unwrap();
        let health_data = serde_json::from_slice::<HealthStatus>(&bytes).unwrap();
        assert_eq!(health_data.files.status, 200);
        assert_eq!(health_data.files.message, "OK");
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
    // {"archive": {"status": 200, "message": "OK"}, ...}
    #[actix_rt::test]
    async fn test_archive_server_ok() {
        let req = test::TestRequest::default().to_http_request();
        let app_data = web::Data::new(AppData { database: get_database_pool(1).await });
        let mut resp = index(req, app_data).await.unwrap();
        
        let bytes = test::load_stream(resp.take_body()).await.unwrap();
        let health_data = serde_json::from_slice::<HealthStatus>(&bytes).unwrap();
        assert_eq!(health_data.archive.status, 200);
        assert_eq!(health_data.archive.message, "OK");
    }

    // when ARCHIVE_SERVER is not set, returns
    // {"archive": {"status": 404, "message": "...ARCHIVE_SERVER is not set"}, ...}
    #[actix_rt::test]
    async fn test_archive_server_unset() {
        let archive_server = env::var("ARCHIVE_SERVER").unwrap();
        env::remove_var("ARCHIVE_SERVER");

        let req = test::TestRequest::default().to_http_request();
        let app_data = web::Data::new(AppData { database: get_database_pool(1).await });
        let mut resp = index(req, app_data).await.unwrap();

        env::set_var("ARCHIVE_SERVER", archive_server);

        let bytes = test::load_stream(resp.take_body()).await.unwrap();
        let health_data = serde_json::from_slice::<HealthStatus>(&bytes).unwrap();
        assert_eq!(health_data.archive.status, 404);
        assert_eq!(health_data.archive.message, "environment variable not found");
    }

    // when ARCHIVE_SERVER is set but not reachable, returns
    // {"archive": {"status": 502, "message": "..."}, ...}
    #[actix_rt::test]
    async fn test_archive_server_non_existent() {
        let archive_server = env::var("ARCHIVE_SERVER").unwrap();
        env::set_var("ARCHIVE_SERVER", "http://localhost.NONE:0000"); // non-existent

        let req = test::TestRequest::default().to_http_request();
        let app_data = web::Data::new(AppData { database: get_database_pool(1).await });
        let mut resp = index(req, app_data).await.unwrap();

        env::set_var("ARCHIVE_SERVER", archive_server);

        let bytes = test::load_stream(resp.take_body()).await.unwrap();
        let health_data = serde_json::from_slice::<HealthStatus>(&bytes).unwrap();
        assert_eq!(health_data.archive.status, 502);
        println!("health_data.archive.message = {:?}", health_data.archive.message);
        assert!(health_data.archive.message.contains("error trying to connect"));
    }

    // ---------------------------------------------------------------------------------
    
    // when DATABASE_URL is set and reachable, returns
    // {"database": {"status": 200, "message": "OK"}, ...}
    #[actix_rt::test]
    async fn test_database_url_ok() {
        let req = test::TestRequest::default().to_http_request();
        let app_data = web::Data::new(AppData { database: get_database_pool(1).await });
        let mut resp = index(req, app_data).await.unwrap();
        
        let bytes = test::load_stream(resp.take_body()).await.unwrap();
        let health_data = serde_json::from_slice::<HealthStatus>(&bytes).unwrap();
        assert_eq!(health_data.database.status, 200);
        assert_eq!(health_data.database.message, "OK");
    }

    // when DATABASE_URL is not set, returns
    // {"archive": {"status": 502, "message": "relative URL without a base"}, ...}
    #[actix_rt::test]
    async fn test_database_url_unset() {
        let database_url = env::var("DATABASE_URL").unwrap();
        env::remove_var("DATABASE_URL");

        let req = test::TestRequest::default().to_http_request();
        let app_data = web::Data::new(AppData { database: get_database_pool(1).await });
        let mut resp = index(req, app_data).await.unwrap();

        env::set_var("DATABASE_URL", database_url);

        let bytes = test::load_stream(resp.take_body()).await.unwrap();
        let health_data = serde_json::from_slice::<HealthStatus>(&bytes).unwrap();
        assert_eq!(health_data.database.status, 502);
        assert_eq!(health_data.database.message, "relative URL without a base");
    }

    // when DATABASE_URL is set but not reachable, returns
    // {"archive": {"status": 502, "message": "..."}, ...}
    #[actix_rt::test]
    async fn test_database_url_non_existent() {
        let database_url = env::var("DATABASE_URL").unwrap();
        env::set_var("DATABASE_URL", format!("{}_NONE", database_url)); // non-existent

        let req = test::TestRequest::default().to_http_request();
        let app_data = web::Data::new(AppData { database: get_database_pool(1).await });
        let mut resp = index(req, app_data).await.unwrap();

        env::set_var("DATABASE_URL", database_url);

        let bytes = test::load_stream(resp.take_body()).await.unwrap();
        let health_data = serde_json::from_slice::<HealthStatus>(&bytes).unwrap();
        assert_eq!(health_data.database.status, 502);
        println!("health_data.database.message = {:?}", health_data.database.message);
        assert!(health_data.database.message.contains("database \""));
        assert!(health_data.database.message.contains("\" does not exist"));
    }
}