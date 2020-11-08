FROM alpine
LABEL maintainer="Sean Harrison <sah@kruxia.com>"

# -- subversion apache server --
# NOTE: Installing apache2 on Alpine creates user apache -u 100 -g 101
RUN apk update \
    && apk add \
        apache2 \
        apache2-webdav \
        apache2-mod-wsgi \
        apache2-proxy \
        curl \
        mod_dav_svn \
        python3 \
        py3-pip \
        py3-psycopg2 \
        subversion \
    && apk upgrade \
    && rm -rf /var/cache/apk/*

RUN mkdir -p /var/svndata \
    && chown apache:apache -R /var/svndata

WORKDIR /var/svn

COPY ./req/ ./req/
RUN pip install -r ./req/install.txt 

COPY ./ /var/svn
RUN rm /etc/apache2/httpd.conf /etc/apache2/conf.d/default.conf \
    # symlinks into the share-mounted package make development so much easier.
    && ln -s /var/svn/conf/httpd.conf /etc/apache2/httpd.conf \
    && ln -s /var/svn/conf/dav_svn.conf /etc/apache2/conf.d/dav_svn.conf \
    && ln -s /var/svn/conf/default-svn.conf /etc/apache2/conf.d/default.conf

RUN pip install -e .

EXPOSE 80

CMD ["/usr/sbin/httpd", "-D", "FOREGROUND"]
