#!/bin/bash

cat configs/prod_config.yml > configs/config.yml

sleep 10

echo Starting Alembic migrations
alembic upgrade head
echo Ending Alembic migrations
python main.py
