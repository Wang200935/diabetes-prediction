#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/health-project}"
APP_ROOT="$PROJECT_ROOT/app"

echo "Installing systemd service files..."
sudo cp "$APP_ROOT/deploy/raspberry_pi/health-project.service" /etc/systemd/system/health-project.service
sudo cp "$APP_ROOT/deploy/raspberry_pi/cloudflared-health-project.service" /etc/systemd/system/cloudflared-health-project.service
sudo systemctl daemon-reload

echo "Services installed."
echo "Use:"
echo "  sudo systemctl enable --now health-project"
echo "  sudo systemctl enable --now cloudflared-health-project"
