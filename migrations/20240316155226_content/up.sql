/* 
## content

A content object is an identifiable item of content belonging to an account.
*/

CREATE SEQUENCE content_id AS smallint CYCLE;
CREATE TABLE content (
    id          uuid        PRIMARY KEY DEFAULT gen_id('content_id'),
    account_id  uuid        NOT NULL REFERENCES account(id),
    created     timestamptz NOT NULL DEFAULT current_timestamp,
    filesize    bigint      NOT NULL DEFAULT 0,
    meta        jsonb
);
