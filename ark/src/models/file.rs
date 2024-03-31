use crate::schema;
use chrono::{DateTime, Utc};
use diesel::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Serialize, Selectable, Queryable, Debug)]
#[diesel(table_name = schema::file_version)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct FileVersion {
    pub id: Uuid,
    pub account_id: Uuid,
    pub created: DateTime<Utc>,
    pub meta: Option<serde_json::Value>,
}

#[derive(Deserialize, Insertable, Debug)]
#[diesel(table_name = schema::file_version)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct NewFileVersion {
    pub id: Option<Uuid>,
    pub account_id: Uuid,
    pub created: Option<DateTime<Utc>>,
    pub meta: Option<serde_json::Value>,
}

#[derive(Serialize, Selectable, Queryable, Debug)]
#[diesel(table_name = schema::file_item)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct FileItem {
    pub account_id: Uuid,
    pub version_id: Uuid,
    pub content_id: Uuid,
    pub filepath: String,
    pub created: DateTime<Utc>,
    pub mimetype: String,
    pub meta: Option<serde_json::Value>,
}

#[derive(Deserialize, Insertable, Debug)]
#[diesel(table_name = schema::file_item)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct NewFileItem {
    pub account_id: Uuid,
    pub version_id: Uuid,
    pub content_id: Uuid,
    pub filepath: String,
    pub created: Option<DateTime<Utc>>,
    pub mimetype: String,
    pub meta: Option<serde_json::Value>,
}
