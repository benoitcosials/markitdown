# --- MODULE: MCP Tool Definitions ---
"""
MCP tool definitions for MarkItDown server.

Exposes convert_to_markdown tool for file-to-markdown conversion with
support for multiple formats and optional image extraction.
"""

from markitdown import MarkItDown
from mcp.server.fastmcp import FastMCP

from .utils import (
    check_plugins_enabled,
    resolve_image_path_for_file_uri,
)

# Initialize FastMCP server instance
mcp = FastMCP("markitdown")


@mcp.tool()
async def convert_to_markdown(
    uri: str,
    output_images: bool = True,
    image_path: str = "images",
    skip_background_images: bool = True,
    skip_icon_images: bool = False,
) -> str:
    """
    Convert a file to Markdown format with optional image extraction.
    
    Supports: PPTX, DOCX, PDF, HTML, XLSX, CSV, JSON, Images, Audio.
    
    Args:
        uri: File URI (file://, http://, https://) or local path to convert
        output_images: Save images from PPTX/DOCX to separate files (default: True)
        image_path: Directory or path for saved images, relative to source file (default: "images")
        skip_background_images: Skip PowerPoint background placeholder images (default: True)
        skip_icon_images: Skip icon images, extract only photos (default: False)
        
    Returns:
        Markdown content
    
    PPTX-specific features (automatic):
        - SmartArt: Extracted as hierarchical bullet lists or tables with images
        - Tables: Cell colors shown as emoji (🔴🟢🔵), embedded/floating images extracted
        - Hyperlinks: Preserved as [text](url) in all text elements
        - Text styles: Bold, italic, strikethrough, underline converted to Markdown
        - Headings: Auto-detected from font size hierarchy within slides
        - Image deduplication: MD5 hash prevents duplicate image files
        - EMF/WMF conversion: Windows metafiles converted to PNG when PIL available
        
    Example:
        >>> result = await convert_to_markdown(
        ...     "file:///C:/docs/presentation.pptx",
        ...     output_images=True
        ... )
    """
    # Step 1: Resolve image_path relative to source file for file:// URIs
    adjusted_image_path = resolve_image_path_for_file_uri(
        uri, image_path, output_images
    )
    
    # Step 2: Check if plugins are enabled via environment variable
    enable_plugins = check_plugins_enabled()
    
    # Step 3: Prepare conversion arguments
    kwargs = {
        "output_images": output_images,
        "image_path": adjusted_image_path,
        "skip_background_images": skip_background_images,
        "skip_icon_images": skip_icon_images,
    }
    
    # Step 4: Perform conversion with MarkItDown
    converter = MarkItDown(enable_plugins=enable_plugins)
    result = converter.convert_uri(uri, **kwargs)
    
    return result.markdown

