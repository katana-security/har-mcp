"""HAR parser -- loading, URL/method extraction, request details, auth redaction."""

import copy
import json
import urllib.request
from typing import Any
from urllib.parse import urlparse

SENSITIVE_HEADERS = {
    "authorization",
    "x-api-key",
    "x-auth-token",
    "cookie",
    "set-cookie",
    "proxy-authorization",
}


def parse_source(source: str) -> dict[str, Any]:
    """Load and parse a HAR file from a file path or HTTP(S) URL.

    Validates that the parsed data contains ``log.entries``.
    """
    parsed = urlparse(source)
    if parsed.scheme in ("http", "https"):
        with urllib.request.urlopen(source) as resp:  # noqa: S310
            data = json.load(resp)
    else:
        with open(source) as fh:
            data = json.load(fh)

    # Validate minimal structure
    if not isinstance(data, dict) or "log" not in data:
        raise ValueError("Invalid HAR file: missing 'log' key")
    if "entries" not in data["log"]:
        raise ValueError("Invalid HAR file: missing 'log.entries' key")

    return data


def get_urls_and_methods(har_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return unique URL+method combinations with their request IDs."""
    entries = har_data.get("log", {}).get("entries", [])
    url_method_map: dict[str, dict[str, Any]] = {}

    for i, entry in enumerate(entries):
        request = entry.get("request")
        if request is None:
            continue

        url = request.get("url", "")
        method = request.get("method", "")
        key = f"{url}|{method}"
        request_id = f"request_{i}"

        if key in url_method_map:
            url_method_map[key]["request_ids"].append(request_id)
        else:
            url_method_map[key] = {
                "url": url,
                "method": method,
                "request_ids": [request_id],
            }

    return list(url_method_map.values())


def get_request_ids_for_url_method(
    har_data: dict[str, Any], url: str, method: str
) -> list[str]:
    """Return all request IDs matching the given URL and method."""
    entries = har_data.get("log", {}).get("entries", [])
    request_ids: list[str] = []

    for i, entry in enumerate(entries):
        request = entry.get("request")
        if request is None:
            continue
        if request.get("url") == url and request.get("method") == method:
            request_ids.append(f"request_{i}")

    return request_ids


def get_request_details(
    har_data: dict[str, Any], request_id: str
) -> dict[str, Any]:
    """Return full request details by ID, with auth headers redacted."""
    if not request_id.startswith("request_"):
        raise ValueError(f"Invalid request ID format: {request_id}")

    try:
        index = int(request_id.removeprefix("request_"))
    except ValueError:
        raise ValueError(f"Invalid request ID format: {request_id}") from None

    entries = har_data.get("log", {}).get("entries", [])
    if index < 0 or index >= len(entries):
        raise ValueError(f"Request ID out of range: {request_id}")

    entry = copy.deepcopy(entries[index])

    # Redact auth headers in request
    request = entry.get("request", {})
    if "headers" in request:
        request["headers"] = redact_auth_headers(request["headers"])

    # Redact auth headers in response
    response = entry.get("response", {})
    if "headers" in response:
        response["headers"] = redact_auth_headers(response["headers"])

    return {
        "request_id": request_id,
        "startedDateTime": entry.get("startedDateTime", ""),
        "time": entry.get("time", 0),
        "request": request,
        "response": response,
        "cache": entry.get("cache"),
        "timings": entry.get("timings"),
        "serverIPAddress": entry.get("serverIPAddress", ""),
        "connection": entry.get("connection", ""),
        "comment": entry.get("comment", ""),
    }


def redact_auth_headers(headers: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return a copy of headers with sensitive values replaced by [REDACTED]."""
    redacted: list[dict[str, str]] = []
    for header in headers:
        name = header.get("name", "")
        value = header.get("value", "")
        if name.lower() in SENSITIVE_HEADERS:
            value = "[REDACTED]"
        redacted.append({"name": name, "value": value})
    return redacted


def get_har_summary(har_data: dict[str, Any]) -> dict[str, Any]:
    """Return a summary of the loaded HAR file for resources."""
    log = har_data.get("log", {})
    entries = log.get("entries", [])

    domains: set[str] = set()
    methods: set[str] = set()
    status_codes: set[int] = set()

    for entry in entries:
        request = entry.get("request", {})
        response = entry.get("response", {})

        url = request.get("url", "")
        if url:
            try:
                domains.add(urlparse(url).netloc)
            except Exception:
                pass

        method = request.get("method", "")
        if method:
            methods.add(method)

        status = response.get("status")
        if status is not None:
            status_codes.add(int(status))

    return {
        "version": log.get("version", ""),
        "creator": log.get("creator", {}),
        "entry_count": len(entries),
        "domains": sorted(domains),
        "methods": sorted(methods),
        "status_codes": sorted(status_codes),
    }
