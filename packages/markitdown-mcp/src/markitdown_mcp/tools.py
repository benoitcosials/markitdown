# --- MODULE: MCP Tool Definitions ---
"""
MCP tool definitions for MarkItDown server.

Exposes convert_to_markdown tool for file-to-markdown conversion with
support for multiple formats and optional image extraction.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

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
        uri: File path or URI to convert. Accepts:
            - Local paths: "C:\\docs\\file.pptx" or "/home/user/file.pptx"
            - File URIs: "file:///C:/docs/file.pptx"
            - HTTP/HTTPS: "https://example.com/file.docx"
            - Data URIs: "data:application/pdf;base64,..."
            Local paths are automatically converted to file:// URIs.
        output_images: Save images from PPTX/DOCX to separate files (default: True)
        image_path: Directory or path for saved images, relative to source file (default: "images")
        skip_background_images: Skip PowerPoint background placeholder images (default: True)
        skip_icon_images: Skip icon images, extract only photos (default: False)
        
    Returns:
        JSON string with the following structure:
        {
            "markdown": "# Converted content...",
            "images": [
                {"name": "slide1_image0.png", "path": "C:/full/path/slide1_image0.png", "size": 12345}
            ],
            "image_dir": "C:/full/path/to/images",
            "used_fallback": false,
            "logs": ["Resolved image_path: ...", "Write access confirmed: ...", "Extracted 2 images..."]
        }
        
        Fields:
        - markdown (str): The converted Markdown content
        - images (list): List of extracted images, each with name, full path, and size in bytes
        - image_dir (str|null): Directory where images were saved, null if no images
        - used_fallback (bool): True if images were saved to temp directory due to write permission issues.
          When True, the agent should copy images from image_dir to the desired destination.
        - logs (list[str]): Diagnostic messages explaining what happened during conversion
    
    PPTX-specific features (automatic):
        - SmartArt: Extracted as hierarchical bullet lists or tables with images
        - Tables: Cell colors shown as emoji (🔴🟢🔵), embedded/floating images extracted
        - Hyperlinks: Preserved as [text](url) in all text elements
        - Text styles: Bold, italic, strikethrough, underline converted to Markdown
        - Headings: Auto-detected from font size hierarchy within slides
        - Image deduplication: MD5 hash prevents duplicate image files
        - EMF/WMF conversion: Windows metafiles converted to PNG when PIL available
        
    Fallback behavior:
        If the specified image_path is not writable (permission denied, sandbox restrictions),
        images are extracted to a system temp directory instead. Check used_fallback=true
        and copy images from image_dir to your target location.
        
    Example:
        >>> result = await convert_to_markdown(
        ...     "file:///C:/docs/presentation.pptx",
        ...     output_images=True,
        ...     image_path="extracted-images"
        ... )
        >>> data = json.loads(result)
        >>> if data["used_fallback"]:
        ...     # Copy images from data["image_dir"] to desired location
        ...     pass
    """
    logs: list[str] = []
    extracted_images: list[dict[str, Any]] = []
    final_image_dir: str | None = None
    
    # Step 0: Auto-convert local paths to file:// URIs
    # Handles Windows paths (C:\...) and Unix absolute paths (/...)
    original_uri = uri
    if not any(uri.startswith(scheme) for scheme in ['file:', 'http:', 'https:', 'data:']):
        # Check if it looks like a local path
        is_windows_path = len(uri) >= 2 and uri[1] == ':' and uri[0].isalpha()
        is_unix_path = uri.startswith('/')
        
        if is_windows_path or is_unix_path:
            # Convert to file:// URI
            import urllib.parse
            normalized = uri.replace('\\', '/')
            if is_windows_path:
                uri = f"file:///{urllib.parse.quote(normalized, safe='/:')}"
            else:
                uri = f"file://{urllib.parse.quote(normalized, safe='/')}"
            logs.append(f"Auto-converted path to URI: {original_uri} -> {uri}")
        else:
            logs.append(f"Warning: URI scheme not recognized: {uri[:20]}...")
    
    # Step 1: Resolve image_path relative to source file for file:// URIs
    adjusted_image_path = resolve_image_path_for_file_uri(
        uri, image_path, output_images
    )
    logs.append(f"Resolved image_path: {adjusted_image_path}")
    
    # Step 2: Test write access to target directory
    can_write_to_target = False
    fallback_temp_dir: str | None = None
    
    if output_images and adjusted_image_path:
        try:
            target_dir = Path(adjusted_image_path)
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Test actual write by creating a temp file
            test_file = target_dir / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            
            can_write_to_target = True
            final_image_dir = str(target_dir)
            logs.append(f"Write access confirmed: {target_dir}")
        except (PermissionError, OSError) as e:
            logs.append(f"Cannot write to {adjusted_image_path}: {e}")
            logs.append("Using temporary directory as fallback")
            
            # Create fallback temp directory
            fallback_temp_dir = tempfile.mkdtemp(prefix="markitdown_images_")
            adjusted_image_path = fallback_temp_dir
            final_image_dir = fallback_temp_dir
            logs.append(f"Fallback temp dir: {fallback_temp_dir}")
    
    # Step 3: Check if plugins are enabled via environment variable
    enable_plugins = check_plugins_enabled()
    
    # Step 4: Prepare conversion arguments
    kwargs = {
        "output_images": output_images,
        "image_path": adjusted_image_path,
        "skip_background_images": skip_background_images,
        "skip_icon_images": skip_icon_images,
    }
    
    # Step 5: Perform conversion with MarkItDown
    converter = MarkItDown(enable_plugins=enable_plugins)
    result = converter.convert_uri(uri, **kwargs)
    
    # Step 6: Collect extracted images info
    if output_images and final_image_dir and os.path.isdir(final_image_dir):
        for filename in os.listdir(final_image_dir):
            filepath = os.path.join(final_image_dir, filename)
            if os.path.isfile(filepath):
                extracted_images.append({
                    "name": filename,
                    "path": filepath,
                    "size": os.path.getsize(filepath)
                })
        logs.append(f"Extracted {len(extracted_images)} images to {final_image_dir}")
    
    # Step 7: Return structured JSON response
    response = {
        "markdown": result.markdown,
        "images": extracted_images,
        "image_dir": final_image_dir,
        "used_fallback": fallback_temp_dir is not None,
        "logs": logs
    }
    
    return json.dumps(response, ensure_ascii=False, indent=2)

