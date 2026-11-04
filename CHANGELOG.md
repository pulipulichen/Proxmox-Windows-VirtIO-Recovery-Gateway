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


## 2026-11-04 — Deploy Recovery ISO endpoint to CT 900

- The Gateway CT is isolated from GitHub DNS, so `bash update.sh` could not pull the public repository (`Could not resolve host: github.com`). No network setting was changed.
- Copied the already committed `gateway/server.py` to CT 900 through the PVE host, after backing up the previous file to `/root/server.py.before-recovery-json.py`. Python bytecode compilation passed and `virtio-gateway` restarted to active.
- Called `GET /virtio-recovery.json` from inside the CT and verified version 1 schema, three host mappings, both static and DHCP modes, and the required static address/prefix fields.
- The CT remains offline and its Git working tree reports the deployed server file as modified relative to its older local checkout. The committed GitHub source is canonical; future offline updates can transfer the repo version through PVE, or use `update.sh` after GitHub DNS/network access is restored. The four shell scripts were restored executable after the failed pull attempt.
- No Windows VM end-to-end test was performed.
