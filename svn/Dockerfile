FROM debian:buster-slim
LABEL maintainer="Sean Harrison <sah@kruxia.com>"

# -- subversion apache server --
RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        apache2 \
        libapache2-mod-svn \
        nano \
    && apt-get upgrade \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /etc/apache2
COPY ./000-default.conf /etc/apache2/sites-available/000-default.conf

EXPOSE 80

CMD ["/usr/sbin/apachectl", "-D", "FOREGROUND"]
