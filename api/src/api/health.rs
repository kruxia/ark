use crate::api;
use actix_web::{HttpResponse, Result};
use futures::join;
use reqwest;
use serde::Serialize;
use std::{env, format, fs};

#[derive(Serialize)]
struct HealthStatus {
    files: api::Message,
    archive: api::Message,
    postgres: api::Message,
}

pub async fn index() -> Result<HttpResponse> {
    // query the health of services in parallel (by using join!)
    let (archive_files_status, archive_server_status, postgresql_status) = join!(
        archive_files_health(),
        archive_server_health(),
        postgresql_health(),
    );

    // return HealthStatus with the status of each service
    Ok(HttpResponse::Ok().json(
        HealthStatus {
            files: archive_files_status,
            archive: archive_server_status,
            postgres: postgresql_status,
        }
    ))
}

async fn archive_files_health() -> api::Message {
    match env::var("ARCHIVE_FILES") {
        Err(_) => api::Message {
            status: 404,
            message: "environment variable ARCHIVE_FILES does not exist".to_string(),
        },
        Ok(archive_files) => match fs::metadata(&archive_files) {
            Ok(_) => api::Message {
                status: 200,
                message: "Ok".to_string(),
            },
            Err(_) => api::Message {
                status: 404,
                message: format!("ARCHIVE_FILES NOT FOUND: {}", &archive_files).to_string(),
            },
        },
    }
}

async fn archive_server_health() -> api::Message {
    match env::var("ARCHIVE_SERVER") {
        Err(err) => api::Message {
            status: 404,
            message: format!("Error: {}", &err).to_string(),
        },
        Ok(archive_server) => match reqwest::get(&archive_server).await {
            Err(err) => api::Message {
                status: 502,
                message: format!("Error: {}", &err).to_string(),
            },
            Ok(_) => api::Message {
                status: 200,
                message: "Ok".to_string(),
            }
        }
    }
}

async fn postgresql_health() -> api::Message {
    api::Message {
        status: 501,
        message: "Not Implemented".to_string(),
    }
}
