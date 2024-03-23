
CREATE SEQUENCE version_id AS smallint;
CREATE TABLE version (
    id      uuid    primary key default gen_id('version_id'), -- globally ordered
    created timestamptz not null default current_timestamp,
    meta    jsonb
);