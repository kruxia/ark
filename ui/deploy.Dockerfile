# -- build stage --
FROM node:14-buster-slim as build
LABEL maintainer="Sean Harrison <sah@kruxia.com>"

WORKDIR /ui

COPY package.json package-lock.json ./
RUN npm install

COPY . /ui/

ARG API_URL
ARG ARCHIVE_URL
ENV NODE_ENV=production

RUN export PATH=node_modules/.bin:$PATH \
    && mkdir dist \
    && cp -R public/* dist/ \
    && tailwind build src/static/main.css -o dist/static/main.css \
    && webpack -p

# -- production stage --
FROM nginx:alpine

COPY --from=build /ui/dist/ /usr/share/nginx/html/
COPY ./default.conf /etc/nginx/conf.d/

# Using default nginx CMD
