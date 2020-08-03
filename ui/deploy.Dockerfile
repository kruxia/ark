# -- build stage --
FROM node:14-buster-slim as build
LABEL maintainer="Sean Harrison <sah@kruxia.com>"

WORKDIR /ui

COPY package.json package-lock.json ./
RUN npm install

ARG API_URL
ARG ARCHIVE_URL
ENV NODE_ENV=production

COPY public/ public/
COPY src/ src/ 
RUN export PATH=node_modules/.bin:$PATH \
    && mkdir dist \
    && cp -R public/* dist/ \
    && tailwind build src/static/main.css -o dist/static/main.css

COPY ./ ./
RUN export PATH=node_modules/.bin:$PATH \
    && webpack -p

# -- production stage --
FROM nginx:alpine

COPY --from=build /ui/dist/ /usr/share/nginx/html/
COPY ./default.conf /etc/nginx/conf.d/

EXPOSE 3000

# Using default nginx CMD
