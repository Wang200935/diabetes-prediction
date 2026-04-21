#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/health-project}"
APP_ROOT="$PROJECT_ROOT/app"
SHARED_ROOT="$PROJECT_ROOT/shared"
VENV_ROOT="$PROJECT_ROOT/venv"

if [[ -f "$SHARED_ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$SHARED_ROOT/.env"
  set +a
fi

APP_BIND_HOST="${APP_BIND_HOST:-127.0.0.1}"
APP_BIND_PORT="${APP_BIND_PORT:-8320}"

cd "$APP_ROOT"
source "$VENV_ROOT/bin/activate"
exec uvicorn app.main:app --host "$APP_BIND_HOST" --port "$APP_BIND_PORT"
