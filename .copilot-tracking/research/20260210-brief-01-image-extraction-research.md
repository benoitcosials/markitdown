# Recherche BRIEF_01 - Extraction et Sauvegarde des Images PPTX

**Date:** 20260210
**Brief:** BRIEF_01_IMAGE_EXTRACTION
**Phase:** Recherche
**Statut:** ✅ Complété

---

## 🔍 Analyse du Code Existant

### Fichier Cible
**Path:** `packages/markitdown/src/markitdown/converters/_pptx_converter.py`
**Lignes:** 265 lignes total
**Classe:** `PptxConverter(DocumentConverter)`

### Patterns Identifiés

#### 1. Gestion Actuelle des Images (lignes 92-154)

**Code existant dans `get_shape_content()`:**
```python
if self._is_picture(shape):
    # Descriptions LLM (déjà implémenté)
    llm_client = kwargs.get("llm_client")
    llm_model = kwargs.get("llm_model")
    if llm_client is not None and llm_model is not None:
        # Appel à llm_caption() pour générer description
        llm_description = llm_caption(...)
    
    # Alt text depuis métadonnées PPTX
    alt_text = shape._element._nvXxPr.cNvPr.attrib.get("descr", "")
    
    # Mode Base64 (fonctionnel)
    if kwargs.get("keep_data_uris", False):
        blob = shape.image.blob
        content_type = shape.image.content_type or "image/png"
        b64_string = base64.b64encode(blob).decode("utf-8")
        md_content += f"\n![{alt_text}](data:{content_type};base64,{b64_string})\n"
    else:
        # ❌ PROBLÈME ICI: génère lien cassé
        filename = re.sub(r"\W", "", shape.name) + ".jpg"
        md_content += "\n![" + alt_text + "](" + filename + ")\n"
        # Aucune sauvegarde du fichier!
```

**Problème identifié:**
- Ligne ~154: Génère `![alt](MyImage.jpg)` sans créer le fichier
- Aucune gestion de dossier de sortie
- Extension hardcodée `.jpg` (ignorer l'extension réelle)

#### 2. Dépendances Disponibles

**Imports actuels:**
```python
import sys
import base64
import os
import io
import re
import html
from typing import BinaryIO, Any
from operator import attrgetter
```

**✅ Disponible:** `os`, `io`, `re`, `base64`
**⚠️ À ajouter:** `hashlib` (standard library - déduplication)

#### 3. Structure de Données Images

**Propriétés accessibles via `python-pptx`:**
```python
shape.image.blob          # bytes - données binaires de l'image
shape.image.filename      # str | None - nom original (ex: "logo.png")
shape.image.content_type  # str - MIME type (ex: "image/png")
shape.name                # str - nom du shape (ex: "Picture 1")
```

#### 4. Patterns de Nommage Observés

**Variables existantes:**
- `slide_num` : compteur de slides (1-indexed) - ligne ~82
- `shape.name` : utilisé pour nommage actuel

**Pattern proposé:** `slide{N}_image{M}.{ext}`
- Compatible avec convention existante
- Facile à tracer vers slide source
- Prévisible pour utilisateurs

### Fonctionnalités à Préserver

#### 1. Mode Base64 (`keep_data_uris=True`)
**Status:** ✅ Fonctionnel - NE PAS TOUCHER
**Code:** Lignes 147-151
```python
if kwargs.get("keep_data_uris", False):
    blob = shape.image.blob
    content_type = shape.image.content_type or "image/png"
    b64_string = base64.b64encode(blob).decode("utf-8")
    md_content += f"\n![{alt_text}](data:{content_type};base64,{b64_string})\n"
```

#### 2. Descriptions LLM
**Status:** ✅ Fonctionnel via `_llm_caption.py`
**Code:** Lignes 100-128
- Appelle `llm_caption()` avec image stream
- Description insérée dans `alt_text`
- **Action:** Vérifier compatibilité (normalement OK)

#### 3. Extraction Alt Text
**Status:** ✅ Fonctionnel
**Code:** Lignes 131-136
- Extraction depuis métadonnées PPTX
- Combinaison avec description LLM

---

## 🏗️ Architecture de la Solution

### Approche Modulaire

**Principe:** Utiliser marqueurs `# --- MODULE: ... ---` pour identifier nouveau code

**Avantages:**
- Facile à réviser pour équipe Microsoft
- Possibilité de désactiver module
- Maintient structure existante
- Facilite tests unitaires

### Modifications Requises

#### 1. Ajout Import (ligne ~5)
```python
import hashlib  # Pour déduplication MD5
```

#### 2. Modification `__init__` (ligne ~38)
```python
def __init__(self):
    super().__init__()
    self._html_converter = HtmlConverter()
    # --- MODULE: Image Management ---
    self._image_hashes = {}  # Déduplication
    # --- END MODULE ---
```

#### 3. Nouvelle Méthode: `_get_image_extension()`

**Position:** Après `_is_table()` (ligne ~220)
**Responsabilité:** Déterminer extension fichier image

**Logique:**
1. Essai: extraire depuis `filename`
2. Essai: mapper depuis `content_type` (MIME)
3. Fallback: `.png`

**Mapping MIME → Extension:**
```python
{
    'image/png': '.png',
    'image/jpeg': '.jpg',
    'image/gif': '.gif',
    'image/bmp': '.bmp',
    'image/webp': '.webp',
    'image/svg+xml': '.svg',
    'image/tiff': '.tiff',
}
```

#### 4. Nouvelle Méthode: `_save_image()`

**Position:** Après `_get_image_extension()`
**Responsabilité:** Sauvegarder image sur disque

**Paramètres:**
- `shape`: Shape PPTX
- `slide_num`: Numéro slide (1-indexed)
- `image_count`: Compteur images dans slide (0-indexed)
- `image_dir`: Dossier destination
- `deduplicate_images`: Flag déduplication

**Algorithme:**
1. Si `deduplicate_images`:
   - Calculer MD5 de `blob`
   - Vérifier si hash existe → retourner chemin existant
2. Obtenir extension via `_get_image_extension()`
3. Générer nom: `slide{slide_num}_image{image_count}{ext}`
4. Créer dossier: `os.makedirs(image_dir, exist_ok=True)`
5. Sauvegarder: `open(path, 'wb').write(blob)`
6. Stocker hash si déduplication active
7. Retourner `(image_path, was_deduplicated)`

#### 5. Modification `convert()`

**Position:** Après création `presentation` (ligne ~80)
**Action:** Initialiser configuration

```python
# --- MODULE: Image Management - Configuration ---
image_dir = kwargs.get("image_dir", "images")
output_images = kwargs.get("output_images", True)
deduplicate_images = kwargs.get("deduplicate_images", False)
self._image_hashes = {}  # Reset par conversion
# --- END MODULE ---
```

#### 6. Modification `get_shape_content()` - Images

**Position:** Bloc images (ligne ~92-154)
**Action:** Ajouter logique de sauvegarde

**Structure proposée:**
```python
if self._is_picture(shape):
    # [CODE EXISTANT] Descriptions LLM + alt text
    # ...
    
    # [MODE BASE64 - PRÉSERVER]
    if kwargs.get("keep_data_uris", False):
        # Code existant ligne 147-151
        pass
    
    # [NOUVEAU] Mode extraction fichier
    elif kwargs.get("output_images", True):
        image_path, deduplicated = self._save_image(
            shape, slide_num, image_count, 
            kwargs.get("image_dir", "images"),
            kwargs.get("deduplicate_images", False)
        )
        md_content += f"\n![{alt_text}]({image_path})\n"
        
        if not deduplicated:
            image_count += 1
    
    # [LEGACY] Mode ancien (déprécié)
    else:
        # Code actuel ligne 153-154
        pass
```

#### 7. Gestion Compteur Images

**Problème:** Besoin de `image_count` par slide
**Solution:** Ajouter compteur dans boucle shapes

**Position:** Ligne ~189 (boucle shapes)
```python
image_count = 0  # Compteur par slide
for shape in sorted_shapes:
    get_shape_content(shape, **kwargs)
    # image_count incrémenté dans get_shape_content
```

---

## 📊 Analyse des Impacts

### Compatibilité Backward

| Fonctionnalité | Impact | Action |
|----------------|--------|--------|
| Mode Base64 (`keep_data_uris`) | ✅ Aucun | Bloc préservé intact |
| Descriptions LLM (`llm_client`) | ✅ Aucun | Compatible sans changement |
| Alt text métadonnées | ✅ Aucun | Code réutilisé |
| Comportement par défaut | ⚠️ Change | Images maintenant sauvegardées |

**Note:** Nouveau comportement par défaut = sauvegarde fichiers (fix du bug)

### Performance

**Optimisations:**
- Déduplication MD5: évite sauvegardes redondantes
- `os.makedirs(exist_ok=True)`: évite checks si dossier existe
- Hash calculé une fois par image unique

**Overhead estimé:**
- MD5 hashing: ~1ms par image (négligeable)
- I/O disque: dépend de la taille des images

### Tests de Régression Requis

1. **test_module_vectors.py** - Vérifier que tests existants passent
2. Mode Base64 - Valider aucun changement de comportement
3. Descriptions LLM - Valider compatibilité
4. Nouveau mode fichiers - Valider sauvegarde correcte

---

## 🎯 Points d'Attention

### Critiques

1. **⚠️ Ne jamais modifier le bloc Base64**
   - Lignes 147-151 sont INTOUCHABLES
   - Tests de régression obligatoires

2. **⚠️ Gestion compteur `image_count`**
   - Doit être dans scope de `get_shape_content()`
   - Nécessite passage via `nonlocal` ou refactoring paramètres

3. **⚠️ Chemins relatifs uniquement**
   - Générer `images/slide1_image0.png`
   - Jamais de chemins absolus

### Moyens

1. **Extension detection fallback**
   - Toujours prévoir `.png` par défaut
   - Logger warning si extension inconnue?

2. **Gestion d'erreurs I/O**
   - `os.makedirs()` peut échouer (permissions)
   - `open()` peut échouer (disque plein)
   - Try/except appropriés

3. **Validation paths**
   - Sanitize `image_dir` si fourni par utilisateur
   - Éviter directory traversal (`../../../etc/passwd`)

---

## 📝 Conclusion Recherche

### Faisabilité
✅ **HAUTE** - Implémentation straightforward avec patterns existants

### Complexité
🟡 **MODÉRÉE** - Nécessite attention aux détails mais pas de blockers

### Risques
🟢 **BAS** - Approche modulaire minimise risques de régression

### Prochaine Étape
➡️ **Créer Plan d'Implémentation Détaillé**

---

**Recherche complétée le:** 10 février 2026
**Temps estimé:** 1h30
**Prêt pour planification:** ✅ OUI
