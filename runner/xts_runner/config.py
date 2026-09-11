from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class RunnerConfig:
    runner_id: str
    site_id: str
    xts_root: Path
    bind_host: str = "0.0.0.0"
    bind_port: int = 8765

    @classmethod
    def load(cls) -> "RunnerConfig":
        path = Path(os.getenv("XTS_RUNNER_CONFIG", "/etc/xts-runner.yaml"))
        data: dict = {}
        if path.exists():
            data = yaml.safe_load(path.read_text()) or {}
        return cls(
            runner_id=str(data.get("runner_id") or os.getenv("XTS_RUNNER_ID") or "LOCAL-RUNNER"),
            site_id=str(data.get("site_id") or os.getenv("XTS_SITE_ID") or "LOCAL"),
            xts_root=Path(data.get("xts_root") or os.getenv("XTS_ROOT") or "/opt/xts"),
            bind_host=str(data.get("bind_host") or "0.0.0.0"),
            bind_port=int(data.get("bind_port") or 8765),
        )

    def tool_path(self, suite: str, source: str, version: str, android_version: str | None = None) -> Path:
        suite_dir = self.xts_root / "tools" / suite.upper()
        source = source.lower()
        if source == "official":
            return suite_dir / "official" / version
        if source == "pab":
            if not android_version:
                raise ValueError("android_version is required for PAB tools")
            return suite_dir / "pab" / android_version / version
        raise ValueError(f"Unsupported tool source: {source}")
