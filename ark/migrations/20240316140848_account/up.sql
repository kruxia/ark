
CREATE TABLE account (
    id      uuid        primary key default gen_random_uuid(),
    ts      timestamptz default current_timestamp,
    title   text,
    meta    jsonb
);