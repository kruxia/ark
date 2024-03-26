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
        filepath -> Text,
        created -> Timestamptz,
    }
}

diesel::table! {
    content_version (content_id, version_id) {
        content_id -> Uuid,
        version_id -> Uuid,
        account_id -> Uuid,
        created -> Timestamptz,
        mimetype -> Text,
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
    mimetype (name) {
        name -> Varchar,
    }
}

diesel::table! {
    version (id) {
        id -> Uuid,
        account_id -> Uuid,
        created -> Timestamptz,
        meta -> Nullable<Jsonb>,
    }
}

diesel::joinable!(content -> account (account_id));
diesel::joinable!(content_version -> account (account_id));
diesel::joinable!(content_version -> content (content_id));
diesel::joinable!(content_version -> mimetype (mimetype));
diesel::joinable!(content_version -> version (version_id));
diesel::joinable!(ext_mimetype -> mimetype (name));
diesel::joinable!(version -> account (account_id));

diesel::allow_tables_to_appear_in_same_query!(
    account,
    content,
    content_version,
    ext_mimetype,
    mimetype,
    version,
);
