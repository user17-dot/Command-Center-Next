# XTS Native Runner

Docker-free Linux execution service for Command Center Next.

The design is inspired by the open-source Android Test Station / TradeFed Cluster separation of device management, host execution and command lifecycle, but this runner is intentionally small and office-lab friendly.

## Requirements

- Ubuntu/Linux
- Python 3.10+
- Java required by the installed xTS suite
- `adb` and `fastboot` in PATH
- CTS/GTS/VTS installed under `/opt/xts/tools`
- No Docker required

## Fixed tool layout

```text
/opt/xts/
├── tools/
│   ├── CTS/
│   │   ├── official/17_R2/
│   │   └── pab/android17/PAB_001/
│   ├── GTS/
│   └── VTS/
├── runner/
├── state/
├── incoming/
├── outgoing/
└── logs/
```

The runner never searches the whole machine for a fallback version. Missing exact versions return `TOOL_NOT_INSTALLED`.

## Local start

```bash
cd runner
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp xts-runner.example.yaml /tmp/xts-runner.yaml
XTS_RUNNER_CONFIG=/tmp/xts-runner.yaml .venv/bin/uvicorn xts_runner.main:app --host 0.0.0.0 --port 8765
```

Check:

```bash
curl http://127.0.0.1:8765/health
curl http://127.0.0.1:8765/devices
```

## Production service

Install the runner code under `/opt/xts/runner`, create a dedicated `xtsrunner` user, place config at `/etc/xts-runner.yaml`, then install `xts-runner.service` under `/etc/systemd/system/`.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now xts-runner
sudo systemctl status xts-runner
```

A desktop screen lock or terminal close does not stop a systemd service. Suspend/hibernate/shutdown still must be disabled on lab hosts.

## API

- `GET /health`
- `GET /devices`
- `GET /jobs`
- `GET /jobs/{job_id}`
- `POST /jobs`
- `POST /jobs/{job_id}/cancel`
- `GET /jobs/{job_id}/log`

`POST /jobs` accepts structured xTS input. It does not accept a raw shell command and subprocesses run with `shell=False`.
