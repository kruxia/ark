#!/bin/bash

docker-compose up -d api

mkdir -p dist 
cp -R public/ dist/
tailwind build src/static/main.css -o dist/static/main.css 

npm run watch &
npm run dev &

docker-compose logs -f
