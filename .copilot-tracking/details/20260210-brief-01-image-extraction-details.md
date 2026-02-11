# Détails Techniques BRIEF_01 - Extraction Images PPTX

**Date:** 20260210
**Brief:** BRIEF_01_IMAGE_EXTRACTION
**Phase:** Détails Techniques

---

## 🔧 Modifications Détaillées

### Modification 1: Import hashlib

**Fichier:** `_pptx_converter.py`
**Ligne:** ~5 (après `import base64`)

```python
import hashlib  # Pour déduplication MD5 (standard library)
```

**Justification:** Nécessaire pour calcul hash MD5 lors de la déduplication d'images.

---

### Modification 2: Initialisation __init__

**Fichier:** `_pptx_converter.py`
**Ligne:** ~38-42

```python
def __init__(self):
    super().__init__()
    self._html_converter = HtmlConverter()
    # --- MODULE: Image Management (BRIEF_01) ---
    self._image_hashes = {}  # Déduplication d'images {hash: path}
    # --- END MODULE ---
```

**Justification:** Dictionnaire pour stocker les hashs MD5 des images et éviter doublons.

---

### Modification 3: Configuration dans convert()

**Fichier:** `_pptx_converter.py`
**Ligne:** ~80 (après `presentation = pptx.Presentation(file_stream)`)

```python
# --- MODULE: Image Management - Configuration (BRIEF_01) ---
image_dir = kwargs.get("image_dir", "images")
output_images = kwargs.get("output_images", True)
deduplicate_images = kwargs.get("deduplicate_images", False)
self._image_hashes = {}  # Reset pour chaque conversion
# --- END MODULE ---
```

**Justification:** Extraire configuration et réinitialiser le dictionnaire de hashs par fichier.

---

### Modification 4: Compteur image_count

**Fichier:** `_pptx_converter.py`
**Ligne:** ~189 (avant boucle `for shape in sorted_shapes:`)

```python
image_count = 0  # Compteur d'images par slide
sorted_shapes = sorted(...)
for shape in sorted_shapes:
    get_shape_content(shape, **kwargs)
```

**Justification:** Nécessaire pour nommage séquentiel des images par slide.

**Note:** Variable doit être accessible dans `get_shape_content()` via `nonlocal` ou passage en paramètre.

---

### Modification 5: Nouvelle Méthode _get_image_extension()

**Fichier:** `_pptx_converter.py`
**Position:** Après `_is_table()` (ligne ~220)

```python
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
    
    Examples:
        >>> self._get_image_extension("logo.png", "image/png")
        '.png'
        >>> self._get_image_extension(None, "image/jpeg")
        '.jpg'
        >>> self._get_image_extension(None, None)
        '.png'
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
    }
    
    # Try mapping from MIME type
    if content_type:
        ext = mime_to_ext.get(content_type.lower())
        if ext:
            return ext
    
    # Fallback to PNG
    return '.png'
# --- END MODULE ---
```

**Justification:** Centralise la logique de détermination d'extension avec fallback robuste.

---

### Modification 6: Nouvelle Méthode _save_image()

**Fichier:** `_pptx_converter.py`
**Position:** Après `_get_image_extension()`

```python
# --- MODULE: Image Extraction (BRIEF_01) ---
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
    
    Examples:
        >>> self._save_image(shape, 1, 0, "images", False)
        ('images/slide1_image0.png', False)
        
        >>> # Second call with same image
        >>> self._save_image(shape_duplicate, 2, 0, "images", True)
        ('images/slide1_image0.png', True)
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
    
    # Generate filename: slide{N}_image{M}.{ext}
    image_filename = f"slide{slide_num}_image{image_count}{ext}"
    image_path = os.path.join(image_dir, image_filename)
    
    # Create directory if needed
    os.makedirs(image_dir, exist_ok=True)
    
    # Save file to disk
    with open(image_path, 'wb') as f:
        f.write(blob)
    
    # Store hash for future deduplication
    if deduplicate_images:
        self._image_hashes[image_hash] = image_path
    
    return image_path, False
# --- END MODULE ---
```

**Justification:** Gère sauvegarde, déduplication et nommage cohérent des images.

---

### Modification 7: Bloc Images dans get_shape_content()

**Fichier:** `_pptx_converter.py`
**Ligne:** ~147-154

**Code ACTUEL:**
```python
if kwargs.get("keep_data_uris", False):
    blob = shape.image.blob
    content_type = shape.image.content_type or "image/png"
    b64_string = base64.b64encode(blob).decode("utf-8")
    md_content += f"\n![{alt_text}](data:{content_type};base64,{b64_string})\n"
else:
    filename = re.sub(r"\W", "", shape.name) + ".jpg"
    md_content += "\n![" + alt_text + "](" + filename + ")\n"
```

**Code NOUVEAU:**
```python
# --- Get configuration (BRIEF_01) ---
keep_data_uris = kwargs.get("keep_data_uris", False)
output_images = kwargs.get("output_images", True)
image_dir = kwargs.get("image_dir", "images")
deduplicate_images = kwargs.get("deduplicate_images", False)
# --- END ---

# Mode Base64 (PRESERVE EXISTING - DO NOT MODIFY)
if keep_data_uris:
    blob = shape.image.blob
    content_type = shape.image.content_type or "image/png"
    b64_string = base64.b64encode(blob).decode("utf-8")
    md_content += f"\n![{alt_text}](data:{content_type};base64,{b64_string})\n"

# --- MODULE: File Extraction (BRIEF_01) ---
elif output_images:
    # Save image to disk
    image_path, deduplicated = self._save_image(
        shape, 
        slide_num, 
        image_count, 
        image_dir, 
        deduplicate_images
    )
    
    # Generate Markdown with correct path
    md_content += f"\n![{alt_text}]({image_path})\n"
    
    # Increment counter if new image (not deduplicated)
    if not deduplicated:
        image_count += 1
# --- END MODULE ---

# Legacy mode (deprecated - generates broken links)
else:
    filename = re.sub(r"\W", "", shape.name) + ".jpg"
    md_content += "\n![" + alt_text + "](" + filename + ")\n"
```

**Justification:** Ajoute nouvelle logique de sauvegarde tout en préservant mode Base64 existant.

**⚠️ CRITIQUE:** Nécessite gestion de `image_count` via `nonlocal` ou refactoring paramètres.

---

## 🧩 Gestion de image_count

### Problème
`image_count` doit être incrémenté dans `get_shape_content()` mais déclaré en dehors.

### Solution 1: nonlocal (Recommandée)

```python
def convert(...):
    # ...
    for slide in presentation.slides:
        slide_num += 1
        
        def get_shape_content(shape, **kwargs):
            nonlocal md_content
            nonlocal image_count  # ← Ajouter cette ligne
            
            # ...reste du code...
        
        image_count = 0  # ← Initialiser ici
        sorted_shapes = sorted(...)
        for shape in sorted_shapes:
            get_shape_content(shape, **kwargs)
```

### Solution 2: Paramètre mutable (Alternative)

Utiliser un dictionnaire pour passer par référence:
```python
counters = {"image": 0}
get_shape_content(shape, counters=counters, **kwargs)
```

**Recommandation:** Solution 1 (nonlocal) - plus simple et cohérent avec `md_content`.

---

## 📝 Paramètres kwargs Ajoutés

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `output_images` | `bool` | `True` | Activer sauvegarde des images |
| `image_dir` | `str` | `"images"` | Dossier destination (relatif) |
| `deduplicate_images` | `bool` | `False` | Activer déduplication MD5 |

**Exemples d'utilisation:**
```python
# Standard (par défaut)
result = converter.convert(stream, stream_info)

# Dossier personnalisé
result = converter.convert(stream, stream_info, image_dir="assets/img")

# Avec déduplication
result = converter.convert(
    stream, 
    stream_info, 
    deduplicate_images=True
)

# Désactiver extraction (mode legacy)
result = converter.convert(stream, stream_info, output_images=False)
```

---

## 🧪 Scénarios de Test

### Test 1: Extraction Standard
```python
converter = PptxConverter()
result = converter.convert(pptx_stream, stream_info)

# Vérifier:
# - Dossier images/ créé
# - Fichiers images/slide1_image0.png, images/slide2_image0.jpg existent
# - Markdown contient ![...](images/slide1_image0.png)
```

### Test 2: Dossier Personnalisé
```python
result = converter.convert(
    pptx_stream, 
    stream_info, 
    image_dir="custom/path"
)

# Vérifier:
# - Dossier custom/path/ créé
# - Markdown contient ![...](custom/path/slide1_image0.png)
```

### Test 3: Déduplication
```python
# PPTX avec même logo sur 3 slides
result = converter.convert(
    pptx_stream, 
    stream_info, 
    deduplicate_images=True
)

# Vérifier:
# - UN SEUL fichier créé: images/slide1_image0.png
# - 3 occurrences dans Markdown pointent vers même fichier
```

### Test 4: Mode Base64 (Régression)
```python
result = converter.convert(
    pptx_stream, 
    stream_info, 
    keep_data_uris=True
)

# Vérifier:
# - Aucun dossier images/ créé
# - Markdown contient ![...](data:image/png;base64,...)
# - Comportement IDENTIQUE à avant modification
```

---

## ⚠️ Points d'Attention Critiques

### 1. Mode Base64 INTOUCHABLE
**Lignes 147-151** ne doivent JAMAIS être modifiées.
Test de régression obligatoire après implémentation.

### 2. Gestion image_count avec nonlocal
Nécessite ajout de `nonlocal image_count` dans `get_shape_content()`.

### 3. Chemins Relatifs Uniquement
Toujours générer `images/file.png`, jamais `/absolute/path`.

### 4. Création Dossier Sécurisée
`os.makedirs(exist_ok=True)` - gère cas où dossier existe déjà.

### 5. Gestion Erreurs I/O
Prévoir try/except autour de:
- `os.makedirs()` (permissions)
- `open()` (disque plein, permissions)

---

## 📊 Checklist Validation

Avant de marquer chaque task complète:

- [ ] Code écrit et sauvegardé
- [ ] **`get_errors` exécuté et aucune erreur**
- [ ] Tests unitaires existants passent
- [ ] Nouveau comportement validé manuellement
- [ ] Docstrings ajoutées
- [ ] Marqueurs MODULE présents

---

**Détails complétés le:** 10 février 2026
**Prêt pour implémentation:** ✅ OUI
