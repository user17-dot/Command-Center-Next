from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import RunnerConfig
from .device_manager import list_devices
from .process_manager import ProcessManager
from .tool_registry import ToolNotInstalled, resolve_tool

config = RunnerConfig.load()
processes = ProcessManager()
app = FastAPI(title="XTS Native Runner", version="0.1.0")


class RunRequest(BaseModel):
    job_id: str = Field(min_length=1, max_length=120)
    suite: Literal["CTS", "GTS", "VTS"]
    source: Literal["official", "pab"] = "official"
    version: str = Field(min_length=1, max_length=100)
    android_version: str | None = None
    args: list[str] = Field(default_factory=list, max_length=100)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "runner_id": config.runner_id,
        "site_id": config.site_id,
        "xts_root": str(config.xts_root),
    }


@app.get("/devices")
def devices() -> list[dict]:
    return [device.to_dict() for device in list_devices()]


@app.get("/jobs")
def jobs() -> list[dict]:
    return [job.to_dict() for job in processes.list()]


@app.get("/jobs/{job_id}")
def job(job_id: str) -> dict:
    item = processes.get(job_id)
    if not item:
        raise HTTPException(404, "Job not found")
    return item.to_dict()


@app.post("/jobs")
def start_job(payload: RunRequest) -> dict:
    if any("\x00" in arg or "\n" in arg or "\r" in arg for arg in payload.args):
        raise HTTPException(400, "Invalid command argument")
    try:
        tool = resolve_tool(
            config,
            payload.suite,
            payload.source,
            payload.version,
            payload.android_version,
        )
    except ToolNotInstalled as exc:
        raise HTTPException(409, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    log_path = config.xts_root / "logs" / f"{payload.job_id}.log"
    argv = [str(tool.launcher), *payload.args]
    try:
        item = processes.start(payload.job_id, argv, tool.root, log_path)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return item.to_dict()


@app.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: str) -> dict:
    try:
        return processes.cancel(job_id).to_dict()
    except KeyError as exc:
        raise HTTPException(404, "Job not found") from exc


@app.get("/jobs/{job_id}/log")
def job_log(job_id: str, tail: int = 200) -> dict:
    item = processes.get(job_id)
    if not item or not item.log_path:
        raise HTTPException(404, "Job/log not found")
    path = Path(item.log_path)
    if not path.exists():
        return {"job_id": job_id, "lines": []}
    lines = path.read_text(errors="replace").splitlines()
    return {"job_id": job_id, "lines": lines[-max(1, min(tail, 2000)):]}
