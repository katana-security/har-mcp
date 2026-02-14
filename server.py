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
1. Load one or more HAR files with load_har (file path or URL). Each gets a label.
2. List loaded files with list_hars
3. List endpoints with list_urls_methods(label)
4. Drill into specific requests with get_request_ids and get_request_details
5. Unload files with unload_har(label) when done
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
