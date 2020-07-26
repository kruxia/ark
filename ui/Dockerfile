# -- build stage --
FROM node:14-buster-slim as build
LABEL maintainer="Sean Harrison <sah@kruxia.com>"

WORKDIR /ui

RUN apt-get update \
    && apt-get install -y inotify-tools

COPY package.json package-lock.json ./
RUN npm install -D

COPY . /ui/

ARG API_URL
ARG ARCHIVE_URL

RUN export PATH=node_modules/.bin:$PATH \
    && mkdir dist \
    && cp -R public/ dist/ \
    && tailwind build src/static/main.css -o dist/static/main.css 

EXPOSE 3000

CMD ["npm", "run", "dev"]
