FROM rust:1.44-slim-buster as build
LABEL maintainer="Sean Harrison <sah@kruxia.com>"

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        subversion \
        nano \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /var/api
COPY ./ ./
RUN cargo build --release

FROM debian:buster-slim as prod
COPY --from=build /var/api/target/release/ark-api /usr/local/bin/ark-api

WORKDIR /var/svn
USER www-data

EXPOSE 8000

CMD ["ark-api"]

