# --- MODULE: Shared Utilities ---
"""
Shared utility functions for MarkItDown MCP server.

Provides common helpers used across multiple modules for path resolution,
environment variable checking, and file operations.
"""

import os
import urllib.parse
from pathlib import Path
from typing import Optional


def resolve_image_dir_for_file_uri(
    uri: str,
    image_dir: Optional[str],
    output_images: bool
) -> Optional[str]:
    """
    Resolve image directory relative to source file for file:// URIs.
    
    For file:// URIs, images should be saved relative to the source file's
    directory, not the current working directory. This ensures predictable
    image locations and proper relative path references in generated Markdown.
    
    Critical for BRIEF_01 functionality where image extraction must work
    correctly regardless of where the MCP server is invoked from.
    
    Args:
        uri: Source file URI (e.g., "file:///C:/docs/presentation.pptx")
        image_dir: Requested image directory name (relative or absolute)
        output_images: Whether images should be saved to disk
        
    Returns:
        Resolved absolute path to image directory, or None if not applicable.
        For file:// URIs, returns path relative to source file's parent directory.
        For non-file URIs or when output_images=False, returns image_dir unchanged.
        
    Example:
        >>> resolve_image_dir_for_file_uri(
        ...     "file:///C:/docs/presentation.pptx",
        ...     "images",
        ...     True
        ... )
        'C:/docs/images'
        
        >>> resolve_image_dir_for_file_uri(
        ...     "https://example.com/file.pptx",
        ...     "images",
        ...     True
        ... )
        'images'
    """
    # Return None if images won't be saved
    if not output_images:
        return None
    
    # Only process file:// URIs
    if not uri.startswith("file://"):
        return image_dir
    
    try:
        # Parse file:// URI to extract OS path
        # Handle both file:/// (Unix) and file://C:/ (Windows) formats
        file_path_str = urllib.parse.unquote(uri.replace("file:///", ""))
        source_file = Path(file_path_str)
        
        # Get parent directory of source file
        base_dir = source_file.parent
        
        # Resolve image_dir relative to source file's directory
        if image_dir:
            resolved_path = base_dir / image_dir
        else:
            # Default to "images" subdirectory
            resolved_path = base_dir / "images"
        
        return str(resolved_path)
    
    except (ValueError, OSError) as e:
        # Fallback to original image_dir if URI parsing fails
        # Log warning but don't raise - graceful degradation
        print(f"Warning: Failed to parse file URI for directory context: {e}")
        return image_dir


def get_base_path_for_uri(uri: str) -> Optional[str]:
    """
    Extract base directory path from a file:// URI.
    
    Used for resolving relative image paths in generated markdown.
    Returns the parent directory of the source file.
    
    Args:
        uri: Source file URI (e.g., "file:///C:/docs/presentation.pptx")
        
    Returns:
        Absolute path to parent directory, or None for non-file URIs.
        
    Example:
        >>> get_base_path_for_uri("file:///C:/docs/presentation.pptx")
        'C:/docs'
    """
    if not uri.startswith("file://"):
        return None
    
    try:
        file_path_str = urllib.parse.unquote(uri.replace("file:///", ""))
        source_file = Path(file_path_str)
        return str(source_file.parent)
    except (ValueError, OSError):
        return None


def check_plugins_enabled() -> bool:
    """
    Check if MarkItDown plugins are enabled via environment variable.
    
    Reads the MARKITDOWN_ENABLE_PLUGINS environment variable and returns
    True if it's set to a truthy value (case-insensitive).
    
    Recognized truthy values: "true", "1", "yes"
    All other values (including unset) return False.
    
    Returns:
        True if plugins should be enabled, False otherwise
        
    Example:
        >>> os.environ["MARKITDOWN_ENABLE_PLUGINS"] = "1"
        >>> check_plugins_enabled()
        True
        
        >>> os.environ["MARKITDOWN_ENABLE_PLUGINS"] = "false"
        >>> check_plugins_enabled()
        False
    """
    value = os.getenv("MARKITDOWN_ENABLE_PLUGINS", "false").strip().lower()
    return value in ("true", "1", "yes")
