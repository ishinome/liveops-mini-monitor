Title: LiveOps Mini Monitor (Python)
What it does:

Checks configured HTTP endpoints for availability + latency

Sends Discord alerts on DOWN/SLOW and a throttled “all green” heartbeat

How it works:

Python script + YAML config + persisted state (consecutive failures + heartbeat timestamp)

Runs every 2 minutes via systemd timer on Ubuntu/Oracle Cloud Linux VM

Alerts via Discord webhook

Runbook:

When DOWN alert: verify target, check DNS, curl from VM, check recent deploys, restart service if applicable

When SLOW alert: check latency trend, resource usage, upstream dependency, rate limits

Where to check logs: journalctl -u liveops-monitor.service -f

Proof / screenshots:

picture incoming
