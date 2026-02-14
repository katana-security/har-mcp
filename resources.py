"""MCP resources -- loadable context data for HAR analysis."""

from typing import Any

from fastmcp import FastMCP

import har_parser
import state


def register_resources(server: FastMCP) -> None:

    @server.resource(uri="har://status")
    def har_status() -> dict[str, Any]:
        """Overview of all loaded HAR files."""
        hars = state.list_hars()
        return {
            "loaded_count": len(hars),
            "files": hars,
        }

    @server.resource(uri="har://{label}/summary")
    def har_summary(label: str) -> dict[str, Any]:
        """Summary of a loaded HAR file: version, creator, domains, methods, status codes."""
        har_data = state.get_har(label)
        return har_parser.get_har_summary(har_data)

    @server.resource(uri="har://{label}/domains")
    def har_domains(label: str) -> list[str]:
        """List of unique domains from a loaded HAR file, sorted alphabetically."""
        har_data = state.get_har(label)
        summary = har_parser.get_har_summary(har_data)
        return summary["domains"]

    @server.resource(uri="har://{label}/entries")
    def har_entries(label: str) -> list[dict[str, Any]]:
        """Compact list of all entries: request_id, method, url, status, time."""
        entries = state.get_entries(label)
        compact: list[dict[str, Any]] = []
        for i, entry in enumerate(entries):
            request = entry.get("request", {})
            response = entry.get("response", {})
            compact.append({
                "request_id": f"request_{i}",
                "method": request.get("method", ""),
                "url": request.get("url", ""),
                "status": response.get("status", 0),
                "time": entry.get("time", 0),
            })
        return compact

    @server.resource(uri="har://{label}/entry/{request_id}")
    def har_entry(label: str, request_id: str) -> dict[str, Any]:
        """Full details of a specific entry by request ID (auth headers redacted)."""
        har_data = state.get_har(label)
        return har_parser.get_request_details(har_data, request_id)
