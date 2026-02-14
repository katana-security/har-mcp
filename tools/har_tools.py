"""HAR tools -- MCP tools for loading and querying multiple HAR files."""

from typing import Any

from pydantic import Field

from fastmcp import FastMCP

import har_parser
import state


def register_har_tools(server: FastMCP) -> None:

    @server.tool
    def load_har(
        source: str = Field(
            description="File path or HTTP URL to the HAR file",
        ),
        label: str | None = Field(
            default=None,
            description="Optional label for this HAR. If omitted, derived from filename.",
        ),
    ) -> str:
        """Load a HAR file from a file path or HTTP URL."""
        data = har_parser.parse_source(source)
        actual_label = state.set_har(label, data, source)
        count = state.get_entry_count(actual_label)
        return f"Loaded HAR '{actual_label}' with {count} entries."

    @server.tool
    def list_hars() -> list[dict[str, Any]]:
        """List all currently loaded HAR files with their labels, sources, and entry counts."""
        return state.list_hars()

    @server.tool
    def list_urls_methods(
        label: str = Field(description="Label of the loaded HAR to query"),
    ) -> list[dict[str, Any]]:
        """List all accessed URLs and their HTTP methods from the loaded HAR file."""
        har_data = state.get_har(label)
        return har_parser.get_urls_and_methods(har_data)

    @server.tool
    def get_request_ids(
        label: str = Field(description="Label of the loaded HAR to query"),
        url: str = Field(description="The URL to filter by"),
        method: str = Field(description="The HTTP method to filter by (GET, POST, etc.)"),
    ) -> list[str]:
        """Get all request IDs for a specific URL and HTTP method."""
        har_data = state.get_har(label)
        return har_parser.get_request_ids_for_url_method(har_data, url, method)

    @server.tool
    def get_request_details(
        label: str = Field(description="Label of the loaded HAR to query"),
        request_id: str = Field(
            description="The request ID to retrieve details for (e.g. request_0)",
        ),
    ) -> dict[str, Any]:
        """Get full request details by request ID (authentication headers will be redacted)."""
        har_data = state.get_har(label)
        return har_parser.get_request_details(har_data, request_id)

    @server.tool
    def unload_har(
        label: str = Field(description="Label of the HAR to unload"),
    ) -> str:
        """Unload a HAR file from memory."""
        if not state.is_loaded(label):
            return f"No HAR loaded with label '{label}'."
        state.remove_har(label)
        return f"Unloaded HAR '{label}'."
