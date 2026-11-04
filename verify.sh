#!/bin/bash
set -euo pipefail
systemctl is-active dnsmasq
systemctl is-active virtio-gateway
python3 -m py_compile /opt/virtio-recovery-gateway/gateway/server.py
curl -fsS --max-time 5 http://172.22.30.1/health
printf '\n'
