"""HAR tools -- 4 MCP tools for loading and querying HAR files."""

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
    ) -> str:
        """Load a HAR file from a file path or HTTP URL."""
        data = har_parser.parse_source(source)
        state.set_har_data(data, source)
        count = state.get_entry_count()
        return f"Successfully loaded HAR file with {count} entries"

    @server.tool
    def list_urls_methods() -> list[dict[str, Any]]:
        """List all accessed URLs and their HTTP methods from the loaded HAR file."""
        har_data = state.get_har_data()
        return har_parser.get_urls_and_methods(har_data)

    @server.tool
    def get_request_ids(
        url: str = Field(description="The URL to filter by"),
        method: str = Field(description="The HTTP method to filter by (GET, POST, etc.)"),
    ) -> list[str]:
        """Get all request IDs for a specific URL and HTTP method."""
        har_data = state.get_har_data()
        return har_parser.get_request_ids_for_url_method(har_data, url, method)

    @server.tool
    def get_request_details(
        request_id: str = Field(
            description="The request ID to retrieve details for (e.g. request_0)",
        ),
    ) -> dict[str, Any]:
        """Get full request details by request ID (authentication headers will be redacted)."""
        har_data = state.get_har_data()
        return har_parser.get_request_details(har_data, request_id)
