from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import RunnerConfig


@dataclass(frozen=True)
class ToolInstall:
    suite: str
    source: str
    version: str
    root: Path
    launcher: Path


class ToolNotInstalled(FileNotFoundError):
    pass


def resolve_tool(
    config: RunnerConfig,
    suite: str,
    source: str,
    version: str,
    android_version: str | None = None,
) -> ToolInstall:
    suite = suite.upper()
    root = config.tool_path(suite, source, version, android_version)
    launchers = {
        "CTS": [root / "android-cts" / "tools" / "cts-tradefed", root / "tools" / "cts-tradefed"],
        "GTS": [root / "android-gts" / "tools" / "gts-tradefed", root / "tools" / "gts-tradefed"],
        "VTS": [root / "android-vts" / "tools" / "vts-tradefed", root / "tools" / "vts-tradefed"],
    }
    if suite not in launchers:
        raise ValueError(f"Unsupported suite: {suite}")
    for launcher in launchers[suite]:
        if launcher.is_file():
            return ToolInstall(suite, source, version, root, launcher)
    raise ToolNotInstalled(f"TOOL_NOT_INSTALLED: {suite} {source} {version} at {root}")
