# Détails Techniques BRIEF_05 - Extraction SmartArt PPTX

**Date:** 20260222
**Brief:** BRIEF_05_SMARTART_EXTRACTION
**Fichier:** `packages/markitdown/src/markitdown/converters/_pptx_converter.py`

---

## 🧬 Architecture Technique

### Vue d'Ensemble

SmartArt dans PPTX sont stockés comme **DrawingML Diagrams** dans l'archive ZIP :

```
presentation.pptx (ZIP)
├── ppt/
│   ├── slides/
│   │   ├── slide1.xml                  # Référence SmartArt via GraphicFrame
│   │   └── _rels/
│   │       └── slide1.xml.rels         # Mapping rId → diagrams/data{N}.xml
│   └── diagrams/
│       ├── data1.xml                   # Données SmartArt (textes, connexions)
│       ├── layout1.xml                 # Algorithme positionnement
│       ├── colors1.xml                 # Schéma couleurs
│       ├── quickStyle1.xml             # Style visuel
│       └── _rels/
│           └── data1.xml.rels          # Mapping images embarquées → media/
```

### Namespaces XML Critiques

```python
NAMESPACES = {
    'dgm': 'http://schemas.openxmlformats.org/drawingml/2006/diagram',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'
}
```

### Structure XML SmartArt

**data{N}.xml - Structure des nœuds** :
```xml
<dgm:dataModel xmlns:dgm="..." xmlns:a="...">
  <dgm:ptLst>
    <!-- Nœud avec texte -->
    <dgm:pt modelId="{UUID}">
      <dgm:prSet>
        <dgm:t>
          <a:p>
            <a:r>
              <a:t>Text content here</a:t>
            </a:r>
          </a:p>
        </dgm:t>
      </dgm:prSet>
    </dgm:pt>
    
    <!-- Nœud avec image embarquée -->
    <dgm:pt modelId="{UUID}">
      <dgm:spPr>
        <a:blipFill>
          <a:blip r:embed="rId1"/>  <!-- Référence vers image -->
        </a:blipFill>
      </dgm:spPr>
      <dgm:t>
        <a:p>
          <a:r>
            <a:t>Node with image</a:t>
          </a:r>
        </a:p>
      </dgm:t>
    </dgm:pt>
  </dgm:ptLst>
  
  <!-- Connexions hiérarchiques (pour Phase 2) -->
  <dgm:cxnLst>
    <dgm:cxn modelId="{UUID}" srcId="{parent}" destId="{child}" type="parOf"/>
  </dgm:cxnLst>
</dgm:dataModel>
```

---

## 🔧 Implémentation Détaillée

### Phase 1: Infrastructure

**Imports requis** (ajouter après ligne ~10) :
```python
import zipfile
from lxml import etree
from typing import List, Dict, Optional, Tuple
```

**Configuration dans convert()** :
```python
# Dans boucle slides, avant boucle shapes
smartart_count = 0
```

**Gestion absence lxml** :
```python
try:
    from lxml import etree
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False
    # Log warning: "lxml not available, SmartArt extraction disabled"
```

### Phase 2: Détection SmartArt

**Méthode _is_smartart()** :
```python
def _is_smartart(self, shape) -> bool:
    """
    Detect if shape is a SmartArt by checking graphic URI.
    
    Note: python-pptx has NO native SmartArt API. We must check
    the GraphicFrame's graphic data URI for diagram namespace.
    
    Args:
        shape: Shape object from python-pptx
        
    Returns:
        bool: True if shape is SmartArt, False otherwise
    """
    try:
        if not hasattr(shape, '_element'):
            return False
        
        # SmartArt are GraphicFrames with specific URI
        if not hasattr(shape._element, 'graphic'):
            return False
        
        graphic_data = shape._element.graphic.graphicData
        uri = graphic_data.get('uri', '')
        
        # Check for diagram namespace
        diagram_uri = "http://schemas.openxmlformats.org/drawingml/2006/diagram"
        return diagram_uri in uri
        
    except AttributeError:
        return False
```

**Positionnement** : Après `_is_table()` (ligne ~120)

### Phase 3: Mapping Diagram Files

**Méthode _get_smartart_diagram_path()** :
```python
def _get_smartart_diagram_path(
    self, 
    pptx_path: str, 
    slide_index: int, 
    shape
) -> Optional[str]:
    """
    Find the diagram data XML path for a SmartArt shape.
    
    SmartArt data is stored in ppt/diagrams/data{N}.xml, but N is not
    the sequential order. We must resolve the relationship ID from
    the slide's relationship file.
    
    Args:
        pptx_path: Path to PPTX file
        slide_index: 0-based slide index
        shape: SmartArt shape object
        
    Returns:
        str: Path within ZIP like "ppt/diagrams/data3.xml" or None if error
    """
    try:
        # Extract relationship ID from GraphicFrame
        graphic_data = shape._element.graphic.graphicData
        # Find the diagram reference element
        diagram_ref = graphic_data.find('.//{http://schemas.openxmlformats.org/drawingml/2006/diagram}relIds')
        if diagram_ref is None:
            return None
        
        r_id = diagram_ref.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}dm')
        if not r_id:
            return None
        
        # Parse slide relationship file
        rels_path = f'ppt/slides/_rels/slide{slide_index + 1}.xml.rels'
        
        with zipfile.ZipFile(pptx_path, 'r') as zf:
            rels_xml = zf.read(rels_path)
            rels_root = etree.fromstring(rels_xml)
            
            # Find relationship with matching Id
            ns = {'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
            for rel in rels_root.findall('.//rel:Relationship', namespaces=ns):
                if rel.get('Id') == r_id:
                    target = rel.get('Target')
                    # Target is like "../diagrams/data1.xml"
                    # Convert to "ppt/diagrams/data1.xml"
                    return target.replace('../', 'ppt/')
        
        return None
        
    except Exception as e:
        # Log error but don't crash conversion
        return None
```

**Positionnement** : Après `_is_smartart()`

### Phase 4: Extraction Texte

**Méthode _extract_smartart_text()** :
```python
def _extract_smartart_text(
    self, 
    pptx_path: str, 
    diagram_path: str
) -> List[str]:
    """
    Extract all text nodes from a SmartArt diagram.
    
    Reads the data{N}.xml file directly from ZIP and parses
    <dgm:pt> nodes to extract <a:t> text elements.
    
    Args:
        pptx_path: Path to PPTX file
        diagram_path: Path within ZIP like "ppt/diagrams/data1.xml"
        
    Returns:
        List[str]: List of text strings from SmartArt nodes
    """
    texts = []
    
    try:
        with zipfile.ZipFile(pptx_path, 'r') as zf:
            xml_bytes = zf.read(diagram_path)
            root = etree.fromstring(xml_bytes)
            
            ns = {
                'dgm': 'http://schemas.openxmlformats.org/drawingml/2006/diagram',
                'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
            }
            
            # Extract all point nodes
            points = root.findall('.//dgm:pt', namespaces=ns)
            
            for pt in points:
                # Find all text elements within this point
                text_elems = pt.findall('.//a:t', namespaces=ns)
                for text_elem in text_elems:
                    if text_elem.text:
                        texts.append(text_elem.text.strip())
        
    except Exception as e:
        # Log error but return partial results
        pass
    
    return texts
```

**Positionnement** : Après `_get_smartart_diagram_path()`

### Phase 5: Extraction Images Embarquées

**Méthode _extract_smartart_images()** :
```python
def _extract_smartart_images(
    self,
    pptx_path: str,
    diagram_path: str,
    slide_number: int,
    smartart_index: int,
    kwargs: dict
) -> List[str]:
    """
    Extract embedded images from SmartArt (if present).
    
    Detects <a:blip> elements, resolves relationship IDs to media paths,
    and saves images using BRIEF_01 logic.
    
    Args:
        pptx_path: Path to PPTX file
        diagram_path: Path within ZIP like "ppt/diagrams/data1.xml"
        slide_number: Slide number for naming
        smartart_index: SmartArt index on slide for naming
        kwargs: Converter options (output_images, etc.)
        
    Returns:
        List[str]: List of saved image paths (relative)
    """
    image_paths = []
    
    if not kwargs.get('output_images'):
        return image_paths
    
    try:
        with zipfile.ZipFile(pptx_path, 'r') as zf:
            # Parse data XML
            xml_bytes = zf.read(diagram_path)
            root = etree.fromstring(xml_bytes)
            
            ns = {
                'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
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
            
            ns_rel = {'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
            
            for idx, blip in enumerate(blips):
                r_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if not r_id:
                    continue
                
                # Resolve rId to media path
                for rel in rels_root.findall('.//rel:Relationship', namespaces=ns_rel):
                    if rel.get('Id') == r_id:
                        target = rel.get('Target')  # "../media/image1.png"
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
                            kwargs
                        )
                        
                        if saved_path:
                            image_paths.append(saved_path)
                        
                        break
        
    except Exception as e:
        # Log error but return partial results
        pass
    
    return image_paths
```

**Note** : Réutilise `_save_image()` de BRIEF_01

### Phase 6-7: Conversion Markdown

**Méthode _convert_smartart_to_markdown()** :
```python
def _convert_smartart_to_markdown(
    self,
    texts: List[str],
    images: List[str],
    smartart_index: int,
    slide_number: int
) -> str:
    """
    Convert SmartArt data to Markdown format.
    
    Type 1 (text only): Simple bulleted list
    Type 2 (with embedded images): Two-column table
    
    Args:
        texts: List of text strings from SmartArt
        images: List of image paths (empty for Type 1)
        smartart_index: SmartArt index for title
        slide_number: Slide number for title
        
    Returns:
        str: Markdown formatted string
    """
    if not texts:
        return ""
    
    markdown = f"\n\n### SmartArt {smartart_index + 1} (Slide {slide_number})\n\n"
    
    # Type 1: Text only (simple list)
    if not images:
        for text in texts:
            markdown += f"- {text}\n"
        return markdown
    
    # Type 2: With embedded images (table format)
    markdown += "| Visual | Details |\n"
    markdown += "|--------|----------|\n"
    
    # Map images to texts (assume 1:1 or fewer images than texts)
    for idx, text in enumerate(texts):
        if idx < len(images):
            # Has corresponding image
            markdown += f"| ![]({{images[idx]}}) | {text} |\n"
        else:
            # No image for this text
            markdown += f"|  | {text} |\n"
    
    return markdown
```

**Positionnement** : Après `_extract_smartart_images()`

### Phase 8: Intégration dans convert()

**Dans boucle shapes** (après ligne ~140) :
```python
# Existing shape processing...

# --- MODULE: SmartArt Extraction (BRIEF_05) ---
if self._is_smartart(shape):
    if not LXML_AVAILABLE:
        # Skip if lxml not installed
        continue
    
    # Find diagram data file
    diagram_path = self._get_smartart_diagram_path(
        local_path,
        slide_index,
        shape
    )
    
    if diagram_path:
        # Extract text nodes
        texts = self._extract_smartart_text(local_path, diagram_path)
        
        # Extract embedded images (if present and enabled)
        images = self._extract_smartart_images(
            local_path,
            diagram_path,
            slide_number,
            smartart_count,
            kwargs
        )
        
        # Convert to Markdown
        smartart_md = self._convert_smartart_to_markdown(
            texts,
            images,
            smartart_count,
            slide_number
        )
        
        if smartart_md:
            result += smartart_md
            smartart_count += 1
    
    continue  # Don't process as regular shape
# --- END MODULE ---

# Continue with other shape types...
```

---

## 🧪 Tests et Validation

### Tests Unitaires

**Test Type 1 (Texte uniquement)** :
```python
def test_smartart_text_extraction():
    """Test extraction of text-only SmartArt."""
    converter = PPTXConverter()
    result = converter.convert('test_smartart_text.pptx')
    
    assert "SmartArt 1" in result.text_content
    assert "- Item 1" in result.text_content
    assert "- Item 2" in result.text_content
```

**Test Type 2 (Avec images)** :
```python
def test_smartart_with_images():
    """Test extraction of SmartArt with embedded images."""
    converter = PPTXConverter()
    result = converter.convert(
        'test_smartart_images.pptx',
        output_images=True
    )
    
    assert "| Visual | Details |" in result.text_content
    assert "![](images/" in result.text_content
    assert os.path.exists('images/slide1_smartart0_item0.png')
```

### Fichiers de Test Requis

1. **test_smartart_text.pptx** : 
   - 1 slide avec SmartArt liste simple
   - 5-10 items textuels
   - Pas d'images embarquées

2. **test_smartart_images.pptx** :
   - 1 slide avec SmartArt "Liste accentuée avec images"
   - 3-5 items avec images embarquées
   - Test extraction images + tableau

---

## ⚠️ Limitations et Edge Cases

### Limitations MVP

1. **Hiérarchie plate uniquement** :
   - Pas de reconstruction complète de la hiérarchie
   - Connexions `<dgm:cxn>` ignorées pour MVP
   - Phase 2 nécessaire pour hiérarchie multi-niveaux

2. **Images SmartArt complets** :
   - Seules les images EMBARQUÉES (photos, logos) extractibles
   - Icônes vectoriels dessinés NON extractibles
   - Pas de rendu PNG du SmartArt complet

3. **python-pptx limitations** :
   - Aucune API SmartArt native
   - XML parsing manuel obligatoire

### Edge Cases à Gérer

1. **SmartArt vide** : Retourner chaîne vide
2. **lxml manquant** : Log warning, skip SmartArt
3. **Fichier diagram manquant** : Skip gracefully
4. **XML malformé** : Catch exception, retourner résultats partiels
5. **Images partielles** : Certains nœuds avec images, autres sans

---

## 📝 Standards de Code

### Type Hints

Toutes les méthodes doivent avoir type hints complets :
```python
def _is_smartart(self, shape) -> bool:
def _get_smartart_diagram_path(self, pptx_path: str, slide_index: int, shape) -> Optional[str]:
def _extract_smartart_text(self, pptx_path: str, diagram_path: str) -> List[str]:
```

### Docstrings

Format Google Style avec Args, Returns, et notes explicatives :
```python
"""
Short description.

Longer explanation if needed. Explain WHY not WHAT when necessary.

Args:
    param1: Description
    param2: Description

Returns:
    Description of return value
"""
```

### Error Handling

- Try/except autour de toutes opérations XML
- Retourner résultats partiels si possible
- Ne jamais crasher la conversion complète
- Log errors pour debugging

### Commentaires

- Expliquer WHY pas WHAT
- Documenter limitations python-pptx
- Annoter sections complexes (XML namespaces, mapping rIds)

