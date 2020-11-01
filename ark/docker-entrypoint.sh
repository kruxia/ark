#!/bin/sh
set -eu

# wait for postgres to be up and running
until psql ${DATABASE_URL} -q -e -c 'select current_timestamp'; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
done
>&2 echo "Postgres is up - continuing"

# Add any commands that depend on the database here (such as database migrations)
diesel migration run

exec "$@"
