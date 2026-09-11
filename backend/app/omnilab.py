from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import httpx


class OmniLabError(RuntimeError):
    pass


@dataclass(slots=True)
class Operation:
    operation_id: str
    method: str
    path: str


class OmniLabClient:
    """Small ATS integration boundary.

    ATS exposes an OpenAPI document. We discover operationIds from the real
    host instead of hardcoding undocumented endpoints.
    """

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout

    async def openapi(self) -> dict[str, Any]:
        url = urljoin(self.base_url, "_ah/api_docs/api.json")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def operations(self) -> dict[str, Operation]:
        spec = await self.openapi()
        result: dict[str, Operation] = {}
        for path, methods in spec.get("paths", {}).items():
            for method, meta in methods.items():
                if not isinstance(meta, dict):
                    continue
                operation_id = meta.get("operationId")
                if operation_id:
                    result[operation_id] = Operation(operation_id, method.upper(), path)
        return result

    async def call(
        self,
        operation_id: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        path_params: dict[str, Any] | None = None,
    ) -> Any:
        operations = await self.operations()
        operation = operations.get(operation_id)
        if not operation:
            raise OmniLabError(f"Unknown ATS operationId: {operation_id}")

        path = operation.path
        for key, value in (path_params or {}).items():
            path = path.replace("{" + key + "}", str(value))

        if "{" in path or "}" in path:
            raise OmniLabError(f"Missing path parameter for {operation.path}")

        url = urljoin(self.base_url, path.lstrip("/"))
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.request(
                operation.method,
                url,
                params=query,
                json=body,
            )
            response.raise_for_status()
            if not response.content:
                return None
            content_type = response.headers.get("content-type", "")
            if "json" in content_type:
                return response.json()
            return {"text": response.text}
