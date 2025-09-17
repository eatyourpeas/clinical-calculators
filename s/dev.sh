#!/usr/bin/env bash
set -euo pipefail

# Dev helper for Dockerized workflow
# Usage:
#   s/dev.sh up        # build and start with reload
#   s/dev.sh down      # stop and remove containers
#   s/dev.sh logs      # tail logs
#   s/dev.sh rebuild   # rebuild image and restart
#   s/dev.sh sh        # open a shell in the running api container

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$here/.." && pwd)"
cd "$repo_root"

cmd="${1:-up}"

case "$cmd" in
  up)
    docker compose up --build -d
    echo "API available at http://localhost:8000 (docs at /docs)"
    ;;
  down)
    docker compose down
    ;;
  logs)
    docker compose logs -f
    ;;
  rebuild)
    docker compose build --no-cache
    docker compose up -d
    ;;
  sh)
    cid=$(docker compose ps -q api)
    if [[ -z "$cid" ]]; then
      echo "api container not running; starting..."
      docker compose up -d
      cid=$(docker compose ps -q api)
    fi
    docker exec -it "$cid" /bin/bash || docker exec -it "$cid" /bin/sh
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    echo "Usage: $0 {up|down|logs|rebuild|sh}" >&2
    exit 2
    ;;
esac
