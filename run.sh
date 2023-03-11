#!/bin/bash
#cat config/prod_config.yaml | envsubst > config/config.yaml

sleep 5

echo Starting Alembic migrations
alembic upgrade head
echo Ending Alembic migrations
python main.py
