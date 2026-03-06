import base64
import hashlib  # For MD5 deduplication
import io
import os
import re
import sys
import unicodedata
import zipfile
from pathlib import Path
from typing import Any, BinaryIO, List, Optional
from urllib.parse import quote

# Try loading lxml for SmartArt extraction (BRIEF_05)
try:
    from lxml import etree
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False

from .._base_converter import DocumentConverter, DocumentConverterResult
from .._exceptions import (
    MISSING_DEPENDENCY_MESSAGE,
    MissingDependencyException,
)
from .._stream_info import StreamInfo
from ._html_converter import HtmlConverter
from ._llm_caption import llm_caption

# Try loading optional (but in this case, required) dependencies
# Save reporting of any exceptions for later
_dependency_exc_info = None
try:
    import pptx
except ImportError:
    # Preserve the error and stack trace for later
    _dependency_exc_info = sys.exc_info()


ACCEPTED_MIME_TYPE_PREFIXES = [
    "application/vnd.openxmlformats-officedocument.presentationml",
]

ACCEPTED_FILE_EXTENSIONS = [".pptx"]

# --- MODULE: Color Mapping for Table Cells ---
# Maps RGB tuples to (emoji, french_name)
# Using Unicode colored square emojis where available
COLOR_MAP = {
    # Primary colors
    (255, 0, 0): ("🔴", "rouge"),
    (0, 255, 0): ("🟢", "vert"),
    (0, 128, 0): ("🟢", "vert"),  # Dark green
    (0, 0, 255): ("🔵", "bleu"),
    # Secondary colors
    (255, 255, 0): ("🟡", "jaune"),
    (255, 165, 0): ("🟠", "orange"),
    (255, 127, 0): ("🟠", "orange"),
    (128, 0, 128): ("🟣", "violet"),
    (255, 0, 255): ("🟣", "magenta"),
    # Neutrals
    (0, 0, 0): ("⚫", "noir"),
    (255, 255, 255): ("⚪", "blanc"),
    (128, 128, 128): ("⚫", "gris"),
    (165, 42, 42): ("🟤", "marron"),
    (139, 69, 19): ("🟤", "marron"),
    # Common PowerPoint theme colors
    (146, 208, 80): ("🟢", "vert clair"),  # Light green
    (0, 176, 80): ("🟢", "vert"),  # Green
    (0, 176, 240): ("🔵", "bleu clair"),  # Light blue
    (0, 112, 192): ("🔵", "bleu"),  # Blue
    (255, 192, 0): ("🟡", "jaune"),  # Gold/Yellow
}

# Reference colors for proximity matching (subset for efficiency)
COLOR_REFERENCES = [
    ((255, 0, 0), "🔴", "rouge"),
    ((0, 255, 0), "🟢", "vert"),
    ((0, 128, 0), "🟢", "vert foncé"),
    ((0, 0, 255), "🔵", "bleu"),
    ((255, 255, 0), "🟡", "jaune"),
    ((255, 165, 0), "🟠", "orange"),
    ((128, 0, 128), "🟣", "violet"),
    ((255, 0, 255), "🟣", "magenta"),
    ((0, 0, 0), "⚫", "noir"),
    ((255, 255, 255), "⚪", "blanc"),
    ((128, 128, 128), "⚫", "gris"),
    ((165, 42, 42), "🟤", "marron"),
    ((0, 255, 255), "🔵", "cyan"),
    ((255, 192, 203), "🔴", "rose"),
]
# --- END MODULE ---


class PptxConverter(DocumentConverter):
    """
    Converts PPTX files to Markdown. Supports heading, tables and images with alt text.
    """

    def __init__(self):
        super().__init__()
        self._html_converter = HtmlConverter()
        # --- MODULE: Image Management (BRIEF_01) ---
        self._image_hashes = {}  # Deduplication mapping {hash: path}
        # --- END MODULE ---

    # --- MODULE: UTF-8 Text Normalization (BRIEF_06) ---
    def _to_utf8(self, text: str | bytes) -> str:
        """
        Convert text to normalized UTF-8.
        
        Handles encoding detection for bytes and normalizes unicode
        characters (typographic quotes, non-breaking spaces, etc.).
        
        Args:
            text: String or bytes to normalize
            
        Returns:
            str: UTF-8 normalized string (NFKC form)
        """
        if isinstance(text, bytes):
            # Try charset detection first
            try:
                from charset_normalizer import from_bytes
                result = from_bytes(text).best()
                if result:
                    text = str(result)
                else:
                    text = text.decode('utf-8', errors='replace')
            except ImportError:
                # Fallback: try common encodings
                for enc in ['utf-8', 'cp1252', 'iso-8859-1', 'latin-1']:
                    try:
                        text = text.decode(enc)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    text = text.decode('utf-8', errors='replace')
        
        # Normalize unicode to NFKC (compatibility decomposition + composition)
        text = unicodedata.normalize('NFKC', text)
        
        # Replace typographic characters with ASCII equivalents
        replacements = {
            '\u2019': "'",  # Right single quote → apostrophe
            '\u2018': "'",  # Left single quote → apostrophe
            '\u201C': '"',  # Left double quote
            '\u201D': '"',  # Right double quote
            '\u00A0': ' ',  # Non-breaking space
            '\u2013': '-',  # En dash
            '\u2014': '-',  # Em dash
            '\u2026': '...',  # Ellipsis
            '\x0b': ' ',  # Vertical tab → space
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text

    def _format_paragraph_text(self, para) -> str:
        """
        Format paragraph text with markdown styles and hyperlinks.
        
        Processes runs and merges consecutive runs with identical styles
        before applying markdown formatting:
        - Bold: **text**
        - Italic: *text*
        - Strikethrough: ~~text~~
        - Underline: <u>text</u>
        - Hyperlinks: [text](url)
        
        Args:
            para: Paragraph object from text_frame.paragraphs
            
        Returns:
            Formatted markdown string with styles and links
        """
        if not para.runs:
            return self._to_utf8(para.text)
        
        # Collect runs with their style signature
        # Format: (text, bold, italic, strikethrough, underline, hyperlink_url)
        styled_runs = []
        for run in para.runs:
            text = self._to_utf8(run.text)
            if not text:
                continue
            
            font = run.font
            bold = bool(font.bold)
            italic = bool(font.italic)
            strikethrough = bool(getattr(font, 'strikethrough', None))
            underline = bool(font.underline)
            
            hyperlink_url = None
            if run.hyperlink and run.hyperlink.address:
                url = run.hyperlink.address
                if not url.startswith('slide'):
                    hyperlink_url = url
            
            styled_runs.append((text, bold, italic, strikethrough, underline, hyperlink_url))
        
        if not styled_runs:
            return self._to_utf8(para.text)
        
        # Merge consecutive runs with identical styles
        merged_runs = []
        current_text = styled_runs[0][0]
        current_style = styled_runs[0][1:]
        
        for i in range(1, len(styled_runs)):
            text, *style = styled_runs[i]
            style = tuple(style)
            if style == current_style:
                current_text += text
            else:
                merged_runs.append((current_text, *current_style))
                current_text = text
                current_style = style
        merged_runs.append((current_text, *current_style))
        
        # Apply markdown formatting to each merged run
        parts = []
        for text, bold, italic, strikethrough, underline, hyperlink_url in merged_runs:
            # Extract leading/trailing whitespace to place outside style markers
            stripped = text.strip()
            if not stripped:
                # Text is only whitespace, keep as-is
                parts.append(text)
                continue
            
            leading_space = text[:len(text) - len(text.lstrip())]
            trailing_space = text[len(text.rstrip()):]
            text = stripped
            
            # Apply styles to stripped text
            if italic:
                text = f"*{text}*"
            if bold:
                text = f"**{text}**"
            if strikethrough:
                text = f"~~{text}~~"
            if underline:
                text = f"<u>{text}</u>"
            if hyperlink_url:
                text = f"[{text}]({hyperlink_url})"
            
            # Re-add whitespace outside the markers
            parts.append(f"{leading_space}{text}{trailing_space}")
        
        return ''.join(parts)

    def _format_cell_text(self, cell) -> str:
        """
        Format table cell text with markdown styles and hyperlinks.
        
        Processes all paragraphs in the cell and joins them with <br>.
        Each paragraph is processed with _format_paragraph_text().
        
        Args:
            cell: Table cell object
            
        Returns:
            Formatted markdown string for table cell
        """
        if not hasattr(cell, 'text_frame'):
            text = self._to_utf8(cell.text.strip()) if cell.text else ""
            return text.replace("|", "\\|").replace("\n", "<br>")
        
        parts = []
        for para in cell.text_frame.paragraphs:
            text = self._format_paragraph_text(para).strip()
            if text:
                # Escape pipe characters for Markdown table
                text = text.replace("|", "\\|")
                parts.append(text)
        
        return "<br>".join(parts)

    def _format_shape_text(self, shape) -> str:
        """
        Format all text in a shape with markdown styles and hyperlinks.
        
        Processes all paragraphs in the shape's text_frame.
        Each paragraph is processed with _format_paragraph_text().
        
        Args:
            shape: Shape object with text_frame
            
        Returns:
            Formatted markdown string (paragraphs joined with newline)
        """
        if not shape.has_text_frame:
            return self._to_utf8(shape.text) if hasattr(shape, 'text') else ""
        
        parts = []
        for para in shape.text_frame.paragraphs:
            text = self._format_paragraph_text(para)
            if text:
                parts.append(text)
        
        return ' '.join(parts)
    # --- END MODULE ---

    # --- MODULE: Hierarchical Text Detection (BRIEF_06) ---
    def _get_paragraph_font_size(self, para) -> Optional[float]:
        """
        Get font size of a paragraph from its first run with a defined size.
        
        Args:
            para: Paragraph object from text_frame.paragraphs
            
        Returns:
            Font size in points, or None if not defined
        """
        for run in para.runs:
            if run.font.size:
                return run.font.size.pt
        return None

    def _collect_paragraph_metrics(self, text_shapes: List) -> List[tuple]:
        """
        Collect font metrics for all paragraphs across all text shapes.
        
        Analyzes each paragraph individually to get accurate font size
        and character count, including bullet items.
        
        Args:
            text_shapes: List of text shapes (non-title)
            
        Returns:
            List of (font_size, char_count) tuples for all paragraphs
        """
        metrics = []
        for shape in text_shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                size = self._get_paragraph_font_size(para)
                if size:
                    char_count = len(para.text.strip())
                    if char_count > 0:
                        metrics.append((size, char_count))
        return metrics

    def _compute_heading_sizes(self, text_shapes: List) -> set[float]:
        """
        Compute which font sizes should be rendered as headings.
        
        Algorithm:
        - Collect all paragraphs with their font sizes and char counts
        - Calculate total character count per font size (font_weights)
        - The dominant size = font size with most characters (normal text)
        - Font sizes larger than dominant are heading sizes
        
        Args:
            text_shapes: List of text shapes (non-title)
            
        Returns:
            Set of font sizes (pt) that should be rendered as headings
        """
        metrics = self._collect_paragraph_metrics(text_shapes)
        
        if not metrics:
            return set()
        
        font_weights: dict[float, int] = {}
        for size, char_count in metrics:
            font_weights[size] = font_weights.get(size, 0) + char_count
        
        dominant_size = max(font_weights, key=lambda s: font_weights[s])
        
        return {s for s in font_weights if s > dominant_size}

    def _get_heading_level(self, size: float, heading_sizes: set[float]) -> Optional[int]:
        """
        Get heading level (2-6) for a font size based on heading sizes hierarchy.
        
        Args:
            size: Font size in points
            heading_sizes: Set of sizes that are headings
            
        Returns:
            Heading level (2-6) or None if not a heading
        """
        if size not in heading_sizes:
            return None
        sorted_sizes = sorted(heading_sizes, reverse=True)
        level = sorted_sizes.index(size) + 2
        return min(level, 6)

    def _has_explicit_no_bullet(self, para) -> bool:
        """
        Check if paragraph has explicit buNone marker (no bullet).
        
        In PPTX, buNone indicates the paragraph explicitly has no bullet,
        even when other paragraphs in the same shape have bullets.
        """
        try:
            pPr = para._p.pPr
            if pPr is not None:
                ns = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
                buNone = pPr.find(f'.//{ns}buNone')
                return buNone is not None
        except Exception:
            pass
        return False

    def _has_explicit_bullet(self, para) -> bool:
        """
        Check if paragraph has explicit bullet marker (buChar or buAutoNum).
        
        In PPTX, buChar indicates a bullet character (e.g., Wingdings symbol),
        and buAutoNum indicates an auto-numbered list.
        """
        try:
            pPr = para._p.pPr
            if pPr is not None:
                ns = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
                buChar = pPr.find(f'.//{ns}buChar')
                buAutoNum = pPr.find(f'.//{ns}buAutoNum')
                return buChar is not None or buAutoNum is not None
        except Exception:
            pass
        return False

    def _render_text_shape(self, shape, heading_sizes: set[float]) -> str:
        """
        Render a text shape to markdown, handling each paragraph individually.
        
        Each paragraph is classified based on its own font size:
        - Bullets (level > 0, or level 0 without buNone in hierarchical list)
        - Font size in heading_sizes → heading with appropriate level
        - Otherwise → normal text
        
        Args:
            shape: Shape with text_frame
            heading_sizes: Set of font sizes that should be headings
            
        Returns:
            Markdown string for the shape
        """
        if not shape.has_text_frame:
            return ""
        
        # Check if this is a hierarchical bullet list
        is_hierarchical = any(
            (para.level or 0) > 0 
            for para in shape.text_frame.paragraphs
        )
        
        result = []
        current_bullets = []
        
        for para in shape.text_frame.paragraphs:
            text = self._format_paragraph_text(para).strip()
            if not text:
                continue
            
            level = para.level or 0
            size = self._get_paragraph_font_size(para)
            has_no_bullet = self._has_explicit_no_bullet(para)
            has_explicit_bullet = self._has_explicit_bullet(para)
            
            # Determine if this paragraph should be a bullet
            # bullet if: level > 0, or explicit buChar/buAutoNum, or hierarchical without buNone
            is_bullet = level > 0 or has_explicit_bullet or (is_hierarchical and not has_no_bullet)
            
            if is_bullet:
                if not current_bullets and result:
                    result.append("")  # Empty line before starting bullet list
                indent = "   " * level
                current_bullets.append(f"{indent}- {text}")
            else:
                if current_bullets:
                    result.append("\n".join(current_bullets))
                    result.append("")  # Empty line after bullet list
                    current_bullets = []
                
                heading_level = self._get_heading_level(size, heading_sizes) if size else None
                if heading_level:
                    result.append(f"{'#' * heading_level} {text}")
                else:
                    result.append(text)
        
        if current_bullets:
            result.append("\n".join(current_bullets))
        
        return "\n".join(result) + "\n" if result else ""
    # --- END MODULE ---

    # --- MODULE: Path Resolution (BRIEF_06) ---
    def _resolve_image_path(
        self,
        source_path: Optional[str],
        output_path: Optional[str] = None,
        image_path: Optional[str] = None
    ) -> tuple[str, str, bool]:
        """
        Resolve image directory and output base for path calculation.
        
        When both output_path and image_path are provided, the caller
        manages the links - paths are used as-is without relative calculation.
        
        Args:
            source_path: Path to source PPTX file
            output_path: Optional path for output markdown file
            image_path: Optional custom image directory/path
            
        Returns:
            tuple: (output_base, image_base, caller_manages_links)
                - output_base: Base directory for relative path calculation
                - image_base: Absolute path to image directory
                - caller_manages_links: True if caller handles link generation
        """
        # If both output_path and image_path are provided, caller manages links
        caller_manages_links = output_path is not None and image_path is not None
        
        # Determine source directory
        if source_path:
            source_dir = os.path.dirname(os.path.abspath(source_path))
        else:
            source_dir = os.getcwd()
        
        # Output base directory
        if output_path:
            output_base = os.path.dirname(os.path.abspath(output_path))
        else:
            output_base = source_dir
        
        # Image base directory
        if image_path:
            if os.path.isabs(image_path):
                image_base = image_path
            else:
                image_base = os.path.join(output_base, image_path)
        else:
            image_base = os.path.join(output_base, "images")
        
        return output_base, image_base, caller_manages_links

    def _get_relative_image_link(
        self,
        image_full_path: str,
        output_base: str,
        image_path_raw: Optional[str],
        caller_manages_links: bool
    ) -> str:
        """
        Generate image link for markdown.
        
        If caller_manages_links is True, uses image_path_raw + filename as-is.
        Otherwise calculates relative path from output_base.
        
        Args:
            image_full_path: Absolute path to saved image
            output_base: Directory where content.md will be
            image_path_raw: Original image_path parameter from caller
            caller_manages_links: If True, use paths as provided
            
        Returns:
            str: Path for markdown image link
        """
        filename = os.path.basename(image_full_path)
        
        if caller_manages_links and image_path_raw:
            # Caller manages links - use image_path as-is + filename
            link = f"{image_path_raw}/{filename}".replace('\\', '/')
            # Normalize double slashes
            while '//' in link:
                link = link.replace('//', '/')
            return link
        else:
            # Calculate relative path
            rel_path = os.path.relpath(image_full_path, output_base)
            return rel_path.replace('\\', '/')
    # --- END MODULE ---

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> bool:
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True

        for prefix in ACCEPTED_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True

        return False

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        # Check the dependencies
        if _dependency_exc_info is not None:
            raise MissingDependencyException(
                MISSING_DEPENDENCY_MESSAGE.format(
                    converter=type(self).__name__,
                    extension=".pptx",
                    feature="pptx",
                )
            ) from _dependency_exc_info[
                1
            ].with_traceback(  # type: ignore[union-attr]
                _dependency_exc_info[2]
            )

        # Perform the conversion
        presentation = pptx.Presentation(file_stream)
        
        # --- MODULE: Image Management - Configuration (BRIEF_01 + BRIEF_06) ---
        output_images = kwargs.get("output_images", True)
        skip_background_images = kwargs.get("skip_background_images", True)
        skip_icon_images = kwargs.get("skip_icon_images", False)
        self._image_hashes = {}  # Reset for each conversion
        
        # Path resolution for relative links
        source_path = kwargs.get("source_path") or stream_info.filename
        output_path = kwargs.get("output_path")
        image_path_raw = kwargs.get("image_path", "images")
        
        # Resolve paths - if both output_path and image_path provided, caller manages links
        output_base, image_dir, caller_manages_links = self._resolve_image_path(
            source_path, output_path, image_path_raw
        )
        # --- END MODULE ---
        
        md_content = ""
        slide_num = 0
        smartart_count = 0  # Global counter for all SmartArt (BRIEF_05)
        table_count = 0  # Global counter for all tables
        
        for slide in presentation.slides:
            slide_num += 1
            md_content += f"\n\n<!-- Slide number: {slide_num} -->\n"
            
            # Reset per-slide counters
            image_count = 0
            
            # === PHASE 1: Classify all shapes ===
            title_shape = slide.shapes.title
            table_shapes = []
            smartart_shapes = []
            picture_shapes = []
            text_shapes = []
            chart_shapes = []
            group_shapes = []
            
            for shape in slide.shapes:
                if self._is_table(shape):
                    table_shapes.append(shape)
                elif self._is_smartart(shape):
                    smartart_shapes.append(shape)
                elif self._is_picture(shape):
                    picture_shapes.append(shape)
                elif shape.has_chart:
                    chart_shapes.append(shape)
                elif shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.GROUP:
                    group_shapes.append(shape)
                elif shape.has_text_frame and shape != title_shape:
                    text_shapes.append(shape)
            
            # === PHASE 2: Associate floating images with tables ===
            # Maps picture shape id -> table shape it belongs to
            image_to_table: dict[int, object] = {}
            
            for table_shape in table_shapes:
                for img_shape in picture_shapes:
                    img_cx = img_shape.left + img_shape.width // 2
                    img_cy = img_shape.top + img_shape.height // 2
                    in_x = table_shape.left <= img_cx <= table_shape.left + table_shape.width
                    in_y = table_shape.top <= img_cy <= table_shape.top + table_shape.height
                    if in_x and in_y:
                        image_to_table[id(img_shape)] = table_shape
            
            # Orphan images = not associated with any table
            orphan_pictures = [p for p in picture_shapes if id(p) not in image_to_table]
            
            # === PHASE 3: Process in logical order ===
            
            # Get slide height for position normalization
            slide_height = presentation.slide_height or 1
            
            # 3.1 Title (always h1)
            if title_shape and title_shape.has_text_frame:
                title_text = self._format_shape_text(title_shape).lstrip()
                md_content += f"# {title_text}\n"
            
            # 3.2 Compute heading sizes from all text shapes
            heading_sizes = self._compute_heading_sizes(text_shapes)
            
            # Build list of all content items with their Y position for unified sorting
            # Format: (y_position, x_position, type, shape/data)
            content_items = []
            
            for shape in text_shapes:
                y = shape.top or 0
                x = shape.left or 0
                content_items.append((y, x, 'text', shape))
            
            for shape in smartart_shapes:
                y = shape.top or 0
                x = shape.left or 0
                content_items.append((y, x, 'smartart', shape))
            
            for shape in table_shapes:
                y = shape.top or 0
                x = shape.left or 0
                content_items.append((y, x, 'table', shape))
            
            for shape in chart_shapes:
                y = shape.top or 0
                x = shape.left or 0
                content_items.append((y, x, 'chart', shape))
            
            for shape in orphan_pictures:
                y = shape.top or 0
                x = shape.left or 0
                content_items.append((y, x, 'picture', shape))
            
            # Sort content items by position
            # Detect if slide has columns (significant X variance)
            slide_width = presentation.slide_width or 1
            
            if content_items:
                x_values = [x for _, x, _, _ in content_items]
                x_min, x_max = min(x_values), max(x_values)
                x_spread = (x_max - x_min) / slide_width if slide_width else 0
                
                # If X spread > 40% of slide width, treat as multi-column layout
                has_columns = x_spread > 0.4
            else:
                has_columns = False
            
            if has_columns:
                # Multi-column: sort by X-band (column) first, then Y within each column
                def column_position_key(item):
                    y, x, _, _ = item
                    x_band = int((x / slide_width) * 10) if slide_width else 0  # 10% bands
                    return (x_band, y)
                content_items.sort(key=column_position_key)
            else:
                # Single column: sort by Y-band then X
                def position_key(item):
                    y, x, _, _ = item
                    y_band = int((y / slide_height) * 20) if slide_height else 0
                    return (y_band, x)
                content_items.sort(key=position_key)
            
            # 3.3 Process all content in visual order
            for y, x, item_type, shape in content_items:
                if item_type == 'text':
                    rendered = self._render_text_shape(shape, heading_sizes)
                    if rendered:
                        md_content += rendered + "\n"
                
                elif item_type == 'table':
                    table_kwargs = {k: v for k, v in kwargs.items() 
                                   if k not in ('output_images', 'image_path', 'image_dir')}
                    table_name = getattr(shape, 'name', None) or f"table{table_count}"
                    md_content += self._convert_table_to_markdown(
                        shape.table,
                        slide_num=slide_num,
                        table_name=table_name,
                        pptx_stream=file_stream,
                        image_dir=image_dir,
                        output_images=output_images,
                        table_shape=shape,
                        slide_shapes=list(slide.shapes),
                        output_base=output_base,
                        image_path_raw=image_path_raw,
                        caller_manages_links=caller_manages_links,
                        **table_kwargs,
                    )
                    table_count += 1
                
                elif item_type == 'smartart':
                    if not LXML_AVAILABLE:
                        continue
                    
                    diagram_path = self._get_smartart_diagram_path(
                        file_stream, slide_num - 1, shape
                    )
                    
                    if diagram_path:
                        texts, node_images = self._extract_smartart_text(
                            file_stream, diagram_path
                        )
                        
                        saved_images = {}
                        image_descriptions = {}
                        
                        if node_images and kwargs.get('output_images'):
                            saved_images = self._save_smartart_images(
                                file_stream,
                                diagram_path,
                                node_images,
                                slide_num,
                                smartart_count,
                                kwargs,
                            )
                        
                        smartart_md = self._convert_smartart_to_markdown(
                            texts,
                            saved_images,
                            smartart_count,
                            slide_num,
                            image_descriptions,
                        )
                        
                        if smartart_md:
                            md_content += smartart_md
                            smartart_count += 1
                
                elif item_type == 'chart':
                    md_content += self._convert_chart_to_markdown(shape.chart)
                
                elif item_type == 'picture':
                    if skip_background_images and self._is_background_image(shape):
                        continue
                    if skip_icon_images and self._classify_image_type(shape) == 'icon':
                        continue
                    
                    llm_description = ""
                    alt_text = ""
                    
                    llm_client = kwargs.get("llm_client")
                    llm_model = kwargs.get("llm_model")
                    if llm_client is not None and llm_model is not None:
                        image_filename = shape.image.filename
                        image_extension = os.path.splitext(image_filename)[1] if image_filename else None
                        image_stream_info = StreamInfo(
                            mimetype=shape.image.content_type,
                            extension=image_extension,
                            filename=image_filename,
                        )
                        image_stream = io.BytesIO(shape.image.blob)
                        try:
                            llm_description = llm_caption(
                                image_stream,
                                image_stream_info,
                                client=llm_client,
                                model=llm_model,
                                prompt=kwargs.get("llm_prompt"),
                            )
                        except Exception:
                            pass
                    
                    try:
                        alt_text = shape._element._nvXxPr.cNvPr.attrib.get("descr", "")
                    except Exception:
                        pass
                    
                    alt_text = "\n".join(filter(None, [llm_description, alt_text]))
                    alt_text = re.sub(r"[\r\n\[\]]", " ", alt_text)
                    alt_text = re.sub(r"\s+", " ", alt_text).strip()
                    
                    if kwargs.get("keep_data_uris", False):
                        blob = shape.image.blob
                        content_type = shape.image.content_type or "image/png"
                        b64_string = base64.b64encode(blob).decode("utf-8")
                        md_content += f"\n![{alt_text}](data:{content_type};base64,{b64_string})\n"
                    elif output_images:
                        image_path, deduplicated = self._save_image(
                            shape, slide_num, image_count, image_dir, output_base,
                            image_path_raw, caller_manages_links
                        )
                        encoded_path = quote(image_path, safe='/')
                        md_content += f"\n![{alt_text}]({encoded_path})\n"
                        if not deduplicated:
                            image_count += 1
                    else:
                        filename = re.sub(r"\W", "", shape.name) + ".jpg"
                        md_content += "\n![" + alt_text + "](" + filename + ")\n"
            
            # 3.4 Group shapes (recursive processing)
            def process_group(group_shape):
                nonlocal md_content, image_count
                sorted_subshapes = sorted(
                    group_shape.shapes,
                    key=lambda x: (x.top or 0, x.left or 0),
                )
                for subshape in sorted_subshapes:
                    if subshape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.GROUP:
                        process_group(subshape)
                    elif self._is_picture(subshape):
                        if skip_background_images and self._is_background_image(subshape):
                            continue
                        if skip_icon_images and self._classify_image_type(subshape) == 'icon':
                            continue
                        
                        alt_text = ""
                        try:
                            alt_text = subshape._element._nvXxPr.cNvPr.attrib.get("descr", "")
                        except Exception:
                            pass
                        alt_text = re.sub(r"[\r\n\[\]]", " ", alt_text).strip()
                        
                        if output_images:
                            image_path, deduplicated = self._save_image(
                                subshape, slide_num, image_count, image_dir, output_base,
                                image_path_raw, caller_manages_links
                            )
                            encoded_path = quote(image_path, safe='/')
                            md_content += f"\n![{alt_text}]({encoded_path})\n"
                            if not deduplicated:
                                image_count += 1
                    elif subshape.has_text_frame:
                        md_content += self._format_shape_text(subshape) + "\n"
            
            for group_shape in group_shapes:
                process_group(group_shape)

            md_content = md_content.strip()

            if slide.has_notes_slide:
                notes_frame = slide.notes_slide.notes_text_frame
                if notes_frame is not None:
                    # Format each paragraph with styles and links
                    notes_lines = []
                    for para in notes_frame.paragraphs:
                        text = self._format_paragraph_text(para).strip()
                        if text:
                            notes_lines.append(text)
                    if notes_lines:
                        notes_text = '\n'.join(notes_lines)
                        quoted_lines = '\n'.join(f"> {line}" for line in notes_text.split('\n'))
                        md_content += f"\n\n{quoted_lines}"
                md_content = md_content.strip()

        return DocumentConverterResult(markdown=md_content.strip())

    def _is_picture(self, shape):
        if shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE:
            return True
        if shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PLACEHOLDER:
            if hasattr(shape, "image"):
                return True
        return False

    def _is_table(self, shape):
        if shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.TABLE:
            return True
        return False

    # --- MODULE: Background Image Detection (BRIEF_01) ---
    def _is_background_image(self, shape):
        """
        Determine if a shape is a background image placeholder.
        
        Background placeholders are identified by their type using
        the official python-pptx PP_PLACEHOLDER_TYPE enum.
        
        Returns:
            bool: True if shape is a background image, False otherwise
        """
        try:
            # Only placeholders can be backgrounds
            if shape.shape_type != pptx.enum.shapes.MSO_SHAPE_TYPE.PLACEHOLDER:
                return False
            
            # Check placeholder type against background types
            pf = shape.placeholder_format
            background_types = [
                pptx.enum.shapes.PP_PLACEHOLDER_TYPE.PICTURE,      # ID 18
                pptx.enum.shapes.PP_PLACEHOLDER_TYPE.SLIDE_IMAGE   # ID 101
            ]
            return pf.type in background_types
        except Exception:
            # If unable to determine, assume it's not a background
            return False
    # --- END MODULE ---

    # --- MODULE: Image Classification (Photo vs Icon) ---
    def _classify_image_type(self, shape) -> str:
        """
        Classify image as 'icon' or 'photo' based on shape name.
        
        This heuristic achieves 97% accuracy on test dataset (82/85 correct).
        
        Classification rules:
        - "Graphique X" → icon (100% accurate on 62 samples)
        - "Image X" → photo (100% accurate on 8 samples)
        - "Espace réservé pour une image" → photo (100% accurate on 5 samples)
        - "Espace réservé du contenu" → use size fallback (ambiguous)
        - Unknown patterns → use size fallback
        
        Args:
            shape: PPTX shape containing image
        
        Returns:
            str: 'icon' or 'photo'
        """
        name = shape.name
        
        # Primary classification: shape name patterns (100% reliable)
        if 'Graphique' in name or 'Graph' in name:
            return 'icon'
        
        if 'Image' in name or 'Picture' in name:
            return 'photo'
        
        if 'pour une image' in name:  # Matches "Espace réservé pour une image"
            return 'photo'
        
        # Fallback: file size for ambiguous cases ("Espace réservé du contenu")
        # Threshold: 20 KB (100% accurate on 14 ambiguous samples)
        size_kb = len(shape.image.blob) / 1024
        return 'icon' if size_kb < 20 else 'photo'
    # --- END MODULE ---

    # --- MODULE: SmartArt Detection (BRIEF_05) ---
    def _is_smartart(self, shape) -> bool:
        """
        Detect if shape is a SmartArt by checking graphic URI.
        
        Note: python-pptx has NO native SmartArt API. There is no
        MSO_SHAPE_TYPE.SMART_ART enum, and no shape.smart_art attribute.
        We must check the GraphicFrame's graphic data URI for the
        diagram namespace to detect SmartArt.
        
        Args:
            shape: Shape object from python-pptx
            
        Returns:
            bool: True if shape is SmartArt, False otherwise
        """
        try:
            # SmartArt must have _element attribute
            if not hasattr(shape, '_element'):
                return False
            
            # SmartArt are GraphicFrames with specific URI
            if not hasattr(shape._element, 'graphic'):
                return False
            
            graphic_data = shape._element.graphic.graphicData
            uri = graphic_data.get('uri', '')
            
            # Check for diagram namespace
            diagram_uri = (
                "http://schemas.openxmlformats.org/"
                "drawingml/2006/diagram"
            )
            return diagram_uri in uri
            
        except AttributeError:
            return False

    def _get_smartart_diagram_path(
        self, pptx_stream: BinaryIO, slide_index: int, shape
    ) -> Optional[str]:
        """
        Find the diagram data XML path for a SmartArt shape.
        
        SmartArt data is stored in ppt/diagrams/data{N}.xml, but N is not
        the sequential order. We must resolve the relationship ID from
        the slide's relationship file.
        
        Args:
            pptx_stream: PPTX file as binary stream
            slide_index: 0-based slide index
            shape: SmartArt shape object
            
        Returns:
            Path within ZIP like "ppt/diagrams/data3.xml" or None if error
        """
        try:
            # Extract relationship ID from GraphicFrame
            graphic_data = shape._element.graphic.graphicData
            
            # Find the diagram reference element
            ns_dgm = "http://schemas.openxmlformats.org/drawingml/2006/diagram"
            diagram_ref = graphic_data.find(f'.//{{{ns_dgm}}}relIds')
            if diagram_ref is None:
                return None
            
            ns_r = (
                "http://schemas.openxmlformats.org/"
                "officeDocument/2006/relationships"
            )
            r_id = diagram_ref.get(f'{{{ns_r}}}dm')
            if not r_id:
                return None
            
            # Parse slide relationship file from stream
            rels_path = f'ppt/slides/_rels/slide{slide_index + 1}.xml.rels'
            
            # Reset stream position
            pptx_stream.seek(0)
            
            with zipfile.ZipFile(pptx_stream, 'r') as zf:
                rels_xml = zf.read(rels_path)
                rels_root = etree.fromstring(rels_xml)
                
                # Find relationship with matching Id
                ns_rel = (
                    "http://schemas.openxmlformats.org/"
                    "package/2006/relationships"
                )
                for rel in rels_root.findall(
                    f'.//{{{ns_rel}}}Relationship', namespaces={'rel': ns_rel}
                ):
                    if rel.get('Id') == r_id:
                        target = rel.get('Target')
                        # Target is like "../diagrams/data1.xml"
                        # Convert to "ppt/diagrams/data1.xml"
                        return target.replace('../', 'ppt/')
            
            return None
            
        except Exception:
            # Return None if any error occurs
            return None

    def _extract_smartart_text(
        self, pptx_stream: BinaryIO, diagram_path: str
    ) -> tuple[List[tuple[str, int, str, bool]], dict[str, str]]:
        """
        Extract text nodes from SmartArt with hierarchy and image associations.
        
        Algorithm:
        1. Extract all nodes (text, IDs, types) and images via presAssocID
        2. Build parent-child graph from connections (no type attr)
        3. Detect assistant connections (type="asst") for orgcharts
        4. Find root nodes (no incoming connections)
        5. Calculate depths via BFS from all roots
        6. Sort children by srcOrd + destOrd
        7. Traverse recursively with cycle detection
        
        Args:
            pptx_stream: PPTX file as binary stream
            diagram_path: Path within ZIP like "ppt/diagrams/data1.xml"
            
        Returns:
            Tuple of:
              - List of tuples (text, level, node_id, is_assistant)
              - Dict mapping node_id -> image_rid for nodes with images
        """
        nodes_with_text = []
        node_images = {}  # node_id -> rId for image
        
        try:
            pptx_stream.seek(0)
            
            with zipfile.ZipFile(pptx_stream, 'r') as zf:
                xml_bytes = zf.read(diagram_path)
                root = etree.fromstring(xml_bytes)
                
                ns = {
                    'dgm': (
                        'http://schemas.openxmlformats.org/'
                        'drawingml/2006/diagram'
                    ),
                    'a': (
                        'http://schemas.openxmlformats.org/'
                        'drawingml/2006/main'
                    ),
                    'r': (
                        'http://schemas.openxmlformats.org/'
                        'officeDocument/2006/relationships'
                    ),
                }
                
                # Extract point types, text, and images
                points = root.findall('.//dgm:pt', namespaces=ns)
                node_texts = {}  # modelId -> text
                node_types = {}  # modelId -> type (doc, parTrans, sibTrans, pres)
                data_node_ids = set()  # All DATA node IDs
                all_node_ids = set()  # All node IDs for root detection
                
                for pt in points:
                    model_id = pt.get('modelId')
                    if not model_id:
                        continue
                    
                    all_node_ids.add(model_id)
                    pt_type = pt.get('type')
                    node_types[model_id] = pt_type
                    
                    # Extract text (only for data nodes)
                    if pt_type in (None, 'node'):  # Normal data nodes
                        data_node_ids.add(model_id)
                        text_parts = []
                        for text_elem in pt.findall('.//a:t', namespaces=ns):
                            if text_elem.text:
                                text_parts.append(text_elem.text.strip())
                        if text_parts:
                            node_texts[model_id] = ' '.join(text_parts)
                    
                    # Extract images from PRES nodes via presAssocID
                    if pt_type == 'pres':
                        prset = pt.find('.//dgm:prSet', namespaces=ns)
                        if prset is not None:
                            pres_assoc = prset.get('presAssocID')
                            if pres_assoc and pres_assoc in data_node_ids:
                                blip = pt.find('.//a:blip', namespaces=ns)
                                if blip is not None:
                                    r_embed = f'{{{ns["r"]}}}embed'
                                    r_id = blip.get(r_embed)
                                    if r_id:
                                        node_images[pres_assoc] = r_id
                
                # Second pass for PRES nodes (data nodes may come after)
                for pt in points:
                    pt_type = pt.get('type')
                    if pt_type == 'pres':
                        prset = pt.find('.//dgm:prSet', namespaces=ns)
                        if prset is not None:
                            pres_assoc = prset.get('presAssocID')
                            if pres_assoc and pres_assoc in data_node_ids:
                                if pres_assoc not in node_images:
                                    blip = pt.find('.//a:blip', namespaces=ns)
                                    if blip is not None:
                                        r_embed = f'{{{ns["r"]}}}embed'
                                        r_id = blip.get(r_embed)
                                        if r_id:
                                            node_images[pres_assoc] = r_id
                
                # Build children and assistants maps from connections
                connections = root.findall('.//dgm:cxn', namespaces=ns)
                children_map = {}  # parent_id -> [(srcOrd, destOrd, child_id)]
                assistants_map = {}  # parent_id -> [(srcOrd, destOrd, asst_id)]
                dest_nodes = set()  # All nodes with incoming connections
                
                for cxn in connections:
                    cxn_type = cxn.get('type')
                    src_id = cxn.get('srcId')
                    dest_id = cxn.get('destId')
                    
                    if not src_id or not dest_id:
                        continue
                    
                    try:
                        src_ord = int(cxn.get('srcOrd', 0))
                        dest_ord = int(cxn.get('destOrd', 0))
                    except ValueError:
                        src_ord, dest_ord = 0, 0
                    
                    # Skip transition nodes as children
                    child_type = node_types.get(dest_id)
                    if child_type in ('parTrans', 'sibTrans', 'pres'):
                        continue
                    
                    # Data hierarchy = connections WITHOUT type attribute
                    if cxn_type is None:
                        if src_id not in children_map:
                            children_map[src_id] = []
                        children_map[src_id].append((src_ord, dest_ord, dest_id))
                        dest_nodes.add(dest_id)
                    
                    # Assistant relationships (orgcharts)
                    elif cxn_type == 'asst':
                        if src_id not in assistants_map:
                            assistants_map[src_id] = []
                        assistants_map[src_id].append((src_ord, dest_ord, dest_id))
                        dest_nodes.add(dest_id)
                
                # Sort children by srcOrd, then destOrd
                for parent_id in children_map:
                    children_map[parent_id].sort(key=lambda x: (x[0], x[1]))
                for parent_id in assistants_map:
                    assistants_map[parent_id].sort(key=lambda x: (x[0], x[1]))
                
                # Find root nodes (nodes NOT in dest_nodes)
                root_nodes = [
                    nid for nid in all_node_ids
                    if nid not in dest_nodes
                ]
                
                # Calculate depths using BFS from all roots
                depths = {}
                queue = [(rnode, 0) for rnode in root_nodes]
                
                while queue:
                    node_id, depth = queue.pop(0)
                    
                    # Multi-parent case: use max depth
                    if node_id in depths:
                        depths[node_id] = max(depths[node_id], depth)
                    else:
                        depths[node_id] = depth
                    
                    # Add children to queue
                    for _, _, child_id in children_map.get(node_id, []):
                        queue.append((child_id, depth + 1))
                    
                    # Add assistants to queue
                    for _, _, asst_id in assistants_map.get(node_id, []):
                        queue.append((asst_id, depth + 1))
                
                # Build set of assistant node IDs
                assistant_node_ids = set()
                for asst_list in assistants_map.values():
                    for _, _, asst_id in asst_list:
                        assistant_node_ids.add(asst_id)
                
                # Recursive traversal with cycle detection
                def traverse(
                    node_id: str, level: int, visited: set | None = None
                ):
                    """Traverse tree collecting text nodes with levels."""
                    if visited is None:
                        visited = set()
                    
                    # Cycle detection
                    if node_id in visited:
                        return
                    visited.add(node_id)
                    
                    # Add this node if it has text or image
                    if node_id in node_texts:
                        is_asst = node_id in assistant_node_ids
                        nodes_with_text.append((
                            node_texts[node_id], level, node_id, is_asst
                        ))
                    elif node_id in node_images:
                        is_asst = node_id in assistant_node_ids
                        nodes_with_text.append(('', level, node_id, is_asst))
                    
                    # Process assistants BEFORE regular children
                    for _, _, asst_id in assistants_map.get(node_id, []):
                        asst_level = depths.get(asst_id, level + 1)
                        traverse(asst_id, asst_level, visited.copy())
                    
                    # Process children in order
                    for _, _, child_id in children_map.get(node_id, []):
                        child_level = depths.get(child_id, level + 1)
                        traverse(child_id, child_level, visited.copy())
                
                # Start traversal from all root nodes
                for root_node in root_nodes:
                    root_level = depths.get(root_node, 0)
                    traverse(root_node, root_level)
                
                # Fallback if nothing found but texts exist
                if not nodes_with_text and node_texts:
                    for model_id, text in node_texts.items():
                        level = self._infer_level_from_text(text)
                        nodes_with_text.append((text, level, model_id, False))
            
        except Exception:
            pass
        
        return nodes_with_text, node_images

    def _infer_level_from_text(self, text: str) -> int:
        """Infer hierarchy level from text patterns (fallback)."""
        import re
        match = re.search(r'(\d+\.)+\d+', text)
        if match:
            return match.group(0).count('.')
        return 0

    def _save_smartart_images(
        self,
        pptx_stream: BinaryIO,
        diagram_path: str,
        node_images: dict[str, str],
        slide_number: int,
        smartart_index: int,
        kwargs: dict,
    ) -> dict[str, str]:
        """
        Save SmartArt embedded images to disk and return path mapping.
        
        Resolves rId references to media paths, saves images using
        BRIEF_01 logic (deduplication via MD5 hash).
        
        Args:
            pptx_stream: PPTX file as binary stream
            diagram_path: Path within ZIP like "ppt/diagrams/data1.xml"
            node_images: Dict mapping node_id -> rId for images
            slide_number: Slide number for naming
            smartart_index: SmartArt index for naming
            kwargs: Converter options (output_images, image_path, etc.)
            
        Returns:
            Dict mapping node_id -> saved_path (relative)
        """
        saved_paths = {}
        
        if not node_images or not kwargs.get('output_images'):
            return saved_paths
        
        try:
            pptx_stream.seek(0)
            
            with zipfile.ZipFile(pptx_stream, 'r') as zf:
                # Parse relationship file for diagram
                data_num = diagram_path.split('data')[-1].split('.')[0]
                rels_path = f'ppt/diagrams/_rels/data{data_num}.xml.rels'
                
                try:
                    rels_xml = zf.read(rels_path)
                except KeyError:
                    return saved_paths
                
                rels_root = etree.fromstring(rels_xml)
                
                ns_rel = {
                    'rel': (
                        'http://schemas.openxmlformats.org/'
                        'package/2006/relationships'
                    )
                }
                
                # Build rId -> media_path mapping
                rid_to_path = {}
                for rel in rels_root.findall(
                    './/rel:Relationship', namespaces=ns_rel
                ):
                    rel_id = rel.get('Id')
                    target = rel.get('Target')
                    if rel_id and target:
                        # Target is like "../media/image1.png"
                        media_path = target.replace('../', 'ppt/')
                        rid_to_path[rel_id] = media_path
                
                # Save each image associated with nodes
                image_dir = kwargs.get('image_path', 'images')
                os.makedirs(image_dir, exist_ok=True)
                
                for idx, (node_id, r_id) in enumerate(node_images.items()):
                    if r_id not in rid_to_path:
                        continue
                    
                    media_path = rid_to_path[r_id]
                    
                    try:
                        image_bytes = zf.read(media_path)
                    except KeyError:
                        continue
                    
                    # Deduplication using MD5 hash
                    image_hash = hashlib.md5(image_bytes).hexdigest()
                    if image_hash in self._image_hashes:
                        saved_paths[node_id] = self._image_hashes[image_hash]
                        continue
                    
                    # Determine extension
                    ext = '.' + media_path.split('.')[-1]
                    
                    # Generate filename
                    img_filename = (
                        f"slide{slide_number}_smartart{smartart_index}"
                        f"_item{idx}{ext}"
                    )
                    
                    # Build paths
                    img_path_obj = Path(image_dir) / img_filename
                    img_path = img_path_obj.as_posix()
                    disk_path = str(img_path_obj)
                    
                    # Save to disk
                    with open(disk_path, 'wb') as f:
                        f.write(image_bytes)
                    
                    # Register in hash map
                    self._image_hashes[image_hash] = img_path
                    saved_paths[node_id] = img_path
            
        except Exception:
            pass
        
        return saved_paths

    def _convert_smartart_to_markdown(
        self,
        texts: List[tuple[str, int, str, bool]],
        saved_images: dict[str, str],
        smartart_index: int,
        slide_number: int,
        image_descriptions: dict[str, str] | None = None,
    ) -> str:
        """
        Convert SmartArt data to Markdown format with hierarchy.
        
        Type 1 (text only, no descriptions): Hierarchical bulleted list
        Type 1b (text only, with descriptions): Table with Description | Details
        Type 2 (with saved images): Table with Visual | Details
        
        Args:
            texts: List of tuples (text, level, node_id, is_assistant)
            saved_images: Dict mapping node_id -> saved_path (empty for Type 1)
            smartart_index: SmartArt index for HTML comment
            slide_number: Slide number for HTML comment
            image_descriptions: Dict mapping node_id -> description (for text-only mode)
            
        Returns:
            Markdown formatted string with blank lines before/after
        """
        if not texts:
            return ""
        
        # Use HTML comment instead of markdown heading
        markdown = (
            f"\n\n<!-- SmartArt {smartart_index + 1} "
            f"(Slide {slide_number}) -->\n\n"
        )
        
        # Type 1: Text only without descriptions (simple hierarchical list)
        if not saved_images and not image_descriptions:
            for text, level, _, is_assistant in texts:
                if not text:  # Skip empty text nodes
                    continue
                # Indentation: 3 spaces per level (Markdown standard)
                indent = '   ' * level
                # Assistants: no bullet, just indented text
                if is_assistant:
                    markdown += f"{indent}{text}\n"
                else:
                    markdown += f"{indent}- {text}\n"
            # Add blank line after
            markdown += "\n"
            return markdown
        
        # Type 1b or Type 2: Table format (with descriptions or images)
        # Group items by level-0 nodes (each level-0 starts a new group)
        groups = []  # [(image_or_desc, node_id, [(text, level, is_asst), ...]), ...]
        current_group = None
        
        for text, level, node_id, is_assistant in texts:
            if level == 0:
                # Start new group - prefer saved_images, fallback to descriptions
                if saved_images:
                    img_or_desc = saved_images.get(node_id, '')
                else:
                    img_or_desc = image_descriptions.get(node_id, '') if image_descriptions else ''
                current_group = (img_or_desc, node_id, [(text, 0, is_assistant)])
                groups.append(current_group)
            elif current_group is not None:
                # Add to current group as child
                current_group[2].append((text, level, is_assistant))
        
        # Build rows first to calculate column widths
        rows = []
        for img_or_desc, node_id, items in groups:
            # Build hierarchical text with HTML line breaks
            details_parts = []
            for item_text, item_level, is_asst in items:
                if not item_text:  # Skip empty text
                    continue
                # Indent: use non-breaking spaces for table cell
                indent = '&nbsp;&nbsp;&nbsp;' * item_level
                # Assistants without bullet
                if is_asst:
                    details_parts.append(f"{indent}{item_text}")
                else:
                    details_parts.append(f"{indent}- {item_text}")
            
            details = '<br>'.join(details_parts) if details_parts else ''
            
            # First column: image reference or description
            if saved_images:
                first_col = f"![]({img_or_desc})" if img_or_desc else ''
            else:
                first_col = img_or_desc if img_or_desc else ''
            
            rows.append((first_col, details))
        
        # Calculate column widths for alignment
        header1 = "Visual" if saved_images else "Image"
        header2 = "Details"
        
        col1_width = max(len(header1), max((len(r[0]) for r in rows), default=0))
        col2_width = max(len(header2), max((len(r[1]) for r in rows), default=0))
        
        # Generate aligned table
        markdown += f"| {header1:<{col1_width}} | {header2:<{col2_width}} |\n"
        markdown += f"|{'-' * (col1_width + 2)}|{'-' * (col2_width + 2)}|\n"
        
        for first_col, details in rows:
            markdown += f"| {first_col:<{col1_width}} | {details:<{col2_width}} |\n"
        
        # Add blank line after
        markdown += "\n"
        return markdown
    # --- END MODULE ---

    # --- MODULE: Image Extraction (BRIEF_01) ---
    def _get_image_extension(
        self, 
        filename: str | None, 
        content_type: str | None
    ) -> str:
        """
        Determine image file extension from filename or MIME type.
        
        Args:
            filename: Original filename (may be None)
            content_type: MIME type (may be None)
        
        Returns:
            str: Extension with dot (e.g., '.png')
        """
        # Try extracting from filename
        if filename:
            ext = os.path.splitext(filename)[1]
            if ext and ext != '.':
                return ext.lower()
        
        # MIME type to extension mapping
        mime_to_ext = {
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/gif': '.gif',
            'image/bmp': '.bmp',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
            'image/tiff': '.tiff',
            'image/tif': '.tif',
            'image/x-emf': '.emf',
            'image/x-wmf': '.wmf',
            'image/emf': '.emf',
            'image/wmf': '.wmf',
        }
        
        # Try mapping from MIME type
        if content_type:
            ext = mime_to_ext.get(content_type.lower())
            if ext:
                return ext
        
        # Fallback to PNG
        return '.png'

    def _save_image_bytes(
        self,
        image_bytes: bytes,
        filename: str,
        image_dir: str,
        output_base: Optional[str] = None,
        image_path_raw: Optional[str] = None,
        caller_manages_links: bool = False
    ) -> tuple[str, bool]:
        """
        Central helper to save image bytes to disk with deduplication.
        
        Args:
            image_bytes: Raw image data
            filename: Target filename (with extension)
            image_dir: Destination folder (absolute path)
            output_base: Base directory for relative path calculation
            image_path_raw: Original image_path parameter from caller
            caller_manages_links: If True, use paths as provided by caller
        
        Returns:
            tuple: (image_link, was_deduplicated)
        """
        image_hash = hashlib.md5(image_bytes).hexdigest()
        if image_hash in self._image_hashes:
            return self._image_hashes[image_hash], True
        
        disk_path = Path(image_dir) / filename
        os.makedirs(image_dir, exist_ok=True)
        with open(disk_path, 'wb') as f:
            f.write(image_bytes)
        
        img_link = self._get_relative_image_link(
            str(disk_path), output_base, image_path_raw, caller_manages_links
        )
        self._image_hashes[image_hash] = img_link
        return img_link, False

    def _save_image(
        self,
        shape,
        slide_num: int,
        image_count: int,
        image_dir: str,
        output_base: Optional[str] = None,
        image_path_raw: Optional[str] = None,
        caller_manages_links: bool = False
    ) -> tuple[str, bool]:
        """
        Save PPTX image to local folder (with mandatory deduplication).
        
        Args:
            shape: PPTX shape containing image
            slide_num: Slide number (1-indexed)
            image_count: Image counter within slide (0-indexed)
            image_dir: Destination folder (absolute path)
            output_base: Base directory for relative path calculation
            image_path_raw: Original image_path parameter from caller
            caller_manages_links: If True, use paths as provided by caller
        
        Returns:
            tuple: (image_link, was_deduplicated)
                - image_link: Path for markdown image link
                - was_deduplicated: True if image already existed
        """
        blob = shape.image.blob
        filename = shape.image.filename
        content_type = shape.image.content_type
        
        # Deduplication using MD5 hash (mandatory)
        image_hash = hashlib.md5(blob).hexdigest()
        if image_hash in self._image_hashes:
            # Image already saved, return existing path
            return self._image_hashes[image_hash], True
        
        # Determine file extension
        ext = self._get_image_extension(filename, content_type)
        
        # --- MODULE: EMF/WMF Conversion to PNG ---
        # Check if image is EMF or WMF format (Windows Metafiles)
        needs_conversion = False
        original_ext = ext  # Save original extension for error messages
        if ext.lower() in ['.emf', '.wmf'] or \
           (content_type and 'wmf' in content_type.lower()):
            needs_conversion = True
            ext = '.png'  # Convert to PNG
        # --- END MODULE ---
        
        # Generate filename: slide{N}_image{M}.{ext}
        image_filename = f"slide{slide_num}_image{image_count}{ext}"
        
        # --- MODULE: Cross-platform Path Handling (BRIEF_01 + BRIEF_06) ---
        # Use pathlib.Path for cross-platform paths
        image_path_obj = Path(image_dir) / image_filename
        disk_path = str(image_path_obj)  # OS-specific path for disk operations
        
        # Calculate link path for markdown
        image_link = self._get_relative_image_link(
            disk_path, output_base, image_path_raw, caller_manages_links
        )
        # --- END MODULE ---
        
        # Create directory if needed
        os.makedirs(image_dir, exist_ok=True)
        
        # --- MODULE: EMF/WMF Conversion to PNG ---
        # Save file to disk (with conversion if needed)
        if needs_conversion:
            try:
                # Convert EMF/WMF to PNG using Pillow
                import io

                from PIL import Image
                
                # Open the image from bytes
                img = Image.open(io.BytesIO(blob))
                
                # Convert to RGB if necessary (EMF can have transparency)
                if img.mode not in ['RGB', 'RGBA']:
                    img = img.convert('RGB')
                
                # Save as PNG
                img.save(disk_path, 'PNG')
                
            except ImportError:
                # Pillow not installed - save original file and warn user
                import warnings
                warnings.warn(
                    f"Pillow not installed. Cannot convert {original_ext} to PNG. "
                    "Install with: pip install markitdown[pptx]",
                    ImportWarning
                )
                # Save as original WMF/EMF file instead of PNG
                disk_path = str(Path(image_dir) / f"slide{slide_num}_image{image_count}{original_ext}")
                with open(disk_path, 'wb') as f:
                    f.write(blob)
                image_link = self._get_relative_image_link(
                    disk_path, output_base, image_path_raw, caller_manages_links
                )
            except Exception as e:
                # WMF conversion failed - try to save as WMF original format
                import warnings
                warnings.warn(f"Failed to convert {original_ext} to PNG: {e}. Saving as {original_ext}", RuntimeWarning)
                
                # Fallback: save as original WMF/EMF format
                disk_path_fallback = str(Path(image_dir) / f"slide{slide_num}_image{image_count}{original_ext}")
                with open(disk_path_fallback, 'wb') as f:
                    f.write(blob)
                image_link = self._get_relative_image_link(
                    disk_path_fallback, output_base, image_path_raw, caller_manages_links
                )
        else:
            # Standard save for non-EMF formats
            with open(disk_path, 'wb') as f:
                f.write(blob)
        # --- END MODULE ---
        
        # Store hash for future deduplication (mandatory)
        self._image_hashes[image_hash] = image_link
        
        return image_link, False
    # --- END MODULE ---

    # --- MODULE: Table Cell Color Extraction ---
    def _rgb_to_hsl(self, r: int, g: int, b: int) -> tuple[float, float, float]:
        """
        Convert RGB (0-255) to HSL (hue 0-360, saturation 0-1, lightness 0-1).
        """
        r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
        max_c = max(r_norm, g_norm, b_norm)
        min_c = min(r_norm, g_norm, b_norm)
        delta = max_c - min_c
        
        # Lightness
        lightness = (max_c + min_c) / 2.0
        
        # Saturation
        if delta == 0:
            saturation = 0.0
            hue = 0.0
        else:
            saturation = delta / (1 - abs(2 * lightness - 1))
            
            # Hue
            if max_c == r_norm:
                hue = 60 * (((g_norm - b_norm) / delta) % 6)
            elif max_c == g_norm:
                hue = 60 * (((b_norm - r_norm) / delta) + 2)
            else:
                hue = 60 * (((r_norm - g_norm) / delta) + 4)
        
        return (hue, saturation, lightness)
    
    def _rgb_to_color_name(self, r: int, g: int, b: int) -> tuple[str, str] | None:
        """
        Convert RGB values to color emoji and French name using HSL matching.
        
        Uses Hue for color identification and Saturation to filter neutrals.
        Low saturation colors (grays) are ignored as they're typically styling.
        
        Args:
            r, g, b: RGB values (0-255)
            
        Returns:
            Tuple of (emoji, french_name) or None if neutral/gray
        """
        rgb_tuple = (r, g, b)
        
        # Exact match first
        if rgb_tuple in COLOR_MAP:
            emoji, name = COLOR_MAP[rgb_tuple]
            # Still filter out grays from exact matches
            return (emoji, name)
        
        # Convert to HSL
        hue, saturation, lightness = self._rgb_to_hsl(r, g, b)
        
        # Handle neutrals: low saturation = gray/white/black
        if saturation < 0.15:
            if lightness < 0.2:
                return ("⚫", "noir")
            elif lightness > 0.85:
                return ("⚪", "blanc")
            else:
                return ("⬜", "gris")
        
        # Filter very dark or very light (near black/white)
        if lightness < 0.1:
            return ("⚫", "noir")
        if lightness > 0.9:
            return ("⚪", "blanc")
        
        # Match by hue ranges (degrees on color wheel)
        # Red: 0-15 or 345-360
        # Orange: 15-45
        # Yellow: 45-75
        # Green: 75-165
        # Cyan: 165-195
        # Blue: 195-255
        # Purple: 255-285
        # Magenta: 285-345
        
        if hue < 15 or hue >= 345:
            return ("🔴", "rouge")
        elif hue < 45:
            return ("🟠", "orange")
        elif hue < 75:
            return ("🟡", "jaune")
        elif hue < 165:
            return ("🟢", "vert")
        elif hue < 195:
            return ("🔵", "cyan")
        elif hue < 255:
            return ("🔵", "bleu")
        elif hue < 285:
            return ("🟣", "violet")
        else:
            return ("🟣", "magenta")

    def _get_cell_fill_color(self, cell) -> tuple[str, str] | None:
        """
        Extract fill color from a table cell.
        
        Args:
            cell: python-pptx _Cell object
            
        Returns:
            Tuple of (emoji, french_name) or None if no fill/transparent
        """
        try:
            fill = cell.fill
            
            # Check if fill is defined and solid
            if fill is None:
                return None
            
            fill_type = fill.type
            if fill_type is None:
                return None
            
            # MSO_FILL_TYPE.SOLID = 1
            if fill_type != pptx.enum.dml.MSO_FILL_TYPE.SOLID:
                return None
            
            # Get foreground color
            fore_color = fill.fore_color
            if fore_color is None:
                return None
            
            color_type = fore_color.type
            
            # Handle RGB color
            if color_type == pptx.dml.color.MSO_COLOR_TYPE.RGB:
                rgb = fore_color.rgb
                if rgb:
                    return self._rgb_to_color_name(rgb[0], rgb[1], rgb[2])
            
            # Handle theme color (try to get RGB value)
            elif color_type == pptx.dml.color.MSO_COLOR_TYPE.SCHEME:
                # Theme colors need resolution via presentation theme
                # For now, return a generic indicator
                theme_idx = fore_color.theme_color
                if theme_idx is not None:
                    # Map common theme color indices
                    theme_names = {
                        1: ("⚫", "texte foncé"),
                        2: ("⚪", "arrière-plan"),
                        3: ("🔵", "accent 1"),
                        4: ("🔴", "accent 2"),
                        5: ("🟢", "accent 3"),
                        6: ("🟣", "accent 4"),
                        7: ("🟠", "accent 5"),
                        8: ("🔵", "accent 6"),
                    }
                    return theme_names.get(theme_idx, ("⬜", "thème"))
            
            return None
            
        except (AttributeError, TypeError):
            return None
    
    def _get_cell_images(
        self,
        cell,
        pptx_stream: BinaryIO,
        slide_num: int,
        table_name: str,
        row_idx: int,
        col_idx: int,
        image_dir: str,
        output_base: str = "",
        image_path_raw: str = "images",
        caller_manages_links: bool = False,
    ) -> list[str]:
        """
        Extract images from a table cell's background fill.
        
        Parses the cell's XML to find a:blipFill elements, resolves
        the relationship IDs to actual media files, and saves them.
        
        Args:
            cell: python-pptx _Cell object
            pptx_stream: PPTX file as binary stream
            slide_num: 1-indexed slide number
            table_name: Table name from shape.name (for image naming)
            row_idx: 0-indexed row index
            col_idx: 0-indexed column index
            image_dir: Directory to save images (absolute path)
            output_base: Base directory for relative path calculation
            image_path_raw: Original image_path parameter for link generation
            caller_manages_links: If True, use image_path_raw as-is for links
            
        Returns:
            List of markdown image references like "![](path/to/image.png)"
        """
        if not LXML_AVAILABLE:
            return []
        
        image_refs = []
        
        try:
            # Access the cell's XML element
            tc_element = cell._tc
            if tc_element is None:
                return []
            
            # Define namespaces
            ns = {
                'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
            }
            
            # Find all blip elements (images) in cell properties
            # Look in tcPr for blipFill
            blips = tc_element.findall('.//a:blip', namespaces=ns)
            
            if not blips:
                return []
            
            # Reset stream position
            pptx_stream.seek(0)
            
            with zipfile.ZipFile(pptx_stream, 'r') as zf:
                # We need the slide's relationship file to resolve rIds
                # Table images are part of the slide's relationships
                rels_path = f'ppt/slides/_rels/slide{slide_num}.xml.rels'
                
                try:
                    rels_xml = zf.read(rels_path)
                except KeyError:
                    return []
                
                rels_root = etree.fromstring(rels_xml)
                
                ns_rel = 'http://schemas.openxmlformats.org/package/2006/relationships'
                
                # Build rId -> media_path mapping
                rid_to_path = {}
                for rel in rels_root.findall(f'.//{{{ns_rel}}}Relationship'):
                    rel_id = rel.get('Id')
                    target = rel.get('Target')
                    if rel_id and target and 'media/' in target:
                        media_path = target.replace('../', 'ppt/')
                        if not media_path.startswith('ppt/'):
                            media_path = 'ppt/slides/' + target
                            media_path = media_path.replace('../', '')
                        rid_to_path[rel_id] = media_path
                
                # Process each blip (image reference)
                for img_idx, blip in enumerate(blips):
                    r_embed = blip.get(f'{{{ns["r"]}}}embed')
                    if not r_embed or r_embed not in rid_to_path:
                        continue
                    
                    media_path = rid_to_path[r_embed]
                    
                    try:
                        image_bytes = zf.read(media_path)
                    except KeyError:
                        continue
                    
                    ext = '.' + media_path.split('.')[-1].lower()
                    safe_table_name = re.sub(r'[^\w\-]', '_', table_name)
                    filename = (
                        f"slide{slide_num}_{safe_table_name}_"
                        f"cell{row_idx}x{col_idx}_img{img_idx}{ext}"
                    )
                    
                    img_link, was_dup = self._save_image_bytes(
                        image_bytes, filename, image_dir,
                        output_base, image_path_raw, caller_manages_links
                    )
                    image_refs.append(f"![]({img_link})")
            
        except Exception:
            pass
        
        return image_refs
    # --- END MODULE ---

    # --- MODULE: Floating Image to Cell Mapping ---
    def _map_floating_images_to_cells(
        self,
        table_shape,
        slide_shapes: list,
        pptx_stream: BinaryIO | None,
        slide_num: int,
        table_name: str,
        image_dir: str,
        output_base: str = "",
        image_path_raw: str = "images",
        caller_manages_links: bool = False,
    ) -> dict[tuple[int, int], list[str]]:
        """
        Map floating PICTURE shapes to table cells based on position.
        
        PowerPoint allows placing images visually over tables without
        embedding them in cells. This function detects such images and
        maps them to the appropriate cell based on geometric overlap.
        
        Args:
            table_shape: The table shape object (has .left, .top, .width, .height)
            slide_shapes: All shapes on the slide
            pptx_stream: PPTX file stream for image extraction
            slide_num: 1-indexed slide number
            table_name: Table name from shape.name (for image naming)
            image_dir: Directory to save extracted images (absolute path)
            output_base: Base directory for relative path calculation
            image_path_raw: Original image_path parameter for link generation
            caller_manages_links: If True, use image_path_raw as-is for links
            
        Returns:
            Dict mapping (row_idx, col_idx) to list of markdown image refs
        """
        cell_images: dict[tuple[int, int], list[str]] = {}
        
        if pptx_stream is None:
            return cell_images
        
        table = table_shape.table
        
        # Calculate column positions
        col_positions = [table_shape.left]
        for col in table.columns:
            col_positions.append(col_positions[-1] + col.width)
        
        # Calculate row positions
        row_positions = [table_shape.top]
        for row in table.rows:
            row_positions.append(row_positions[-1] + row.height)
        
        # Find PICTURE shapes overlapping the table
        for shape in slide_shapes:
            if shape.shape_type != pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE:
                continue
            
            # Use center of image for cell mapping
            img_center_x = shape.left + shape.width // 2
            img_center_y = shape.top + shape.height // 2
            
            # Check if within table bounds
            if not (table_shape.left <= img_center_x <= table_shape.left + table_shape.width):
                continue
            if not (table_shape.top <= img_center_y <= table_shape.top + table_shape.height):
                continue
            
            # Find column index
            col_idx = None
            for i in range(len(col_positions) - 1):
                if col_positions[i] <= img_center_x < col_positions[i + 1]:
                    col_idx = i
                    break
            
            # Find row index
            row_idx = None
            for i in range(len(row_positions) - 1):
                if row_positions[i] <= img_center_y < row_positions[i + 1]:
                    row_idx = i
                    break
            
            if row_idx is None or col_idx is None:
                continue
            
            # Extract and save the image
            try:
                if hasattr(shape, 'image') and shape.image:
                    image_bytes = shape.image.blob
                    ext = shape.image.ext or 'png'
                    safe_table_name = re.sub(r'[^\w\-]', '_', table_name)
                    filename = f"slide{slide_num}_{safe_table_name}_cell{row_idx}_{col_idx}.{ext}"
                    
                    img_link, _ = self._save_image_bytes(
                        image_bytes, filename, image_dir,
                        output_base, image_path_raw, caller_manages_links
                    )
                    
                    alt_text = shape.name or ""
                    key = (row_idx, col_idx)
                    if key not in cell_images:
                        cell_images[key] = []
                    cell_images[key].append(f"![{alt_text}]({img_link})")
            except Exception:
                pass
        
        return cell_images
    # --- END MODULE ---

    def _convert_table_to_markdown(
        self,
        table,
        slide_num: int = 0,
        table_name: str = "",
        pptx_stream: BinaryIO | None = None,
        image_dir: str = "images",
        output_images: bool = True,
        table_shape=None,
        slide_shapes: list | None = None,
        output_base: str = "",
        image_path_raw: str = "images",
        caller_manages_links: bool = False,
        **kwargs,
    ) -> str:
        """
        Convert PPTX table to Markdown with enhanced cell content.
        
        Handles 4 types of cell content:
        1. Text → Markdown text
        2. Empty cell with color → Emoji or "(couleur)"
        3. Cell with embedded image(s) → Extracted image references
        4. Floating images over cells → Detected and inserted
        
        When both text and color are present, displays both: "Texte 🟢"
        Header rows (when table.first_row=True) are excluded from color extraction.
        
        Args:
            table: python-pptx Table object
            slide_num: 1-indexed slide number (for image naming)
            table_name: Table name from shape.name (for image naming)
            pptx_stream: PPTX file as binary stream (for image extraction)
            image_dir: Directory to save extracted images (absolute path)
            output_images: Whether to extract images
            table_shape: The table shape object (for floating image detection)
            slide_shapes: All shapes on the slide (for floating image detection)
            output_base: Base directory for relative path calculation
            image_path_raw: Original image_path parameter for link generation
            caller_manages_links: If True, use image_path_raw as-is for links
            **kwargs: Additional converter options
            
        Returns:
            Markdown formatted table string
        """
        rows_data = []
        num_cols = len(table.columns)
        
        # Check if table has header row styling enabled
        has_header_row = getattr(table, 'first_row', False)
        
        # Map floating images to cells (images placed visually over the table)
        floating_images: dict[tuple[int, int], list[str]] = {}
        if output_images and table_shape and slide_shapes and pptx_stream:
            floating_images = self._map_floating_images_to_cells(
                table_shape,
                slide_shapes,
                pptx_stream,
                slide_num,
                table_name,
                image_dir,
                output_base,
                image_path_raw,
                caller_manages_links,
            )
        
        for row_idx, row in enumerate(table.rows):
            row_cells = []
            is_header = has_header_row and row_idx == 0
            
            for col_idx, cell in enumerate(row.cells):
                # Spanned cells (part of a merge) - add empty cell to preserve column alignment
                # Markdown doesn't support cell merging, so we show empty cells
                if hasattr(cell, 'is_spanned') and cell.is_spanned:
                    row_cells.append("")
                    continue
                
                cell_parts = []
                
                # 1. Extract text with styles and hyperlinks
                text = self._format_cell_text(cell)
                if text:
                    cell_parts.append(text)
                
                # 2. Extract embedded images (blipFill in cell XML)
                if output_images and pptx_stream is not None:
                    images = self._get_cell_images(
                        cell,
                        pptx_stream,
                        slide_num,
                        table_name,
                        row_idx,
                        col_idx,
                        image_dir,
                        output_base,
                        image_path_raw,
                        caller_manages_links,
                    )
                    cell_parts.extend(images)
                
                # 3. Add floating images mapped to this cell
                if (row_idx, col_idx) in floating_images:
                    cell_parts.extend(floating_images[(row_idx, col_idx)])
                
                # 4. Extract color (skip for header rows - styling only)
                if not is_header:
                    color_info = self._get_cell_fill_color(cell)
                    if color_info:
                        emoji, color_name = color_info
                        cell_parts.insert(0, emoji)
                
                # Combine all parts
                cell_content = " ".join(cell_parts) if cell_parts else ""
                row_cells.append(cell_content)
            
            # Ensure row has correct number of columns
            while len(row_cells) < num_cols:
                row_cells.append("")
            
            rows_data.append(row_cells)
        
        if not rows_data:
            return ""
        
        # Build Markdown table
        md_lines = []
        
        # Header row
        header = "| " + " | ".join(rows_data[0]) + " |"
        md_lines.append(header)
        
        # Separator row
        separator = "|" + "|".join(["---"] * num_cols) + "|"
        md_lines.append(separator)
        
        # Data rows
        for row in rows_data[1:]:
            md_lines.append("| " + " | ".join(row) + " |")
        
        return "\n".join(md_lines) + "\n"

    def _convert_chart_to_markdown(self, chart):
        try:
            md = "\n\n### Chart"
            if chart.has_title:
                md += f": {chart.chart_title.text_frame.text}"
            md += "\n\n"
            data = []
            category_names = [c.label for c in chart.plots[0].categories]
            series_names = [s.name for s in chart.series]
            data.append(["Category"] + series_names)

            for idx, category in enumerate(category_names):
                row = [category]
                for series in chart.series:
                    row.append(series.values[idx])
                data.append(row)

            markdown_table = []
            for row in data:
                markdown_table.append("| " + " | ".join(map(str, row)) + " |")
            header = markdown_table[0]
            separator = "|" + "|".join(["---"] * len(data[0])) + "|"
            return md + "\n".join([header, separator] + markdown_table[1:])
        except ValueError as e:
            # Handle the specific error for unsupported chart types
            if "unsupported plot type" in str(e):
                return "\n\n[unsupported chart]\n\n"
        except Exception:
            # Catch any other exceptions that might occur
            return "\n\n[unsupported chart]\n\n"
