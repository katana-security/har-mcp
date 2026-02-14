"""MCP prompts -- reusable LLM analysis templates for HAR files."""

from typing import Any

from pydantic import Field

from fastmcp import FastMCP

import har_parser
import state


def register_prompts(server: FastMCP) -> None:

    @server.prompt("analyze_api")
    def analyze_api_prompt(
        label: str = Field(description="Label of the HAR to analyze"),
    ) -> dict[str, Any]:
        """Analyze API endpoints captured in a HAR file."""
        har_data = state.get_har(label)
        endpoints = har_parser.get_urls_and_methods(har_data)
        summary = har_parser.get_har_summary(har_data)

        return {
            "prompt": f"""\
Analyze the API traffic captured in HAR '{label}'.

Domains: {', '.join(summary['domains'])}
Total entries: {summary['entry_count']}
HTTP methods used: {', '.join(summary['methods'])}
Status codes seen: {', '.join(str(c) for c in summary['status_codes'])}

Endpoints ({len(endpoints)} unique URL+method combinations):
{_format_endpoints(endpoints)}

Tasks:
1. Map all API endpoints and group them by service/domain
2. Identify authentication patterns (API keys, OAuth, session tokens)
3. Document request/response data models for each endpoint
4. Note any pagination, rate limiting, or versioning patterns
5. Highlight any errors or unusual status codes

Use get_request_details with label='{label}' to inspect individual requests.""",
            "context": {
                "label": label,
                "summary": summary,
                "endpoints": endpoints,
            },
        }

    @server.prompt("security_audit")
    def security_audit_prompt(
        label: str = Field(description="Label of the HAR to audit"),
    ) -> dict[str, Any]:
        """Perform a security audit of the captured HTTP traffic."""
        har_data = state.get_har(label)
        summary = har_parser.get_har_summary(har_data)
        entries = state.get_entries(label)

        compact_entries: list[dict[str, str]] = []
        for i, entry in enumerate(entries):
            request = entry.get("request", {})
            response = entry.get("response", {})
            compact_entries.append({
                "request_id": f"request_{i}",
                "method": request.get("method", ""),
                "url": request.get("url", ""),
                "status": str(response.get("status", 0)),
            })

        return {
            "prompt": f"""\
Perform a security audit of the HTTP traffic in HAR '{label}'.

Domains: {', '.join(summary['domains'])}
Total entries: {summary['entry_count']}

Check for:
1. Sensitive data in URLs (tokens, passwords, PII in query strings)
2. HTTP instead of HTTPS (unencrypted traffic)
3. Authentication patterns and potential weaknesses
4. Information leakage in headers or response bodies
5. Cookie security (missing Secure, HttpOnly, SameSite flags)
6. CORS misconfigurations visible in headers
7. Excessive data exposure in API responses
8. Missing security headers (CSP, HSTS, X-Frame-Options)

Use get_request_details with label='{label}' to inspect suspicious requests.""",
            "context": {
                "label": label,
                "summary": summary,
                "entries": compact_entries,
            },
        }

    @server.prompt("analyze_request")
    def analyze_request_prompt(
        label: str = Field(description="Label of the HAR to query"),
        request_id: str = Field(description="The request ID to analyze (e.g. request_0)"),
    ) -> dict[str, Any]:
        """Analyze a specific request/response pair in detail."""
        har_data = state.get_har(label)
        details = har_parser.get_request_details(har_data, request_id)

        request = details.get("request", {})
        response = details.get("response", {})

        return {
            "prompt": f"""\
Analyze this HTTP request/response from HAR '{label}'.

Request: {request.get('method', '')} {request.get('url', '')}
Status: {response.get('status', '')} {response.get('statusText', '')}
Time: {details.get('time', 0)}ms

Tasks:
1. What is the purpose of this request?
2. Analyze request headers and their significance
3. Examine query parameters or POST body if present
4. Analyze the response status, headers, and body
5. Identify any security concerns (sensitive data, missing headers, etc.)
6. Note any caching, compression, or performance implications""",
            "context": {
                "label": label,
                "request_details": details,
            },
        }


def _format_endpoints(endpoints: list[dict[str, Any]]) -> str:
    """Format endpoints list for prompt display."""
    lines: list[str] = []
    for ep in endpoints:
        ids = ", ".join(ep["request_ids"])
        lines.append(f"  {ep['method']} {ep['url']}  [{ids}]")
    return "\n".join(lines)
