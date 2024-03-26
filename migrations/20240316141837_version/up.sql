/* 
## version

A version is an identifiable set of content changes at a particular point in time. Every
version has zero or more content objects; every content object has one or more versions.
Any set of content changes is made as a new version.
*/

CREATE SEQUENCE version_id AS smallint;
CREATE TABLE version (
    id          uuid        PRIMARY KEY DEFAULT gen_id('version_id'),
    account_id  uuid        NOT NULL REFERENCES account(id),
    created     timestamptz NOT NULL DEFAULT current_timestamp,
    meta        jsonb
);
