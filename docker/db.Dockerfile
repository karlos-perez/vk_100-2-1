FROM postgres:14.7-alpine

COPY init.sql /docker-entrypoint-initdb.d/