#!/bin/bash
set -euo pipefail
cd /opt/virtio-recovery-gateway
apt-get update
apt-get install -y dnsmasq python3 curl git ca-certificates
install -d -m 700 /etc/virtio-gateway
if [ ! -e /etc/virtio-gateway/config.toml ]; then
  install -m 600 config/config.example.toml /etc/virtio-gateway/config.toml
fi
install -m 644 config/dnsmasq-recovery.conf /etc/dnsmasq.d/virtio-recovery.conf
install -m 644 systemd/virtio-gateway.service /etc/systemd/system/virtio-gateway.service
systemctl daemon-reload
systemctl enable dnsmasq virtio-gateway
systemctl restart dnsmasq virtio-gateway
./verify.sh
