# --- MODULE: Server Setup (HTTP/SSE) ---
"""
HTTP and SSE server configuration for MarkItDown MCP.

Provides Starlette application setup with SSE (Server-Sent Events) and
Streamable HTTP transports for MCP protocol communication.
"""

import contextlib
from collections.abc import AsyncIterator

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """
    Create Starlette application for MCP over HTTP/SSE.
    
    Configures a Starlette ASGI application with:
    - SSE (Server-Sent Events) transport at /sse
    - Streamable HTTP transport at /mcp
    - Message handling at /messages/
    
    Args:
        mcp_server: Configured FastMCP server instance
        debug: Enable debug logging and detailed error responses
        
    Returns:
        Configured Starlette app ready for uvicorn deployment
        
    Example:
        >>> app = create_starlette_app(mcp._server, debug=True)
        >>> uvicorn.run(app, host="0.0.0.0", port=3000)
    """
    sse = SseServerTransport("/messages/")
    session_manager = StreamableHTTPSessionManager(
        app=mcp_server,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    async def handle_sse(request: Request) -> None:
        """
        Handle SSE (Server-Sent Events) connections.
        
        Establishes bidirectional communication channel using SSE for
        real-time MCP message streaming.
        """
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        """
        Handle Streamable HTTP requests.
        
        Processes stateless HTTP requests with streaming support for
        larger payloads and long-running conversions.
        """
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """
        Manage application lifespan and session manager lifecycle.
        
        Context manager that initializes and cleans up the StreamableHTTP
        session manager during application startup and shutdown.
        """
        async with session_manager.run():
            print("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                print("Application shutting down...")

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/mcp", app=handle_streamable_http),
            Mount("/messages/", app=sse.handle_post_message),
        ],
        lifespan=lifespan,
    )
