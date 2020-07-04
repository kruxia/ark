use crate::api;
use crate::AppState;
use actix_web::{web, HttpRequest, HttpResponse, Result};
use futures;
use reqwest;
use serde::Serialize;
use sqlx;
use std::{env, format, fs};

#[derive(Serialize)]
struct HealthStatus {
    files: api::StatusMessage,
    archive: api::StatusMessage,
    database: api::StatusMessage,
}

pub async fn index(_req: HttpRequest, app_state: web::Data<AppState>) -> Result<HttpResponse> {
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
        Err(_) => api::StatusMessage {
            status: 404,
            message: "environment variable ARCHIVE_FILES is not set".to_string(),
        },
        Ok(archive_files) => match fs::metadata(&archive_files) {
            Err(_) => api::StatusMessage {
                status: 502,
                message: format!("ARCHIVE_FILES NOT FOUND: {}", &archive_files).to_string(),
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
            message: format!("Error: {}", &err).to_string(),
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

async fn database_health(app_state: web::Data<AppState>) -> api::StatusMessage {
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
