# --- MODULE: Shared Utilities ---
"""
Shared utility functions for MarkItDown MCP server.

Provides common helpers used across multiple modules for environment
variable checking and other shared operations.
"""

import os


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
