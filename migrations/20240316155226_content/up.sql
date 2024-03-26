/* 
## content

A content object is an identifiable item of content belonging to an account. Every
content object has 1 or more versions of the content item.
*/

CREATE TABLE content (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),

    account_id  uuid        NOT NULL REFERENCES account(id),
    filepath    text        NOT NULL, -- relative path in the account
                            UNIQUE(account_id, filepath),

    created     timestamptz NOT NULL DEFAULT current_timestamp
);

CREATE TABLE content_version(
    content_id  uuid        NOT NULL REFERENCES content(id),
    version_id  uuid        NOT NULL REFERENCES version(id),
                            PRIMARY KEY (content_id, version_id),

    account_id  uuid        NOT NULL REFERENCES account(id),
 
    created     timestamptz NOT NULL DEFAULT current_timestamp,
    mimetype    text        NOT NULL REFERENCES mimetype(name) 
                                DEFAULT 'application/octet-stream',
    filesize    bigint      NOT NULL DEFAULT 0,
    meta        jsonb
);
