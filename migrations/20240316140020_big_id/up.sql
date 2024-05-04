/*
Create a function `big_id(varchar) that takes a sequence name as parameter and returns
the next big_id using that sequence and the current clock timestamp.

The ids created by this function are monotonically increasing bigints that don't
communicate anything about how many have been created.

Example usage:

```psql
# create sequence my_seq as bigint;
# select big_id('my_seq');
  big_id
-----------
 637754117
(1 row)

# create table my_table (
    id      bigint primary key default big_id('my_seq'),
    created timestamptz default current_timestamp,
    meta    jsonb    
);
# insert into my_table (meta) values (null);
INSERT 0 1
# select * from my_table;
     id     |            created            | meta
------------+-------------------------------+------
 1204795659 | 2024-04-15 03:13:24.826133+00 |
(1 row)
```

The ids created by this function are bigints based on the current clock timestamp minus
the base timestamp. The base timestamp is the clock timestamp at the time the
big_id(varchar) function was created. The timestamps are multiplied by 1 million to have
microsecond resolution. The id then has the nextval() of the given sequence added to it.

By this procedure, big_id(varchar) results in bigint ids that are reasonably small (as
compared with the clock timestamp), guaranteed monotonically increasing due to the
sequence, not communicating anything about the number of ids that have been created, and
with enough headroom to continue generating ids for many thousands of years.
*/

create or replace function create_big_id_exec(sql text) returns void as $$
begin
    execute sql;
end;
$$ language plpgsql;

select create_big_id_exec(
    $create_function$
        create function big_id(varchar) returns bigint as $$
        select (
            -- big_id is current timestamp minus the base timestamp for this function,
            -- plus the next value for the given sequence. The base timestamp is 1 year
            -- before when this function is defined. (Adding an additional year to the
            -- difference helps the early numbers have the same size.) Including a
            -- sequence ensures uniqueness.
            (extract(epoch from clock_timestamp())*1e6) 
            - $create_function$ ||
                (extract(epoch from clock_timestamp()-make_interval(1))*1e6)::bigint::text
                || $create_function$ 
            + nextval($1)
        );
        $$ language 'sql';
    $create_function$
);

drop function create_big_id_exec(text);
