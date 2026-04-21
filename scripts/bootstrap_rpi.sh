#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/health-project}"
APP_ROOT="$PROJECT_ROOT/app"
SHARED_ROOT="$PROJECT_ROOT/shared"
VENV_ROOT="$PROJECT_ROOT/venv"
LOG_ROOT="$PROJECT_ROOT/logs"

echo "[1/6] Create directories"
sudo mkdir -p "$PROJECT_ROOT" "$SHARED_ROOT/artifacts" "$SHARED_ROOT/dataset" "$LOG_ROOT"
sudo chown -R "$USER":"$USER" "$PROJECT_ROOT"

echo "[2/6] Create virtual environment"
python3 -m venv "$VENV_ROOT"
source "$VENV_ROOT/bin/activate"

echo "[3/6] Install requirements"
python -m pip install --upgrade pip
python -m pip install -r "$APP_ROOT/requirements.txt"

echo "[4/6] Prepare env file"
if [[ ! -f "$SHARED_ROOT/.env" ]]; then
  cp "$APP_ROOT/.env.example" "$SHARED_ROOT/.env"
  echo "Created $SHARED_ROOT/.env from .env.example"
fi

echo "[5/6] Ensure artifacts directory exists"
mkdir -p "$SHARED_ROOT/artifacts"

echo "[6/6] Bootstrap complete"
echo "Next: edit $SHARED_ROOT/.env, place model artifacts under $SHARED_ROOT/artifacts, then install systemd services."
