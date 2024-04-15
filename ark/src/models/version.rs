use crate::models::file::FileVersion;
use crate::schema;
use chrono::{DateTime, Utc};
use diesel::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Deserialize, Insertable, Debug)]
#[diesel(table_name = schema::version)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct NewVersion {
    pub id: Option<i64>,
    pub account_id: i64,
    pub meta: Option<serde_json::Value>,
}

#[derive(Serialize, Selectable, Queryable, Debug)]
#[diesel(table_name = schema::version)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct Version {
    pub id: i64,
    pub account_id: i64,
    pub created: DateTime<Utc>,
    pub meta: Option<serde_json::Value>,
}

#[derive(Serialize, Debug)]
pub struct VersionData {
    pub id: i64,
    pub account_id: i64,
    pub created: DateTime<Utc>,
    pub meta: Option<serde_json::Value>,
    pub files: Vec<FileVersion>,
}
