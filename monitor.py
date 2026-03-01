from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
import yaml

STATE_FILE = Path("state.json")


@dataclass
class Target:
    name: str
    url: str


def load_config(path: str = "config.yaml") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"failures": {}, "last_heartbeat_ts": 0}


def save_state(state: Dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def send_discord(webhook_url: str, message: str) -> None:
    # Discord webhook: POST JSON with "content"
    # (Webhooks are meant for simple message posting without a bot user.) 
    payload = {"content": message}
    r = requests.post(webhook_url, json=payload, timeout=5)
    r.raise_for_status()


def check_target(t: Target, timeout_s: int) -> Tuple[bool, int, Optional[int], str]:
    """Returns (ok, latency_ms, http_status, info)."""
    start = time.perf_counter()
    try:
        resp = requests.get(t.url, timeout=timeout_s)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return (200 <= resp.status_code < 400, latency_ms, resp.status_code, "ok")
    except requests.RequestException as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return (False, latency_ms, None, f"error: {type(e).__name__}: {e}")


def main() -> int:
    cfg = load_config()
    webhook_url = cfg["discord_webhook_url"].strip()
    timeout_s = int(cfg.get("timeout_seconds", 4))
    fail_after = int(cfg.get("fail_after", 2))
    max_latency_ms = int(cfg.get("max_latency_ms", 1200))

    targets: List[Target] = [Target(**t) for t in cfg.get("targets", [])]
    if not targets:
        print("No targets in config.yaml")
        return 2

    if not webhook_url or "PASTE_YOUR" in webhook_url:
        print("Set discord_webhook_url in config.yaml")
        return 2

    state = load_state()
    failures: Dict[str, int] = state.setdefault("failures", {})

    alerts: List[str] = []
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    all_ok = True
    ok_lines: List[str] = []

    for t in targets:
        ok, latency_ms, status, info = check_target(t, timeout_s)

        slow = ok and latency_ms > max_latency_ms
        if ok and not slow:
            failures[t.name] = 0
            print(f"[{now}] OK   {t.name} {latency_ms}ms status={status}")
            ok_lines.append(f"✅ {t.name}: {latency_ms}ms (status {status})")
            continue

        # Not OK or too slow
        all_ok = False
        failures[t.name] = failures.get(t.name, 0) + 1
        print(f"[{now}] WARN {t.name} {latency_ms}ms status={status} ({info}) "
              f"fail_count={failures[t.name]}")

        if failures[t.name] >= fail_after:
            reason = "SLOW" if slow else "DOWN"
            alerts.append(
                f"🚨 **{reason}**: `{t.name}`\n"
                f"- url: {t.url}\n"
                f"- latency: {latency_ms}ms (threshold {max_latency_ms}ms)\n"
                f"- status: {status}\n"
                f"- info: {info}\n"
                f"- consecutive failures: {failures[t.name]}"
            )

    save_state(state)

    heartbeat_enabled = bool(cfg.get("heartbeat_enabled", True))
    heartbeat_min_interval = int(cfg.get("heartbeat_min_interval_seconds", 1800))

    if heartbeat_enabled and all_ok:
        last = int(state.get("last_heartbeat_ts", 0))
        now_ts = int(time.time())
        if heartbeat_min_interval <= 0 or (now_ts - last) >= heartbeat_min_interval:
            msg = "🟢 LiveOps monitor: all green\n" + "\n".join(ok_lines)
            try:
                send_discord(webhook_url, msg)
                print("Sent Discord heartbeat (all green).")
                state["last_heartbeat_ts"] = now_ts
                save_state(state)
            except Exception as e:
                print(f"Failed to send Discord heartbeat: {e}")
                return 1

    if alerts:
        msg = "LiveOps monitor alert(s):\n\n" + "\n\n".join(alerts)
        try:
            send_discord(webhook_url, msg)
            print("Sent Discord alert(s).")
        except Exception as e:
            print(f"Failed to send Discord alert: {e}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
