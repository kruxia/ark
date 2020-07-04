#!/bin/bash

# make sure the supporting services are running
docker-compose up -d

# make sure the postgres test server exists
psql -e -q -c "DROP DATABASE IF EXISTS ${DATABASE_NAME}_test;" ${DATABASE_URL}
psql -e -q -c "CREATE DATABASE ${DATABASE_NAME}_test;" ${DATABASE_URL}

# some of the tests change env::var values without mutex, so we can only use one thread
# (TODO: Make these tests thread-safe.)

DATABASE_URL="${DATABASE_URL}_test" cargo test $@ -- --test-threads=1
