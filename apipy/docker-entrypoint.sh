#!/bin/sh
set -eu

until psql ${DATABASE_URL} -q -e -c 'select current_timestamp'; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
done
>&2 echo "Postgres is up - continuing"

# Add any commands that depend on the database here (such as database migrations)

exec "$@"
