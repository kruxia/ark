// @generated automatically by Diesel CLI.

diesel::table! {
    account (id) {
        id -> Uuid,
        created -> Timestamptz,
        title -> Nullable<Text>,
        meta -> Nullable<Jsonb>,
    }
}

diesel::table! {
    content (id, version_id) {
        id -> Uuid,
        version_id -> Uuid,
        project_id -> Uuid,
        mimetype -> Text,
        size -> Int8,
        path -> Text,
        title -> Nullable<Text>,
        meta -> Nullable<Jsonb>,
    }
}

diesel::table! {
    ext_mimetype (ext) {
        ext -> Varchar,
        name -> Varchar,
    }
}

diesel::table! {
    mimetype (name) {
        name -> Varchar,
    }
}

diesel::table! {
    project (id) {
        id -> Uuid,
        created -> Timestamptz,
        title -> Nullable<Text>,
        account_id -> Uuid,
        meta -> Nullable<Jsonb>,
    }
}

diesel::table! {
    version (id) {
        id -> Uuid,
        created -> Timestamptz,
        meta -> Nullable<Jsonb>,
    }
}

diesel::joinable!(content -> mimetype (mimetype));
diesel::joinable!(content -> project (project_id));
diesel::joinable!(content -> version (version_id));
diesel::joinable!(ext_mimetype -> mimetype (name));
diesel::joinable!(project -> account (account_id));

diesel::allow_tables_to_appear_in_same_query!(
    account,
    content,
    ext_mimetype,
    mimetype,
    project,
    version,
);
