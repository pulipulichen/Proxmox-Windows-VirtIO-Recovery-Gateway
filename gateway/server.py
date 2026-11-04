#!/usr/bin/env python3
"""Read-only MAC-address network configuration API (Python 3.11+ stdlib)."""
import ipaddress
import json
import os
import re
import tomllib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

CONFIG = Path(os.environ.get("VIRTIO_CONFIG", "/etc/virtio-gateway/config.toml"))
MAC = re.compile(r"^[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}$")
MAX_BODY = 16384

def normalize_mac(value):
    if not isinstance(value, str) or not MAC.fullmatch(value):
        raise ValueError("Invalid MAC address")
    return value.upper()

def load_hosts():
    with CONFIG.open("rb") as f:
        entries = tomllib.load(f).get("hosts", [])
    if not isinstance(entries, list):
        raise ValueError("hosts must be an array")
    hosts = {}
    for entry in entries:
        mac = normalize_mac(entry["mac"])
        if mac in hosts:
            raise ValueError("Duplicate MAC: " + mac)
        mode = entry.get("mode", "static")
        if mode not in ("static", "dhcp"):
            raise ValueError("Invalid mode")
        item = {"mac": mac, "mode": mode}
        if mode == "static":
            for key in ("ip", "subnet_mask"):
                if key not in entry:
                    raise ValueError("Missing " + key + " for " + mac)
            ipaddress.IPv4Address(entry["ip"])
            ipaddress.IPv4Network("0.0.0.0/" + entry["subnet_mask"])
            item["ip"] = entry["ip"]
            item["subnet_mask"] = entry["subnet_mask"]
            if "gateway" in entry:
                ipaddress.IPv4Address(entry["gateway"])
                item["gateway"] = entry["gateway"]
            if "dns" in entry:
                if not isinstance(entry["dns"], list):
                    raise ValueError("dns must be an array")
                for dns in entry["dns"]:
                    ipaddress.IPv4Address(dns)
                item["dns"] = entry["dns"]
        hosts[mac] = item
    return hosts

def as_toml(item):
    lines = []
    for key in ("mac", "mode", "ip", "subnet_mask", "gateway"):
        if key in item:
            lines.append(key + " = " + json.dumps(item[key]))
    if "dns" in item:
        lines.append("dns = " + json.dumps(item["dns"]))
    return "\n".join(lines) + "\n"

class Handler(BaseHTTPRequestHandler):
    def respond(self, code, payload, content_type="application/json"):
        data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self.respond(200, {"status": "ok"})
        if self.path == "/virtio-recovery.json":
            try:
                hosts = load_hosts()
                result = {}
                for mac, item in hosts.items():
                    if item["mode"] == "dhcp":
                        result[mac] = {"mode": "dhcp"}
                        continue
                    network = ipaddress.IPv4Network("0.0.0.0/" + item["subnet_mask"])
                    mapped = {
                        "mode": "static",
                        "address": item["ip"],
                        "prefix": network.prefixlen,
                    }
                    for key in ("gateway", "dns"):
                        if key in item:
                            mapped[key] = item[key]
                    result[mac] = mapped
                return self.respond(200, {"version": 1, "hosts": result})
            except Exception:
                self.log_exception()
                return self.respond(500, {"error": "configuration error"})
        if not (self.path.startswith("/config/") and self.path.endswith(".toml")):
            return self.respond(404, {"error": "not found"})
        try:
            mac = normalize_mac(unquote(self.path[len("/config/"):-len(".toml")]))
            item = load_hosts().get(mac)
            if item is None:
                return self.respond(404, {"error": "unknown MAC"})
            return self.respond(200, as_toml(item).encode(), "application/toml")
        except ValueError as exc:
            return self.respond(400, {"error": str(exc)})
        except Exception:
            self.log_exception()
            return self.respond(500, {"error": "configuration error"})

    def do_POST(self):
        if self.path != "/config":
            return self.respond(404, {"error": "not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > MAX_BODY:
                return self.respond(413, {"error": "invalid body size"})
            request = json.loads(self.rfile.read(length))
            macs = request["macs"]
            if not isinstance(macs, list) or len(macs) > 128:
                raise ValueError("macs must be a list of at most 128 MACs")
            hosts = load_hosts()
            result = [hosts[mac] for value in macs if (mac := normalize_mac(value)) in hosts]
            return self.respond(200, {"hosts": result})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            return self.respond(400, {"error": str(exc)})
        except Exception:
            self.log_exception()
            return self.respond(500, {"error": "configuration error"})

    def log_exception(self):
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    address = os.environ.get("VIRTIO_LISTEN", "172.22.30.1")
    port = int(os.environ.get("VIRTIO_PORT", "80"))
    ThreadingHTTPServer((address, port), Handler).serve_forever()
