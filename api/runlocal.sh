#!/bin/bash
cd $(dirname $0)
systemfd --no-pid -s http::8000 -- cargo watch -x run
