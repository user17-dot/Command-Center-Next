# XTS Command Center Next

Redesigned Android xTS lab control plane integrating OmniLab Android Test Station (ATS) 2.0 as the Linux execution backend.

## Architecture

```text
Windows Browser
      |
      v
Command Center Next (FastAPI + React)
      |
      v
OmniLab Gateway
      |
      v
Linux ATS 2.0 Host(s)
      |
      v
Tradefed / CTS / GTS / VTS
      |
      v
Android Devices
```

The legacy `user17-dot/Project` repository is reference-only and is not modified.

## Principle

Command Center owns project workflow, role-aware UX, job lineage, review and reporting. OmniLab ATS owns host/device execution, scheduling, Tradefed lifecycle and test-run state.

The gateway does not invent ATS endpoints. It discovers each host's OpenAPI document (normally `/_ah/api_docs/api.json`) and maps semantic operations to that host's actual `operationId`s.

## Initial scope

- Register ATS Linux hosts
- Health + OpenAPI discovery
- Host/device/run dashboard
- Start/cancel/inspect test runs through mapped ATS operations
- Clean Tester-first dashboard
- Adapter boundary for later IR/MR/SQC, result review, CR and verification workflows

## Stack

- Backend: FastAPI, SQLAlchemy, SQLite locally / PostgreSQL-ready
- Frontend: React + TypeScript + Vite
- Integration: HTTPX + OmniLab ATS OpenAPI discovery
