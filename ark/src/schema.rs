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
    content (id) {
        id -> Uuid,
        account_id -> Uuid,
        created -> Timestamptz,
        filesize -> Int8,
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
    file_item (account_id, filepath, version_id) {
        account_id -> Uuid,
        filepath -> Text,
        version_id -> Uuid,
        content_id -> Uuid,
        created -> Timestamptz,
        mimetype -> Text,
        meta -> Nullable<Jsonb>,
    }
}

diesel::table! {
    file_version (id) {
        id -> Uuid,
        account_id -> Uuid,
        created -> Timestamptz,
        meta -> Nullable<Jsonb>,
    }
}

diesel::table! {
    mimetype (name) {
        name -> Varchar,
    }
}

diesel::joinable!(content -> account (account_id));
diesel::joinable!(ext_mimetype -> mimetype (name));
diesel::joinable!(file_item -> account (account_id));
diesel::joinable!(file_item -> content (content_id));
diesel::joinable!(file_item -> file_version (version_id));
diesel::joinable!(file_item -> mimetype (mimetype));
diesel::joinable!(file_version -> account (account_id));

diesel::allow_tables_to_appear_in_same_query!(
    account,
    content,
    ext_mimetype,
    file_item,
    file_version,
    mimetype,
);
