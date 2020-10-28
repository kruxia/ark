-- Your SQL goes here

BEGIN;
CREATE TABLE ark.projects (
    id          uuid primary key default gen_random_uuid(),
    name        varchar not null unique,
    created     timestamptz default now(),
    modified    timestamptz,    -- when the archive was last modified
    size        bigint,         -- the archive filesystem size
    rev         integer,        -- the archive latest revision
    descr       text
);
COMMIT;