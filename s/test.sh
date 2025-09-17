#!/bin/bash -e

docker compose exec api pytest -v $*