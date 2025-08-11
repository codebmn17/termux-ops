#!/usr/bin/env python3
import json, hashlib, os, sys
from datetime import datetime, timezone

VAULT = os.path.join(os.path.dirname(__file__), "api_vault.json")

def sha256_hex(b: bytes) -> str:
    import hashlib
    return hashlib.sha256(b).hexdigest()

def load_vault():
    if not os.path.exists(VAULT):
        raise SystemExit("Vault not found: " + VAULT)
    with open(VAULT, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_key(api_key:str, require_scope=None):
    v = load_vault()
    h = sha256_hex(api_key.encode())
    match = None
    for k in v.get("keys", []):
        if k.get("stored_hash") == h:
            match = k; break
    if not match: return (False, "Key not found")
    if match.get("disabled"): return (False, "Key disabled")
    exp = match.get("expires_at")
    if exp:
        now = datetime.now(timezone.utc)
        from datetime import datetime as dt
        if dt.fromisoformat(exp.replace("Z","+00:00")) < now:
            return (False, "Key expired")
    if require_scope and require_scope not in (match.get("scopes") or []):
        return (False, f"Missing scope: {require_scope}")
    return (True, match)

if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--api-key", required=True)
    p.add_argument("--require-scope", default=None)
    a=p.parse_args()
    ok,info = validate_key(a.api_key, a.require_scope)
    print(json.dumps({"ok":ok,"info":info}, ensure_ascii=False))
