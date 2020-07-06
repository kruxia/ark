FROM rust:1.44-slim-buster as build
LABEL maintainer="Sean Harrison <sah@kruxia.com>"

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        subversion \
        nano \
        pkg-config \
        libssl-dev \
        postgresql-client \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /var/api

RUN cargo install systemfd cargo-watch 
COPY ./ ./
RUN cargo build

RUN useradd -m -d /var/svn apache

EXPOSE 8000

CMD ["systemfd", "--no-pid", "-s", "http::0.0.0.0:8000", "--", "cargo", "watch", "-x", "run"]
