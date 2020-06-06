FROM kruxia/app

# -- install the micro editor --
RUN echo deb http://deb.debian.org/debian buster-backports main contrib non-free \
        >>/etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        micro \
    && apt-get upgrade \
    && rm -rf /var/lib/apt/lists/*

