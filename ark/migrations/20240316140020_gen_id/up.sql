-- gen_id(varchar) - generate the next id with the given smallint sequence.
CREATE OR REPLACE FUNCTION gen_id(varchar) RETURNS uuid AS $$
-- $1 = sequence name
SELECT (
    -- timestamp to ms resolution: 6 bytes (= 12 hex)
    lpad(to_hex((extract(epoch from clock_timestamp()) * 1000)::bigint), 12, '0')
    -- seq ($1) is smallint sequence (2 bytes = 4 hex)
    || lpad(to_hex(nextval($1)), 4, '0')
    -- 8 bytes (16 hex) of randomness
    || lpad(to_hex((random()*2147483647)::int), 8, '0')
    || lpad(to_hex((random()*2147483647)::int), 8, '0')
)::uuid;
$$ LANGUAGE SQL;
