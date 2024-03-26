/* 
## account

Every object in ark belongs to a particular account. Each account exists in object
storage as a separate bucket, which eventually will have owner-customizable settings.
Users will have accounts, and accounts will have users with roles. 

No input fields are required -- even title is optional.
*/

CREATE TABLE account (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    created     timestamptz NOT NULL DEFAULT current_timestamp,
    title       text,
    meta        jsonb
);