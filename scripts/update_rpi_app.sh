#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/health-project}"
APP_ROOT="$PROJECT_ROOT/app"
VENV_ROOT="$PROJECT_ROOT/venv"
SHARED_ROOT="$PROJECT_ROOT/shared"
RETRAIN="${RETRAIN:-false}"

cd "$APP_ROOT"
echo "[1/5] Pull latest code"
git pull --ff-only

echo "[2/5] Install / update dependencies"
source "$VENV_ROOT/bin/activate"

if [[ -f "$SHARED_ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$SHARED_ROOT/.env"
  set +a
fi

python -m pip install -r requirements.txt

if [[ "$RETRAIN" == "true" ]]; then
  echo "[3/5] Retrain and export artifacts"
  python scripts/train_and_export.py
else
  echo "[3/5] Skip retraining (RETRAIN=false)"
fi

echo "[4/5] Restart app service"
sudo systemctl restart health-project

echo "[5/5] Show service status"
sudo systemctl --no-pager --full status health-project
