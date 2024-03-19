
CREATE TABLE project (
    id          uuid        primary key default gen_random_uuid(),
    created     timestamptz not null default current_timestamp,
    title       text,
    account_id  uuid        not null references account(id),
    meta        jsonb
);