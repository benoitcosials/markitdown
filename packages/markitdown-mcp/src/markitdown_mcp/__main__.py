# --- MODULE: Entry Point ---
"""
MarkItDown MCP Server - Entry Point

Command-line interface for running MarkItDown as an MCP server.
Supports STDIO mode (default) for direct integration with MCP clients,
and HTTP/SSE mode (--http) for web-based communication.
"""

import argparse
import sys

import uvicorn

from .server import create_starlette_app
from .tools import mcp


def main():
    """Main entry point for MarkItDown MCP server."""
    # Access underlying MCP server instance for HTTP mode
    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(
        description="Run MarkItDown MCP server for file-to-markdown conversion"
    )

    parser.add_argument(
        "--http",
        action="store_true",
        help="Run with HTTP/SSE transport instead of STDIO (default: False)",
    )
    parser.add_argument(
        "--sse",
        action="store_true",
        help="(Deprecated) Alias for --http (default: False)",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to listen on (default: 3001)"
    )
    args = parser.parse_args()

    use_http = args.http or args.sse

    if not use_http and (args.host or args.port):
        parser.error(
            "Host and port arguments are only valid when using streamable HTTP or SSE transport (see: --http)."
        )
        sys.exit(1)

    if use_http:
        starlette_app = create_starlette_app(mcp_server, debug=True)
        uvicorn.run(
            starlette_app,
            host=args.host if args.host else "127.0.0.1",
            port=args.port if args.port else 3001,
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()
