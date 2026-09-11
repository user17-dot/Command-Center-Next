# OmniLab / TradeFed Cluster port map

Command Center Next does not vendor the complete Android Test Station tree because the upstream deployment brings Docker and cloud/App Engine dependencies that are not suitable for every office lab host.

Instead, the architecture is being ported into a small native Linux execution service.

| Upstream concept | Command Center Next | Status |
| --- | --- | --- |
| Device inventory/state | `runner/xts_runner/device_manager.py` | Implemented |
| Host execution API | `runner/xts_runner/main.py` | Implemented |
| Command lifecycle | `runner/xts_runner/process_manager.py` | Implemented |
| Structured execution | `shell=False`, argv-only jobs | Implemented |
| Exact tool ownership | `runner/xts_runner/tool_registry.py` | Implemented |
| Host service lifetime | `runner/xts-runner.service` | Implemented |
| Result correlation | before/after suite results snapshot | Implemented |
| Central host abstraction | Native + OmniLab backends | Implemented |
| OmniLab OpenAPI adapter | `backend/app/omnilab.py` | Implemented |
| Native Runner adapter | `backend/app/native_runner.py` | Implemented |
| Tester-first dashboard | `backend/app/static/index.html` | Implemented |
| Persistent runner state | SQLite job state | Next |
| Heartbeat/lease model | Server-owned job lease | Next |
| Same-PC native retry | session-aware retry | Next |
| Cross-PC result import retry | result folder + ZIP import and target-session mapping | Next |
| Artifact upload/retry | resumable central upload | Next |
| Authentication | per-runner token | Next |
| Full IR/MR/SQC/CR workflow | Command Center business layer | Later |

## Rule

The Native Runner stays an execution bridge. Project workflow, IR/MR/SQC, CR review and reporting belong to the central Command Center, not to the Linux runner.
