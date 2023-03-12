#!/bin/sh

docker-compose down
docker build -t app .
docker-compose build
docker-compose up -d
