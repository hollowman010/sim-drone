#!/bin/bash
set -euxo pipefail
exec >/var/log/startup-script.log 2>&1

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y openssh-server google-guest-agent || true

systemctl enable ssh || true
systemctl restart ssh || systemctl start ssh || true
systemctl enable google-guest-agent || true
systemctl restart google-guest-agent || true

if command -v ufw >/dev/null 2>&1; then
  ufw allow 22 || true
  ufw --force enable || true
  ufw reload || true
fi

echo "startup-script completed"
