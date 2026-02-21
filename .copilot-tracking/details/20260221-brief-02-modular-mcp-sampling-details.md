# Spécifications Techniques : BRIEF_02 - MCP Sampling avec Architecture Modulaire

**Date** : 21 février 2026  
**Version MCP** : Protocol 2024-11-05  
**Client Principal** : VS Code + GitHub Copilot

---

## 🏗️ Architecture Modulaire Détaillée

### Structure des Fichiers

```
packages/markitdown-mcp/src/markitdown_mcp/
├── __init__.py              # Package exports (48 lignes)
├── __about__.py             # Version metadata (4 lignes) [UNCHANGED]
├── __main__.py              # Entry point (80 lignes) [REFACTORED]
├── tools.py                 # MCP tool definitions (120 lignes)
├── vision_enhancement.py    # MCP sampling logic (250 lignes) [NEW - BRIEF_02]
├── utils.py                 # Shared utilities (60 lignes)
└── server.py                # HTTP/SSE server setup (110 lignes)
```

**Total Lines** : ~672 lignes (vs 176 lignes monolithique)  
**Modularity Gain** : 7 fichiers séparés vs 1 fichier

---

## 📄 Spécifications par Fichier

### 1. `utils.py` - Shared Utilities

**Responsabilité** : Fonctions utilitaires partagées entre modules.

**Functions** :

#### `resolve_image_dir_for_file_uri(uri: str, image_dir: Optional[str], output_images: bool) -> Optional[str]`

**Signature complète** :
```python
from typing import Optional
from pathlib import Path
from urllib.parse import urlparse, unquote

def resolve_image_dir_for_file_uri(
    uri: str,
    image_dir: Optional[str],
    output_images: bool
) -> Optional[str]:
    """
    Resolve image directory relative to source file for file:// URIs.
    
    This ensures images are saved relative to the source PPTX file, not the
    current working directory. Critical for BRIEF_01 functionality.
    
    Args:
        uri: Source file URI (e.g., "file:///C:/path/presentation.pptx")
        image_dir: Requested image directory (relative or absolute)
        output_images: Whether images should be saved
        
    Returns:
        Resolved image directory path, or None if not applicable
        
    Example:
        >>> resolve_image_dir_for_file_uri("file:///C:/docs/pres.pptx", "images", True)
        'C:/docs/images'
    """
    # Implementation details in plan
```

**Logic** :
1. Return None si `not output_images`
2. Parse URI avec `urlparse(uri)`
3. Si scheme != "file" → return image_dir (unchanged)
4. Extraire path avec `Path(unquote(parsed.path))`
5. Get parent directory : `source_dir = path.parent`
6. Resolve image_dir : `Path(source_dir) / (image_dir or "images")`
7. Return str(resolved_path)

---

#### `check_plugins_enabled() -> bool`

**Signature complète** :
```python
import os

def check_plugins_enabled() -> bool:
    """
    Check if MarkItDown plugins are enabled via environment variable.
    
    Returns:
        True if MARKITDOWN_ENABLE_PLUGINS is set to true/1/yes (case-insensitive),
        False otherwise
        
    Example:
        >>> os.environ["MARKITDOWN_ENABLE_PLUGINS"] = "1"
        >>> check_plugins_enabled()
        True
    """
    # Implementation
```

**Logic** :
1. Lire `os.environ.get("MARKITDOWN_ENABLE_PLUGINS", "").lower()`
2. Return `value in ["1", "true", "yes"]`

---

### 2. `server.py` - HTTP/SSE Server Setup

**Responsabilité** : Configuration serveur Starlette pour mode HTTP/SSE.

**Functions** :

#### `create_starlette_app(mcp_server: Server, debug: bool = False) -> Starlette`

**Signature complète** :
```python
from contextlib import asynccontextmanager
from typing import AsyncIterator
from mcp.server import Server, SseServerTransport, StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.requests import Request
from starlette.types import Receive, Scope, Send

def create_starlette_app(mcp_server: Server, debug: bool = False) -> Starlette:
    """
    Create Starlette application for MCP over HTTP/SSE.
    
    Args:
        mcp_server: Configured FastMCP server instance
        debug: Enable debug logging
        
    Returns:
        Configured Starlette app ready for uvicorn
    """
    # Implementation
```

**Code à migrer depuis __main__.py** :
- `create_starlette_app()` function entière
- `handle_sse()` async handler
- `handle_streamable_http()` handler  
- `lifespan()` context manager

**Dépendances** :
- `mcp.server` : Server, SseServerTransport, StreamableHTTPSessionManager
- `starlette.*` : Starlette, Request, Mount, Route, Receive, Scope, Send
- `contextlib.asynccontextmanager`

---

### 3. `tools.py` - MCP Tool Definitions

**Responsabilité** : Définir tous les outils MCP exposés aux clients.

**Global Objects** :
```python
from mcp import FastMCP
from markitdown import MarkItDown
from .utils import resolve_image_dir_for_file_uri, check_plugins_enabled

# Initialize FastMCP instance
mcp = FastMCP("markitdown")

# Initialize MarkItDown converter
converter = MarkItDown()
```

**Tools** :

#### `@mcp.tool() async def convert_to_markdown(...)`

**Signature complète** :
```python
@mcp.tool()
async def convert_to_markdown(
    uri: str,
    output_images: bool = True,
    image_dir: str = "images",
    use_client_vision: bool = True
) -> str:
    """
    Convert a file to Markdown format with optional image extraction.
    
    Supports: PPTX, DOCX, PDF, HTML, XLSX, CSV, JSON, Images, Audio.
    
    Args:
        uri: File URI (file://, http://, https://) or local path
        output_images: Save images from PPTX/DOCX to separate files
        image_dir: Directory for saved images (relative to source file)
        use_client_vision: Use client's multimodal vision for image analysis (BRIEF_02)
        
    Returns:
        Markdown content with potential vision enhancements
        
    Example:
        >>> result = await convert_to_markdown(
        ...     "file:///C:/docs/presentation.pptx",
        ...     output_images=True,
        ...     use_client_vision=True
        ... )
    """
    # Implementation steps:
    # 1. Resolve image_dir relative to source file
    # 2. Check plugins enabled
    # 3. Call converter.convert_uri()
    # 4. If use_client_vision → enhance with client vision
    # 5. Return markdown result
```

**Logic détaillée** :
```python
# Step 1: Resolve image directory
adjusted_image_dir = resolve_image_dir_for_file_uri(uri, image_dir, output_images)

# Step 2: Check plugins
enable_plugins = check_plugins_enabled()

# Step 3: Convert file
result = converter.convert_uri(
    uri=uri,
    image_dir=adjusted_image_dir,
    output_images=output_images,
    enable_plugins=enable_plugins
)
markdown = result.text_content

# Step 4: Vision enhancement (BRIEF_02)
if use_client_vision:
    from .vision_enhancement import enhance_markdown_with_client_vision
    markdown = await enhance_markdown_with_client_vision(
        markdown=markdown,
        server=mcp._server,  # Access underlying FastMCP server
        output_images=output_images
    )

# Step 5: Return result
return markdown
```

---

### 4. `vision_enhancement.py` - MCP Sampling Logic (BRIEF_02)

**Responsabilité** : Déléguer analyse d'images au LLM client via MCP Sampling.

**Imports** :
```python
from typing import Optional
from pathlib import Path
import base64
import re
import imghdr

from mcp.server import Server
from mcp.types import (
    CreateMessageRequest,
    CreateMessageResult,
    SamplingMessage,
    TextContent,
    ImageContent,
)
```

---

#### `async def enhance_markdown_with_client_vision(markdown, server, output_images)`

**Signature complète** :
```python
async def enhance_markdown_with_client_vision(
    markdown: str,
    server: Server,
    output_images: bool
) -> str:
    """
    Enhance Markdown with client vision analysis via MCP Sampling.
    
    Delegates image analysis to the calling LLM client (VS Code Copilot, Claude, etc.)
    using MCP Protocol 2024-11-05 sampling capability.
    
    Args:
        markdown: Markdown content to enhance
        server: MCP server instance for sampling requests
        output_images: If True → Mode 1 (alt text), else → Mode 2 (description blocks)
        
    Returns:
        Enhanced markdown with vision-generated descriptions
        
    Behavior:
        - Mode 1 (output_images=True): Enrich alt text of images without alt text (max 100 chars)
        - Mode 2 (output_images=False): Generate description blocks for ALL images (title + 10 lines)
        - Graceful fallback if client doesn't support sampling
        
    Example:
        >>> enhanced = await enhance_markdown_with_client_vision(
        ...     markdown="![](image1.png)",
        ...     server=mcp_server,
        ...     output_images=False
        ... )
    """
    # Check sampling support
    if not await client_supports_sampling(server):
        return markdown  # Graceful fallback
    
    # Delegate to mode-specific function
    if output_images:
        return await _enhance_alt_texts(markdown, server)
    else:
        return await _generate_description_blocks(markdown, server)
```

---

#### `async def client_supports_sampling(server)`

**Signature complète** :
```python
async def client_supports_sampling(server: Server) -> bool:
    """
    Check if the connected MCP client supports sampling capability.
    
    Args:
        server: MCP server instance
        
    Returns:
        True if client supports sampling/createMessage, False otherwise
        
    Example:
        >>> supports = await client_supports_sampling(mcp_server)
        >>> if supports:
        ...     # Use sampling features
    """
    try:
        caps = await server.get_client_capabilities()
        return caps.get("sampling", False)
    except Exception:
        return False  # Graceful fallback
```

---

#### `async def _enhance_alt_texts(markdown, server)`

**Signature complète** :
```python
async def _enhance_alt_texts(markdown: str, server: Server) -> str:
    """
    Mode 1: Enrich alt text for images without alt text via sampling.
    
    Only processes images with empty alt text. Preserves existing alt text.
    Requests SHORT descriptions (max 100 characters) from client.
    
    Args:
        markdown: Markdown content
        server: MCP server for sampling
        
    Returns:
        Markdown with enriched alt text
        
    Example:
        Input:  "![](image.png)"
        Output: "![Product team meeting with 5 people around table](image.png)"
    """
    # Parse images
    images = parse_markdown_images(markdown)
    
    for alt_text, image_path in images:
        # Skip if alt text exists
        if alt_text and alt_text.strip():
            continue
        
        # Read image file
        image_data = read_image_file(image_path)
        if not image_data:
            continue  # Skip if file not found
        
        # Request short description
        prompt = "Describe this PowerPoint image in 1 concise phrase (max 100 characters):"
        description = await request_client_image_analysis(
            server=server,
            image_data=image_data,
            prompt=prompt,
            max_tokens=100
        )
        
        if description:
            # Replace empty alt text with description
            markdown = markdown.replace(
                f'![{alt_text}]({image_path})',
                f'![{description}]({image_path})'
            )
    
    return markdown
```

---

#### `async def _generate_description_blocks(markdown, server)`

**Signature complète** :
```python
async def _generate_description_blocks(markdown: str, server: Server) -> str:
    """
    Mode 2: Generate description blocks for ALL images via sampling.
    
    Processes every image found in markdown. Requests DETAILED descriptions
    (title + max 10 lines) from client. Formats as ```image-description blocks.
    
    Args:
        markdown: Markdown content
        server: MCP server for sampling
        
    Returns:
        Markdown with image-description blocks replacing image references
        
    Example:
        Input:  "![Product team](image.png)"
        Output: 
        ```image-description
        Product Team Meeting
        
        Five team members gathered around a conference table discussing 
        quarterly results. The whiteboard in the background shows project 
        timelines and milestones. The atmosphere appears collaborative 
        with engaged body language.
        ```
    """
    # Parse ALL images
    images = parse_markdown_images(markdown)
    
    for alt_text, image_path in images:
        # Read image file
        image_data = read_image_file(image_path)
        if not image_data:
            continue  # Skip if file not found
        
        # Request detailed description
        prompt = """Analyze this PowerPoint image and provide:
1. A descriptive title (1 line)
2. Detailed description (max 10 lines) covering:
   - What is shown
   - Key visual elements
   - Context/purpose
   - Notable details"""
        
        description = await request_client_image_analysis(
            server=server,
            image_data=image_data,
            prompt=prompt,
            max_tokens=500
        )
        
        if description:
            # Format as description block
            block = f"\n```image-description\n{description}\n```\n"
            
            # Replace image reference with block
            markdown = markdown.replace(
                f'![{alt_text}]({image_path})',
                block
            )
    
    return markdown
```

---

#### `async def request_client_image_analysis(server, image_data, prompt, max_tokens)`

**Signature complète** :
```python
async def request_client_image_analysis(
    server: Server,
    image_data: bytes,
    prompt: str,
    max_tokens: int
) -> Optional[str]:
    """
    Request image analysis from MCP client via sampling/createMessage.
    
    Implements MCP Protocol 2024-11-05 sampling specification.
    
    Args:
        server: MCP server instance
        image_data: Raw image bytes
        prompt: Analysis instructions for client
        max_tokens: Maximum response length
        
    Returns:
        Generated description text, or None if sampling fails
        
    Raises:
        None (graceful fallback on errors)
        
    Example:
        >>> description = await request_client_image_analysis(
        ...     server=mcp_server,
        ...     image_data=image_bytes,
        ...     prompt="Describe this image briefly:",
        ...     max_tokens=100
        ... )
    """
    # Detect MIME type
    mime_type = detect_image_mime_type(image_data)
    
    # Encode base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Create MCP sampling request (MCP 2024-11-05 spec)
    request = CreateMessageRequest(
        messages=[
            SamplingMessage(
                role="user",
                content=[
                    TextContent(
                        type="text",
                        text=prompt
                    ),
                    ImageContent(
                        type="image",
                        data=image_base64,
                        mimeType=mime_type
                    )
                ]
            )
        ],
        maxTokens=max_tokens,
        systemPrompt="You are analyzing images from a PowerPoint presentation."
    )
    
    try:
        # Send sampling request
        result: CreateMessageResult = await server.request_sampling(request)
        
        # Extract text content
        description = result.content.text.strip()
        
        # Respect max_tokens
        return description[:max_tokens]
    
    except Exception as e:
        # Graceful fallback (no description)
        return None
```

**Conformité MCP Protocol 2024-11-05** :
- ✅ `CreateMessageRequest` avec `messages`, `maxTokens`, `systemPrompt`
- ✅ `SamplingMessage` avec `role="user"`, `content=list[TextContent|ImageContent]`
- ✅ `ImageContent` avec `type="image"`, `data=base64`, `mimeType`
- ✅ `await server.request_sampling(request)` → `CreateMessageResult`

---

#### Helper Functions

**`parse_markdown_images(markdown: str) -> list[tuple[str, str]]`**
```python
def parse_markdown_images(markdown: str) -> list[tuple[str, str]]:
    """
    Extract image references from markdown.
    
    Returns:
        List of (alt_text, image_path) tuples
        
    Example:
        >>> parse_markdown_images("![alt](image.png)")
        [('alt', 'image.png')]
    """
    pattern = r'!\[(.*?)\]\((.*?)\)'
    return re.findall(pattern, markdown)
```

**`read_image_file(image_path: str) -> Optional[bytes]`**
```python
def read_image_file(image_path: str) -> Optional[bytes]:
    """Read image file and return bytes, or None if not found."""
    try:
        with open(image_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return None
```

**`detect_image_mime_type(image_data: bytes) -> str`**
```python
def detect_image_mime_type(image_data: bytes) -> str:
    """
    Detect MIME type from image bytes.
    
    Returns:
        MIME type string (e.g., 'image/png', 'image/jpeg')
    """
    image_type = imghdr.what(None, h=image_data)
    return f"image/{image_type or 'png'}"
```

---

### 5. `__main__.py` - Entry Point (Refactored)

**Responsabilité** : Point d'entrée CLI, configuration args, démarrage serveur.

**Contenu après refactoring (80 lignes)** :
```python
# --- MODULE: Entry Point ---
"""
MarkItDown MCP Server - Entry Point

Command-line interface for running MarkItDown as an MCP server.
Supports STDIO mode (default) and HTTP/SSE mode (--http).
"""

import sys
import argparse
from .tools import mcp
from .server import create_starlette_app

def main():
    """Main entry point for MarkItDown MCP server."""
    parser = argparse.ArgumentParser(
        description="MarkItDown MCP Server"
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run in HTTP/SSE mode instead of STDIO"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Port for HTTP mode (default: 3000)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.http:
        # HTTP/SSE mode with uvicorn
        import uvicorn
        app = create_starlette_app(mcp._server, debug=args.debug)
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=args.port,
            log_level="debug" if args.debug else "info"
        )
    else:
        # STDIO mode (default)
        mcp.run()

if __name__ == "__main__":
    main()
```

**Imports supprimés (migrés)** :
- ❌ `contextlib`, `AsyncIterator`
- ❌ `mcp.server.*` (Server, SseServerTransport, etc.)
- ❌ `starlette.*`

**Imports conservés** :
- ✅ `sys`, `argparse`
- ✅ `from .tools import mcp`
- ✅ `from .server import create_starlette_app`

---

### 6. `__init__.py` - Package Exports

**Contenu après refactoring** :
```python
"""
MarkItDown MCP Server

MCP server providing file-to-markdown conversion tools.
Supports PowerPoint, Word, PDF, HTML, Excel, CSV, JSON, Images, and Audio files.
"""

from .__about__ import __version__
from .tools import mcp

__all__ = ["mcp", "__version__"]
```

---

## 🔄 Modes de Fonctionnement BRIEF_02

### Mode 1 : Alt Text Enrichi (`output_images=True`)

**Objectif** : Enrichir uniquement les images **sans alt text** avec descriptions courtes.

**Workflow** :
1. Parser markdown pour trouver `![](image.png)` (alt text vide)
2. Pour chaque image sans alt text :
   - Lire fichier image
   - Envoyer à client via sampling avec prompt court
   - Recevoir description (max 100 chars)
   - Remplacer `![](image.png)` → `![description](image.png)`
3. Préserver images **avec** alt text existant

**Prompt** :
```
"Describe this PowerPoint image in 1 concise phrase (max 100 characters):"
```

**Exemple** :
```markdown
Before: ![](sales_chart.png)
After:  ![Q4 sales bar chart showing 25% growth across all regions](sales_chart.png)
```

---

### Mode 2 : Description Blocks (`output_images=False`)

**Objectif** : Générer descriptions détaillées pour **TOUTES** les images.

**Workflow** :
1. Parser markdown pour trouver **toutes** les images `![...](image.png)`
2. Pour chaque image :
   - Lire fichier image
   - Envoyer à client via sampling avec prompt détaillé
   - Recevoir description (titre + max 10 lignes)
   - Remplacer `![...](image.png)` → bloc ```image-description
3. Pas de sauvegarde physique d'images (output_images=False)

**Prompt** :
```
"""Analyze this PowerPoint image and provide:
1. A descriptive title (1 line)
2. Detailed description (max 10 lines) covering:
   - What is shown
   - Key visual elements
   - Context/purpose
   - Notable details"""
```

**Exemple** :
```markdown
Before: ![Sales chart](sales_chart.png)

After:
```image-description
Quarterly Sales Performance Chart

A vertical bar chart displaying Q4 2025 sales performance across 
five geographic regions. The chart shows consistent 25% growth 
compared to Q3, with North America leading at $2.5M. Color-coded 
bars use blue (Q3) and green (Q4) for clear comparison. The 
y-axis displays revenue in millions, ranging from 0 to 3M.
```
```

---

## 🌐 Compatibilité Clients

### Client Principal : VS Code + GitHub Copilot

**Capabilities** :
- ✅ MCP Protocol 2024-11-05 compliant
- ✅ Sampling capability (sampling/createMessage)
- ✅ Multimodal models (GPT-4o, Claude 3.5 Sonnet)
- ✅ Image content (base64 + MIME type)

**Configuration MCP** :
```json
{
  "mcpServers": {
    "markitdown": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "markitdown_mcp"]
    }
  }
}
```

---

### Client Secondaire : Claude Desktop

**Capabilities** :
- ✅ MCP Protocol 2024-11-05 compliant
- ✅ Sampling capability
- ✅ Claude 3.5 Sonnet (multimodal)

**Configuration** :
```json
{
  "mcpServers": {
    "markitdown": {
      "command": "python",
      "args": ["-m", "markitdown_mcp"]
    }
  }
}
```

---

### Client Test : MCP Inspector

**Capabilities** :
- ✅ MCP Protocol inspector
- ✅ SSE connection
- ⚠️ Limited sampling support (test only)

**Lancement** :
```bash
# Mode HTTP
python -m markitdown_mcp --http --port 3000

# Inspector
npx @modelcontextprotocol/inspector
# Connect to http://localhost:3000/sse
```

---

## 📊 Performance Estimée

### Comparison : OpenAI API vs MCP Sampling

| Métrique | OpenAI API | MCP Sampling |
|----------|-----------|--------------|
| Configuration | API keys requis | 0 setup |
| Latence (50 images) | ~100s | ~50s (2× faster) |
| Coût (50 images) | $0.50 | $0 (client pays) |
| Offline support | ❌ Non | ✅ Oui (si client local) |
| Model choice | Fixed (gpt-4o-mini) | Client's model |

**MCP Sampling Advantages** :
- ✅ **2× faster** (parallel requests)
- ✅ **Zero cost** for MCP server
- ✅ **Zero config** (no API keys)
- ✅ **Client's model** (user choice)

---

## 🧪 Stratégie de Test

### Tests Unitaires

**À créer** : `packages/markitdown-mcp/tests/test_vision_enhancement.py`

```python
import pytest
from markitdown_mcp.vision_enhancement import (
    parse_markdown_images,
    detect_image_mime_type,
    read_image_file
)

def test_parse_markdown_images():
    markdown = "![alt1](img1.png) text ![](img2.jpg)"
    images = parse_markdown_images(markdown)
    assert images == [('alt1', 'img1.png'), ('', 'img2.jpg')]

def test_detect_mime_type_png():
    png_header = b'\x89PNG\r\n\x1a\n'
    assert detect_image_mime_type(png_header) == "image/png"

@pytest.mark.asyncio
async def test_enhance_alt_texts_no_sampling(mock_server):
    # Mock server without sampling capability
    markdown = "![](test.png)"
    result = await enhance_markdown_with_client_vision(
        markdown, mock_server, output_images=True
    )
    assert result == markdown  # Unchanged (fallback)
```

### Tests d'Intégration

**Scénario 1** : Mode 1 avec VS Code
```python
# Test with real VS Code + Copilot
pptx_uri = "file:///C:/test/presentation.pptx"
result = await convert_to_markdown(
    uri=pptx_uri,
    output_images=True,
    use_client_vision=True
)
# Verify alt text enriched
assert "![" in result
assert len(alt_text) <= 100
```

**Scénario 2** : Mode 2 avec descriptions
```python
result = await convert_to_markdown(
    uri=pptx_uri,
    output_images=False,
    use_client_vision=True
)
# Verify description blocks
assert "```image-description" in result
assert "```\n" in result
```

---

## 📚 Standards et Références

### MCP Protocol 2024-11-05

**Specification** : https://spec.modelcontextprotocol.io/specification/2024-11-05/

**Key Types** :
- `CreateMessageRequest` : Request structure for sampling
- `SamplingMessage` : Message with role and content
- `TextContent` : Text content type
- `ImageContent` : Image with base64 data and MIME type
- `CreateMessageResult` : Response with generated content

**Conformité** :
- ✅ Utilise types officiels du package `mcp`
- ✅ Structure requests selon spec 2024-11-05
- ✅ Gère errors gracefully (fallback)

### Python Instructions

**python.instructions.md** :
- ✅ Type hints obligatoires
- ✅ Docstrings Google style
- ✅ PEP 8 compliance (79 chars, 4 espaces)
- ✅ Imports groupés (standard, external, internal)
- ✅ Error handling avec try/except

**self-explanatory-code.instructions.md** :
- ✅ Commenter le WHY, pas le WHAT
- ✅ Noms variables explicites
- ✅ Annotations (TODO, FIXME, NOTE, etc.)

---

## 🚨 Contraintes Critiques

### Architecture
- ✅ **Modifications UNIQUEMENT** : `packages/markitdown-mcp/`
- ❌ **AUCUNE modification** : `packages/markitdown/` (core)
- ❌ **N'UTILISE PAS** : `_llm_caption.py` (obsolète pour BRIEF_02)

### Qualité
- ✅ `get_errors` après chaque modification
- ✅ Fix immédiat des erreurs avant de continuer
- ✅ Type hints et docstrings complets
- ✅ Tests unitaires et intégration

### Workflow
- ✅ Phase 1 COMPLÈTE avant Phase 2
- ✅ Tests régression après Phase 1
- ✅ Validation checkpoint entre phases

---

**Prochaine étape** : Utiliser ce document comme référence durant l'implémentation Python Expert.
