"""
HTTP 请求辅助：支持直连或通过 Worker relay 中转。
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx


def _merge_query_params(url: str, params: dict[str, Any] | None) -> str:
    if not params:
        return url

    parts = urlsplit(url)
    query_items = parse_qsl(parts.query, keep_blank_values=True)
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            for item in value:
                if item is not None:
                    query_items.append((key, str(item)))
        else:
            query_items.append((key, str(value)))

    return urlunsplit((
        parts.scheme,
        parts.netloc,
        parts.path,
        urlencode(query_items, doseq=True),
        parts.fragment,
    ))


def _clean_headers(headers: dict[str, Any] | None) -> dict[str, str]:
    return {
        str(key): str(value)
        for key, value in (headers or {}).items()
        if value is not None and str(value) != ""
    }


def _encode_body(
    *, headers: dict[str, Any] | None = None, json_body: Any = None, data: Any = None
) -> tuple[str | None, dict[str, str]]:
    target_headers = _clean_headers(headers)

    if json_body is not None:
        target_headers.setdefault("Content-Type", "application/json")
        return json.dumps(json_body, ensure_ascii=False), target_headers

    if data is None:
        return None, target_headers

    if isinstance(data, bytes):
        raise TypeError("Worker relay does not support raw bytes request bodies")

    if isinstance(data, (dict, list, tuple)):
        target_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
        return urlencode(data, doseq=True), target_headers

    return str(data), target_headers


async def send_request(
    method: str,
    url: str,
    *,
    headers: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    json_body: Any = None,
    data: Any = None,
    timeout: int = 30,
    relay_url: str = "",
) -> httpx.Response:
    request_method = method.upper()
    relay_url = relay_url.strip()

    async with httpx.AsyncClient(timeout=timeout, trust_env=False) as client:
        if not relay_url:
            return await client.request(
                request_method,
                url,
                headers=headers,
                params=params,
                json=json_body,
                data=data,
            )

        target_url = _merge_query_params(url, params)
        target_body, target_headers = _encode_body(
            headers=headers,
            json_body=json_body,
            data=data,
        )
        payload: dict[str, Any] = {
            "url": target_url,
            "method": request_method,
            "headers": target_headers,
        }
        if target_body is not None:
            payload["body"] = target_body

        relay_response = await client.post(relay_url, json=payload)
        relay_response.raise_for_status()

        return httpx.Response(
            status_code=relay_response.status_code,
            headers={
                "Content-Type": relay_response.headers.get("Content-Type", ""),
            },
            content=relay_response.content,
            request=relay_response.request,
        )
