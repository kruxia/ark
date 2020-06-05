FROM python:3.8-slim-buster

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        subversion \
        nano \
    && apt-get upgrade \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /var/svn
USER www-data

CMD ["python"]
