# /// script
# dependencies = ["fastmcp"]
# requires-python = ">=3.10"
# ///
"""HAR MCP server -- analyze HTTP Archive files via Model Context Protocol."""

from fastmcp import FastMCP

from tools import register_har_tools
from resources import register_resources
from prompts import register_prompts

server = FastMCP(
    "HAR",
    instructions="""\
HAR (HTTP Archive) analysis server. Workflow:
1. Load a HAR file with load_har (file path or URL)
2. List endpoints with list_urls_methods
3. Drill into specific requests with get_request_ids and get_request_details
Authentication headers are automatically redacted for security.""",
)

register_har_tools(server)
register_resources(server)
register_prompts(server)


def main() -> None:
    """Run the HAR MCP server (stdio transport)."""
    server.run()


if __name__ == "__main__":
    main()
