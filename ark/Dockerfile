FROM rust:1.77-bullseye as build
WORKDIR /opt/ark
RUN apt-get update \
    && apt-get install -y upx 
COPY Cargo.lock Cargo.toml ./
COPY ./ark ./ark
COPY ./ark-s3 ./ark-s3
RUN cargo build --release --bin ark 
RUN upx target/release/ark

FROM debian:bullseye-slim
# RUN apt-get update && apt-get install -y extra-runtime-dependencies && rm -rf /var/lib/apt/lists/*
RUN apt-get update \
    && apt-get install -y  --no-install-recommends libpq5 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /opt/ark/target/release/ark /usr/local/bin/ark
CMD ["ark"]
