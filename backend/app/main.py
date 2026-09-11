from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .omnilab import OmniLabClient, OmniLabError

app = FastAPI(title="XTS Command Center Next", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HostCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    base_url: str = Field(min_length=4)


class OperationMap(BaseModel):
    list_devices: str | None = None
    create_run: str | None = None
    get_run: str | None = None
    cancel_run: str | None = None


class RunCreate(BaseModel):
    host_id: str
    request: dict[str, Any]


HOSTS: dict[str, dict[str, Any]] = {}
RUNS: dict[str, dict[str, Any]] = {}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "command-center-next"}


@app.get("/api/hosts")
def list_hosts() -> list[dict[str, Any]]:
    return list(HOSTS.values())


@app.post("/api/hosts")
def create_host(payload: HostCreate) -> dict[str, Any]:
    host_id = str(uuid4())
    host = {
        "id": host_id,
        "name": payload.name,
        "base_url": payload.base_url.rstrip("/"),
        "status": "UNKNOWN",
        "last_seen": None,
        "operation_map": OperationMap().model_dump(),
    }
    HOSTS[host_id] = host
    return host


@app.post("/api/hosts/{host_id}/discover")
async def discover(host_id: str) -> dict[str, Any]:
    host = HOSTS.get(host_id)
    if not host:
        raise HTTPException(404, "Host not found")
    try:
        operations = await OmniLabClient(host["base_url"]).operations()
    except Exception as exc:
        host["status"] = "OFFLINE"
        raise HTTPException(502, f"ATS discovery failed: {exc}") from exc

    host["status"] = "ONLINE"
    host["last_seen"] = now()
    return {
        "host": host,
        "operations": [
            {"operation_id": op.operation_id, "method": op.method, "path": op.path}
            for op in sorted(operations.values(), key=lambda value: value.operation_id)
        ],
    }


@app.put("/api/hosts/{host_id}/operation-map")
def set_operation_map(host_id: str, payload: OperationMap) -> dict[str, Any]:
    host = HOSTS.get(host_id)
    if not host:
        raise HTTPException(404, "Host not found")
    host["operation_map"] = payload.model_dump()
    return host


@app.get("/api/hosts/{host_id}/devices")
async def devices(host_id: str) -> Any:
    host = HOSTS.get(host_id)
    if not host:
        raise HTTPException(404, "Host not found")
    operation_id = host["operation_map"].get("list_devices")
    if not operation_id:
        raise HTTPException(409, "list_devices operation is not mapped")
    try:
        return await OmniLabClient(host["base_url"]).call(operation_id)
    except OmniLabError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, f"ATS request failed: {exc}") from exc


@app.post("/api/runs")
async def create_run(payload: RunCreate) -> dict[str, Any]:
    host = HOSTS.get(payload.host_id)
    if not host:
        raise HTTPException(404, "Host not found")
    operation_id = host["operation_map"].get("create_run")
    if not operation_id:
        raise HTTPException(409, "create_run operation is not mapped")

    run_id = str(uuid4())
    local = {
        "id": run_id,
        "host_id": payload.host_id,
        "status": "SUBMITTING",
        "created_at": now(),
        "remote": None,
    }
    RUNS[run_id] = local
    try:
        remote = await OmniLabClient(host["base_url"]).call(
            operation_id, body=payload.request
        )
        local["remote"] = remote
        local["status"] = "SUBMITTED"
        return local
    except Exception as exc:
        local["status"] = "SUBMIT_FAILED"
        local["error"] = str(exc)
        raise HTTPException(502, f"ATS run submission failed: {exc}") from exc


@app.get("/api/runs")
def runs() -> list[dict[str, Any]]:
    return sorted(RUNS.values(), key=lambda value: value["created_at"], reverse=True)
