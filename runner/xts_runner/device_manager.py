from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass


@dataclass
class Device:
    serial: str
    state: str
    model: str | None = None
    product: str | None = None
    android_version: str | None = None
    sdk: str | None = None
    fingerprint: str | None = None
    build_type: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _run(args: list[str], timeout: int = 8) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)


def _prop(serial: str, name: str) -> str | None:
    result = _run(["adb", "-s", serial, "shell", "getprop", name])
    value = result.stdout.strip()
    return value or None


def list_devices() -> list[Device]:
    try:
        result = _run(["adb", "devices"])
    except FileNotFoundError:
        return [Device(serial="", state="ADB_NOT_FOUND")]

    devices: list[Device] = []
    for line in result.stdout.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        serial = parts[0]
        state = parts[1] if len(parts) > 1 else "UNKNOWN"
        if state != "device":
            devices.append(Device(serial=serial, state=state.upper()))
            continue
        devices.append(
            Device(
                serial=serial,
                state="READY",
                model=_prop(serial, "ro.product.model"),
                product=_prop(serial, "ro.product.name"),
                android_version=_prop(serial, "ro.build.version.release"),
                sdk=_prop(serial, "ro.build.version.sdk"),
                fingerprint=_prop(serial, "ro.build.fingerprint"),
                build_type=_prop(serial, "ro.build.type"),
            )
        )
    return devices
