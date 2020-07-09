# development Dockerfile
FROM python:3.8-slim-buster
LABEL maintainer="Sean Harrison <sah@kruxia.com>"

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        # run tools
        subversion \
        # build tools
        curl \
        # development tools
        nano \
        postgresql-client \
        ipython \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# install poetry

WORKDIR /var/api

COPY req/ req/
RUN pip install -r req/dev.txt

COPY ./ ./
RUN pip install -e .

# create user apache -u 100 -g 101 to match what is in kruxia/svn(:alpine) -- we will
# use this user for all svnadmin and svnlook
RUN userdel _apt \ 
    && groupadd -g 101 apache \
    && useradd -m -d /var/svn -u 100 -g 101 apache

EXPOSE 8000

# for this development image, use uvicorn --reload
ENTRYPOINT ["/var/api/docker-entrypoint.sh"]
CMD ["uvicorn", "api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
