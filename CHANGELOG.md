# CHANGELOG

## 2026-11-04 — Initial implementation
- Adopted standalone Debian 13 LXC gateway; PVE host remains free of DHCP/API packages.
- MAC-based mapping supports multiple NICs per Windows VM, static IP/mask/gateway/DNS and DHCP mode.
- DHCP uses isolated recovery bridge and **does not advertise a default route**.
- API binds to 172.22.30.1:80, no TLS or authentication; network isolation is mandatory.
- Scripts install, update, verify, and offline restore. Configuration preserved outside git.
- Pending: end-to-end WinPE offline registry/NIC driver validation; offline restore test and release packaging.
