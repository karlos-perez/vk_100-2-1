#!/bin/bash
cat configs/prod_config.yaml | envsubst > configs/config.yaml

sleep 10

echo Starting Alembic migrations
alembic upgrade head
echo Ending Alembic migrations
python main.py
