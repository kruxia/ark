FROM rust:1.44-slim-buster
LABEL maintainer="Sean Harrison <sah@kruxia.com>"

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        subversion \
        nano \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

RUN cargo install systemfd cargo-watch

WORKDIR /var/api
USER www-data

EXPOSE 8000

CMD ["systemfd", "--no-pid", "-s", "http::8000", "--", "cargo", "watch", "-x", "run"]
