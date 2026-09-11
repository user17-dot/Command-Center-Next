from __future__ import annotations

from typing import Any

import httpx


class NativeRunnerClient:
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _request(self, method: str, path: str, *, json: Any = None, params: dict | None = None) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(method, self.base_url + path, json=json, params=params)
            response.raise_for_status()
            if not response.content:
                return None
            return response.json()

    async def health(self) -> dict:
        return await self._request("GET", "/health")

    async def devices(self) -> list[dict]:
        return await self._request("GET", "/devices")

    async def jobs(self) -> list[dict]:
        return await self._request("GET", "/jobs")

    async def start_job(self, request: dict) -> dict:
        return await self._request("POST", "/jobs", json=request)

    async def cancel_job(self, job_id: str) -> dict:
        return await self._request("POST", f"/jobs/{job_id}/cancel")

    async def job_log(self, job_id: str, tail: int = 200) -> dict:
        return await self._request("GET", f"/jobs/{job_id}/log", params={"tail": tail})
