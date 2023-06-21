#!/bin/bash

cd src/fastapi_app/rest

printf "TEST_ENV=${TEST_ENV}" > .env

uvicorn server:app --host "0.0.0.0" --port 4747 --reload --reload-dir ../common/ --reload-dir ../api/ --reload-dir ../../../etc/ --reload-include *.json
