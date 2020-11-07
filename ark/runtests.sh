#!/bin/bash
set -eu

export DATABASE_NAME=${DATABASE_NAME}_test
psql -e -q -c "DROP DATABASE IF EXISTS ${DATABASE_NAME}" $DATABASE_URL
psql -e -q -c "CREATE DATABASE ${DATABASE_NAME}" $DATABASE_URL
export DATABASE_URL=${DATABASE_URL}_test

diesel migration run

pytest $@
