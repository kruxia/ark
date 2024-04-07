use crate::schema;
use chrono::{DateTime, Utc};
use diesel::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Deserialize, Debug)]
pub struct NewVersionRequest {
    pub account_id: Uuid,
    pub meta: Option<serde_json::Value>,
    pub files: Option<Vec<NewVersionRequestFile>>,
}

#[derive(Deserialize, Debug)]
pub struct NewVersionRequestFile {
    pub filepath: String,
    pub mimetype: Option<String>,
    pub meta: Option<serde_json::Value>,
}

#[derive(Deserialize, Insertable, Debug)]
#[diesel(table_name = schema::version)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct NewVersion {
    pub account_id: Uuid,
    pub meta: Option<serde_json::Value>,
}

#[derive(Serialize, Selectable, Queryable, Debug)]
#[diesel(table_name = schema::version)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct Version {
    pub id: Uuid,
    pub account_id: Uuid,
    pub created: DateTime<Utc>,
    pub meta: Option<serde_json::Value>,
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

#[derive(Serialize, Selectable, Queryable, Debug)]
#[diesel(table_name = schema::ext_mimetype)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct ExtMimetype {
    pub ext: String,
    pub name: String,
}
