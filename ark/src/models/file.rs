use crate::schema;
use chrono::{DateTime, Utc};
use diesel::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Serialize, Selectable, Queryable, Debug)]
#[diesel(table_name = schema::ext_mimetype)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct ExtMimetype {
    pub ext: String,
    pub name: String,
}

#[derive(Serialize, Selectable, Queryable, Debug)]
#[diesel(table_name = schema::file_version)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct FileVersion {
    pub account_id: Uuid,
    pub version_id: Uuid,
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
    pub account_id: Uuid,
    pub version_id: Uuid,
    pub filepath: String,
    pub filesize: i64,

    pub mimetype: String,
    pub meta: Option<serde_json::Value>,
}
