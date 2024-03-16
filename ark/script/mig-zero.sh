#!/bin/bash
set -eu
for m in $(diesel migration list); do
    if [[ ! $m == 'Migrations:' && ! $m == '[X]' && ! $m == '[' && ! $m == ']' \
       && ! $m == '00000000000000_diesel_initial_setup' ]]; then
        diesel migration revert
    fi
done
