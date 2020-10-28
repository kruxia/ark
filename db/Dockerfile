# --------------
# -- COMPILER --
# --------------
# 
# Compile diesel so it's available for use as a migration tool in the database

FROM rust:slim-buster as compiler
LABEL maintainer="Sean Harrison <sah@kruxia.com>"

RUN apt-get update \
    && apt-get install -y \
        # build tools
        # - ca-certificates are necessary for curl and cargo install
        ca-certificates \
        curl \
        # - cargo build diesel-cli requires gcc, libpq5
        gcc \
        libc-dev-bin \
        libpq5 \
        libpq-dev \
    && apt-get upgrade -y 

RUN cargo install diesel_cli --no-default-features --features "postgres"

# -------------
# -- RELEASE --
# -------------
# 
# Copy the diesel binary to the postgres image so it's available for use

FROM postgres:13 as release
LABEL maintainer="Sean Harrison <sah@kruxia.com>"

WORKDIR /var/db

COPY --from=compiler /usr/local/cargo/bin/diesel /usr/local/bin/diesel

RUN apt-get update \
    && apt-get install -y --no-install-suggests --no-install-recommends \
        # run tools
        postgresql-client \
        # development tools
        nano \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

COPY ./docker-entrypoint-initdb.d/ /docker-entrypoint-initdb.d/
