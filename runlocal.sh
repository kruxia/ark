#!/bin/bash

CWD=$(pwd)

docker-compose up -d api

cd $(dirname $0)/ui
mkdir -p dist 
cp -R public/ dist/
node_modules/.bin/tailwind build src/static/main.css -o dist/static/main.css 

npm run watch &
npm run dev &

docker-compose logs -f

cd $CWD
