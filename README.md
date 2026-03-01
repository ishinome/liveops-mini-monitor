# LiveOps Mini Monitor (Python)


## What it does:
  - Checks configured HTTP endpoints for:
  - availability (request success + HTTP status)
  - latency (response time threshold)
- Sends Discord notifications:
  -  **DOWN** when a check fails (timeout/network/HTTP error)
  -  **SLOW** when latency exceeds a threshold
  -  **Heartbeat** “all green” message on a configurable interval
- Persists state between runs:
  - consecutive failures (noise reduction / anti-flapping)
  - heartbeat last-sent timestamp


## How it works
- Python script + YAML config + persisted state (`state.json`)
- Runs every 2 minutes via `systemd` timer on an Ubuntu VM (Oracle Cloud)
- Alerts via Discord webhook

## Runbook


When DOWN alert: verify target, check DNS, curl from VM, check recent deploys, restart service if applicable

When SLOW alert: check latency trend, resource usage, upstream dependency, rate limits

Where to check logs: journalctl -u liveops-monitor.service -f


## Proof / screenshots:

<img width="603" height="752" alt="image" src="https://github.com/user-attachments/assets/2c7f0649-bb7c-4233-874a-b5c68b402859" />

## Timer running
<img width="1139" height="305" alt="image" src="https://github.com/user-attachments/assets/4349296e-f4b8-446e-bc65-8bc19e2b26a6" />

## Output of service
<img width="1068" height="193" alt="image" src="https://github.com/user-attachments/assets/a2104c22-88c1-454f-b331-0a96d946d193" />


