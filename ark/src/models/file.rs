use crate::schema;
use chrono::{DateTime, Utc};
use diesel::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Selectable, Queryable, QueryableByName, Debug)]
#[diesel(table_name = schema::ext_mimetype)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct ExtMimetype {
    pub ext: String,
    pub name: String,
}

#[derive(Serialize, Selectable, Queryable, QueryableByName, Debug)]
#[diesel(table_name = schema::file_version)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct FileVersion {
    pub account_id: i64,
    pub version_id: i64,
    pub filepath: String,
    pub filesize: i64,

    pub created: DateTime<Utc>,
    pub mimetype: String,
    pub meta: Option<serde_json::Value>,
}

#[derive(Deserialize, Insertable, Debug)]
#[diesel(table_name = schema::file_version)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct NewFileVersion {
    pub account_id: i64,
    pub version_id: i64,
    pub filepath: String,
    pub filesize: i64,

    pub mimetype: String,
    pub meta: Option<serde_json::Value>,
}

#[derive(Serialize, Debug)]
pub struct FileHistory {
    pub account_id: i64,
    pub filepath: String,
    pub versions: Vec<FileVersion>,
}

#[derive(Deserialize, Debug)]
pub struct FileQuery {
    pub _version: Option<i64>,
}
