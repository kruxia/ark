FROM alpine
LABEL maintainer="Sean Harrison <sah@kruxia.com>"

# -- subversion apache server --
# NOTE: Installing apache2 on Alpine creates user apache -u 100 -g 101
RUN apk update \
    && apk add \
        apache2 \
        apache2-webdav \
        apache2-mod-wsgi \
        curl \
        mod_dav_svn \
        python3 \
        py3-pip \
        subversion \
    && apk upgrade \
    && rm -rf /var/cache/apk/*

WORKDIR /var/ark/svn

COPY ./req/ ./req/
RUN pip install -r ./req/install.txt 

RUN mkdir -p /var/svn \
    && chown apache:apache -R /var/svn

# COPY ./conf/httpd.conf /etc/apache2/httpd.conf
# COPY ./conf/dav_svn.conf /etc/apache2/conf.d/dav_svn.conf
# COPY ./conf/default-svn.conf /etc/apache2/conf.d/default.conf
COPY ./ /var/ark/svn
RUN rm /etc/apache2/httpd.conf /etc/apache2/conf.d/default.conf \
    && ln -s /var/ark/svn/conf/httpd.conf /etc/apache2/httpd.conf \
    && ln -s /var/ark/svn/conf/dav_svn.conf /etc/apache2/conf.d/dav_svn.conf \
    && ln -s /var/ark/svn/conf/default-svn.conf /etc/apache2/conf.d/default.conf

RUN pip install -e .

EXPOSE 80

CMD ["/usr/sbin/httpd", "-D", "FOREGROUND"]
