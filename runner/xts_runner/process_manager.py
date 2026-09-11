from __future__ import annotations

import os
import signal
import subprocess
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import IO


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ManagedProcess:
    job_id: str
    argv: list[str]
    cwd: str
    pid: int
    pgid: int
    status: str = "RUNNING"
    started_at: str = field(default_factory=now)
    finished_at: str | None = None
    exit_code: int | None = None
    log_path: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class ProcessManager:
    def __init__(self) -> None:
        self._jobs: dict[str, ManagedProcess] = {}
        self._processes: dict[str, subprocess.Popen[str]] = {}
        self._lock = threading.Lock()

    def start(self, job_id: str, argv: list[str], cwd: Path, log_path: Path) -> ManagedProcess:
        with self._lock:
            if job_id in self._processes and self._processes[job_id].poll() is None:
                raise ValueError(f"job already running: {job_id}")
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log: IO[str] = log_path.open("a", encoding="utf-8", buffering=1)
            process = subprocess.Popen(
                argv,
                cwd=str(cwd),
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
                shell=False,
            )
            item = ManagedProcess(
                job_id=job_id,
                argv=argv,
                cwd=str(cwd),
                pid=process.pid,
                pgid=os.getpgid(process.pid),
                log_path=str(log_path),
            )
            self._jobs[job_id] = item
            self._processes[job_id] = process
            thread = threading.Thread(target=self._wait, args=(job_id, process, log), daemon=True)
            thread.start()
            return item

    def _wait(self, job_id: str, process: subprocess.Popen[str], log: IO[str]) -> None:
        code = process.wait()
        log.close()
        with self._lock:
            item = self._jobs[job_id]
            item.exit_code = code
            item.status = "COMPLETED" if code == 0 else "FAILED"
            item.finished_at = now()

    def get(self, job_id: str) -> ManagedProcess | None:
        with self._lock:
            return self._jobs.get(job_id)

    def list(self) -> list[ManagedProcess]:
        with self._lock:
            return list(self._jobs.values())

    def cancel(self, job_id: str) -> ManagedProcess:
        with self._lock:
            item = self._jobs.get(job_id)
            process = self._processes.get(job_id)
            if not item or not process:
                raise KeyError(job_id)
            if process.poll() is not None:
                return item
            os.killpg(item.pgid, signal.SIGTERM)
            item.status = "CANCELLING"
            return item
