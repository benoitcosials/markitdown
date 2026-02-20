import contextlib
import os
import sys
import urllib.parse
from collections.abc import AsyncIterator
from pathlib import Path

import uvicorn
from markitdown import MarkItDown
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

# Initialize FastMCP server for MarkItDown (SSE)
mcp = FastMCP("markitdown")


@mcp.tool()
async def convert_to_markdown(
    uri: str,
    output_images: bool = True,
    image_dir: str = "images",
    skip_background_images: bool = True,
    skip_icon_images: bool = True,
) -> str:
    """Convert a resource described by an http:, https:, file: or data: URI to markdown.
    
    Args:
        uri: Resource URI to convert (http:, https:, file:, or data:)
        output_images: Extract and save images to disk (default: True)
        image_dir: Directory for saved images relative to output (default: "images")
                   For file:// URIs, this is resolved relative to the source file directory.
        skip_background_images: Skip PowerPoint background placeholder images (default: True)
        skip_icon_images: Skip icon images, extract only photos (default: True)
    
    Returns:
        Markdown conversion of the resource
    """
    # CRITICAL FIX: Resolve image_dir relative to source file for file:// URIs
    adjusted_image_dir = image_dir
    
    if uri.startswith("file://") and output_images:
        try:
            # Parse file:// URI to extract OS path
            file_path_str = urllib.parse.unquote(uri.replace("file:///", ""))
            source_file = Path(file_path_str)
            
            # Get parent directory of source file
            base_dir = str(source_file.parent)
            
            # Resolve image_dir relative to source file's directory
            adjusted_image_dir = os.path.join(base_dir, image_dir)
        except (ValueError, OSError) as e:
            # If URI parsing fails, fall back to default image_dir
            print(f"Warning: Failed to parse file URI for directory context: {e}")
            adjusted_image_dir = image_dir
    
    kwargs = {
        "output_images": output_images,
        "image_dir": adjusted_image_dir,
        "skip_background_images": skip_background_images,
        "skip_icon_images": skip_icon_images,
    }
    
    return MarkItDown(enable_plugins=check_plugins_enabled()).convert_uri(uri, **kwargs).markdown



def check_plugins_enabled() -> bool:
    return os.getenv("MARKITDOWN_ENABLE_PLUGINS", "false").strip().lower() in (
        "true",
        "1",
        "yes",
    )


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    sse = SseServerTransport("/messages/")
    session_manager = StreamableHTTPSessionManager(
        app=mcp_server,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    async def handle_sse(request: Request) -> None:
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
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
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


# Main entry point
def main():
    import argparse

    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description="Run a MarkItDown MCP server")

    parser.add_argument(
        "--http",
        action="store_true",
        help="Run the server with Streamable HTTP and SSE transport rather than STDIO (default: False)",
    )
    parser.add_argument(
        "--sse",
        action="store_true",
        help="(Deprecated) An alias for --http (default: False)",
    )
    parser.add_argument(
        "--host", default=None, help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=None, help="Port to listen on (default: 3001)"
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
