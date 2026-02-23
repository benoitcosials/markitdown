# --- MODULE: MCP Tool Definitions ---
"""
MCP tool definitions for MarkItDown server.

Exposes convert_to_markdown tool for file-to-markdown conversion with
support for multiple formats and optional image extraction.
"""

import asyncio
import concurrent.futures
from typing import Optional

from markitdown import MarkItDown
from mcp.server import Server
from mcp.server.fastmcp import FastMCP

from .utils import (
    check_plugins_enabled,
    get_base_path_for_uri,
    resolve_image_dir_for_file_uri,
)
from .vision_enhancement import (
    enhance_markdown_with_client_vision,
    request_client_image_analysis,
)

# Initialize FastMCP server instance
mcp = FastMCP("markitdown")


# --- Helper Functions ---


def create_llm_callback_wrapper(server: Server, max_tokens: int = 150) -> callable:
    """
    Create synchronous callback wrapper for async MCP image analysis.
    
    The MarkItDown converter is synchronous but MCP sampling is async.
    This wrapper bridges the gap by running async code in a separate thread
    with its own event loop, allowing the sync converter to call async MCP.
    
    Args:
        server: MCP server instance for sampling requests
        max_tokens: Maximum response length for image descriptions
    
    Returns:
        Synchronous callback function: (image_bytes, prompt) -> description
        
    Example:
        >>> llm_callback = create_llm_callback_wrapper(mcp_server)
        >>> description = llm_callback(image_bytes, "Describe this image")
    """
    def llm_callback(image_bytes: bytes, prompt: str) -> Optional[str]:
        """
        Synchronous callback for image description via MCP sampling.
        
        Args:
            image_bytes: Raw image data
            prompt: Description instructions for client
            
        Returns:
            Generated description or None if sampling fails
        """
        try:
            # Run async function in separate thread with its own event loop
            # This avoids "RuntimeError: asyncio.run() cannot be called from a running event loop"
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    request_client_image_analysis(
                        server=server,
                        image_data=image_bytes,
                        prompt=prompt,
                        max_tokens=max_tokens
                    )
                )
                # Block until result available (with timeout to prevent hang)
                return future.result(timeout=30)  # 30 second timeout
        except Exception:
            # Graceful fallback - return None to trigger next cascade level
            return None
    
    return llm_callback


# Initialize MarkItDown converter (will be instantiated per-request with plugins setting)
# NOTE: We create a new instance per convert call to handle plugin settings dynamically


@mcp.tool()
async def convert_to_markdown(
    uri: str,
    output_images: bool = True,
    image_dir: str = "images",
    skip_background_images: bool = True,
    skip_icon_images: bool = False,
    use_client_vision: bool = True,
) -> str:
    """
    Convert a file to Markdown format with optional image extraction.
    
    Supports: PPTX, DOCX, PDF, HTML, XLSX, CSV, JSON, Images, Audio.
    
    Images can be extracted to a local directory (output_images=True) or
    optionally enhanced with AI-generated descriptions via client vision
    capabilities (BRIEF_02).
    
    Args:
        uri: File URI (file://, http://, https://) or local path to convert
        output_images: Save images from PPTX/DOCX to separate files (default: True)
        image_dir: Directory for saved images, relative to source file (default: "images")
        skip_background_images: Skip PowerPoint background placeholder images (default: True)
        skip_icon_images: Skip icon images, extract only photos (default: False)
        use_client_vision: Use client's multimodal vision for image analysis via
                          MCP sampling (BRIEF_02). Enables adaptive descriptions
                          based on output_images mode. (default: True)
        
    Returns:
        Markdown content with potential vision enhancements
        
    Example:
        >>> result = await convert_to_markdown(
        ...     "file:///C:/docs/presentation.pptx",
        ...     output_images=True,
        ...     use_client_vision=True
        ... )
    """
    # Step 1: Resolve image_dir relative to source file for file:// URIs
    # CRITICAL: Ensures images are saved next to source file, not in CWD
    adjusted_image_dir = resolve_image_dir_for_file_uri(
        uri, image_dir, output_images
    )
    
    # Step 2: Check if plugins are enabled via environment variable
    enable_plugins = check_plugins_enabled()
    
    # Step 3: Prepare conversion arguments
    kwargs = {
        "output_images": output_images,
        "image_dir": adjusted_image_dir,
        "skip_background_images": skip_background_images,
        "skip_icon_images": skip_icon_images,
    }
    
    # Step 3.5: Add LLM callback for inline image descriptions via MCP sampling
    # This enables the cascade: llm_callback → llm_caption → PIL
    # Callback is called DURING conversion for text-only mode (SmartArt, etc.)
    if use_client_vision:
        llm_callback = create_llm_callback_wrapper(
            server=mcp._mcp_server,
            max_tokens=150
        )
        kwargs["llm_callback"] = llm_callback
    
    # Step 4: Perform conversion with MarkItDown
    converter = MarkItDown(enable_plugins=enable_plugins)
    result = converter.convert_uri(uri, **kwargs)
    markdown = result.markdown
    
    # Step 5: Vision enhancement (BRIEF_02)
    # Delegate image analysis to calling LLM client via MCP sampling
    # (MCP Protocol 2024-11-05 - sampling/createMessage capability)
    if use_client_vision:
        # Get base path for resolving relative image paths
        base_path = get_base_path_for_uri(uri)
        
        markdown = await enhance_markdown_with_client_vision(
            markdown=markdown,
            server=mcp._mcp_server,
            output_images=output_images,
            base_path=base_path
        )
    
    # Step 6: Return final markdown
    return markdown
