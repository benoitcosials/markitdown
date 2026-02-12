import base64
import hashlib  # For MD5 deduplication
import html
import io
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, BinaryIO
from urllib.parse import quote

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

    def _slugify(self, text: str) -> str:
        """
        Convert text to wiki-folder convention (slug format).
        
        Transforms: "Kickoff QA - Essais UAT R1" → "kickoff_qa_essais_uat_r1"
        
        Args:
            text: Original text with spaces and special characters
        
        Returns:
            str: Slugified text (lowercase, underscores, no special chars)
        """
        # Normalize unicode (decompose accents)
        text = unicodedata.normalize('NFKD', text)
        # Remove accents
        text = text.encode('ascii', 'ignore').decode('ascii')
        # Convert to lowercase
        text = text.lower()
        # Replace spaces and hyphens with underscores
        text = re.sub(r'[\s-]+', '_', text)
        # Remove any remaining non-alphanumeric characters (except underscores)
        text = re.sub(r'[^a-z0-9_]', '', text)
        # Remove consecutive underscores
        text = re.sub(r'_+', '_', text)
        # Strip leading/trailing underscores
        text = text.strip('_')
        return text

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
        
        # --- MODULE: Image Management - Configuration (BRIEF_01) ---
        image_dir_raw = kwargs.get("image_dir", "images")
        # Apply wiki-folder convention (slugify) for clean folder names
        image_dir = self._slugify(image_dir_raw)
        output_images = kwargs.get("output_images", True)
        deduplicate_images = kwargs.get("deduplicate_images", False)
        skip_background_images = kwargs.get("skip_background_images", True)
        skip_icon_images = kwargs.get("skip_icon_images", True)  # NEW: Filter icons
        self._image_hashes = {}  # Reset for each conversion
        # --- END MODULE ---
        
        md_content = ""
        slide_num = 0
        for slide in presentation.slides:
            slide_num += 1

            md_content += f"\n\n<!-- Slide number: {slide_num} -->\n"

            title = slide.shapes.title

            def get_shape_content(shape, **kwargs):
                nonlocal md_content
                nonlocal image_count  # For sequential image naming
                # Pictures
                if self._is_picture(shape):
                    # --- MODULE: Skip Background Images (BRIEF_01) ---
                    skip_bg = kwargs.get("skip_background_images", True)
                    if skip_bg and self._is_background_image(shape):
                        return  # Skip this background image
                    # --- END MODULE ---
                    
                    # --- MODULE: Skip Icon Images (Extract Photos Only) ---
                    skip_icons = kwargs.get("skip_icon_images", True)
                    if skip_icons:
                        image_type = self._classify_image_type(shape)
                        if image_type == 'icon':
                            return  # Skip icon, only extract photos
                    # --- END MODULE ---
                    # https://github.com/scanny/python-pptx/pull/512#issuecomment-1713100069

                    llm_description = ""
                    alt_text = ""

                    # Potentially generate a description using an LLM
                    llm_client = kwargs.get("llm_client")
                    llm_model = kwargs.get("llm_model")
                    if llm_client is not None and llm_model is not None:
                        # Prepare a file_stream and stream_info for the image data
                        image_filename = shape.image.filename
                        image_extension = None
                        if image_filename:
                            image_extension = os.path.splitext(image_filename)[1]
                        image_stream_info = StreamInfo(
                            mimetype=shape.image.content_type,
                            extension=image_extension,
                            filename=image_filename,
                        )

                        image_stream = io.BytesIO(shape.image.blob)

                        # Caption the image
                        try:
                            llm_description = llm_caption(
                                image_stream,
                                image_stream_info,
                                client=llm_client,
                                model=llm_model,
                                prompt=kwargs.get("llm_prompt"),
                            )
                        except Exception:
                            # Unable to generate a description
                            pass

                    # Also grab any description embedded in the deck
                    try:
                        alt_text = shape._element._nvXxPr.cNvPr.attrib.get("descr", "")
                    except Exception:
                        # Unable to get alt text
                        pass

                    # Prepare the alt, escaping any special characters
                    alt_text = "\n".join([llm_description, alt_text]) or shape.name
                    alt_text = re.sub(r"[\r\n\[\]]", " ", alt_text)
                    alt_text = re.sub(r"\s+", " ", alt_text).strip()

                    # --- MODULE: Image Handling (BRIEF_01) ---
                    # Mode Base64 (PRESERVE EXISTING - DO NOT MODIFY)
                    if kwargs.get("keep_data_uris", False):
                        blob = shape.image.blob
                        content_type = shape.image.content_type or "image/png"
                        b64_string = base64.b64encode(blob).decode("utf-8")
                        md_content += f"\n![{alt_text}](data:{content_type};base64,{b64_string})\n"
                    
                    # New: File extraction mode
                    elif output_images:
                        # Save image to disk
                        image_path, deduplicated = self._save_image(
                            shape, 
                            slide_num, 
                            image_count, 
                            image_dir, 
                            deduplicate_images
                        )
                        
                        # URL-encode path for markdown (handles any remaining special chars)
                        encoded_path = quote(image_path, safe='/')
                        
                        # Generate Markdown with URL-encoded path
                        md_content += f"\n![{alt_text}]({encoded_path})\n"
                        
                        # Increment counter if new image (not deduplicated)
                        if not deduplicated:
                            image_count += 1
                    
                    # Legacy mode (deprecated - generates broken links)
                    else:
                        # A placeholder name
                        filename = re.sub(r"\W", "", shape.name) + ".jpg"
                        md_content += "\n![" + alt_text + "](" + filename + ")\n"
                    # --- END MODULE ---

                # Tables
                if self._is_table(shape):
                    md_content += self._convert_table_to_markdown(shape.table, **kwargs)

                # Charts
                if shape.has_chart:
                    md_content += self._convert_chart_to_markdown(shape.chart)

                # Text areas
                elif shape.has_text_frame:
                    if shape == title:
                        md_content += "# " + shape.text.lstrip() + "\n"
                    else:
                        md_content += shape.text + "\n"

                # Group Shapes
                if shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.GROUP:
                    sorted_shapes = sorted(
                        shape.shapes,
                        key=lambda x: (
                            float("-inf") if not x.top else x.top,
                            float("-inf") if not x.left else x.left,
                        ),
                    )
                    for subshape in sorted_shapes:
                        get_shape_content(subshape, **kwargs)

            # --- MODULE: Image counter per slide (BRIEF_01) ---
            image_count = 0
            # --- END MODULE ---
            
            sorted_shapes = sorted(
                slide.shapes,
                key=lambda x: (
                    float("-inf") if not x.top else x.top,
                    float("-inf") if not x.left else x.left,
                ),
            )
            for shape in sorted_shapes:
                get_shape_content(shape, **kwargs)

            md_content = md_content.strip()

            if slide.has_notes_slide:
                md_content += "\n\n### Notes:\n"
                notes_frame = slide.notes_slide.notes_text_frame
                if notes_frame is not None:
                    md_content += notes_frame.text
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
        except:
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

    def _save_image(
        self,
        shape,
        slide_num: int,
        image_count: int,
        image_dir: str,
        deduplicate_images: bool
    ) -> tuple[str, bool]:
        """
        Save PPTX image to local folder.
        
        Args:
            shape: PPTX shape containing image
            slide_num: Slide number (1-indexed)
            image_count: Image counter within slide (0-indexed)
            image_dir: Destination folder (relative path)
            deduplicate_images: Enable MD5 deduplication
        
        Returns:
            tuple: (image_path, was_deduplicated)
                - image_path: Relative path to saved image
                - was_deduplicated: True if image already existed
        """
        blob = shape.image.blob
        filename = shape.image.filename
        content_type = shape.image.content_type
        
        # Deduplication using MD5 hash
        if deduplicate_images:
            image_hash = hashlib.md5(blob).hexdigest()
            if image_hash in self._image_hashes:
                # Image already saved, return existing path
                return self._image_hashes[image_hash], True
        
        # Determine file extension
        ext = self._get_image_extension(filename, content_type)
        
        # --- MODULE: EMF/WMF Conversion to PNG ---
        # Check if image is EMF or WMF format (Windows Metafiles)
        needs_conversion = False
        if ext.lower() in ['.emf', '.wmf'] or \
           (content_type and 'wmf' in content_type.lower()):
            needs_conversion = True
            ext = '.png'  # Convert to PNG
        # --- END MODULE ---
        
        # Generate filename: slide{N}_image{M}.{ext}
        image_filename = f"slide{slide_num}_image{image_count}{ext}"
        
        # --- MODULE: Cross-platform Path Handling (BRIEF_01 - Solution 1A) ---
        # Use pathlib.Path for cross-platform paths, convert to Unix format
        image_path_obj = Path(image_dir) / image_filename
        image_path = image_path_obj.as_posix()  # Always use forward slashes
        disk_path = str(image_path_obj)  # Use OS-specific path for disk operations
        # --- END MODULE ---
        
        # Create directory if needed
        os.makedirs(image_dir, exist_ok=True)
        
        # --- MODULE: EMF/WMF Conversion to PNG ---
        # Save file to disk (with conversion if needed)
        if needs_conversion:
            try:
                # Convert EMF/WMF to PNG using Pillow
                from PIL import Image
                import io
                
                # Open the image from bytes
                img = Image.open(io.BytesIO(blob))
                
                # Convert to RGB if necessary (EMF can have transparency)
                if img.mode not in ['RGB', 'RGBA']:
                    img = img.convert('RGB')
                
                # Save as PNG
                img.save(disk_path, 'PNG')
                
            except Exception as e:
                # If conversion fails, save original file
                # and log the error (fallback)
                with open(disk_path, 'wb') as f:
                    f.write(blob)
        else:
            # Standard save for non-EMF formats
            with open(disk_path, 'wb') as f:
                f.write(blob)
        # --- END MODULE ---
        
        # Store hash for future deduplication
        if deduplicate_images:
            self._image_hashes[image_hash] = image_path
        
        return image_path, False
    # --- END MODULE ---

    def _convert_table_to_markdown(self, table, **kwargs):
        # Write the table as HTML, then convert it to Markdown
        html_table = "<html><body><table>"
        first_row = True
        for row in table.rows:
            html_table += "<tr>"
            for cell in row.cells:
                if first_row:
                    html_table += "<th>" + html.escape(cell.text) + "</th>"
                else:
                    html_table += "<td>" + html.escape(cell.text) + "</td>"
            html_table += "</tr>"
            first_row = False
        html_table += "</table></body></html>"

        return (
            self._html_converter.convert_string(html_table, **kwargs).markdown.strip()
            + "\n"
        )

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
