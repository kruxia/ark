/* 
## file_version

A file_version is an identifiable set of changes at a particular point in time. Every
file_version has zero or more objects; every object has one or more file_versions. Any set of
changes is made as a new file_version.

TODO: file_versions are currently linear: The latest file_version is implicitly the most
recent one, and it is implicitly based on the previous one in time. Adding a "base_id"
would enable a tree of file_versions; also adding a "merge_base_id" would enable 2-way merges
and file_versions to be a DAG.
*/

CREATE SEQUENCE file_version_id AS smallint CYCLE;
CREATE TABLE file_version (
    id          uuid        PRIMARY KEY DEFAULT gen_id('file_version_id'),
    account_id  uuid        NOT NULL REFERENCES account(id),
    created     timestamptz NOT NULL DEFAULT current_timestamp,
    meta        jsonb
);

/* 
## file_item

Every file item represents a particular file in a particular version. Each account has
its own set of versions and files. A given file version has one content item, which
represents the content of the file. (Content items can be referenced by many files.)
*/

CREATE TABLE file_item (
    account_id  uuid        NOT NULL REFERENCES account(id),
    filepath    text        NOT NULL, -- relative path in the account
    version_id  uuid        NOT NULL REFERENCES file_version(id),

    -- In a given account and version, a given filepath must be unique
    PRIMARY KEY (account_id, filepath, version_id),

    content_id  uuid        NOT NULL REFERENCES content(id),
    created     timestamptz NOT NULL DEFAULT current_timestamp,
    mimetype    text        NOT NULL REFERENCES mimetype(name)
                                DEFAULT 'application/octet-stream',
    meta        jsonb
);
