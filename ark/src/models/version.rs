use crate::models::file::FileVersion;
use crate::schema;
use chrono::{DateTime, Utc};
use diesel::prelude::*;
use serde::{Deserialize, Serialize};

/// A single Version
#[derive(Serialize, Selectable, Queryable, QueryableByName, Debug)]
#[diesel(table_name = schema::version)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct Version {
    pub id: i64,
    pub account_id: i64,
    pub created: DateTime<Utc>,
    pub meta: Option<serde_json::Value>,
}

/// Input to create a new Version
#[derive(Deserialize, Insertable, Debug)]
#[diesel(table_name = schema::version)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct NewVersion {
    pub id: Option<i64>,
    pub account_id: i64,
    pub meta: Option<serde_json::Value>,
}

/// Data for a Version, which joins the Version object with the FileVersions it includes
#[derive(Serialize, Debug)]
pub struct VersionData {
    pub id: i64,
    pub account_id: i64,
    pub created: DateTime<Utc>,
    pub meta: Option<serde_json::Value>,
    pub files: Vec<FileVersion>,
}
