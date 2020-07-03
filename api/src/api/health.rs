use actix_web::{HttpResponse, Result};
use serde::{Serialize};
use std::{env, fs};

#[derive(Serialize)]
struct HealthStatus {
    files: u16,
    archive: u16,
    postgres: u16,
}

pub async fn index() -> Result<HttpResponse> {
    // check for the presence of the archive files at ARCHIVE_FILES
    let archive_files = env::var("ARCHIVE_FILES").unwrap();
    let archive_files_status = match fs::metadata(archive_files) {
        Ok(_) => 200,
        Err(_) => 404,
    };

    // check for the presence of the archive server at ARCHIVE_SERVER

    // check for the presence of the postgresql database at POSTGRES_DSN

    // return HealthStatus with the status of each service
    Ok(HttpResponse::Ok().json(HealthStatus {
        files: archive_files_status,
        archive: 0,
        postgres: 0,
    }))
}
