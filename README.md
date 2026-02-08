# har-mcp

MCP server for analyzing HAR (HTTP Archive) files. Load a HAR file from disk or URL, then explore endpoints, inspect requests, and audit security — all through the Model Context Protocol.

## Quick Start

```bash
uv run server.py
```

## Configuration

### Claude Code

```bash
claude mcp add har -- uv run /path/to/har-mcp/server.py
```

### Claude Desktop / Cursor

```json
{
  "mcpServers": {
    "har": {
      "command": "uv",
      "args": ["run", "/path/to/har-mcp/server.py"]
    }
  }
}
```

## Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `load_har` | `source` (file path or URL) | Load a HAR file |
| `list_urls_methods` | — | List all unique URL+method combinations |
| `get_request_ids` | `url`, `method` | Get request IDs for a specific endpoint |
| `get_request_details` | `request_id` | Get full request/response details (auth redacted) |

## Resources

| URI | Description |
|-----|-------------|
| `har://status` | Load status (loaded, source, entry count) |
| `har://summary` | HAR summary (version, creator, domains, methods, status codes) |
| `har://domains` | Unique domains sorted alphabetically |
| `har://entries` | Compact entry list (request_id, method, url, status, time) |
| `har://entry/{request_id}` | Full entry details with auth headers redacted |

## Prompts

| Prompt | Parameters | Description |
|--------|-----------|-------------|
| `analyze_api` | — | Map API endpoints, group by service, document patterns |
| `security_audit` | — | Audit traffic for sensitive data, auth issues, misconfigurations |
| `analyze_request` | `request_id` | Deep-dive into a specific request/response pair |

## Workflow

1. **Load** a HAR file: `load_har(source="traffic.har")`
2. **List** endpoints: `list_urls_methods()`
3. **Filter** by endpoint: `get_request_ids(url="https://api.example.com/users", method="GET")`
4. **Inspect** a request: `get_request_details(request_id="request_0")`

## Security

Authentication headers (`Authorization`, `Cookie`, `X-API-Key`, etc.) are automatically redacted in all tool and resource outputs.

## License

MIT
