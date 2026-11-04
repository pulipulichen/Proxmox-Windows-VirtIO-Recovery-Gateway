# Proxmox Windows VirtIO Recovery Gateway

Offline-ready Debian 13 LXC DHCP and MAC-based network configuration service for [Windows VirtIO Recovery ISO](https://github.com/pulipulichen/Proxmox-Windows-VirtIO-Recovery-ISO).

## Development

Clone to `/opt/virtio-recovery-gateway` in a Debian 13 CT. Run `bash start.sh` (the installed CT has executable scripts). Edit `/etc/virtio-gateway/config.toml`, then restart `virtio-gateway`.

Dedicated isolated recovery network: `172.22.30.1/24`; DHCP pool `172.22.30.100-200`; API HTTP port `80`. No NAT or default route advertised. Do not expose this unauthenticated service to production networks.

## API

- `GET /health` returns JSON status.
- `GET /config/BC:24:11:AA:BB:01.toml` returns a single NIC TOML.
- `POST /config` with `{"macs":["BC:24:11:AA:BB:01"]}` returns matching NIC configurations as JSON.

## Offline deployment

Install all software in a CT before generating a clean `vzdump` archive. Target offline PVE hosts need only the archive and an isolated `vmbr-recovery` bridge. Use `restore.sh` on the PVE host. Remove test-specific network settings and secrets before public distribution. Keep real production MAC/IP settings only in `/etc/virtio-gateway/config.toml`, not in Git.
