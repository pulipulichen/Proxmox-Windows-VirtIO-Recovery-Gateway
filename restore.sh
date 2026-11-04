#!/usr/bin/env bash
# Run on an offline PVE host after copying a clean vzdump archive.
set -euo pipefail
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/vzdump-lxc-*.tar.zst [CTID=900] [storage=local-lvm]"
  exit 2
fi
archive=$1
ctid=${2:-900}
storage=${3:-local-lvm}
bridge=vmbr-recovery
[[ -f "$archive" ]] || { echo "Archive not found"; exit 1; }
command -v pct >/dev/null || { echo "Run on Proxmox VE"; exit 1; }
if pct status "$ctid" >/dev/null 2>&1; then
  echo "CTID $ctid already exists; refusing to overwrite"
  exit 1
fi
if ! ip link show "$bridge" >/dev/null 2>&1; then
  echo "Bridge $bridge is missing. Create an isolated Linux bridge in PVE first."
  exit 1
fi
pct restore "$ctid" "$archive" --storage "$storage" --net0 "name=eth0,bridge=$bridge,ip=172.22.30.1/24"
pct start "$ctid"
pct exec "$ctid" -- systemctl is-active dnsmasq virtio-gateway
echo "Restored CT $ctid. Configure /etc/virtio-gateway/config.toml inside CT."
