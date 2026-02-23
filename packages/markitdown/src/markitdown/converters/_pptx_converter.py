import base64
import hashlib  # For MD5 deduplication
import html
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
        
        # Apply wiki-folder slugify ONLY if using default "images" folder
        # If user provides custom path, respect it as-is (may contain subfolders)
        if image_dir_raw == "images":
            # Default: slugify based on presentation filename if available
            image_dir = self._slugify(image_dir_raw)
        else:
            # Custom path: use as-is, normalize path separators
            image_dir = image_dir_raw.replace('\\', '/')
        
        output_images = kwargs.get("output_images", True)
        skip_background_images = kwargs.get("skip_background_images", True)
        skip_icon_images = kwargs.get("skip_icon_images", False)  # Extract all images by default
        self._image_hashes = {}  # Reset for each conversion
        # --- END MODULE ---
        
        md_content = ""
        slide_num = 0
        smartart_count = 0  # Global counter for all SmartArt (BRIEF_05)
        
        for slide in presentation.slides:
            slide_num += 1

            md_content += f"\n\n<!-- Slide number: {slide_num} -->\n"

            title = slide.shapes.title

            def get_shape_content(shape, **kwargs):
                nonlocal md_content
                nonlocal image_count  # For sequential image naming
                nonlocal smartart_count  # For sequential SmartArt naming (BRIEF_05)
                nonlocal file_stream  # For SmartArt ZIP access (BRIEF_05)
                # Pictures
                if self._is_picture(shape):
                    # --- MODULE: Skip Background Images (BRIEF_01) ---
                    if skip_background_images and self._is_background_image(shape):
                        return  # Skip this background image
                    # --- END MODULE ---
                    
                    # --- MODULE: Skip Icon Images (Extract Photos Only) ---
                    if skip_icon_images:
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
                    # Note: If alt_text is empty, it will remain empty (BRIEF_02 will handle LLM generation)
                    alt_text = "\n".join(filter(None, [llm_description, alt_text]))
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
                            image_dir
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

                # --- MODULE: SmartArt Extraction (BRIEF_05) ---
                # SmartArt (must check before charts/text)
                if self._is_smartart(shape):
                    if not LXML_AVAILABLE:
                        # Skip if lxml not installed
                        return
                    
                    nonlocal smartart_count
                    
                    # Find diagram data file
                    diagram_path = self._get_smartart_diagram_path(
                        file_stream, slide_num - 1, shape
                    )
                    
                    if diagram_path:
                        # Extract text nodes
                        texts = self._extract_smartart_text(
                            file_stream, diagram_path
                        )
                        
                        # Extract embedded images (if present and enabled)
                        images = self._extract_smartart_images(
                            file_stream,
                            diagram_path,
                            slide_num,
                            smartart_count,
                            kwargs,
                        )
                        
                        # Convert to Markdown
                        smartart_md = self._convert_smartart_to_markdown(
                            texts, images, smartart_count, slide_num
                        )
                        
                        if smartart_md:
                            md_content += smartart_md
                            smartart_count += 1
                    
                    return  # Don't process as regular shape
                # --- END MODULE ---

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
    ) -> List[tuple[str, int]]:
        """
        Extract text nodes from SmartArt with hierarchy levels.
        
        Reads data{N}.xml, extracts <dgm:pt> nodes, and determines hierarchy
        using <dgm:cxn> connections with srcOrd for ordering.
        
        Args:
            pptx_stream: PPTX file as binary stream
            diagram_path: Path within ZIP like "ppt/diagrams/data1.xml"
            
        Returns:
            List of tuples (text, level) where level is indentation depth (0-based)
        """
        nodes_with_text = []
        
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
                }
                
                # Extract point types and text
                points = root.findall('.//dgm:pt', namespaces=ns)
                node_texts = {}  # modelId -> text
                node_types = {}  # modelId -> type (doc, parTrans, sibTrans, pres)
                doc_node_id = None
                
                for pt in points:
                    model_id = pt.get('modelId')
                    if not model_id:
                        continue
                    
                    pt_type = pt.get('type')
                    node_types[model_id] = pt_type
                    
                    if pt_type == 'doc':
                        doc_node_id = model_id
                    
                    # Extract text (only for data nodes)
                    if pt_type in (None, 'node'):  # Normal data nodes
                        text_parts = []
                        for text_elem in pt.findall('.//a:t', namespaces=ns):
                            if text_elem.text:
                                text_parts.append(text_elem.text.strip())
                        if text_parts:
                            node_texts[model_id] = ' '.join(text_parts)
                
                # Build children map: parent_id -> [(srcOrd, child_id), ...]
                connections = root.findall('.//dgm:cxn', namespaces=ns)
                children_map = {}  # parent_id -> list of (order, child_id)
                
                for cxn in connections:
                    cxn_type = cxn.get('type')
                    # Data hierarchy = connections WITHOUT type attribute
                    if cxn_type is None:
                        src_id = cxn.get('srcId')   # Parent
                        dest_id = cxn.get('destId')  # Child
                        src_ord = cxn.get('srcOrd', '0')
                        
                        if src_id and dest_id:
                            # Skip transition nodes as children
                            child_type = node_types.get(dest_id)
                            if child_type in ('parTrans', 'sibTrans', 'pres'):
                                continue
                            
                            if src_id not in children_map:
                                children_map[src_id] = []
                            try:
                                order = int(src_ord)
                            except ValueError:
                                order = 0
                            children_map[src_id].append((order, dest_id))
                
                # Sort children by order
                for parent_id in children_map:
                    children_map[parent_id].sort(key=lambda x: x[0])
                
                # Traverse tree recursively starting from doc node
                def traverse(node_id: str, level: int):
                    """Traverse tree, collecting text nodes with levels."""
                    # Add this node if it has text
                    if node_id in node_texts:
                        nodes_with_text.append((node_texts[node_id], level))
                    
                    # Process children in order
                    if node_id in children_map:
                        for _, child_id in children_map[node_id]:
                            # Children of doc = level 0, their children = level 1
                            child_level = level if node_id == doc_node_id else level + 1
                            traverse(child_id, child_level)
                
                if doc_node_id:
                    traverse(doc_node_id, 0)
                elif node_texts:
                    # Fallback: no doc node, use text-based heuristic
                    for model_id, text in node_texts.items():
                        level = self._infer_level_from_text(text)
                        nodes_with_text.append((text, level))
            
        except Exception:
            pass
        
        return nodes_with_text

    def _infer_level_from_text(self, text: str) -> int:
        """Infer hierarchy level from text patterns (fallback)."""
        import re
        match = re.search(r'(\d+\.)+\d+', text)
        if match:
            return match.group(0).count('.')
        return 0

    def _extract_smartart_images(
        self,
        pptx_stream: BinaryIO,
        diagram_path: str,
        slide_number: int,
        smartart_index: int,
        kwargs: dict,
    ) -> List[str]:
        """
        Extract embedded images from SmartArt (if present).
        
        Detects <a:blip> elements, resolves relationship IDs to media paths,
        and saves images using BRIEF_01 logic.
        
        Args:
            pptx_stream: PPTX file as binary stream
            diagram_path: Path within ZIP like "ppt/diagrams/data1.xml"
            slide_number: Slide number for naming
            smartart_index: SmartArt index on slide for naming
            kwargs: Converter options (output_images, etc.)
            
        Returns:
            List of saved image paths (relative)
        """
        image_paths = []
        
        if not kwargs.get('output_images'):
            return image_paths
        
        try:
            # Reset stream position
            pptx_stream.seek(0)
            
            with zipfile.ZipFile(pptx_stream, 'r') as zf:
                # Parse data XML
                xml_bytes = zf.read(diagram_path)
                root = etree.fromstring(xml_bytes)
                
                ns = {
                    'a': (
                        'http://schemas.openxmlformats.org/'
                        'drawingml/2006/main'
                    ),
                    'r': (
                        'http://schemas.openxmlformats.org/'
                        'officeDocument/2006/relationships'
                    ),
                }
                
                # Find all blip elements (embedded images)
                blips = root.findall('.//a:blip', namespaces=ns)
                
                if not blips:
                    return image_paths
                
                # Parse relationship file for diagram
                data_num = diagram_path.split('data')[-1].split('.')[0]
                rels_path = f'ppt/diagrams/_rels/data{data_num}.xml.rels'
                
                rels_xml = zf.read(rels_path)
                rels_root = etree.fromstring(rels_xml)
                
                ns_rel = {
                    'rel': (
                        'http://schemas.openxmlformats.org/'
                        'package/2006/relationships'
                    )
                }
                
                for idx, blip in enumerate(blips):
                    r_id = blip.get(f'{{{ns["r"]}}}embed')
                    if not r_id:
                        continue
                    
                    # Resolve rId to media path
                    for rel in rels_root.findall(
                        './/rel:Relationship', namespaces=ns_rel
                    ):
                        if rel.get('Id') == r_id:
                            target = rel.get('Target')
                            # Target is like "../media/image1.png"
                            media_path = target.replace('../', 'ppt/')
                            
                            # Extract image bytes
                            image_bytes = zf.read(media_path)
                            
                            # Determine extension
                            ext = media_path.split('.')[-1]
                            
                            # Save using BRIEF_01 logic
                            shape_name = f'smartart{smartart_index}_item{idx}'
                            saved_path = self._save_image(
                                image_bytes,
                                shape_name,
                                slide_number,
                                ext,
                                kwargs,
                            )
                            
                            if saved_path:
                                image_paths.append(saved_path)
                            
                            break
            
        except Exception:
            # Return partial results if error occurs
            pass
        
        return image_paths

    def _convert_smartart_to_markdown(
        self,
        texts: List[tuple[str, int]],
        images: List[str],
        smartart_index: int,
        slide_number: int,
    ) -> str:
        """
        Convert SmartArt data to Markdown format with hierarchy.
        
        Type 1 (text only): Hierarchical bulleted list with indentation
        Type 2 (with embedded images): Two-column table
        
        Args:
            texts: List of tuples (text, level) from SmartArt
            images: List of image paths (empty for Type 1)
            smartart_index: SmartArt index for HTML comment
            slide_number: Slide number for HTML comment
            
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
        
        # Type 1: Text only (hierarchical list)
        if not images:
            for text, level in texts:
                # Indentation: 3 spaces per level (Markdown standard)
                indent = '   ' * level
                markdown += f"{indent}- {text}\n"
            # Add blank line after
            markdown += "\n"
            return markdown
        
        # Type 2: With embedded images (table format)
        markdown += "| Visual | Details |\n"
        markdown += "|--------|----------|\n"
        
        # Map images to texts (assume 1:1 or fewer images than texts)
        for idx, (text, _) in enumerate(texts):  # Ignore level for tables
            if idx < len(images):
                # Has corresponding image
                markdown += f"| ![({images[idx]}) | {text} |\n"
            else:
                # No image for this text
                markdown += f"|  | {text} |\n"
        
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

    def _save_image(
        self,
        shape,
        slide_num: int,
        image_count: int,
        image_dir: str
    ) -> tuple[str, bool]:
        """
        Save PPTX image to local folder (with mandatory deduplication).
        
        Args:
            shape: PPTX shape containing image
            slide_num: Slide number (1-indexed)
            image_count: Image counter within slide (0-indexed)
            image_dir: Destination folder (relative path)
        
        Returns:
            tuple: (image_path, was_deduplicated)
                - image_path: Relative path to saved image
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
                image_path = Path(disk_path).relative_to(Path(image_dir).parent).as_posix()
            except Exception as e:
                # WMF conversion failed - try to save as WMF original format
                import warnings
                warnings.warn(f"Failed to convert {original_ext} to PNG: {e}. Saving as {original_ext}", RuntimeWarning)
                
                # Fallback: save as original WMF/EMF format
                disk_path_fallback = str(Path(image_dir) / f"slide{slide_num}_image{image_count}{original_ext}")
                with open(disk_path_fallback, 'wb') as f:
                    f.write(blob)
                image_path = Path(disk_path_fallback).relative_to(Path(image_dir).parent).as_posix()
        else:
            # Standard save for non-EMF formats
            with open(disk_path, 'wb') as f:
                f.write(blob)
        # --- END MODULE ---
        
        # Store hash for future deduplication (mandatory)
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
