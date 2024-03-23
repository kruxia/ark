#!/bin/bash
set -eu
PACKAGE_PATH=$(dirname $(dirname $0))
diesel migration run

# for fixture in $(ls ${PACKAGE_PATH}/fixtures/*.py); do
#     echo Load fixtures: $fixture
#     ${PACKAGE_PATH}/$fixture
# done