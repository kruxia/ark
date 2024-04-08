use crate::schema;
use chrono::{DateTime, Utc};
use diesel::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Deserialize, Insertable, Debug)]
#[diesel(table_name = schema::version)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct NewVersion {
    pub id: Option<Uuid>,
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
