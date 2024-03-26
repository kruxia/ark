#!/bin/bash
set -eu
NAME=$1; shift
TABLES=$@

diesel migration generate --version $(date -u +%Y%m%d%H%M%S) $NAME $TABLES
