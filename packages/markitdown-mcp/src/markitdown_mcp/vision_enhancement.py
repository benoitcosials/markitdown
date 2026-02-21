# --- MODULE: Vision Enhancement via MCP Sampling (BRIEF_02) ---
"""
Vision enhancement for image descriptions via MCP Sampling.

Delegates image analysis to the calling LLM client (VS Code Copilot, Claude, etc.)
using MCP Protocol 2024-11-05 sampling capability. Provides two modes:
- Mode 1 (output_images=True): Enrich alt text for images without alt text
- Mode 2 (output_images=False): Generate detailed description blocks for all images

This approach eliminates the need for external API configuration (OpenAI/Azure)
by leveraging the client's own multimodal vision capabilities.
"""

import base64
import imghdr
import re
from typing import Optional

from mcp.server import Server
from mcp.types import (
    CreateMessageRequest,
    CreateMessageResult,
    ImageContent,
    SamplingMessage,
    TextContent,
)

# --- Helper Functions ---


def parse_markdown_images(markdown: str) -> list[tuple[str, str]]:
    """
    Extract image references from markdown content.
    
    Finds all markdown image syntax ![alt](path) and returns tuples
    of (alt_text, image_path).
    
    Args:
        markdown: Markdown content to parse
        
    Returns:
        List of (alt_text, image_path) tuples
        
    Example:
        >>> parse_markdown_images("![Photo](img.png) text ![](img2.jpg)")
        [('Photo', 'img.png'), ('', 'img2.jpg')]
    """
    pattern = r'!\[(.*?)\]\((.*?)\)'
    return re.findall(pattern, markdown)


def read_image_file(image_path: str) -> Optional[bytes]:
    """
    Read image file and return bytes content.
    
    Args:
        image_path: Path to image file (relative or absolute)
        
    Returns:
        Image bytes if file exists, None otherwise
        
    Example:
        >>> data = read_image_file("images/photo.png")
        >>> data is not None
        True
    """
    try:
        with open(image_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return None


def detect_image_mime_type(image_data: bytes) -> str:
    """
    Detect MIME type from image bytes.
    
    Uses imghdr to identify image format from binary data.
    Defaults to 'image/png' if detection fails.
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        MIME type string (e.g., 'image/png', 'image/jpeg')
        
    Example:
        >>> png_data = b'\\x89PNG\\r\\n\\x1a\\n...'
        >>> detect_image_mime_type(png_data)
        'image/png'
    """
    image_type = imghdr.what(None, h=image_data)
    return f"image/{image_type or 'png'}"


# --- MCP Sampling Core ---


async def request_client_image_analysis(
    server: Server,
    image_data: bytes,
    prompt: str,
    max_tokens: int
) -> Optional[str]:
    """
    Request image analysis from MCP client via sampling/createMessage.
    
    Implements MCP Protocol 2024-11-05 sampling specification to delegate
    image analysis to the calling LLM client's vision capabilities.
    
    This avoids the need for external API configuration (OpenAI/Azure) by
    using the client's own multimodal model (GPT-4o, Claude 3.5, etc.).
    
    Args:
        server: MCP server instance for sampling requests
        image_data: Raw image bytes
        prompt: Analysis instructions for the client
        max_tokens: Maximum response length
        
    Returns:
        Generated description text, or None if sampling fails
        
    Conformance:
        MCP Protocol 2024-11-05:
        - CreateMessageRequest with messages, maxTokens, systemPrompt
        - SamplingMessage with role="user", content=[TextContent, ImageContent]
        - ImageContent with type="image", data=base64, mimeType
        
    Example:
        >>> description = await request_client_image_analysis(
        ...     server=mcp_server,
        ...     image_data=image_bytes,
        ...     prompt="Describe this image briefly:",
        ...     max_tokens=100
        ... )
    """
    # Detect MIME type from image data
    mime_type = detect_image_mime_type(image_data)
    
    # Encode image as base64 string (required by MCP ImageContent)
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Create MCP sampling request (MCP Protocol 2024-11-05)
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
        # Send sampling request to MCP client
        result: CreateMessageResult = await server.request_sampling(request)
        
        # Extract text content from response
        description = result.content.text.strip()
        
        # Respect max_tokens limit
        return description[:max_tokens]
    
    except Exception:
        # Graceful fallback - return None if sampling fails
        # This allows the system to continue without descriptions
        # rather than crashing when client doesn't support sampling
        return None


# --- Capability Detection ---


async def client_supports_sampling(server: Server) -> bool:
    """
    Check if the connected MCP client supports sampling capability.
    
    Queries the client's capabilities to determine if sampling/createMessage
    requests are supported. Used for graceful degradation when client lacks
    vision capabilities.
    
    Args:
        server: MCP server instance
        
    Returns:
        True if client supports sampling, False otherwise
        
    Example:
        >>> supports = await client_supports_sampling(mcp_server)
        >>> if supports:
        ...     # Use vision enhancement
        ... else:
        ...     # Skip vision enhancement
    """
    try:
        caps = await server.get_client_capabilities()
        return caps.get("sampling", False)
    except Exception:
        # Graceful fallback if capabilities check fails
        return False


# --- Mode 1: Alt Text Enrichment ---


async def _enhance_alt_texts(markdown: str, server: Server) -> str:
    """
    Mode 1: Enrich alt text for images WITHOUT existing alt text.
    
    Only processes images with empty alt text ![](image.png).
    Preserves existing alt text ![existing](image.png) unchanged.
    Requests SHORT descriptions (max 100 characters) from client.
    
    Used when output_images=True (images saved to disk).
    
    Args:
        markdown: Markdown content to enhance
        server: MCP server for sampling requests
        
    Returns:
        Markdown with enriched alt text
        
    Example:
        Input:  "![](chart.png) and ![Photo](team.png)"
        Output: "![Q4 sales bar chart](chart.png) and ![Photo](team.png)"
    """
    # Parse all image references
    images = parse_markdown_images(markdown)
    
    for alt_text, image_path in images:
        # Skip if alt text already exists
        if alt_text and alt_text.strip():
            continue
        
        # Read image file
        image_data = read_image_file(image_path)
        if not image_data:
            # Skip if file not found (broken reference)
            continue
        
        # Request short description from client
        prompt = "Describe this PowerPoint image in 1 concise phrase (max 100 characters):"
        description = await request_client_image_analysis(
            server=server,
            image_data=image_data,
            prompt=prompt,
            max_tokens=100
        )
        
        if description:
            # Replace empty alt text with generated description
            markdown = markdown.replace(
                f'![{alt_text}]({image_path})',
                f'![{description}]({image_path})'
            )
    
    return markdown


# --- Mode 2: Description Blocks ---


async def _generate_description_blocks(markdown: str, server: Server) -> str:
    """
    Mode 2: Generate detailed description blocks for ALL images.
    
    Processes every image found in markdown, regardless of alt text.
    Requests DETAILED descriptions (title + max 10 lines) from client.
    Formats as ```image-description code blocks.
    
    Used when output_images=False (images not saved, text descriptions only).
    
    Args:
        markdown: Markdown content to enhance
        server: MCP server for sampling requests
        
    Returns:
        Markdown with image-description blocks replacing image references
        
    Example:
        Input:  "![Chart](sales.png)"
        Output: 
        ```image-description
        Quarterly Sales Performance Chart
        
        A vertical bar chart displaying Q4 2025 sales...
        ```
    """
    # Parse ALL image references
    images = parse_markdown_images(markdown)
    
    for alt_text, image_path in images:
        # Read image file
        image_data = read_image_file(image_path)
        if not image_data:
            # Skip if file not found
            continue
        
        # Request detailed description from client
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
            
            # Replace image reference with description block
            markdown = markdown.replace(
                f'![{alt_text}]({image_path})',
                block
            )
    
    return markdown


# --- Main Entry Point ---


async def enhance_markdown_with_client_vision(
    markdown: str,
    server: Server,
    output_images: bool
) -> str:
    """
    Enhance Markdown with client vision analysis via MCP Sampling.
    
    Main entry point for BRIEF_02 vision enhancement. Delegates image analysis
    to the calling LLM client (VS Code Copilot, Claude Desktop, etc.) using
    MCP Protocol 2024-11-05 sampling capability.
    
    Two modes based on output_images parameter:
    - Mode 1 (output_images=True): Enrich alt text for images without alt text
    - Mode 2 (output_images=False): Generate description blocks for all images
    
    Gracefully degrades if client doesn't support sampling - returns markdown unchanged.
    
    Args:
        markdown: Markdown content to enhance
        server: MCP server instance for sampling
        output_images: Mode selector (True=alt text, False=description blocks)
        
    Returns:
        Enhanced markdown with vision-generated descriptions
        
    Behavior:
        - Checks client sampling support first
        - Returns unchanged markdown if sampling not supported
        - Mode 1: Only enhances images WITHOUT alt text
        - Mode 2: Processes ALL images with detailed descriptions
        
    Example:
        >>> enhanced = await enhance_markdown_with_client_vision(
        ...     markdown="![](chart.png)",
        ...     server=mcp_server,
        ...     output_images=False
        ... )
        # Returns markdown with ```image-description block
    """
    # Check if client supports sampling capability
    if not await client_supports_sampling(server):
        # Graceful fallback - return unchanged if no sampling support
        return markdown
    
    # Delegate to mode-specific function
    if output_images:
        # Mode 1: Enrich alt text for images without alt text
        return await _enhance_alt_texts(markdown, server)
    else:
        # Mode 2: Generate description blocks for all images
        return await _generate_description_blocks(markdown, server)
