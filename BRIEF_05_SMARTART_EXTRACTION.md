# Brief Technique #05 - Extraction et Transformation des SmartArt PPTX

**Date:** 22 février 2026  
**Fonctionnalité ROADMAP:** #5 - Extraction et Conversion SmartArt en Markdown  
**Statut:** 🔬 Recherche Complétée - Prêt pour Implémentation  
**Priorité:** 🟠 HAUTE (Enhancement Prioritaire)  
**Complexité:** Modérée-Haute  
**Estimation:** 10h (Recherche: 1h ✅ + Implémentation: 7h + Tests: 2h)  
**Dépendances:** BRIEF_01 ✅ (extraction d'images - complété)

**⚠️ SCOPE MVP** : Extraction texte plat uniquement (hiérarchie complète = Phase 2)

---

## 📋 Résumé Exécutif

### Vision
Améliorer la représentation des **diagrammes SmartArt PPTX** pour les LLMs en extrayant et convertissant leur contenu structuré en **Markdown natif** avec deux approches adaptatives selon le type de SmartArt.

### Problème Actuel
Les SmartArt dans PowerPoint contiennent des **données structurées hiérarchiques** (listes, organigrammes, processus) qui sont actuellement **ignorées** ou mal converties. Les LLMs perdent ainsi des informations critiques sur l'organisation et les relations entre éléments.

### Solution
Implémenter une **détection et extraction intelligente** des SmartArt avec conversion adaptative :

#### Type 1 : SmartArt Textuels (Liste Hiérarchique Pure)
**Détection** : SmartArt sans images/objets visuels, uniquement texte  
**Conversion** : Liste Markdown hiérarchique
```markdown
### Project Phases

- Phase 1: Planning
  - Define scope
  - Identify stakeholders
- Phase 2: Execution
  - Development
  - Testing
- Phase 3: Deployment
  - Production release
  - Monitoring
```

#### Type 2 : SmartArt Visuels (Avec Images Embarquées) ⚠️ LIMITÉ
**Détection** : SmartArt avec images **embarquées** via `<a:blip>` nodes  
**Conversion** : Tableau Markdown 2 colonnes (Image | Hiérarchie)

**⚠️ NOTE CRITIQUE** : Les SmartArt sont vectoriels (DrawingML XML), **PAS des images PNG**.  
Seules les **images embarquées dans les nœuds** (photos, logos insérés) sont extractibles.  
Les **icônes visuels dessinés** par PowerPoint ne sont PAS extractibles comme PNG sans rendu externe.

**Exemple (si images embarquées présentes)** :
```markdown
### Team Structure

| Visual | Details |
|--------|---------|
| ![](images/slide5_smartart0_item0.png) | **Engineering Team**<br>- Backend Development<br>  - API Design<br>  - Database<br>- Frontend Development |
| ![](images/slide5_smartart0_item1.png) | **QA Team**<br>- Test Automation<br>- Manual Testing |
| ![](images/slide5_smartart0_item2.png) | **DevOps Team**<br>- CI/CD Pipeline<br>- Infrastructure |
```

### Bénéfices
- ✅ Préserver le texte structuré des SmartArt (actuellement perdu)
- ✅ Conversion Markdown native lisible par LLMs
- ✅ Support SmartArt textuels (Type 1 - MVP)
- ⚠️ Support partiel SmartArt avec images embarquées (Type 2 - limité)
- ✅ Meilleure compréhension des processus et organisations pour LLMs
- ⚠️ **Note** : Reconstruction hiérarchie complète en Phase 2 (MVP = liste plate)

---

## 🎯 Objectifs Fonctionnels

### Objectif Principal (MVP)
Détecter les SmartArt dans les présentations PPTX, extraire leur contenu textuel, et les convertir en **listes Markdown plates**.

**Scope MVP** :
- ✅ Détection SmartArt via XML URI
- ✅ Extraction texte via ZIP + lxml parsing
- ✅ Conversion liste Markdown simple (sans hiérarchie complète)
- ⚠️ Hiérarchie complète : Phase 2 (algorithme tri topologique requis)
- ❌ Images SmartArt complet : Non faisable (vectoriel)

### Prérequis
- ✅ BRIEF_01 implémenté (sauvegarde d'images fonctionne)
- ✅ `python-pptx` disponible (déjà existant)
- ✅ `lxml` disponible (déjà présent dans projet)
- ⚠️ **Note**: python-pptx n'a PAS de support SmartArt natif → parsing XML manuel requis

### Nouveaux Éléments à Implémenter
- ⚠️ Détection des SmartArt via **XML URI check** (python-pptx n'a pas d'API SmartArt)
- ⚠️ Extraction de la structure hiérarchique via **ZIP + lxml parsing**
- ⚠️ Lecture des fichiers `ppt/diagrams/data{N}.xml` directement
- ⚠️ Reconstruction hiérarchie via connexions `<dgm:cxn>` (parOf, presOf)
- ⚠️ Détection de présence d'images embarquées via `<a:blip>` nodes
- ⚠️ **Algorithme Type 1** : Conversion hiérarchie → Liste Markdown (MVP)
- ⚠️ **Algorithme Type 2** : Extraction images embarquées + Table Markdown (Future)
- ⚠️ Nommage images SmartArt : `slide{N}_smartart{M}_item{K}.{ext}`
- ⚠️ Gestion titres SmartArt (si présents)
- ⚠️ Support multi-niveaux (indentation correcte via algorithme de tri topologique)

### ⚠️ LIMITATIONS ET CONTRAINTES TECHNIQUES

**Découvertes de la recherche** (voir `.copilot-tracking/research/20260222-brief-05-smartart-capabilities-research.md`) :

1. **python-pptx : Pas de Support SmartArt** ❌
   - Aucune API pour accéder aux données SmartArt
   - Pas de `MSO_SHAPE_TYPE.SMART_ART` enum
   - Pas d'attribut `shape.smart_art` ou `shape.diagram`
   - **Solution** : Parsing XML manuel avec lxml

2. **Images SmartArt : Non Extractibles comme PNG** ❌
   - SmartArt sont **vectoriels** (DrawingML XML), pas bitmap
   - PowerPoint les rend dynamiquement, pas de pré-render
   - **Pas d'attribut** `shape.image.blob` disponible
   - **Impact** : Type 2 (tableaux avec images SmartArt complets) NON FAISABLE pour MVP
   - **Alternatives** :
     - ✅ Extraire images **embarquées** dans SmartArt via `<a:blip>` nodes (photos, logos)
     - ❌ Icônes vectoriels dessinés (non extractibles sans rendu PPT)

3. **Hiérarchie : Complexité Modérée** ⚠️
   - Connexions stockées dans `<dgm:cxn>` avec types variés (`parOf`, `presOf`, `unknown`)
   - Reconstruction nécessite algorithme de graphe (tri topologique)
   - Cycles possibles (à gérer)

4. **Fichier Diagram : Mapping Non Trivial** ⚠️
   - SmartArt → `ppt/diagrams/data{N}.xml` : N n'est pas l'ordre d'apparition
   - **Solution** : Parser `ppt/slides/_rels/slide{N}.xml.rels` pour trouver rId → data{N}.xml

**Scope MVP Ajusté** :
- ✅ **Inclus** : Extraction texte plat + Liste Markdown simple (sans hiérarchie complète)
- ⚠️ **Future** : Reconstruction hiérarchie complète (Phase 2)
- ❌ **Exclu** : Images PNG du SmartArt complet (vectoriel non convertible)

---

## 📊 Types de SmartArt PowerPoint

### SmartArt Courants (Prioritaires)
1. **List (Liste)** - Simple liste à puces ou numérotée
2. **Process (Processus)** - Étapes séquentielles
3. **Hierarchy (Hiérarchie)** - Organigrammes, structures
4. **Cycle (Cycle)** - Processus cycliques
5. **Relationship (Relations)** - Connexions entre éléments
6. **Matrix (Matrice)** - Grilles 2D
7. **Pyramid (Pyramide)** - Structures triangulaires

### Catégorisation pour BRIEF_05
| Catégorie SmartArt | Type de Conversion | Détection |
|--------------------|-------------------|-----------|
| **Sans images** (texte pur) | Type 1 : Liste Markdown | Aucune image dans nœuds |
| **Avec images** (icônes, photos) | Type 2 : Tableau Markdown | Au moins 1 image détectée |

---

## 📝 Cas d'Usage Détaillés

### Use Case 1 : Type 1 - SmartArt Textuel (Liste Hiérarchique)

**Input PowerPoint** :
```
SmartArt "Vertical Bullet List":
- Company Values
  - Innovation
    - R&D Investment
    - Continuous Learning
  - Integrity
    - Transparency
    - Ethics
  - Excellence
    - Quality Standards
    - Customer Satisfaction
```

**Output Markdown** :
```markdown
### Company Values

- Innovation
  - R&D Investment
  - Continuous Learning
- Integrity
  - Transparency
  - Ethics
- Excellence
  - Quality Standards
  - Customer Satisfaction
```

**Comportement** :
- ✅ Titre SmartArt → Heading H3
- ✅ Structure hiérarchique préservée (niveaux 0, 1, 2)
- ✅ Indentation Markdown correcte (2 espaces par niveau)
- ✅ Texte nettoyé (trim whitespace)

---

### Use Case 2 : Type 1 - SmartArt Processus (Sans Images)

**Input PowerPoint** :
```
SmartArt "Basic Process":
Development Lifecycle
├─ 1. Requirements
├─ 2. Design
├─ 3. Implementation
├─ 4. Testing
└─ 5. Deployment
```

**Output Markdown** :
```markdown
### Development Lifecycle

1. Requirements
2. Design
3. Implementation
4. Testing
5. Deployment
```

**Comportement** :
- ✅ Détection liste ordonnée (si numéros présents)
- ✅ Conversion en liste numérotée Markdown
- ✅ Préservation de l'ordre

---

### Use Case 3 : Type 2 - SmartArt avec Icônes (Tableau)

**Input PowerPoint** :
```
SmartArt "Picture Caption List":
├─ Item 1: [icon_cloud.png] "Cloud Services"
│   └─ Details: "AWS, Azure, GCP"
│   └─ Details: "Scalable infrastructure"
├─ Item 2: [icon_security.png] "Security"
│   └─ Details: "End-to-end encryption"
│   └─ Details: "Compliance: SOC2, ISO27001"
└─ Item 3: [icon_analytics.png] "Analytics"
    └─ Details: "Real-time dashboards"
    └─ Details: "ML-powered insights"
```

**Output Markdown** :
```markdown
### Our Platform Features

| Feature | Description |
|---------|-------------|
| ![Cloud Services](images/slide3_smartart0_item0.png) | **Cloud Services**<br>- AWS, Azure, GCP<br>- Scalable infrastructure |
| ![Security](images/slide3_smartart0_item1.png) | **Security**<br>- End-to-end encryption<br>- Compliance: SOC2, ISO27001 |
| ![Analytics](images/slide3_smartart0_item2.png) | **Analytics**<br>- Real-time dashboards<br>- ML-powered insights |
```

**Comportement** :
- ✅ Extraction et sauvegarde des icônes (PNG/SVG)
- ✅ Tableau 2 colonnes : `Feature | Description`
- ✅ Titre item → **Bold** dans cellule Description
- ✅ Sous-éléments → Liste Markdown (`<br>` pour retours ligne)
- ✅ Images dans colonne 1 avec alt text du titre

**Fichiers créés** :
```
images/
├─ slide3_smartart0_item0.png  (icône cloud)
├─ slide3_smartart0_item1.png  (icône security)
└─ slide3_smartart0_item2.png  (icône analytics)
```

---

### Use Case 4 : Type 2 - SmartArt Organigramme (Avec Photos)

**Input PowerPoint** :
```
SmartArt "Organization Chart":
CEO [photo_ceo.jpg]
├─ CTO [photo_cto.jpg]
│   ├─ Engineering Lead
│   └─ DevOps Lead
├─ CFO [photo_cfo.jpg]
│   └─ Accounting Manager
└─ CMO [photo_cmo.jpg]
    ├─ Marketing Manager
    └─ Communications Lead
```

**Output Markdown** :
```markdown
### Leadership Team

| Person | Role & Reports |
|--------|----------------|
| ![CEO](images/slide7_smartart0_item0.jpg) | **CEO**<br>- CTO<br>- CFO<br>- CMO |
| ![CTO](images/slide7_smartart0_item1.jpg) | **CTO**<br>- Engineering Lead<br>- DevOps Lead |
| ![CFO](images/slide7_smartart0_item2.jpg) | **CFO**<br>- Accounting Manager |
| ![CMO](images/slide7_smartart0_item3.jpg) | **CMO**<br>- Marketing Manager<br>- Communications Lead |
```

**Comportement** :
- ✅ Photos extraites et sauvegardées
- ✅ Hiérarchie aplatie en tableau (meilleure lisibilité)
- ✅ Relations indiquées par listes dans colonne 2

---

### Use Case 5 : SmartArt Mixte (Certains Items avec Images)

**Input PowerPoint** :
```
SmartArt avec 3 items:
├─ Item 1: "Strategy" (texte seul, pas d'image)
├─ Item 2: "Execution" [icon_execution.png]
└─ Item 3: "Results" (texte seul)
```

**Règle de Conversion** :
Si **au moins 1 item** contient une image → **Type 2 (Tableau)**

**Output Markdown** :
```markdown
### Approach

| Phase | Details |
|-------|---------|
| *(no image)* | **Strategy**<br>- Define objectives<br>- Market analysis |
| ![Execution](images/slide4_smartart0_item1.png) | **Execution**<br>- Implementation<br>- Team coordination |
| *(no image)* | **Results**<br>- KPI tracking<br>- ROI measurement |
```

**Comportement** :
- ✅ Détection globale : 1+ image → Table complète
- ✅ Items sans image : Cellule vide avec `*(no image)*` ou juste texte
- ✅ Cohérence du format (tous en table)

---

## 🔧 Spécifications Techniques

### Détection SmartArt avec python-pptx

**Approche 1 : Détection via Type de Shape**
```python
from pptx.enum.shapes import MSO_SHAPE_TYPE

for shape in slide.shapes:
    if shape.shape_type == MSO_SHAPE_TYPE.SMART_ART:
        # SmartArt détecté
        smart_art = shape.smart_art
```

**Approche 2 : Détection via Attribut (Fallback)**
```python
for shape in slide.shapes:
    if hasattr(shape, 'smart_art') and shape.smart_art is not None:
        # SmartArt détecté
```

**Note** : `python-pptx` a un support limité des SmartArt. Vérification nécessaire.

### Extraction de la Structure Hiérarchique

**Méthode Recommandée** : Parsing XML du SmartArt
```python
from pptx.oxml import parse_xml

def extract_smartart_structure(shape):
    """
    Extract hierarchical text structure from SmartArt.
    
    Returns:
        list[dict]: Nodes with text, level, and optional image
        Example: [
            {'text': 'Root', 'level': 0, 'image': None},
            {'text': 'Child 1', 'level': 1, 'image': None},
            {'text': 'Child 2', 'level': 1, 'image': blob_bytes}
        ]
    """
    # Parse SmartArt XML structure
    smart_art_xml = shape._element
    
    # Extract nodes with:
    # - Text content
    # - Hierarchical level (parent-child relations)
    # - Associated images (if any)
    
    nodes = []
    # Implementation: traverse XML, build node list
    
    return nodes
```

**Éléments XML à Parser** :
- `<dgm:pt>` : Points (nœuds du SmartArt)
- `<dgm:prSet>` : Properties (texte, styles)
- `<a:blip>` : Images embarquées
- Relations parent-child via `<dgm:cxn>`

### Nommage des Images SmartArt

**Convention** : `slide{N}_smartart{M}_item{K}.{ext}`

Exemples :
- `slide3_smartart0_item0.png` ← Slide 3, premier SmartArt, item 0
- `slide3_smartart0_item1.jpg` ← Slide 3, premier SmartArt, item 1
- `slide5_smartart1_item0.png` ← Slide 5, deuxième SmartArt, item 0

Où :
- `{N}` = numéro du slide (1-indexed)
- `{M}` = numéro séquentiel du SmartArt dans le slide (0-indexed)
- `{K}` = numéro de l'item dans le SmartArt (0-indexed)
- `{ext}` = extension (`.png`, `.jpg`, `.svg`, etc.)

### Paramètres de Configuration

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `extract_smartart` | bool | `True` | Activer extraction SmartArt |
| `smartart_format` | str | `"auto"` | Format: `"auto"` (détection), `"list"` (force Type 1), `"table"` (force Type 2) |
| `smartart_max_depth` | int | `5` | Profondeur hiérarchique max (prévenir recursion infinie) |
| `smartart_table_no_image_text` | str | `"*(no image)*"` | Texte pour items sans image en mode Table |

### Structure de Données Interne

```python
@dataclass
class SmartArtNode:
    """Represents a node in SmartArt hierarchy."""
    text: str
    level: int  # 0 = root, 1 = child, 2 = grandchild, etc.
    image_blob: Optional[bytes] = None
    image_extension: str = "png"
    children: list['SmartArtNode'] = field(default_factory=list)

@dataclass
class SmartArtInfo:
    """Metadata about extracted SmartArt."""
    title: Optional[str] = None
    nodes: list[SmartArtNode] = field(default_factory=list)
    has_images: bool = False
    smartart_type: str = "unknown"  # list, process, hierarchy, etc.
```

---

## 🏗️ Architecture et Implémentation

### Fichier Cible
**Modifications dans** : `packages/markitdown/src/markitdown/converters/_pptx_converter.py`

### Modules à Créer/Modifier

#### 1. Module de Détection SmartArt
```python
# --- MODULE: SmartArt Detection (BRIEF_05) ---

def _is_smartart(shape) -> bool:
    """
    Detect if shape is a SmartArt via XML GraphicFrame URI.
    
    Note: python-pptx has NO native SmartArt support (no MSO_SHAPE_TYPE.SMART_ART).
    Detection must be done via XML inspection.
    
    Args:
        shape: python-pptx Shape object
    
    Returns:
        bool: True if SmartArt detected
    """
    try:
        # SmartArt are GraphicFrame shapes with diagram URI
        if hasattr(shape._element, 'graphic'):
            graphic_data = shape._element.graphic.graphicData
            uri = graphic_data.get('uri', '')
            diagram_uri = "http://schemas.openxmlformats.org/drawingml/2006/diagram"
            return diagram_uri in uri
    except AttributeError:
        return False
    
    return False
```

#### 2. Module d'Extraction Hiérarchique
```python
import zipfile
from lxml import etree

def _extract_smartart_nodes(
    pptx_path: str, 
    diagram_index: int
) -> list[SmartArtNode]:
    """
    Extract hierarchical structure from SmartArt via ZIP + XML parsing.
    
    Note: python-pptx has NO SmartArt API. Must read diagram data XML directly.
    SmartArt data is stored in ppt/diagrams/data{N}.xml files.
    
    Args:
        pptx_path: Path to PPTX file
        diagram_index: Index of diagram data file (1-based)
    
    Returns:
        list[SmartArtNode]: Flat list of nodes with levels
    """
    nodes = []
    
    with zipfile.ZipFile(pptx_path, 'r') as zf:
        # Read diagram data XML
        xml_bytes = zf.read(f'ppt/diagrams/data{diagram_index}.xml')
        root = etree.fromstring(xml_bytes)
        
        # Define namespaces
        ns = {
            'dgm': 'http://schemas.openxmlformats.org/drawingml/2006/diagram',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        }
        
        # Extract nodes
        points = root.findall('.//dgm:pt', namespaces=ns)
        
        for pt in points:
            # Extract text
            text_elems = pt.findall('.//a:t', namespaces=ns)
            texts = [elem.text for elem in text_elems if elem.text]
            
            # Extract images (if any)
            image_blobs = pt.findall('.//a:blip', namespaces=ns)
            
            if texts:
                node = SmartArtNode(
                    text=' '.join(texts),
                    level=0,  # Will be computed via connections
                    image_blob=None  # Will be extracted if blip found
                )
                nodes.append(node)
    
    return nodes

def _detect_smartart_images(nodes: list[SmartArtNode]) -> bool:
    """Check if any node contains an image."""
    return any(node.image_blob is not None for node in nodes)
```

#### 3. Module de Conversion Type 1 (Liste)
```python
def _convert_smartart_to_list(
    smartart_info: SmartArtInfo, 
    slide_number: int
) -> str:
    """
    Convert SmartArt to Markdown hierarchical list.
    
    Args:
        smartart_info: Extracted SmartArt data
        slide_number: Current slide index
    
    Returns:
        str: Markdown list representation
    """
    markdown = ""
    
    # Add title if present
    if smartart_info.title:
        markdown += f"### {smartart_info.title}\n\n"
    
    # Convert nodes to list
    for node in smartart_info.nodes:
        indent = "  " * node.level  # 2 spaces per level
        markdown += f"{indent}- {node.text}\n"
    
    return markdown
```

#### 4. Module de Conversion Type 2 (Tableau)
```python
def _convert_smartart_to_table(
    smartart_info: SmartArtInfo,
    slide_number: int,
    smartart_index: int,
    image_dir: str,
    kwargs: dict
) -> tuple[str, list[str]]:
    """
    Convert SmartArt to Markdown table with images.
    
    Args:
        smartart_info: Extracted SmartArt data
        slide_number: Current slide index
        smartart_index: SmartArt counter in slide
        image_dir: Destination folder for images
        kwargs: Converter options
    
    Returns:
        tuple[str, list[str]]: (Markdown table, list of image paths)
    """
    markdown = ""
    saved_images = []
    
    # Add title
    if smartart_info.title:
        markdown += f"### {smartart_info.title}\n\n"
    
    # Table header
    markdown += "| Visual | Details |\n"
    markdown += "|--------|----------|\n"
    
    # Process root-level nodes only (flatten hierarchy)
    item_index = 0
    for node in smartart_info.nodes:
        if node.level != 0:
            continue
        
        # Column 1: Image (if present)
        if node.image_blob:
            # Save image
            image_filename = f"slide{slide_number}_smartart{smartart_index}_item{item_index}.{node.image_extension}"
            image_path = _save_image_to_folder(
                node.image_blob, 
                image_filename, 
                slide_number, 
                kwargs
            )
            saved_images.append(image_path)
            
            col1 = f"![{node.text}]({image_path})"
        else:
            col1 = "*(no image)*"
        
        # Column 2: Text + Children
        col2 = f"**{node.text}**"
        
        # Add children as list
        children_text = _format_children_as_list(node.children)
        if children_text:
            col2 += f"<br>{children_text}"
        
        # Add row
        markdown += f"| {col1} | {col2} |\n"
        item_index += 1
    
    return markdown, saved_images

def _format_children_as_list(children: list[SmartArtNode]) -> str:
    """Format children nodes as HTML list for table cell."""
    parts = []
    for child in children:
        parts.append(f"- {child.text}")
        # Recursively add grandchildren with indentation
        for grandchild in child.children:
            parts.append(f"  - {grandchild.text}")
    
    return "<br>".join(parts)
```

#### 5. Intégration dans Convertisseur Principal
```python
def convert(self, local_path, **kwargs) -> DocumentConverionResult:
    """Main PPTX converter with SmartArt support."""
    
    # ... existing code ...
    
    for slide_idx, slide in enumerate(prs.slides, start=1):
        smartart_counter = 0
        
        for shape in slide.shapes:
            # BRIEF_05: SmartArt Detection
            if _is_smartart(shape):
                # Extract structure
                nodes = _extract_smartart_nodes(shape)
                
                smartart_info = SmartArtInfo(
                    title=_extract_smartart_title(shape),
                    nodes=nodes,
                    has_images=_detect_smartart_images(nodes)
                )
                
                # Choose conversion type
                if smartart_info.has_images:
                    # Type 2: Table
                    markdown_block, saved_imgs = _convert_smartart_to_table(
                        smartart_info,
                        slide_idx,
                        smartart_counter,
                        image_dir,
                        kwargs
                    )
                    markdown_parts.append(markdown_block)
                else:
                    # Type 1: List
                    markdown_block = _convert_smartart_to_list(
                        smartart_info,
                        slide_idx
                    )
                    markdown_parts.append(markdown_block)
                
                smartart_counter += 1
                continue
            
            # ... existing shape processing ...
```

---

## 🧪 Tests et Validation

### Fichiers de Test à Créer

**Nouveaux fichiers PPTX** :
```
packages/markitdown/tests/test_files/
├─ test_smartart_text_only.pptx       (Type 1: Liste pure)
├─ test_smartart_with_icons.pptx      (Type 2: Icônes)
├─ test_smartart_orgchart.pptx        (Type 2: Photos organigramme)
├─ test_smartart_mixed.pptx           (Type 2: Certains items avec images)
└─ test_smartart_complex_hierarchy.pptx (Type 1: 5 niveaux profondeur)
```

### Tests Unitaires

**Fichier** : `packages/markitdown/tests/test_pptx_smartart.py`

```python
import pytest
from markitdown import MarkItDown

class TestSmartArtExtraction:
    
    def test_smartart_text_only_converts_to_list(self):
        """Type 1: SmartArt textuel → Liste Markdown."""
        md = MarkItDown()
        result = md.convert("test_files/test_smartart_text_only.pptx")
        
        # Vérifier présence de liste hiérarchique
        assert "- Innovation" in result.text_content
        assert "  - R&D Investment" in result.text_content
        assert "  - Continuous Learning" in result.text_content
    
    def test_smartart_with_icons_converts_to_table(self):
        """Type 2: SmartArt avec icônes → Table Markdown."""
        md = MarkItDown()
        result = md.convert("test_files/test_smartart_with_icons.pptx", output_images=True)
        
        # Vérifier table Markdown
        assert "| Visual | Details |" in result.text_content
        assert "![" in result.text_content  # Images présentes
        assert "slide1_smartart0_item0.png" in result.text_content
    
    def test_smartart_images_are_saved(self, tmp_path):
        """Vérifier sauvegarde physique des images SmartArt."""
        md = MarkItDown()
        result = md.convert(
            "test_files/test_smartart_with_icons.pptx",
            output_images=True,
            image_dir=str(tmp_path / "images")
        )
        
        # Vérifier fichiers créés
        image1 = tmp_path / "images" / "slide1_smartart0_item0.png"
        image2 = tmp_path / "images" / "slide1_smartart0_item1.png"
        
        assert image1.exists()
        assert image2.exists()
        assert image1.stat().st_size > 0
    
    def test_smartart_preserves_hierarchy_levels(self):
        """Vérifier préservation des niveaux hiérarchiques."""
        md = MarkItDown()
        result = md.convert("test_files/test_smartart_complex_hierarchy.pptx")
        
        # Vérifier indentation correcte (2 espaces par niveau)
        assert "- Level 0" in result.text_content
        assert "  - Level 1" in result.text_content
        assert "    - Level 2" in result.text_content
        assert "      - Level 3" in result.text_content
    
    def test_smartart_mixed_mode_forces_table(self):
        """SmartArt mixte (certains items avec images) → Table complète."""
        md = MarkItDown()
        result = md.convert("test_files/test_smartart_mixed.pptx", output_images=True)
        
        # Vérifier format table pour tous les items
        assert "| Visual | Details |" in result.text_content
        assert "*(no image)*" in result.text_content  # Items sans image
    
    def test_smartart_title_extracted(self):
        """Vérifier extraction du titre SmartArt."""
        md = MarkItDown()
        result = md.convert("test_files/test_smartart_text_only.pptx")
        
        assert "### Company Values" in result.text_content
    
    def test_smartart_disabled_via_param(self):
        """Vérifier désactivation via paramètre."""
        md = MarkItDown()
        result = md.convert(
            "test_files/test_smartart_text_only.pptx",
            extract_smartart=False
        )
        
        # SmartArt ignoré → pas de contenu extrait
        assert "Innovation" not in result.text_content
```

### Tests d'Intégration

```python
def test_smartart_integration_with_images(self, tmp_path):
    """
    Test intégration complète :
    - Slide avec SmartArt + images normales
    - Vérifier nommage distinct
    """
    md = MarkItDown()
    result = md.convert(
        "test_files/test_mixed_content.pptx",  # SmartArt + images normales
        output_images=True,
        image_dir=str(tmp_path / "images")
    )
    
    # Vérifier images normales
    assert (tmp_path / "images" / "slide1_image0.jpg").exists()
    
    # Vérifier images SmartArt
    assert (tmp_path / "images" / "slide2_smartart0_item0.png").exists()
    
    # Vérifier Markdown contient les deux
    assert "![Photo](images/slide1_image0.jpg)" in result.text_content
    assert "![Icon](images/slide2_smartart0_item0.png)" in result.text_content
```

### Tests Edge Cases

```python
def test_smartart_empty_nodes():
    """SmartArt avec nœuds vides → ignorés."""
    # Test robustesse

def test_smartart_very_deep_hierarchy():
    """SmartArt avec 10+ niveaux → tronqué à max_depth."""
    # Test limite profondeur

def test_smartart_special_characters_in_text():
    """SmartArt avec caractères spéciaux → échappement correct."""
    # Test sanitization

def test_smartart_without_title():
    """SmartArt sans titre → pas de heading H3."""
    # Test optionnalité titre
```

---

## ✅ Critères d'Acceptation

### Fonctionnels
- [ ] ✅ **Détection SmartArt** : 100% des SmartArt détectés dans PPTX
- [ ] ✅ **Type 1 (Texte)** : Conversion correcte en liste Markdown hiérarchique
- [ ] ✅ **Type 2 (Visuel)** : Conversion en table 2 colonnes avec images extraites
- [ ] ✅ **Hiérarchie** : Préservation des niveaux (jusqu'à 5 niveaux)
- [ ] ✅ **Images SmartArt** : Extraction et sauvegarde dans `images/` avec nommage correct
- [ ] ✅ **Titres** : Extraction et formatage en H3 si présents
- [ ] ✅ **Mode Mixte** : Détection automatique → Table si 1+ image

### Techniques
- [ ] ✅ **Aucune régression** : BRIEF_01 tests passent à 100%
- [ ] ✅ **Tests unitaires** : 10+ tests SmartArt passent
- [ ] ✅ **Linting** : 0 erreur `get_errors`
- [ ] ✅ **Type hints** : 100% des fonctions typées
- [ ] ✅ **Docstrings** : Google style pour toutes nouvelles fonctions
- [ ] ✅ **Module markers** : `# --- MODULE: SmartArt (BRIEF_05) ---`

### Qualité
- [ ] ✅ **PEP 8** : Code conforme (79 chars, 4 espaces)
- [ ] ✅ **Self-documenting** : Noms explicites, commentaires WHY
- [ ] ✅ **Error handling** : Try/except pour XML parsing
- [ ] ✅ **Fallback gracieux** : Si SmartArt corrompu → skip sans crash

---

## 📚 Références Techniques

### Documentation python-pptx
- SmartArt API (limité) : https://python-pptx.readthedocs.io/en/latest/
- Shape Types : https://python-pptx.readthedocs.io/en/latest/api/enum/MsoShapeType.html
- XML Handling : https://python-pptx.readthedocs.io/en/latest/dev/analysis/placeholders.html

### Spécifications XML SmartArt (Office Open XML)
- DrawingML Diagrams : http://officeopenxml.com/drwDiagram.php
- Diagram Data Model : http://officeopenxml.com/drwDiagramDefine.php

### Exemples de Parsing XML SmartArt
```python
from lxml import etree

def parse_smartart_xml(shape):
    """Parse SmartArt XML structure."""
    # Namespace definitions
    nsmap = {
        'dgm': 'http://schemas.openxmlformats.org/drawingml/2006/diagram',
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
    }
    
    # Get diagram data part
    diagram_part = shape.part.related_parts[shape._element.graphic_frame.rId]
    diagram_xml = diagram_part.blob
    
    # Parse XML
    root = etree.fromstring(diagram_xml)
    
    # Extract points (nodes)
    points = root.xpath('//dgm:pt', namespaces=nsmap)
    
    # Extract connections (hierarchy)
    connections = root.xpath('//dgm:cxn', namespaces=nsmap)
    
    # Build hierarchy
    # ...
```

---

## 🚀 Plan de Déploiement

### Phase 1 : Recherche et Prototypage (1h)
1. Analyser capacités `python-pptx` pour SmartArt
2. Identifier limitations (parsing XML si nécessaire)
3. Créer PPTX tests avec différents types SmartArt
4. Prototyper extraction basique

### Phase 2 : Implémentation Type 1 (2h)
1. Détection SmartArt
2. Extraction hiérarchie textuelle
3. Conversion → Liste Markdown
4. Tests unitaires Type 1

### Phase 3 : Implémentation Type 2 (3h)
1. Détection images dans SmartArt
2. Extraction et sauvegarde images
3. Conversion → Table Markdown
4. Gestion items mixtes (avec/sans images)
5. Tests unitaires Type 2

### Phase 4 : Intégration et Polish (2h)
1. Intégration dans `_pptx_converter.py`
2. Gestion titres SmartArt
3. Edge cases et error handling
4. Tests d'intégration complets
5. Documentation et docstrings

### Phase 5 : Tests et Validation (2h)
1. Tests régression BRIEF_01
2. Tests sur PPTX réels (slides utilisateur)
3. Validation qualité code (`get_errors`)
4. Review et ajustements finaux

**Temps total** : 10h

---

## 🔗 Liens avec Autres Briefs

### Dépendances
- ✅ **BRIEF_01** (Extraction Images) : Réutilise `_save_image_to_folder()` pour images SmartArt
- 🟡 **BRIEF_02** (Descriptions LLM) : Compatible - peut décrire images SmartArt si configuré
- ❌ **BRIEF_03** (Charts ASCII) : Indépendant - SmartArt ≠ Charts

### Synergies
- **BRIEF_01 + BRIEF_05** : Images normales + Images SmartArt dans même dossier `images/`
- **BRIEF_02 + BRIEF_05** : LLM peut analyser icônes SmartArt si `use_client_vision=True`

---

## 💡 Extensions Futures (Hors Scope BRIEF_05)

### Priorité Basse
- Support SmartArt 3D (nécessite rendering)
- Support animations SmartArt (nécessite vidéo)
- Conversion SmartArt → SVG (au lieu de PNG)
- Support styles SmartArt avancés (gradients, ombres)

### Idées Avancées
- LLM analysis de SmartArt complets (via BRIEF_02)
- Export SmartArt vers formats structurés (JSON, YAML)
- Reconstruction SmartArt depuis Markdown (reverse conversion)

---

**Note** : Ce brief vise une implémentation pragmatique et robuste pour les 80% de cas d'usage courants. Les SmartArt exotiques ou très complexes peuvent nécessiter des extensions futures.
