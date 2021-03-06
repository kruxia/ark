# deployment Dockerfile
FROM python:3.8-slim-buster
LABEL maintainer="Sean Harrison <sah@kruxia.com>"

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        # run tools
        subversion \
        postgresql-client \
        # build tools
        curl \
        # development tools
        nano \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /var/ark

COPY req/ req/
RUN pip install -r req/install.txt

COPY ./ ./
RUN pip install -e .

# create user apache -u 100 -g 101 to match what is in kruxia/svn(:alpine) -- we will
# use this user for all svnadmin and svnlook
RUN userdel _apt \ 
    && groupadd -g 101 apache \
    && useradd -m -d /var/svn -u 100 -g 101 apache \
    && chown -R apache:apache svntemplate

EXPOSE 8000

# for this development image, use uvicorn --reload
ENTRYPOINT ["/var/ark/docker-entrypoint.sh"]
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
