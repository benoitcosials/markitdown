# --- MODULE: MCP Tool Definitions ---
"""
MCP tool definitions for MarkItDown server.

Exposes convert_to_markdown tool for file-to-markdown conversion with
support for multiple formats and optional image extraction.
"""

from markitdown import MarkItDown
from mcp.server.fastmcp import FastMCP

from .utils import check_plugins_enabled, resolve_image_dir_for_file_uri

# Initialize FastMCP server instance
mcp = FastMCP("markitdown")

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
    
    # Step 4: Perform conversion with MarkItDown
    converter = MarkItDown(enable_plugins=enable_plugins)
    result = converter.convert_uri(uri, **kwargs)
    markdown = result.markdown
    
    # Step 5: Vision enhancement (BRIEF_02 - will be implemented in Phase 2)
    # BRIEF_02: Vision enhancement will be added in Phase 2
    # When implemented, this will delegate image analysis to the calling LLM client
    # via MCP sampling capability (MCP Protocol 2024-11-05)
    # if use_client_vision:
    #     from .vision_enhancement import enhance_markdown_with_client_vision
    #     markdown = await enhance_markdown_with_client_vision(
    #         markdown=markdown,
    #         server=mcp._mcp_server,
    #         output_images=output_images
    #     )
    
    # Step 6: Return final markdown
    return markdown
