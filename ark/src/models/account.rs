use crate::schema;
use chrono::{DateTime, Utc};
use diesel::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

// the input to our `account` handler
#[derive(Serialize, Selectable, Queryable, Debug)]
#[diesel(table_name = schema::account)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct Account {
    #[serde(serialize_with = "uuid::serde::simple::serialize")]
    pub id: Uuid,
    pub created: DateTime<Utc>,
    pub title: Option<String>,
    pub meta: Option<serde_json::Value>,
}

#[derive(Deserialize, Insertable, Debug, AsChangeset)]
#[diesel(table_name = schema::account)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct NewAccount {
    pub id: Option<Uuid>,
    pub created: Option<DateTime<Utc>>,
    pub title: Option<String>,
    pub meta: Option<serde_json::Value>,
}
