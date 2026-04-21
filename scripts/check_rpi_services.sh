#!/usr/bin/env bash
set -euo pipefail

echo "== health-project.service =="
sudo systemctl --no-pager --full status health-project || true
echo
echo "== cloudflared-health-project.service =="
sudo systemctl --no-pager --full status cloudflared-health-project || true
echo
echo "== Local health endpoint =="
curl -sS http://127.0.0.1:8000/health || true
