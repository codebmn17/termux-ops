#!/usr/bin/env python3
# Local conductor for Storm/Echo message passing (filesystem bus)
import os, json, time, uuid, argparse, sys
from datetime import datetime, timezone
from auth import validate_key

ROOT = os.path.dirname(os.path.abspath(__file__))
BUS_IN  = os.path.join(ROOT, "bus", "inbox")
BUS_OUT = os.path.join(ROOT, "bus", "outbox")
BUS_LOG = os.path.join(ROOT, "bus", "logs")

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def write_msg(target, payload:dict):
    os.makedirs(BUS_IN, exist_ok=True)
    mid = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    msg = {
        "id": mid,
        "ts": now(),
        "to": target,
        "from": "conductor",
        "type": payload.get("type","message"),
        "body": payload.get("body",""),
        "meta": payload.get("meta",{})
    }
    path = os.path.join(BUS_IN, f"{target}__{mid}.json")
    with open(path,"w",encoding="utf-8") as f: json.dump(msg,f,ensure_ascii=False,indent=2)
    return msg

def list_msgs(folder):
    if not os.path.exists(folder): return []
    return sorted([f for f in os.listdir(folder) if f.endswith(".json")])

def tail_log():
    os.makedirs(BUS_LOG, exist_ok=True)
    lf = os.path.join(BUS_LOG, "bus.log")
    open(lf,"a").close()
    print(f"[tailing] {lf} (Ctrl+C to stop)")
    with open(lf,"r",encoding="utf-8") as f:
        f.seek(0,2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5); continue
            print(line, end="")

def log(event):
    os.makedirs(BUS_LOG, exist_ok=True)
    lf = os.path.join(BUS_LOG, "bus.log")
    with open(lf,"a",encoding="utf-8") as f:
        f.write(json.dumps({"ts":now(), **event}, ensure_ascii=False)+"\n")

def main():
    ap = argparse.ArgumentParser(description="Local Conductor")
    ap.add_argument("--api-key", required=True, help="Your admin key")
    sub = ap.add_subparsers(dest="cmd")

    s1 = sub.add_parser("send", help="Send to one agent")
    s1.add_argument("--to", required=True, choices=["Storm","Echo"])
    s1.add_argument("--text", required=True)

    s2 = sub.add_parser("broadcast", help="Send to both")
    s2.add_argument("--text", required=True)

    s3 = sub.add_parser("list", help="List bus inbox/outbox")
    s4 = sub.add_parser("tail", help="Tail bus log")

    args = ap.parse_args()

    ok,info = validate_key(args.api_key, require_scope="admin")
    if not ok:
        print(json.dumps({"ok":False,"error":"auth_failed","info":info})); return

    if args.cmd=="send":
        m = write_msg(args.to, {"type":"message","body":args.text})
        log({"evt":"send","to":args.to,"id":m["id"]})
        print(json.dumps({"ok":True,"sent":m}, ensure_ascii=False))
    elif args.cmd=="broadcast":
        out=[]
        for target in ("Storm","Echo"):
            m = write_msg(target, {"type":"message","body":args.text})
            out.append(m); log({"evt":"broadcast","to":target,"id":m["id"]})
        print(json.dumps({"ok":True,"sent":out}, ensure_ascii=False))
    elif args.cmd=="list":
        print(json.dumps({
            "inbox": list_msgs(BUS_IN),
            "outbox": list_msgs(BUS_OUT)
        }, ensure_ascii=False, indent=2))
    elif args.cmd=="tail":
        tail_log()
    else:
        ap.print_help()

if __name__=="__main__":
    main()
