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

# create user apache -u 100 -g 101 to match what is in kruxia/svn(:alpine) -- we will
# use this user for all svnadmin and svnlook
RUN groupadd -g 101 apache \
    & useradd -m -d /var/svn -u 100 -g 101 apache

EXPOSE 8000

# for this development image, use cargo watch to auto-reload changes in the code.
CMD ["systemfd", "--no-pid", "-s", "http::0.0.0.0:8000", "--", "cargo", "watch", "-x", "run"]
