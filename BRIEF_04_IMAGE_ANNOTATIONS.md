# Brief Technique #04 - Conversion et Composition des Annotations Visuelles

**Date:** 11 février 2026  
**Fonctionnalité ROADMAP:** #4 - Annotations Visuelles avec Rendu Graphique  
**Statut:** À Implémenter  
**Priorité:** 🟡 MOYENNE  
**Dépend de:** BRIEF_01 ✅ (Extraction Images - Complété)  
**Complexité:** Moyenne-Haute  
**Estimation:** 10h (Phase 1: 6h + Phase 2: 4h)

---

## 📋 Résumé Exécutif

### Problème
Les présentations PPTX contiennent souvent des **annotations visuelles** superposées aux images :
- **AUTO_SHAPE** (ellipses, rectangles, flèches) avec code couleur (A/B, 1/2/3)
- **TEXT_BOX** (légendes, notes explicatives)

Actuellement, ces annotations sont **perdues** lors de extraction → contexte visuel incomplet.

### Solution
**Phase 1 (Tier 1)** : Convertir shapes **standalone** (ne touchant pas d''image) en images PNG individuelles  
**Phase 2 (Tier 2)** : Créer images **composites** pour shapes touchant une image (image base + annotations)

### Impact
✅ Préserver le contexte visuel complet des slides  
✅ Diagrammes annotés restent compréhensibles  
✅ Workflow LLM bénéficie d''annotations conservées

---

## 🎯 Phase 1 (Tier 1) : Shapes Standalone

### Objectif
Convertir les **AUTO_SHAPE** et **TEXT_BOX** qui **ne touchent PAS** une image en images PNG individuelles.

### Règles de Conversion

#### AUTO_SHAPE
**Stratégie :**
1. **Si forme existe dans Pillow** (ellipse, rectangle, polygon, etc.)
   - ✅ Convertir avec forme exacte
   - ✅ Garder couleur de remplissage uniquement
   - ❌ Ignorer effets avancés (gradients, shadows, 3D)

2. **Si forme n''existe pas dans Pillow**
   - ✅ Fallback : Rectangle simple
   - ✅ Garder couleur de remplissage uniquement

**Formes supportées (mapping PPTX → Pillow) :**
```python
SHAPE_MAPPING = {
    "OVAL": "ellipse",           # MSO_SHAPE.OVAL
    "RECTANGLE": "rectangle",     # MSO_SHAPE.RECTANGLE
    "ROUNDED_RECTANGLE": "rounded_rectangle",
    "ISOSCELES_TRIANGLE": "polygon",  # 3 points
    # Autres : fallback → rectangle
}
```

**Exemple :** Ellipse rouge avec texte "A"
```
Input:  AUTO_SHAPE (Ellipse, fill=rouge, texte="A")
Output: images/slide29_shape3.png (ellipse rouge PNG avec "A" centré)
```

#### TEXT_BOX
**Stratégie :**
- ✅ Rectangle avec fond **transparent**
- ✅ Texte noir simple (police système)
- ✅ Bordure optionnelle si définie dans PPTX

**Exemple :** Text box "2 chemins a tester A et B"
```
Input:  TEXT_BOX (texte="2 chemins...", no border)
Output: images/slide29_shape18.png (texte sur fond transparent)
```

### Algorithme Phase 1

```python
def _should_convert_shape(self, shape, image_shapes):
    """
    Détermine si un shape doit être converti en image.
    
    Args:
        shape: Shape à évaluer
        image_shapes: Liste des shapes IMAGE du slide
    
    Returns:
        bool: True si conversion nécessaire
    """
    # Ignorer si déjà une image
    if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
        return False
    
    # Ignorer si placeholder
    if shape.shape_type == MSO_SHAPE_TYPE.PLACEHOLDER:
        return False
    
    # Convertir si AUTO_SHAPE ou TEXT_BOX
    if shape.shape_type in [MSO_SHAPE_TYPE.AUTO_SHAPE, MSO_SHAPE_TYPE.TEXT_BOX]:
        # Vérifier collision avec images
        for image_shape in image_shapes:
            if self._shapes_overlap(shape, image_shape):
                return False  # Phase 2 s''occupera de ce cas
        return True  # Standalone → convertir
    
    return False

def _shapes_overlap(self, shape1, shape2):
    """
    Détecte si 2 shapes se chevauchent (même partiellement).
    
    Returns:
        bool: True si overlap >= 1 pixel
    """
    # Bounding boxes
    x1_left, y1_top = shape1.left, shape1.top
    x1_right = x1_left + shape1.width
    y1_bottom = y1_top + shape1.height
    
    x2_left, y2_top = shape2.left, shape2.top
    x2_right = x2_left + shape2.width
    y2_bottom = y2_top + shape2.height
    
    # Overlap test
    return not (x1_right < x2_left or x2_right < x1_left or
                y1_bottom < y2_top or y2_bottom < y1_top)

def _convert_shape_to_image(self, shape, slide_num, shape_idx, image_dir):
    """
    Convertit AUTO_SHAPE ou TEXT_BOX en image PNG.
    
    Returns:
        str: Chemin relatif de l''image générée
    """
    from PIL import Image, ImageDraw, ImageFont
    
    # Créer canvas avec dimensions du shape
    width = int(shape.width / 9525)  # EMU → pixels (96 DPI)
    height = int(shape.height / 9525)
    
    # Fond transparent par défaut
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Extraire couleur de remplissage
    fill_color = self._get_shape_fill_color(shape)
    
    # Dessiner forme
    if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
        shape_name = self._get_shape_name(shape)
        
        if shape_name == "OVAL":
            draw.ellipse([0, 0, width, height], fill=fill_color)
        elif shape_name == "RECTANGLE":
            draw.rectangle([0, 0, width, height], fill=fill_color)
        else:
            # Fallback : rectangle simple
            draw.rectangle([0, 0, width, height], fill=fill_color)
    
    elif shape.shape_type == MSO_SHAPE_TYPE.TEXT_BOX:
        # Fond transparent déjà configuré
        pass
    
    # Ajouter texte si présent
    if hasattr(shape, "text") and shape.text.strip():
        text = shape.text.strip()
        font = ImageFont.load_default()
        
        # Centrer texte
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        
        draw.text((text_x, text_y), text, fill="black", font=font)
    
    # Sauvegarder
    shape_filename = f"slide{slide_num}_shape{shape_idx}.png"
    shape_path = Path(image_dir) / shape_filename
    img.save(str(shape_path), "PNG")
    
    return shape_path.as_posix()
```

### Nommage des Fichiers Phase 1

**Convention :** `slide{N}_shape{M}.png`

Exemples :
- `slide29_shape3.png` ← Ellipse "A" (shape index 3)
- `slide29_shape18.png` ← Text box "2 chemins..." (shape index 18)

---

## 🎯 Phase 2 (Tier 2) : Images Composites

### Objectif
Pour les shapes qui **touchent une image** (overlap ≥ 1 pixel), créer une **image composite** = image de base + annotations rendues.

### Algorithme Phase 2

```python
def _create_composite_image(self, base_image_path, overlapping_shapes, slide_num, image_dir):
    """
    Crée image composite : image de base + shapes annotées.
    
    Args:
        base_image_path: Chemin de l''image PPTX extraite
        overlapping_shapes: Liste des shapes qui touchent cette image
        slide_num: Numéro du slide
        image_dir: Dossier de destination
    
    Returns:
        str: Chemin de l''image composite
    """
    from PIL import Image, ImageDraw, ImageFont
    
    # Charger image de base
    base_img = Image.open(base_image_path).convert("RGBA")
    
    # Créer calque de composition
    overlay = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Image PPTX position/dimensions (pour calcul offset)
    base_shape = overlapping_shapes["base_shape"]
    base_left = base_shape.left
    base_top = base_shape.top
    
    # Dessiner chaque shape superposée
    for shape in overlapping_shapes["annotations"]:
        # Calculer position relative à l''image
        rel_x = int((shape.left - base_left) / 9525)
        rel_y = int((shape.top - base_top) / 9525)
        rel_width = int(shape.width / 9525)
        rel_height = int(shape.height / 9525)
        
        # Dessiner shape (même logique que Phase 1)
        fill_color = self._get_shape_fill_color(shape)
        
        if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
            shape_name = self._get_shape_name(shape)
            if shape_name == "OVAL":
                draw.ellipse(
                    [rel_x, rel_y, rel_x + rel_width, rel_y + rel_height],
                    fill=fill_color
                )
            else:
                draw.rectangle(
                    [rel_x, rel_y, rel_x + rel_width, rel_y + rel_height],
                    fill=fill_color
                )
        
        # Ajouter texte du shape
        if hasattr(shape, "text") and shape.text.strip():
            font = ImageFont.load_default()
            text_x = rel_x + rel_width // 2
            text_y = rel_y + rel_height // 2
            draw.text((text_x, text_y), shape.text.strip(), 
                     fill="black", font=font, anchor="mm")
    
    # Composer les calques
    composite = Image.alpha_composite(base_img, overlay)
    
    # Sauvegarder image composite
    composite_filename = f"slide{slide_num}_composite.png"
    composite_path = Path(image_dir) / composite_filename
    composite.save(str(composite_path), "PNG")
    
    return composite_path.as_posix()
```

### Workflow Phase 2

```
1. Extraire image PPTX → slide29_image0.png (base)
2. Détecter shapes avec overlap
   - Ellipse 3 (A) : overlap ✅
   - Ellipse 7 (A) : overlap ✅
   - Text box 18 : overlap ✅
3. Créer composite → slide29_image0_composite.png
4. Markdown :
   ![Process Flow](images/slide29_image0_composite.png)
```

### Nommage des Fichiers Phase 2

**Convention :** `slide{N}_image{M}_composite.png`

Exemple :
- `slide29_image0_composite.png` ← Image originale + 19 ellipses + 2 text boxes

**Alternative (garder original aussi) :**
- `slide29_image0.png` ← Image brute (sans annotations)
- `slide29_image0_composite.png` ← Image annotée

---

## 🔧 Spécifications Techniques

### Dépendances
- ✅ **Pillow** : Déjà installée (ajoutée dans BRIEF_01)
- ✅ **python-pptx** : Déjà requise

**Aucune nouvelle dépendance externe.**

### Paramètres de Configuration

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `convert_shapes` | bool | `True` | Activer conversion des shapes |
| `composite_images` | bool | `True` | Activer images composites (Phase 2) |
| `keep_standalone_shapes` | bool | `True` | Sauvegarder aussi shapes standalone (Phase 1) |
| `shape_rendering_dpi` | int | `96` | DPI pour conversion EMU → pixels |
| `default_text_color` | str | `"black"` | Couleur texte par défaut |

### Détection des Couleurs PPTX

```python
def _get_shape_fill_color(self, shape):
    """
    Extrait couleur de remplissage d''un shape PPTX.
    
    Returns:
        tuple: (R, G, B, A) ou None
    """
    try:
        if shape.fill.type == MSO_FILL_TYPE.SOLID:
            color = shape.fill.fore_color
            rgb = color.rgb
            # Convertir bytes → tuple
            return (rgb[0], rgb[1], rgb[2], 255)
    except:
        pass
    
    # Fallback : blanc opaque
    return (255, 255, 255, 255)
```

### Unités de Mesure PPTX

**EMU → Pixels :**
```python
# EMU (English Metric Units) = unité PPTX
# 1 inch = 914400 EMU
# 96 DPI standard → 1 pixel = 9525 EMU

def emu_to_pixels(emu, dpi=96):
    return int(emu / 9525)
```

---

## 🧪 Tests

### Test 1 : Shapes Standalone (Phase 1)
**Input :** Slide avec 3 ellipses (A, B, C) **sans image**  
**Expected :**
```
✅ 3 fichiers créés :
   - slide1_shape0.png (ellipse A)
   - slide1_shape1.png (ellipse B)
   - slide1_shape2.png (ellipse C)
✅ Markdown :
   ![A](images/slide1_shape0.png)
   ![B](images/slide1_shape1.png)
   ![C](images/slide1_shape2.png)
```

### Test 2 : Text Box Standalone (Phase 1)
**Input :** Slide avec 1 text box "Note importante"  
**Expected :**
```
✅ images/slide2_shape0.png (texte sur fond transparent)
✅ Markdown :
   ![Note importante](images/slide2_shape0.png)
```

### Test 3 : Image Composite (Phase 2)
**Input :** Slide 29 "Design des essais" (image + 19 ellipses + 2 text boxes)  
**Expected :**
```
✅ images/slide29_image0.png (image originale)
✅ images/slide29_image0_composite.png (image + annotations)
✅ Markdown :
   ![Process Flow](images/slide29_image0_composite.png)
```

### Test 4 : Mix Standalone + Composite
**Input :** Slide avec image annotée + shape isolé  
**Expected :**
```
✅ images/slide3_image0_composite.png (image + annotations)
✅ images/slide3_shape10.png (shape standalone)
✅ Markdown correct pour les deux
```

### Test 5 : Forme Non Supportée (Fallback)
**Input :** AUTO_SHAPE type "STAR" (étoile - pas dans Pillow)  
**Expected :**
```
✅ images/slide4_shape0.png (rectangle simple avec couleur)
✅ Pas d''erreur, fallback graceful
```

---

## 📋 Plan d''Implémentation

### Phase 1 : Shapes Standalone (6h)

**Sprint 1A : Infrastructure (2h)**
- [ ] Ajouter `_shapes_overlap()` pour détection collision
- [ ] Ajouter `_should_convert_shape()` pour filtrage
- [ ] Ajouter `_get_shape_fill_color()` extraction couleur
- [ ] Ajouter `_get_shape_name()` identification type

**Sprint 1B : Rendu Formes (2h)**
- [ ] Implémenter `_convert_shape_to_image()`
- [ ] Mapping PPTX shapes → Pillow primitives
- [ ] Rendu AUTO_SHAPE (ellipse, rectangle, fallback)
- [ ] Rendu TEXT_BOX (fond transparent)

**Sprint 1C : Intégration Markdown (2h)**
- [ ] Modifier `get_shape_content()` pour détecter shapes standalone
- [ ] Générer Markdown pour shapes convertis
- [ ] Tests 1-2 validés

### Phase 2 : Images Composites (4h)

**Sprint 2A : Détection Overlap (1h)**
- [ ] Identifier shapes touchant chaque image
- [ ] Grouper par image de base
- [ ] Structure de données `overlapping_shapes`

**Sprint 2B : Composition (2h)**
- [ ] Implémenter `_create_composite_image()`
- [ ] Calcul positions relatives
- [ ] Composition de calques (alpha blending)
- [ ] Sauvegarder images composites

**Sprint 2C : Tests & Edge Cases (1h)**
- [ ] Tests 3-5 validés
- [ ] Test régression BRIEF_01 (images sans annotations)
- [ ] Gestion shapes partiellement hors image

**Estimation Totale :** 10h

---

## ✅ Conditions d''Acceptation

### Phase 1 (Tier 1)
- [ ] AUTO_SHAPE standalone converties en PNG
- [ ] TEXT_BOX standalone converties en PNG (fond transparent)
- [ ] Couleurs de remplissage préservées
- [ ] Mapping formes PPTX → Pillow fonctionnel
- [ ] Fallback rectangle pour formes non supportées
- [ ] Texte centré dans les shapes
- [ ] Fichiers nommés `slide{N}_shape{M}.png`
- [ ] Liens Markdown corrects

### Phase 2 (Tier 2)
- [ ] Détection overlap (≥1 pixel) fonctionne
- [ ] Images composites créées correctement
- [ ] Positions relatives des annotations exactes
- [ ] Alpha blending transparent fonctionnel
- [ ] Fichiers nommés `slide{N}_image{M}_composite.png`
- [ ] Pas de régression sur images sans annotations

### Général
- [ ] Aucune nouvelle dépendance externe
- [ ] Compatible avec BRIEF_01 (extraction standard)
- [ ] Tests 1-5 passent tous
- [ ] Performance acceptable (< 2s par slide)

---

## 🔄 Dépendances entre Briefs

```
BRIEF_01 (Images) ✅ COMPLÉTÉ
  └─→ BRIEF_04 (Annotations Visuelles) ← CE BRIEF
       ├─ Phase 1 : Shapes standalone
       └─ Phase 2 : Images composites

BRIEF_02 (Image Descriptions LLM) → Peut bénéficier des composites
BRIEF_03 (Chart ASCII Art) → Indépendant
```

---

## ⚠️ Mise à Jour MCP Obligatoire

**CRITIQUE** : Après implémentation, les nouveaux paramètres **DOIVENT** être exposés dans le MCP.

**Fichier à modifier :** `packages/markitdown-mcp/src/markitdown_mcp/__main__.py`

**Paramètres à ajouter pour BRIEF_04 :**
- `convert_shapes: bool = True` - Activer conversion des shapes
- `composite_images: bool = True` - Activer images composites (Phase 2)
- `keep_standalone_shapes: bool = True` - Sauvegarder shapes standalone (Phase 1)
- `shape_rendering_dpi: int = 96` - DPI pour conversion EMU → pixels

**Action requise :**
1. Ajouter les paramètres à `convert_to_markdown()`
2. Documenter dans la docstring
3. Tester : `pip install -e packages/markitdown-mcp`

**Référence :** Voir commit e3dcb49 (BRIEF_01) pour exemple d'implémentation MCP.

---

## 📚 Références

- **Fichier :** [`_pptx_converter.py`](packages/markitdown/src/markitdown/converters/_pptx_converter.py)
- **Dépendance :** Pillow (installée), python-pptx (existante)
- **BRIEF_01 :** Extraction images (prérequis)
- **Pillow Documentation :** https://pillow.readthedocs.io/

---

## 🚀 Extensions Futures (Hors Scope)

- Gradients / Shadows / 3D effects
- Formes complexes (flèches customisées, polygones irréguliers)
- Polices PPTX embedded
- Rotation des shapes
- Animations / Transitions

**Note :** Ces features nécessiteraient un moteur de rendu PPTX complet (LibreOffice backend). Hors scope pour ce brief.

---

**Prochaine étape :** Implémenter Phase 1 (Shapes Standalone) puis Phase 2 (Composites).
