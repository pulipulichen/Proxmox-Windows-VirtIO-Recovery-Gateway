# CHANGELOG

## 2026-11-04 — First working PVE LXC deployment

- Created isolated `vmbr-recovery` bridge on `pulipuli-chen--pve-workspace` without changing vmbr0 or the existing livecd bridge.
- Created unprivileged Debian 13 CT 900 on ZFS, 1 vCPU, 512 MiB RAM, 4 GiB disk, 172.22.30.1/24.
- Temporarily attached a management-network NIC for apt/git installation; **removed it before backup**. Verified that the running CT has only eth0 and no default route.
- Installed dnsmasq, Python HTTP API and systemd service using repository `start.sh`.
- Verified dnsmasq syntax and UDP/67 listener; HTTP health, single-MAC TOML, multi-MAC JSON, unknown MAC omission, and service restart with no external network.
- Created PVE vzdump archive `/var/lib/vz/dump/vzdump-lxc-900-2026_11_04-20_58_27.tar.zst` (247 MB). SHA256 `920b9314a7889d6a2eeb7e432b17a4696c3d032d21c2dfeac797beb616110ec6`.
- Archive is **development-only** and is not suitable for public GitHub Releases until SSH host keys, machine ID, logs and sample settings are scrubbed and a clean restore is tested.

### Known limitations / next steps

- No DHCP client lease handshake was tested yet (only dnsmasq configuration and socket).
- No Windows LiveCD end-to-end test yet; offline Windows NIC configuration remains to be validated.
- A GitHub Release has not been published; current backup exists only on the PVE host.
- GitHub Contents API creates scripts without executable file mode; CT-local scripts were chmod +x, but git tree file modes need to be corrected for future clones.
- Debian 13 systemd 257 emits a nesting warning; CT runs successfully with nesting disabled.
- Initial attempt to create README.md failed because the new repository already contained README.md; updated it instead.


## 2026-11-04 — Recovery ISO compatibility endpoint

- Added `GET /virtio-recovery.json`, returning the Recovery ISO's version 1 JSON schema keyed by normalized MAC address.
- Static entries expose `address`, CIDR `prefix`, optional `gateway` and `dns`; DHCP entries expose `mode: "dhcp"`. Existing TOML and POST JSON APIs are unchanged.
- Validation: source review only; no Gateway CT or Windows VM deployment was performed for this change. Run `bash update.sh` in the CT before using a newly built ISO.
- Release status: not released; no workflow run was available during the edit.
