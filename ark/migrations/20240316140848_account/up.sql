
CREATE TABLE account (
    id      uuid        primary key default gen_random_uuid(),
    created timestamptz not null default current_timestamp,
    title   text,
    meta    jsonb
);