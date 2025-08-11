#!/usr/bin/env python3
# Minimal agent loop that reads its inbox and replies to outbox
import os, json, time, argparse, random
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
BUS_IN  = os.path.join(ROOT, "bus", "inbox")
BUS_OUT = os.path.join(ROOT, "bus", "outbox")
BUS_LOG = os.path.join(ROOT, "bus", "logs")

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def log(event):
    os.makedirs(BUS_LOG, exist_ok=True)
    lf = os.path.join(BUS_LOG, "bus.log")
    with open(lf,"a",encoding="utf-8") as f:
        f.write(json.dumps({"ts":now(), **event}, ensure_ascii=False)+"\n")

def handle_message(agent, msg):
    body = msg.get("body","")
    # Demo behavior: reflect + add a small intent
    reply_text = f"[{agent}] received: {body}"
    if "plan" in body.lower():
        reply_text += " | plan: break task into steps and confirm."
    elif "code" in body.lower():
        reply_text += " | note: run tests, then commit snapshot."
    return reply_text

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True, choices=["Storm","Echo"])
    args = ap.parse_args()
    agent = args.agent

    os.makedirs(BUS_OUT, exist_ok=True)

    print(f"[{agent}] agent online. Watching inbox...")
    while True:
        try:
            files = sorted([f for f in os.listdir(BUS_IN) if f.startswith(agent+"__") and f.endswith(".json")])
            for fn in files:
                path = os.path.join(BUS_IN, fn)
                with open(path,"r",encoding="utf-8") as f: msg=json.load(f)
                reply = {
                    "id": msg["id"],
                    "ts": now(),
                    "to": msg.get("from","conductor"),
                    "from": agent,
                    "type": "reply",
                    "in_reply_to": msg["id"],
                    "body": handle_message(agent, msg),
                    "meta": {"orig": msg.get("body","")}
                }
                out_path = os.path.join(BUS_OUT, f"{agent}__{msg['id']}.json")
                with open(out_path,"w",encoding="utf-8") as f: json.dump(reply,f,ensure_ascii=False,indent=2)
                log({"evt":"reply", "by":agent, "id":msg["id"]})
                os.remove(path)  # consume message
        except Exception as e:
            log({"evt":"error", "by":agent, "error":str(e)})
        time.sleep(0.5)

if __name__=="__main__":
    main()
