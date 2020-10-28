#!/bin/bash
set -e
POSTGRESQL_CONF=/var/lib/postgresql/data/postgresql.conf

# Make the postgresql search path prioritize public schema before others. (This is
# necessary to keep a second copy of the diesel migrations table from being added to the
# ark schema and shadowing the diesel migrations table in the public schema. It also is
# a more sensible default way to handle schemas as namespaces, IMO.)

echo "search_path = 'public, "'"$user"'"'" >>$POSTGRESQL_CONF
