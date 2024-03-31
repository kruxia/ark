use crate::schema;
use chrono::{DateTime, Utc};
use diesel::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Serialize, Selectable, Queryable, Debug)]
#[diesel(table_name = schema::content)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct Content {
    pub id: Uuid,
    pub account_id: Uuid,
    pub created: DateTime<Utc>,
    pub filesize: u64,
    pub meta: Option<serde_json::Value>,
}

#[derive(Deserialize, Insertable, Debug)]
#[diesel(table_name = schema::content)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct NewContent {
    pub id: Option<Uuid>,
    pub account_id: Uuid,
    pub created: Option<DateTime<Utc>>,
    pub filesize: Option<u64>,
    pub meta: Option<serde_json::Value>,
}
