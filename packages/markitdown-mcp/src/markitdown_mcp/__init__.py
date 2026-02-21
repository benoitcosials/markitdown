# SPDX-FileCopyrightText: 2024-present Adam Fourney <adamfo@microsoft.com>
#
# SPDX-License-Identifier: MIT

"""
MarkItDown MCP Server

MCP server providing file-to-markdown conversion tools.
Supports PowerPoint, Word, PDF, HTML, Excel, CSV, JSON, Images, and Audio files.
"""

from .__about__ import __version__
from .tools import mcp

__all__ = [
    "__version__",
    "mcp",
]
