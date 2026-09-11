# XTS Command Center Next

Redesigned Android xTS lab control plane inspired by the open-source Android Test Station / TradeFed Cluster architecture.

## Architecture

```text
Windows Browser
      |
      v
Command Center Next (FastAPI)
      |
      +-----------------------------+
      |                             |
      v                             v
Native Linux Runner             OmniLab ATS 2
PRIMARY / Docker-free           OPTIONAL
      |                             |
      +-------------+---------------+
                    v
             Tradefed / xTS
                    v
            Android Devices
```

The legacy `user17-dot/Project` repository is reference-only and is not modified.

## Why this design

Full OmniLab ATS deployment uses Docker. Office lab hosts may not permit Docker, so Command Center Next keeps the good separation used by Android Test Station / TradeFed Cluster while providing a small native Linux runner that needs only Python, ADB/Fastboot, Java and installed CTS/GTS/VTS tools.

OmniLab support remains available as an optional backend on hosts where Docker is allowed.

## Native Runner

The Docker-free runner lives under `runner/` and provides:

- ADB device inventory and explicit states
- Fixed xTS tool/version paths
- CTS/GTS/VTS Tradefed execution
- Structured subprocess lifecycle (`shell=False`)
- Job status
- Process-group cancellation
- Tail logs
- systemd service support

See `runner/README.md`.

## Tool layout

```text
/opt/xts/
├── tools/
│   ├── CTS/
│   │   ├── official/
│   │   └── pab/
│   ├── GTS/
│   └── VTS/
├── runner/
├── state/
├── incoming/
├── outgoing/
└── logs/
```

The runner never searches the machine for another tool build. A requested version must exist at its exact configured path.

## Command Center

The dashboard supports both execution backends and defaults to Native Runner. It can register hosts, verify health, read connected devices and submit native xTS jobs. OmniLab OpenAPI discovery is retained for optional ATS hosts.

## Run the Command Center

Windows:

```bat
start.bat
```

Linux:

```bash
bash start.sh
```

Open `http://127.0.0.1:8000`.

## Upstream references

See `docs/UPSTREAM_OMNILAB.md` for the Android Test Station and TradeFed Cluster upstream projects and licensing notes.
