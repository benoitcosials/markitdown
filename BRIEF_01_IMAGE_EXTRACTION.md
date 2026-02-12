# Brief Technique #01 - Extraction et Sauvegarde des Images PPTX

**Date:** 10 février 2026  
**Fonctionnalité ROADMAP:** #0 - Extraction et Sauvegarde Réelle des Images  
**Statut:** À Implémenter  
**Priorité:** 🔴 CRITIQUE (Correction de bug)  
**Complexité:** Basse-Modérée  
**Estimation:** 5h (Implémentation: 3h + Tests: 2h)

---

## 📋 Résumé Exécutif

### Problème Critique
Actuellement, le convertisseur PPTX génère des **liens Markdown cassés** pour les images. Le code génère `![alt](image.jpg)` sans jamais créer le fichier `image.jpg`.

### Solution
Implémenter une **vraie extraction et sauvegarde des images** sur disque avec :
- ✅ Sauvegarde automatique dans dossier `images/`
- ✅ Nommage cohérent : `slide{N}_image{M}.{ext}`
- ✅ Gestion dossiers personnalisés
- ✅ Déduplication optionnelle (hash MD5)

### Fonctionnalités Existantes à Préserver
- ✅ **Descriptions LLM** : Déjà implémenté via `llm_caption()` - description placée dans alt text
- ✅ **Mode Base64** : Déjà implémenté via `keep_data_uris=True` - **MUST** rester intact

**Impact:** Rendre les images réellement utilisables (corriger les liens cassés).

---

## 🎯 Objectifs Fonctionnels

### Objectif Principal
Extraire les images des présentations PPTX et les sauvegarder dans un dossier `images/` avec des liens Markdown corrects.

**Ce qui existe déjà ✅:**
- Détection des images (via `python-pptx`)
- Descriptions LLM via `llm_caption()` (placées dans alt text)
- Mode Base64 via `keep_data_uris=True`
- Extraction du blob binaire (`shape.image.blob`)

**Ce qui doit être implémenté ⚠️:**
- Sauvegarde réelle des images sur disque
- Création automatique du dossier `images/`
- Nommage cohérent (`slide{N}_image{M}.{ext}`)
- Gestion dossier personnalisé (`image_dir`)
- Déduplication optionnelle (hash MD5)
- Détection automatique des extensions

---

## 📝 Cas d'Usage

### Use Case 1 : Conversion Standard (Mode par défaut)
```
Input:  presentation.pptx (avec 3 images)
Output: 
  - output.md (Markdown avec liens relatifs)
  - images/
    ├── slide1_image0.png
    ├── slide2_image0.jpg
    └── slide3_image0.gif

Exemple Markdown généré:
![Company Logo](images/slide1_image0.png)
![Sales Chart](images/slide2_image0.jpg)
```

**Comportement:**
- Dossier `images/` créé automatiquement
- Images sauvegardées avec noms logiques
- Extensions préservées depuis fichier original

### Use Case 2 : Dossier Personnalisé
```
Input:  presentation.pptx
Option: image_dir="assets/img"
Output:
  - output.md
  - assets/
    └── img/
        ├── slide1_image0.png
        └── slide2_image0.jpg

Markdown:
![Logo](assets/img/slide1_image0.png)
```

### Use Case 3 : Descriptions LLM ✅ **DÉJÀ IMPLÉMENTÉ**
```
Input:  presentation.pptx (avec images)
Option: llm_client=openai_client, llm_model="gpt-4o"
Output:
  - output.md (avec descriptions LLM dans alt text)
  - images/
    ├── slide1_image0.png
    └── slide2_image0.jpg
    
Exemple Markdown:
![AI-generated: "A bar chart showing Q1-Q4 sales growth with peak in Q4 at 89%"](images/slide1_image0.png)
```

**Status:** Cette fonctionnalité **existe déjà** via `_llm_caption.py`. La fonction `llm_caption()`:
- Encode l'image en base64
- Appelle l'API OpenAI avec le prompt configuré
- La description est insérée dans l'attribut `alt` de l'image Markdown

**Action requise:** **VÉRIFIER** la compatibilité avec le nouveau système de sauvegarde (aucun changement nécessaire normalement).

### Use Case 4 : Mode Base64 (Existant - À Préserver)
```
Input:  presentation.pptx
Option: keep_data_uris=True
Output:
  - output.md (Markdown avec base64 embarqué)
  - images/ (non créé)

Markdown:
![Logo](data:image/png;base64,iVBORw0KGgoAAAANS...)
```

**Important:** Ce mode est **déjà implémenté et fonctionnel**. Il **DOIT** rester intact et compatible avec les nouvelles fonctionnalités.

### Use Case 5 : Déduplication
```
Input:  presentation.pptx (logo répété sur 5 slides)
Option: deduplicate_images=True
Output:
  - images/
    └── slide1_image0.png (sauvegardé une seule fois)

Markdown (tous les slides):
![Logo](images/slide1_image0.png)  ← même chemin
![Logo](images/slide1_image0.png)  ← même chemin
![Logo](images/slide1_image0.png)  ← même chemin
```

**Mécanisme:** Hash MD5 du blob binaire pour identifier les doublons.

### Use Case 6 : Mode Legacy (Désactiver Extraction)
```
Input:  presentation.pptx
Option: output_images=False
Output:
  - output.md (Markdown avec liens cassés - DÉPRÉCIÉ)
  - images/ (non créé)

Markdown:
![Logo](MyLogo.jpg)  ← fichier n'existe pas!
```

**Note:** Mode déprécié, génère un warning.

---

## 🔧 Spécifications Techniques

### Paramètres de Configuration

| Paramètre | Type | Défaut | Description | Status |
|-----------|------|--------|---|---|
| `output_images` | bool | `True` | Activer sauvegarde des images | À implémenter |
| `image_dir` | str | `"images"` | Dossier de destination relatif au Markdown | À implémenter |
| `keep_data_uris` | bool | `False` | Encoder en base64 au lieu de fichiers | ✅ **Existant** |
| `deduplicate_images` | bool | `False` | Dédupliquer les images identiques | À implémenter |
| `image_naming_scheme` | str | `"slide"` | Format naming: `"slide"` (seul supporté) | À implémenter |
| `llm_client` | object | `None` | Client LLM pour descriptions (OpenAI) | ✅ **Existant** |
| `llm_model` | str | `None` | Modèle LLM (ex: gpt-4o, gpt-4-turbo) | ✅ **Existant** |
| `llm_prompt` | str | (défaut) | Prompt custom pour descriptions LLM | ✅ **Existant** |

### Nommage des Images

**Convention:** `slide{N}_image{M}.{ext}`

Exemples:
- `slide1_image0.png` ← Premier slide, première image
- `slide1_image1.jpg` ← Premier slide, deuxième image
- `slide2_image0.gif` ← Deuxième slide, première image

Où:
- `{N}` = numéro du slide (1-indexed)
- `{M}` = numéro séquentiel d'image dans le slide (0-indexed)
- `{ext}` = extension du fichier original

### Extensions des Fichiers

**Résolution par ordre de priorité:**
1. `shape.image.filename` (si disponible) → extraire extension
2. `shape.image.content_type` (MIME type) → mapper vers extension
3. `.png` (fallback par défaut)

**Mapping MIME → Extension:**
```python
mime_to_ext = {
    'image/png': '.png',
    'image/jpeg': '.jpg',
    'image/gif': '.gif',
    'image/bmp': '.bmp',
    'image/webp': '.webp',
    'image/svg+xml': '.svg',
    'image/tiff': '.tiff',
}
```

### Chemins dans le Markdown

**Format:** Chemins relatifs uniquement
```markdown
![Image](images/slide1_image0.png)  ← ✅ Correct
![Image](./images/slide1_image0.png) ← ✅ Accepté
![Image](/absolute/path/images/slide1_image0.png) ← ❌ Interdit
```

### Déduplication

**Algorithme:**
1. Calculer `hash = md5(shape.image.blob)`
2. Vérifier si `hash` existe dans `self._image_hashes`
3. Si oui → réutiliser chemin existant
4. Si non → sauvegarder nouveau fichier, stocker hash

**Bénéfices:**
- Économie d'espace disque
- Logos répétés sauvegardés une seule fois
- Liens Markdown pointent vers même fichier

---

## 🏗️ Architecture de l'Implémentation

### Principes Directeurs ⚠️

1. **Respect de la structure existante**
   - ✅ Conserver classe `PptxConverter` actuelle
   - ✅ Utiliser patterns existants (`_method_name`)
   - ❌ Ne pas modifier signatures publiques

2. **Approche modulaire**
   - ✅ Marqueurs `# --- MODULE: ... ---` pour identifier ajouts
   - ✅ Code facile à désactiver/tester
   - ✅ Faciliter révision par équipe Microsoft

3. **Gestion des dépendances**
   - ✅ **Aucune nouvelle dépendance externe**
   - ✅ Utiliser uniquement :
     - `hashlib` (standard library)
     - `os`, `io`, `re` (standard library)
     - `python-pptx` (déjà requis)

4. **Backward compatibility**
   - ✅ Mode Base64 (`keep_data_uris`) **STRICTEMENT préservé**
   - ✅ Nouvelles options opt-in (défaut compatible)

### Fichier à Modifier

**Fichier:** `packages/markitdown/src/markitdown/converters/_pptx_converter.py`

### Modifications Détaillées

#### 1. Ajout Import (ligne ~5)
```python
import hashlib  # Pour déduplication MD5 (standard library)
```

#### 2. Modification `__init__` (ligne ~38)
```python
def __init__(self):
    super().__init__()
    self._html_converter = HtmlConverter()
    # --- MODULE: Image Management ---
    self._image_hashes = {}  # Déduplication d'images
    # --- END MODULE ---
```

#### 3. Modification `convert()` - Configuration (ligne ~80)
```python
# --- MODULE: Image Management - Configuration ---
image_dir = kwargs.get("image_dir", "images")
output_images = kwargs.get("output_images", True)
deduplicate_images = kwargs.get("deduplicate_images", False)
self._image_hashes = {}  # Reset pour chaque conversion
# --- END MODULE ---
```

#### 4. Nouvelle Méthode `_get_image_extension()`
```python
# --- MODULE: Image Management ---
def _get_image_extension(self, filename, content_type):
    """
    Détermine l'extension du fichier image.
    
    Args:
        filename: Nom original du fichier (peut être None)
        content_type: MIME type (peut être None)
    
    Returns:
        str: Extension avec le point (ex: '.png')
    """
    # Essayer depuis filename
    if filename:
        ext = os.path.splitext(filename)[1]
        if ext and ext != '.':
            return ext
    
    # Mapping MIME → extension
    mime_to_ext = {
        'image/png': '.png',
        'image/jpeg': '.jpg',
        'image/gif': '.gif',
        'image/bmp': '.bmp',
        'image/webp': '.webp',
        'image/svg+xml': '.svg',
        'image/tiff': '.tiff',
    }
    
    # Essayer depuis MIME type
    if content_type:
        ext = mime_to_ext.get(content_type.lower())
        if ext:
            return ext
    
    # Fallback
    return '.png'
# --- END MODULE ---
```

#### 5. Nouvelle Méthode `_save_image()`
```python
# --- MODULE: Image Management ---
def _save_image(self, shape, slide_num, image_count, 
                image_dir, deduplicate_images):
    """
    Sauvegarde une image sur disque.
    
    Args:
        shape: Shape PPTX contenant l'image
        slide_num: Numéro du slide (1-indexed)
        image_count: Compteur d'images dans le slide (0-indexed)
        image_dir: Dossier de destination
        deduplicate_images: Activer déduplication MD5
    
    Returns:
        tuple: (image_path, was_deduplicated)
    """
    blob = shape.image.blob
    filename = shape.image.filename
    content_type = shape.image.content_type
    
    # Déduplication optionnelle
    if deduplicate_images:
        image_hash = hashlib.md5(blob).hexdigest()
        if image_hash in self._image_hashes:
            return self._image_hashes[image_hash], True
    
    # Déterminer extension
    ext = self._get_image_extension(filename, content_type)
    
    # Générer nom et chemin
    image_filename = f"slide{slide_num}_image{image_count}{ext}"
    image_path = os.path.join(image_dir, image_filename)
    
    # Créer dossier
    os.makedirs(image_dir, exist_ok=True)
    
    # Sauvegarder fichier
    with open(image_path, 'wb') as f:
        f.write(blob)
    
    # Stocker pour déduplication
    if deduplicate_images:
        self._image_hashes[image_hash] = image_path
    
    return image_path, False
# --- END MODULE ---
```

#### 6. Modification `get_shape_content()` - Images (ligne ~100)
```python
if self._is_picture(shape):
    # ... CODE EXISTANT extraction alt_text (NE PAS MODIFIER) ...
    
    # --- MODULE: Configuration ---
    output_images = kwargs.get("output_images", True)
    image_dir = kwargs.get("image_dir", "images")
    keep_data_uris = kwargs.get("keep_data_uris", False)
    deduplicate_images = kwargs.get("deduplicate_images", False)
    # --- END MODULE ---
    
    # ⚠️ MODE BASE64 - NE PAS MODIFIER (EXISTANT)
    if keep_data_uris:
        # CODE EXISTANT - PRÉSERVER
        blob = shape.image.blob
        content_type = shape.image.content_type or "image/png"
        b64_string = base64.b64encode(blob).decode("utf-8")
        md_content += f"\n![{alt_text}](data:{content_type};base64,{b64_string})\n"
    
    # --- MODULE: File Extraction (NOUVEAU) ---
    elif output_images:
        image_path, deduplicated = self._save_image(
            shape, slide_num, image_count, image_dir, deduplicate_images
        )
        md_content += f"\n![{alt_text}]({image_path})\n"
        
        if not deduplicated:
            image_count += 1
    # --- END MODULE ---
    
    # ⚠️ MODE LEGACY (DÉPRÉCIÉ)
    else:
        filename = re.sub(r"\W", "", shape.name) + ".jpg"
        md_content += "\n![" + alt_text + "](" + filename + ")\n"
        # TODO: Ajouter warning de déprécation
```

---

## 🧪 Tests

### Test 1 : Images Sauvegardées (Standard)
**Input:** PPTX avec 2 images PNG  
**Expected:**
```
✅ Dossier images/ créé
✅ images/slide1_image0.png existe
✅ images/slide2_image0.png existe
✅ Markdown contient liens corrects
```

### Test 2 : Dossier Personnalisé
**Input:** PPTX avec 1 image  
**Option:** `image_dir="assets/img"`  
**Expected:**
```
✅ Dossier assets/img/ créé
✅ assets/img/slide1_image0.png existe
✅ Markdown: ![...](assets/img/slide1_image0.png)
```

### Test 3 : Déduplication
**Input:** PPTX avec logo identique sur 3 slides  
**Option:** `deduplicate_images=True`  
**Expected:**
```
✅ UN SEUL fichier sauvegardé: images/slide1_image0.png
✅ Markdown (3 occurrences): ![...](images/slide1_image0.png)
```

### Test 4 : Mode Base64 (Régression)
**Input:** PPTX avec 1 image  
**Option:** `keep_data_uris=True`  
**Expected:**
```
✅ Aucun dossier créé
✅ Markdown contient data:image/png;base64,...
✅ Même comportement qu'avant (régression test)
```

### Test 5 : Extensions Multiples
**Input:** PPTX avec PNG, JPEG, GIF  
**Expected:**
```
✅ images/slide1_image0.png
✅ images/slide2_image0.jpg
✅ images/slide3_image0.gif
✅ Extensions correctes préservées
```

### Test 6 : LLM Descriptions (Régression)
**Input:** PPTX avec 1 image  
**Option:** `llm_client=..., llm_model="gpt-4o"`  
**Expected:**
```
✅ Image sauvegardée
✅ Alt text contient description LLM
✅ Markdown: ![AI-generated desc](images/slide1_image0.png)
```

### Test 7 : PPTX Sans Images
**Input:** PPTX sans images  
**Expected:**
```
✅ Aucun dossier créé
✅ Markdown généré sans erreur
```

---

## 📋 Plan d'Implémentation

### Sprint 1 : Implémentation Base (2h)
- [ ] Ajouter `import hashlib`
- [ ] Modifier `__init__` (ajouter `_image_hashes`)
- [ ] Implémenter `_get_image_extension()`
- [ ] Implémenter `_save_image()`
- [ ] Modifier `get_shape_content()` avec blocs modulaires
- [ ] Tests manuels (Use Case 1, 2)

### Sprint 2 : Vérification LLM + Déduplication (1h)
- [ ] Tester avec `llm_client` configuré (Use Case 3)
- [ ] Implémenter déduplication MD5 (Use Case 5)
- [ ] Vérifier mode Base64 intact (Use Case 4)

### Sprint 3 : Tests & Documentation (2h)
- [ ] Tests 1-7 validés
- [ ] Tests edge cases
- [ ] Vérifier aucune régression
- [ ] Documentation inline

**Estimation Totale:** 5h

---

## ✅ Conditions d'Acceptation

- [ ] Images réellement sauvegardées sur disque
- [ ] Liens Markdown valides (non cassés)
- [ ] Extensions correctes préservées
- [ ] Dossier `images/` créé automatiquement
- [ ] Option `image_dir` personnalisable
- [ ] Déduplication optionnelle fonctionne
- [ ] **Mode Base64 reste INTACT** (aucune régression)
- [ ] Descriptions LLM continuent de fonctionner
- [ ] Tests 1-7 passent tous
- [ ] Aucune nouvelle dépendance externe
- [ ] **⚠️ MCP mis à jour** (nouveaux paramètres exposés)

---

## ⚠️ Intégration MCP - CRITIQUE POUR EFFICACITÉ

**Important :** L'extraction d'images n'est utile que si le MCP peut créer les fichiers au bon endroit dans le repo de l'utilisateur.

### Le Problème

Actuellement, quand un agent utilise le MCP :
```
@markitdown-ia Convert file:///C:/Users/.../presentation.pptx
```

Le MCP exécute avec le **répertoire courant = dossier temp VS Code Copilot**, pas le répertoire du fichier PPTX.

**Résultat :**
- ❌ Images créées dans `C:\Users\ledoee\AppData\Roaming\Code\User\workspaceStorage\...`
- ❌ Pas dans le repo où le fichier PPTX se trouve
- ❌ Agent doit créer des scripts manuels pour extraire les images (friction !)

### La Solution - Modifier le MCP

**Nouveau comportement requis :**
```python
@mcp.tool()
async def convert_to_markdown(
    uri: str,
    output_images: bool = True,
    image_dir: str = "images",
    skip_background_images: bool = True,
    skip_icon_images: bool = True,
    deduplicate_images: bool = False,
) -> str:
    """Convert resource to markdown with images in correct location.
    
    CRITICAL: When uri is file:// path, images must be created relative to 
    that file's directory, not the current working directory.
    
    Args:
        uri: Resource URI (file://, http://, https://, data:)
        output_images: Extract images
        image_dir: Relative to FILE's directory (not CWD!)
        ...other params...
    """
    
    # Extract file directory from URI if applicable
    base_dir = None
    if uri.startswith("file://"):
        from pathlib import Path
        file_path = Path(uri.replace("file:///", "").replace("%20", " "))
        base_dir = str(file_path.parent)  # ← KEY: Use file's directory
    
    # Adjust image_dir to be relative to base_dir
    if base_dir and output_images:
        image_dir = os.path.join(base_dir, image_dir)
    
    kwargs = {
        "output_images": output_images,
        "image_dir": image_dir,  # ← Now absolute, pointing to correct location
        "skip_background_images": skip_background_images,
        "skip_icon_images": skip_icon_images,
        "deduplicate_images": deduplicate_images,
    }
    return MarkItDown().convert_uri(uri, **kwargs).markdown
```

### Validation MCP Integration

**Tester que :**
1. ✅ URI `file:///C:/Repos/Bancaire_Documentation/.../file.pptx`
2. ✅ MCP crée images dans `C:/Repos/Bancaire_Documentation/.../images/`
3. ✅ **PAS** dans le répertoire temp VS Code
4. ✅ Markdown contient `![](images/slide1_image0.png)`
5. ✅ Fichier existe à ce chemin dans le repo

**Sans cette correction, agents devront créer des scripts de support !**

---

## ⚠️ Mise à Jour MCP Obligatoire

**✅ IMPLÉMENTÉE** - Commit [6c7ee07](https://github.com/benoitcosials/markitdown/commit/6c7ee07)

**CRITIQUE** : Les paramètres **SONT MAINTENANT** exposés dans le MCP avec détection automatique du répertoire.

**Fichier modifié :** `packages/markitdown-mcp/src/markitdown_mcp/__main__.py`

### 1. ✅ Paramètres Exposés

```python
@mcp.tool()
async def convert_to_markdown(
    uri: str,
    output_images: bool = True,
    image_dir: str = "images",
    skip_background_images: bool = True,
    skip_icon_images: bool = True,
    deduplicate_images: bool = False,
) -> str:
    """Convert resource to markdown with image extraction.
    
    Args:
        uri: Resource URI (file://, http://, https://, data:)
        output_images: Extract and save images (default: True)
        image_dir: Directory for images relative to source file (default: "images")
        skip_background_images: Skip PPTX backgrounds (default: True)
        skip_icon_images: Extract photos only, skip icons (default: True)
        deduplicate_images: Deduplicate identical images (default: False)
    """
```

### 2. ✅ Base Directory Detection Implémentée

La logique CRITIQUE est maintenant en place :

```python
# CRITICAL FIX: Resolve image_dir relative to source file for file:// URIs
adjusted_image_dir = image_dir

if uri.startswith("file://") and output_images:
    try:
        # Parse file:// URI to extract OS path
        file_path_str = urllib.parse.unquote(uri.replace("file:///", ""))
        source_file = Path(file_path_str)
        
        # Get parent directory of source file
        base_dir = str(source_file.parent)
        
        # Resolve image_dir relative to source file's directory
        adjusted_image_dir = os.path.join(base_dir, image_dir)
    except (ValueError, OSError) as e:
        # If URI parsing fails, fall back to default image_dir
        print(f"Warning: Failed to parse file URI for directory context: {e}")
        adjusted_image_dir = image_dir
```

### 3. ✅ Test et Validation

```bash
# MCP est déjà installé et mise à jour
pip install -e packages/markitdown-mcp

# Test avec file:// URI
@markitdown-ia Convert file:///C:/Repos/test/document.pptx

# Vérifier: images créées dans C:/Repos/test/images/ (CORRECT -ENFIN!)
```

**✅ L'INTÉGRATION MCP EST MAINTENANT COMPLÈTE !**

**Impact**: 
- Images créées relative au fichier PPTX ✅
- Agent workflow seamless sans scripts manuels ✅
- Tous les BRIEFs peuvent utiliser le MCP ✅


---

## 📚 Références

- **Fichier:** [`_pptx_converter.py`](packages/markitdown/src/markitdown/converters/_pptx_converter.py)
- **Module LLM:** [`_llm_caption.py`](packages/markitdown/src/markitdown/converters/_llm_caption.py)
- **Dépendance:** `python-pptx` (existante)
- **ROADMAP:** Fonctionnalité #0

---

**Prochaine étape:** Voir [BRIEF_02_CHART_DESCRIPTIONS.md](BRIEF_02_CHART_DESCRIPTIONS.md) pour Tier 2 (descriptions contextuelles des charts).
