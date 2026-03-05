# --- MODULE: MCP Tool Definitions ---
"""
MCP tool definitions for MarkItDown server.

Exposes convert_to_markdown tool for file-to-markdown conversion with
support for multiple formats and optional image extraction.
"""

import json
import re
import tempfile
import urllib.parse
from pathlib import Path
from typing import Any

from markitdown import MarkItDown
from mcp.server.fastmcp import FastMCP

from .utils import check_plugins_enabled

# Initialize FastMCP server instance
mcp = FastMCP("markitdown")


def _get_source_filename(uri: str) -> str:
    """Extract base filename from URI without extension."""
    if uri.startswith('file:'):
        path = urllib.parse.unquote(uri.replace('file:///', '').replace('file://', ''))
    elif uri.startswith(('http:', 'https:')):
        path = urllib.parse.urlparse(uri).path
    else:
        path = uri
    
    return Path(path).stem


def _make_image_links_relative(markdown: str) -> str:
    """Convert image paths in markdown to filenames only."""
    def replace_path(match):
        full_path = match.group(1)
        filename = Path(full_path.replace('\\', '/')).name
        return f'![]({filename})'
    
    return re.sub(r'!\[\]\(([^)]+)\)', replace_path, markdown)


@mcp.tool()
async def convert_to_markdown(
    uri: str,
    output_path: str | None = None,
    image_path: str | None = None,
    output_images: bool = True,
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
        output_path: Directory for the output markdown file. If not specified,
            uses image_path if provided, otherwise a temporary directory.
        image_path: Directory for extracted images. If not specified,
            uses output_path if provided, otherwise a temporary directory.
        output_images: Save images from PPTX/DOCX to separate files (default: True)
        skip_background_images: Skip PowerPoint background placeholder images (default: True)
        skip_icon_images: Skip icon images, extract only photos (default: False)
        
    Returns:
        JSON string with the following structure:
        {
            "markdown_file": "C:/output/presentation.md",
            "markdown": "# Converted content...",
            "images": [
                {"name": "slide1_image0.png", "path": "C:/images/slide1_image0.png", "size": 12345}
            ],
            "output_dir": "C:/output",
            "image_dir": "C:/images",
            "is_temp_dir": false,
            "logs": ["Created output directory...", "Extracted 2 images...", "Saved markdown file..."]
        }
        
        Fields:
        - markdown_file (str): Full path to the saved .md file
        - markdown (str): The converted Markdown content
        - images (list): List of extracted images, each with name, full path, and size in bytes
        - output_dir (str): Directory where markdown file was saved
        - image_dir (str): Directory where images were saved
        - is_temp_dir (bool): True if using temporary directory (agent should copy files)
        - logs (list[str]): Diagnostic messages explaining what happened during conversion
    
    PPTX-specific features (automatic):
        - SmartArt: Extracted as hierarchical bullet lists or tables with images
        - Tables: Cell colors shown as emoji, embedded/floating images extracted
        - Hyperlinks: Preserved as [text](url) in all text elements
        - Text styles: Bold, italic, strikethrough, underline converted to Markdown
        - Headings: Auto-detected from font size hierarchy within slides
        - Image deduplication: MD5 hash prevents duplicate image files
        - EMF/WMF conversion: Windows metafiles converted to PNG when PIL available
        
    Example:
        >>> result = await convert_to_markdown(
        ...     "C:/docs/presentation.pptx",
        ...     output_path="C:/output",
        ...     image_path="C:/output/images"
        ... )
        >>> data = json.loads(result)
        >>> print(f"Markdown saved to: {data['markdown_file']}")
        >>> print(f"Images: {len(data['images'])}")
    """
    logs: list[str] = []
    extracted_images: list[dict[str, Any]] = []
    is_temp_dir = False
    
    # Step 0: Auto-convert local paths to file:// URIs
    original_uri = uri
    if not any(uri.startswith(scheme) for scheme in ['file:', 'http:', 'https:', 'data:']):
        is_windows_path = len(uri) >= 2 and uri[1] == ':' and uri[0].isalpha()
        is_unix_path = uri.startswith('/')
        
        if is_windows_path or is_unix_path:
            normalized = uri.replace('\\', '/')
            if is_windows_path:
                uri = f"file:///{urllib.parse.quote(normalized, safe='/:')}"
            else:
                uri = f"file://{urllib.parse.quote(normalized, safe='/')}"
            logs.append(f"Auto-converted path to URI: {original_uri} -> {uri}")
        else:
            logs.append(f"Warning: URI scheme not recognized: {uri[:20]}...")
    
    # Step 1: Determine output directories (independent logic)
    # output_path specified → MD goes there, otherwise temp
    # image_path specified → images go there, otherwise temp
    use_relative_links = image_path is None
    
    if output_path:
        output_dir = Path(output_path)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logs.append(f"Using output directory: {output_dir}")
        except (PermissionError, OSError) as e:
            output_dir = Path(tempfile.mkdtemp(prefix="markitdown_output_"))
            is_temp_dir = True
            logs.append(f"Cannot write to {output_path}: {e}, using temp: {output_dir}")
    else:
        output_dir = Path(tempfile.mkdtemp(prefix="markitdown_output_"))
        is_temp_dir = True
        logs.append(f"No output_path, using temp directory: {output_dir}")
    
    if image_path:
        img_dir = Path(image_path)
        try:
            img_dir.mkdir(parents=True, exist_ok=True)
            logs.append(f"Using image directory: {img_dir}")
        except (PermissionError, OSError) as e:
            img_dir = Path(tempfile.mkdtemp(prefix="markitdown_images_"))
            is_temp_dir = True
            use_relative_links = True
            logs.append(f"Cannot write to {image_path}: {e}, using temp: {img_dir}")
    else:
        img_dir = Path(tempfile.mkdtemp(prefix="markitdown_images_"))
        is_temp_dir = True
        logs.append(f"No image_path, using temp directory: {img_dir}")
    
    # Step 2: Check if plugins are enabled via environment variable
    enable_plugins = check_plugins_enabled()
    
    # Step 3: Prepare conversion arguments - images go to img_dir
    kwargs = {
        "output_images": output_images,
        "image_path": str(img_dir),
        "skip_background_images": skip_background_images,
        "skip_icon_images": skip_icon_images,
    }
    
    # Step 4: Perform conversion with MarkItDown
    converter = MarkItDown(enable_plugins=enable_plugins)
    result = converter.convert_uri(uri, **kwargs)
    
    # Step 5: Adjust image links based on image_path
    # If image_path specified → keep full paths
    # If not specified → use relative filenames only
    if use_relative_links:
        markdown_content = _make_image_links_relative(result.markdown)
        logs.append("Image links converted to relative filenames")
    else:
        markdown_content = result.markdown
        logs.append("Image links kept as full paths")
    
    # Step 6: Save markdown file
    source_name = _get_source_filename(original_uri)
    md_filename = f"{source_name}.md"
    md_filepath = output_dir / md_filename
    md_filepath.write_text(markdown_content, encoding='utf-8')
    logs.append(f"Saved markdown file: {md_filepath}")
    
    # Step 7: Collect extracted images info
    if output_images and img_dir.is_dir():
        for filepath in img_dir.iterdir():
            if filepath.is_file() and filepath.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                extracted_images.append({
                    "name": filepath.name,
                    "path": str(filepath),
                    "size": filepath.stat().st_size
                })
        logs.append(f"Extracted {len(extracted_images)} images to {img_dir}")
    
    # Step 8: Return structured JSON response
    response = {
        "markdown_file": str(md_filepath),
        "markdown": markdown_content,
        "images": extracted_images,
        "output_dir": str(output_dir),
        "image_dir": str(img_dir),
        "is_temp_dir": is_temp_dir,
        "logs": logs
    }
    
    return json.dumps(response, ensure_ascii=False, indent=2)

