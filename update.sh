#!/usr/bin/env bash
set -euo pipefail
cd /opt/virtio-recovery-gateway
git pull --ff-only
install -m 0644 config/dnsmasq-recovery.conf /etc/dnsmasq.d/virtio-recovery.conf
install -m 0644 systemd/virtio-gateway.service /etc/systemd/system/virtio-gateway.service
systemctl daemon-reload
systemctl restart dnsmasq virtio-gateway
./verify.sh
