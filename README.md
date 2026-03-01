**LiveOps Mini Monitor (Python)**


**What it does:**

  Checks configured HTTP endpoints for availability + latency
  
  Sends Discord alerts on DOWN/SLOW and a throttled “all green” heartbeat


**How it works:**


Python script + YAML config + persisted state (consecutive failures + heartbeat timestamp)

Runs every 2 minutes via systemd timer on Ubuntu/Oracle Cloud Linux VM

Alerts via Discord webhook

**Runbook:**


When DOWN alert: verify target, check DNS, curl from VM, check recent deploys, restart service if applicable

When SLOW alert: check latency trend, resource usage, upstream dependency, rate limits

Where to check logs: journalctl -u liveops-monitor.service -f


**Proof / screenshots:**

<img width="603" height="752" alt="image" src="https://github.com/user-attachments/assets/2c7f0649-bb7c-4233-874a-b5c68b402859" />
<img width="1139" height="305" alt="image" src="https://github.com/user-attachments/assets/4349296e-f4b8-446e-bc65-8bc19e2b26a6" />

