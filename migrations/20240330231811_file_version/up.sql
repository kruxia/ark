/* 
## version

A version is an identifiable set of changes at a particular point in time. Every version
has zero or more objects; every object has one or more versions. Any set of changes is
made as a new version.

(TODO: versions are currently linear: The latest version is implicitly the most recent
one, and it is implicitly based on the previous one in time. Adding a "base_id" would
enable a tree of versions; also adding a "merge_id" would enable 2-way merges and
versions to be a DAG.)
*/

CREATE SEQUENCE version_id_seq AS bigint;
CREATE TABLE version (
    id          bigint      PRIMARY KEY DEFAULT big_id('version_id_seq'),
    account_id  bigint      NOT NULL REFERENCES account(id),
    created     timestamptz NOT NULL DEFAULT current_timestamp,
    meta        jsonb
);

/* 
## file_version

Every file version represents a particular file in a particular version. Each account has
its own set of versions and files. (TODO: A given file version has one content item
representing the content of the file. Content items can be referenced by many files.)
*/

CREATE TABLE file_version (
    account_id  bigint      NOT NULL REFERENCES account(id),
    filepath    text        NOT NULL, -- relative path in the account
    version_id  bigint      NOT NULL REFERENCES version(id),

    -- In a given account and version, filepath must be unique (filepath second so that
    -- the index can be used to look up all versions for a given account + filepath)
    PRIMARY KEY (account_id, filepath, version_id),

    created     timestamptz NOT NULL DEFAULT current_timestamp,
    mimetype    text        NOT NULL REFERENCES mimetype(name)
                                DEFAULT 'application/octet-stream',
    filesize    bigint      NOT NULL DEFAULT 0,
    meta        jsonb
);
