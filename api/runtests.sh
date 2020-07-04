#!/bin/bash

# some of the tests change env::var values without mutex, so we can only use one thread
# (TODO: Make these tests thread-safe.)

cargo test $@ -- --test-threads=1
