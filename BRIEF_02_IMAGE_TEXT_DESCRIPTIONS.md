# Brief Technique #02 - Descriptions Textuelles LLM pour Images

**Date:** 10 février 2026 (Mis à jour: 20 février 2026)  
**Fonctionnalité ROADMAP:** Nouvelle - Descriptions LLM Adaptatives pour Images  
**Statut:** 🚧 En Cours  
**Priorité:** 🟡 MOYENNE (Enhancement)  
**Complexité:** Modérée  
**Estimation:** 8h (Implémentation: 6h + Tests: 2h)  
**Dépendances:** `llm_client` configuré, BRIEF_01 ✅ complété

---

## 📋 Résumé Exécutif

### Vision
Améliorer la représentation des **images PPTX** pour les LLMs via descriptions textuelles générées par LLM, avec **deux modes adaptatifs** selon la configuration.

### Deux Modes d'Utilisation

#### Mode 1 : Alt Text Amélioré (avec extraction `output_images=True`)
Générer un **alt text en une phrase** si non existant pour enrichir l'affichage des images extraites :
```markdown
![Modern corporate office building with glass facade and landscaped entrance](images/slide1_image0.jpg)
```

#### Mode 2 : Description Complète (sans extraction `output_images=False`)
Générer un **bloc de description contextuelle** détaillé pour remplacer l'image :
```markdown
```image-description
Company Office Building - Exterior View

Modern glass and steel building with corporate branding visible on facade.
Surrounded by landscaped gardens with pathway leading to main entrance.
Clear blue sky suggests professional photography for marketing materials.
```
```

### Bénéfices
- ✅ Mode adaptatif selon contexte utilisateur (avec/sans fichiers)
- ✅ Alt text enrichi automatiquement pour accessibilité
- ✅ Mode "pure text" pour environnements contraints (tokens, stockage)
- ✅ Meilleure compréhension par les LLMs dans les deux modes
- ✅ Fallback gracieux (affiche image/nom si LLM absent)

### ⚠️ Note Importante
Cette fonctionnalité génère des **descriptions textuelles LLM** pour **toutes les images**, pas uniquement les charts.
Les **charts statistiques** ont leur propre traitement spécifique (voir [BRIEF_03_CHART_ASCII_ART.md](BRIEF_03_CHART_ASCII_ART.md)).

---

## 🎯 Objectifs Fonctionnels

### Objectif Principal
Détecter les images dans les présentations PPTX et générer des descriptions LLM **adaptées au mode d'utilisation** :

- **Mode 1 (avec extraction)** : Générer alt text en une phrase si absent/vide
- **Mode 2 (sans extraction)** : Générer description contextuelle complète (titre + max 10 lignes)

**Scope:** Toutes les images (photos, logos, screenshots, etc.), **SAUF** les charts statistiques qui ont leur propre traitement (BRIEF_03).

### Prérequis
- ✅ `llm_client` et `llm_model` configurés
- ✅ `_llm_caption()` disponible (déjà existant)
- ⚠️ BRIEF_01 implémenté (optionnel, requis pour Mode 1)

### Nouveaux Éléments
- ⚠️ Paramètre `image_text_description=True`
- ⚠️ **Deux prompts LLM** selon `output_images`
  - Prompt court (1 phrase) pour Mode 1
  - Prompt détaillé (titre + 10 lignes) pour Mode 2
- ⚠️ Logique adaptative selon `output_images`
- ⚠️ Format bloc ```image-description pour Mode 2
- ⚠️ Exclusion des charts (traités séparément dans BRIEF_03)

---

## 📝 Cas d'Usage

### Use Case 1 : Mode 1 - Alt Text Amélioré (avec extraction)
```
Input:  presentation.pptx (avec 1 photo de bureau sans alt text)
Option: 
  - output_images=True
  - image_text_description=True
  - llm_client=...
  - llm_model="gpt-4o"

Output:
  - output.md
  - images/slide1_image0.jpg

Markdown:
![Modern corporate office building with glass facade and landscaped entrance](images/slide1_image0.jpg)
```

**Comportement:**
- Image détectée via `_is_picture(shape)`
- **Exclusion** : Si `shape.has_chart == True` → ignorer (traité dans BRIEF_03)
- Image sauvegardée (BRIEF_01)
- Alt text PowerPoint récupéré
- **Si alt text vide/absent** → Génération LLM d'une phrase concise
- Image **affichée** avec alt text enrichi

### Use Case 2 : Mode 2 - Description Complète (sans extraction)
```
Input:  presentation.pptx (avec 1 photo de bureau)
Option: 
  - output_images=False
  - image_text_description=True
  - llm_client=...
  - llm_model="gpt-4o"

Output:
  - output.md (SANS dossier images/)

Markdown:
```image-description
Office Team Meeting Photo

Professional photograph showing diverse team of 6 people seated around
conference table reviewing documents. Modern office setting with natural
lighting from large windows. Collaborative atmosphere evident from body
language and engaged expressions. Likely used for HR or company culture
materials.
```
```
```

**Comportement:**
- Image détectée, **NON sauvegardée** (output_images=False)
- **Exclusion** : Si `shape.has_chart == True` → ignorer
- Génération LLM description complète (titre + max 10 lignes)
- Bloc ```image-description dans Markdown
- Aucun fichier image créé

### Use Case 3 : Sans LLM (Fallbacks)

**Mode 1 (avec extraction) :**
```
Option: output_images=True, image_text_description=True (SANS llm_client)

Markdown:
![Picture 1](images/slide1_image0.png)  ← Fallback au nom du shape
```

**Mode 2 (sans extraction) :**
```
Option: output_images=False, image_text_description=True (SANS llm_client)

Markdown:
**Image:** Picture 1  ← Fallback texte simple (évite liens cassés)
```

**Comportement:**
- `llm_client` absent → pas de génération LLM
- Mode 1 : Affiche image avec nom du shape comme alt text
- Mode 2 : Affiche nom du shape en texte simple (évite `![]()`cassé)
- Comportement graceful (pas d'erreur)

### Use Case 4 : Mix Images Normales + Charts
```
Input:  presentation.pptx (1 photo + 1 chart)
Option: output_images=False, image_text_description=True, llm_client=...

Markdown:
```image-description
Company Photo: Exterior Building View
Modern glass and steel architecture...
```

**Chart:** Sales Performance Q4 2025  ← Chart exclu (pas de description)
```

**Comportement:**
- Photos normales → descriptions complètes (BRIEF_02 Mode 2)
- **Charts (`shape.has_chart`) → nom du shape** (traités dans BRIEF_03)
- Séparation claire entre images et charts
```
Input:  presentation.pptx (avec chart)
Option: 
  - chart_text_description=True
  - llm_client=...
  - llm_model="gpt-4o"
  - llm_prompt="Analyze this chart focusing on trends and anomalies"

Output:
  Bloc chart-description avec analyse orientée tendances/anomalies
```

---

## 🔧 Spécifications Techniques

### Nouveau Paramètre

| Paramètre | Type | Défaut | Description | Status |
|-----------|------|--------|---|---|
| `image_text_description` | bool | `False` | Activer génération LLM de descriptions pour images | À implémenter |

**Note:** Comportement **adaptatif** selon `output_images` :
- **Mode 1** (`output_images=True`) : Génère alt text en une phrase si absent/vide
- **Mode 2** (`output_images=False`) : Génère description complète (titre + max 10 lignes)

### Formats de Sortie

#### Mode 1 : Alt Text Enrichi
```markdown
![<description LLM en une phrase>](images/slide1_image0.jpg)
```

#### Mode 2 : Bloc de Description
```markdown
```image-description
<Ligne 1: Titre de l'image>

<Lignes 2-11: Description contextuelle LLM>
<Maximum 10 lignes de texte>
```
```

### Prompts LLM Adaptatifs

#### Prompt Mode 1 (Alt Text Court)
```python
# Génère une phrase concise pour alt text
alt_text_prompt = (
    "Describe this image in a single concise sentence suitable for alt text. "
    "Focus on the main subject and key visual elements. "
    "Maximum 100 characters."
)
```

**Exemple sortie** :
```
"Modern corporate office building with glass facade and landscaped entrance"
```

#### Prompt Mode 2 (Description Complète)
```python
# Génère titre + description détaillée
full_description_prompt = (
    "Provide a title for this image on the first line, "
    "then a contextual description in maximum 10 lines explaining "
    "what the image shows, key details, and likely purpose. "
    "Use descriptive language suitable for text-only consumption."
)
```

**Exemple sortie** :
```
Office Team Meeting Photo

Professional photograph showing diverse team of 6 people seated around
conference table reviewing documents. Modern office setting with natural
lighting from large windows. Collaborative atmosphere evident from body
language and engaged expressions. Likely used for HR or company culture
materials.
```
    "Provide a title for this image on the first line, "
    "then a contextual description in maximum 10 lines explaining "
    "what the image shows, key details, and likely purpose."
)
```

**Prompt Personnalisé:**
```python
# Utilisateur peut fournir via kwargs
llm_prompt="Your custom prompt for chart analysis"
```

### Détection des Images

**Mécanisme:**
```python
if self._is_picture(shape) and not shape.has_chart:
    # Ce shape est une IMAGE normale (pas un chart)
    # Appliquer traitement BRIEF_02
    ...
```

**Note:** Les **charts** (`shape.has_chart == True`) sont **exclus** de ce traitement et gérés séparément dans BRIEF_03.

---

## 🏗️ Architecture de l'Implémentation

### Principes

1. **Comportement Adaptatif**
   - ✅ Mode détecté automatiquement via `output_images`
   - ✅ Prompts différents selon mode
   - ✅ Sortie adaptée au contexte

2. **Réutiliser l'existant**
   - ✅ Utiliser `llm_caption()` existant
   - ✅ Pas de nouvelles méthodes nécessaires
   - ✅ Intégration dans `get_shape_content()`

3. **Fallback gracieux**
   - ✅ Si `llm_client` absent → comportements par défaut
   - ✅ Si génération échoue → comportements par défaut

### Fichier à Modifier

**Fichier:** `packages/markitdown/src/markitdown/converters/_pptx_converter.py`

### Modifications Détaillées

#### Modification `get_shape_content()` - Détection Images

**Localisation:** Ligne ~150 (logique d'images existante)

```python
# --- MODULE: Image Text Description (BRIEF_02) ---
if self._is_picture(shape) and not shape.has_chart:
    """
    Traitement des images selon configuration :
    - Mode 1 (output_images=True) : Alt text enrichi si absent
    - Mode 2 (output_images=False) : Description complète
    
    IMPORTANT: Exclut les charts (shape.has_chart == True) traités dans BRIEF_03.
    """
    
    llm_client = kwargs.get("llm_client")
    llm_model = kwargs.get("llm_model")
    output_images = kwargs.get("output_images", True)
    image_text_description = kwargs.get("image_text_description", False)
    image_dir = kwargs.get("image_dir", "images")
    
    # Récupérer alt text existant (PowerPoint ou LLM précédent)
    alt_text = ""
    try:
        alt_text = shape._element._nvXxPr.cNvPr.attrib.get("descr", "")
    except Exception:
        pass
    
    # Appliquer logique selon mode
    if image_text_description and llm_client and llm_model:
        
        # Préparer stream pour LLM
        image_stream = io.BytesIO(shape.image.blob)
        image_stream_info = StreamInfo(
            mimetype=shape.image.content_type,
            extension=os.path.splitext(shape.image.filename or "")[1],
        )
        
        # MODE 1 : Alt Text Enrichi (avec extraction)
        if output_images:
            # Sauvegarder l'image (BRIEF_01)
            image_path, deduplicated = self._save_image(
                shape, slide_num, image_count, image_dir, 
                kwargs.get("deduplicate_images", False)
            )
            if not deduplicated:
                image_count += 1
            
            # Générer alt text SEULEMENT si absent/vide
            if not alt_text or not alt_text.strip():
                short_prompt = kwargs.get("llm_prompt") or (
                    "Describe this image in a single concise sentence "
                    "suitable for alt text. Focus on the main subject and "
                    "key visual elements. Maximum 100 characters."
                )
                
                try:
                    alt_text = llm_caption(
                        image_stream, image_stream_info,
                        client=llm_client, model=llm_model, prompt=short_prompt
                    )
                    # Nettoyer (enlever newlines, limiter à 100 chars)
                    alt_text = re.sub(r"\s+", " ", alt_text).strip()[:100]
                except Exception:
                    # Fallback au nom du shape
                    alt_text = shape.name or "Image"
            
            # Afficher image avec alt text enrichi
            # Escape special chars
            alt_text = re.sub(r"[\[\]]", " ", alt_text).strip()
            md_content += f"\n![{alt_text}]({image_path})\n"
        
        # MODE 2 : Description Complète (sans extraction)
        else:
            full_prompt = kwargs.get("llm_prompt") or (
                "Provide a title for this image on the first line, "
                "then a contextual description in maximum 10 lines explaining "
                "what the image shows, key details, and likely purpose. "
                "Use descriptive language suitable for text-only consumption."
            )
            
            try:
                description = llm_caption(
                    image_stream, image_stream_info,
                    client=llm_client, model=llm_model, prompt=full_prompt
                )
                
                # Afficher en bloc description
                md_content += f"\n```image-description\n{description}\n```\n"
            except Exception:
                # Fallback : afficher nom du shape en texte
                shape_name = shape.name or "Image"
                md_content += f"\n**Image:** {shape_name}\n"
    
    else:
        # Pas de LLM ou feature désactivée → comportement par défaut
        if output_images:
            # BRIEF_01 : Extraction normale
            image_path, deduplicated = self._save_image(
                shape, slide_num, image_count, image_dir,
                kwargs.get("deduplicate_images", False)
            )
            if not deduplicated:
                image_count += 1
            
            # Utiliser alt text existant ou fallback vers shape.name
            final_alt = "\n".join(filter(None, ["", alt_text])) or shape.name
            final_alt = re.sub(r"[\r\n\[\]]", " ", final_alt).strip()
            md_content += f"\n![{final_alt}]({image_path})\n"
        else:
            # Pas d'extraction : afficher nom du shape (évite lien cassé)
            shape_name = shape.name or "Image"
            md_content += f"\n**Image:** {shape_name}\n"
# --- END MODULE ---
```

**Note:** Ce bloc remplace TOUTE la logique d'images dans `get_shape_content()`, interceptant les images AVANT le traitement BRIEF_01.

---

## 🧪 Tests

### Test 1 : Mode 1 - Alt Text Enrichi (avec LLM)
**Input:** PPTX avec 2 images (l'une avec alt texte, l'autre sans)  
**Option:** `image_text_description=True, output_images=True, llm_client=..., llm_model="gpt-4o"`  
**Expected:**
```
✅ images/slide1_image0.png et image1.png sauvegardés
✅ Image AVEC alt text existant : ![Alt text PowerPoint](images/slide1_image0.png)
✅ Image SANS alt text : ![LLM generated alt text](images/slide1_image1.png)
✅ Alt text LLM max 100 chars, 1 phrase
✅ Aucun bloc image-description
```

### Test 2 : Mode 2 - Description Complète (avec LLM)
**Input:** PPTX avec 2 images  
**Option:** `image_text_description=True, output_images=False, llm_client=..., llm_model="gpt-4o"`  
**Expected:**
```
✅ Aucun fichier image créé
✅ Blocs image-description présents (titre + 10 lignes)
✅ Aucune syntaxe ![...](...)
✅ Descriptions détaillées pour chaque image
```

### Test 3 : Mode 1 Sans LLM (Fallback)
**Input:** PPTX avec image sans alt text  
**Option:** `image_text_description=True, output_images=True` (SANS llm_client)  
**Expected:**
```
✅ images/slide1_image0.png sauvegardé
✅ Image affichée : ![Picture 1](images/slide1_image0.png)
✅ Alt text fallback vers shape.name (BRIEF_01)
✅ Pas d'erreur
```

### Test 4 : Mode 2 Sans LLM (Fallback)
**Input:** PPTX avec image  
**Option:** `image_text_description=True, output_images=False` (SANS llm_client)  
**Expected:**
```
✅ Aucun fichier créé
✅ Texte simple : **Image:** Picture 1
✅ Aucun bloc image-description
✅ Pas d'erreur
```

### Test 5 : Mix Images + Charts
**Input:** PPTX avec 1 photo + 1 chart  
**Option:** `image_text_description=True, output_images=True, llm_client=..., llm_model="..."`  
**Expected:**
```
✅ Photo : ![LLM alt text](images/slide1_image0.jpg) (enrichi si pas alt text)
✅ Chart : Image normale (pas de traitement BRIEF_02)
✅ Charts exclus car gérés dans BRIEF_03
```

### Test 6 : Prompt Personnalisé Mode 1
**Input:** PPTX avec image sans alt text  
**Option:** `image_text_description=True, output_images=True, llm_client=..., llm_prompt="Focus on colors"`  
**Expected:**
```
✅ Alt text généré mentionne les couleurs
✅ Respecte la contrainte 100 chars max
```

### Test 7 : Prompt Personnalisé Mode 2
**Input:** PPTX avec image  
**Option:** `image_text_description=True, output_images=False, llm_client=..., llm_prompt="Technical description"`  
**Expected:**
```
✅ Description technique détaillée
✅ Bloc image-description présent
✅ Max 10 lignes respecté
```

### Test 8 : Erreur LLM (Fallback)
**Input:** PPTX avec image  
**Option:** `image_text_description=True, output_images=True, llm_client=invalid`  
**Expected:**
```
✅ Exception capturée
✅ Mode 1 : image affichée avec shape.name
✅ Mode 2 : texte simple **Image:** shapename
✅ Pas de crash
```

---

## 📋 Plan d'Implémentation

### Sprint 1 : Logique Adaptative (2h)
- [ ] Ajouter détection mode via `output_images`
- [ ] Implémenter branche conditionnelle Mode 1 vs Mode 2
- [ ] Gérer récupération alt text existant (PowerPoint)
- [ ] Tester détection sur différents types d'images

### Sprint 2 : Mode 1 - Alt Text Enrichi (2h)
- [ ] Implémenter prompt court (100 chars)
- [ ] Appeler `llm_caption()` SEULEMENT si alt text absent/vide
- [ ] Nettoyer résultat LLM (newlines, limite chars)
- [ ] Générer syntaxe markdown avec alt text enrichi
- [ ] Tests 1, 3, 6, 8 validés

### Sprint 3 : Mode 2 - Description Complète (2h)
- [ ] Implémenter prompt long (titre + 10 lignes)
- [ ] Appeler `llm_caption()` pour toutes les images
- [ ] Générer blocs ```image-description
- [ ] Gérer fallback sans LLM (texte simple)
- [ ] Tests 2, 4, 7 validés

### Sprint 4 : Fallbacks & Tests Finaux (2h)
- [ ] Implémenter fallback sans LLM pour les deux modes
- [ ] Implémenter fallback erreur LLM (Test 8)
- [ ] Vérifier exclusion des charts (Test 5)
- [ ] Tous tests 1-8 passent
- [ ] Edge cases et régression BRIEF_01

**Estimation Totale:** 8h

---

## ✅ Conditions d'Acceptation

### Mode 1 : Alt Text Enrichi (output_images=True)
- [ ] Alt text existant PowerPoint préservé (pas de génération LLM)
- [ ] Alt text absent → génération LLM (1 phrase, max 100 chars)
- [ ] Images sauvegardées et affichées : `![alt text](images/...)`
- [ ] Prompt court spécifique au mode 1

### Mode 2 : Description Complète (output_images=False)
- [ ] Blocs ```image-description générés pour toutes les images
- [ ] Descriptions contiennent titre + max 10 lignes
- [ ] Aucun fichier image créé
- [ ] Prompt long spécifique au mode 2

### Comportements Communs
- [ ] Charts exclus (`shape.has_chart == True`)
- [ ] Fallback Mode 1 sans LLM : shape.name comme alt text
- [ ] Fallback Mode 2 sans LLM : texte simple `**Image:** shapename`
- [ ] Fallback erreur LLM : comportements par défaut
- [ ] Prompt personnalisable via `llm_prompt`
- [ ] Tests 1-8 passent tous
- [ ] BRIEF_01 non affecté (régression test)

---

## 🔄 Dépendances

### Prérequis
- ✅ **BRIEF_01** implémenté et validé
- ✅ `_llm_caption.py` fonctionnel
- ✅ `llm_client` et `llm_model` configurés par utilisateur

### Impact
- ⚠️ Modifie `get_shape_content()` (même fichier que BRIEF_01)
- ✅ Pas de nouvelles dépendances externes
- ✅ Réutilise infrastructure LLM existante

---

## ⚠️ Intégration MCP - CRITIQUE POUR EFFICACITÉ

**Important :** Les descriptions LLM adaptatives nécessitent une intégration MCP correcte pour gérer les deux modes.

### Le Problème de Base

**Hérité de BRIEF_01 :** Les images doivent être créées relatives au répertoire du fichier PPTX, pas au répertoire temp VS Code.

**Problème supplémentaire pour BRIEF_02 :**
- Le LLM choisi doit être accessible via le MCP
- Mode 1 : Alt text LLM uniquement si absent (nécessite vérification)
- Mode 2 : Descriptions complètes pour toutes les images
- Les clés API doivent être disponibles dans l'environnement MCP

### Solution - Étendre le MCP

**Ajouter les paramètres BRIEF_02 au MCP :**

```python
@mcp.tool()
async def convert_to_markdown(
    uri: str,
    output_images: bool = True,
    image_dir: str = "images",
    skip_background_images: bool = True,
    skip_icon_images: bool = True,
    deduplicate_images: bool = False,
    # BRIEF_02 new params:
    image_text_description: bool = False,           # ← NEW (opt-in)
    llm_model: str = "gpt-4o",                      # ← NEW
    llm_prompt: str = None,                         # ← NEW (custom prompt)
) -> str:
    """Convert resource with adaptive LLM image descriptions.
    
    Args:
        image_text_description: Enable LLM descriptions (default: False)
        llm_model: LLM model for descriptions
        llm_prompt: Custom prompt override
        
    Behavior:
        - output_images=True + image_text_description=True:
          Enrich missing alt text with 1 phrase (max 100 chars)
        - output_images=False + image_text_description=True:
          Generate full description blocks (title + 10 lines)
    """
    kwargs = {
        "output_images": output_images,
        "image_dir": image_dir,
        "skip_background_images": skip_background_images,
        "skip_icon_images": skip_icon_images,
        "deduplicate_images": deduplicate_images,
        "image_text_description": image_text_description,
        "llm_model": llm_model,
        "llm_prompt": llm_prompt,
    }
    
    # llm_client configured at server level (API keys)
    return MarkItDown().convert_uri(uri, **kwargs).markdown
```

### Validation MCP Integration

**✅ Foundation de BRIEF_01 maintenant stable** - Commit 6c7ee07
- Images créées au BON endroit automatiquement
- Répertoire source détecté depuis file:// URI
- Agent workflow seamless sans scripts manuels

**Tester Mode 1 (Alt Text Enrichi) :**
1. ✅ Images extraites au bon endroit (BRIEF_01 - RÉSOLU)
2. ✅ Alt text existants PowerPoint préservés
3. ✅ Alt text absents → génération LLM (max 100 chars)
4. ✅ Images affichées avec alt text enrichi
5. ✅ Performance acceptable (LLM appelé uniquement si nécessaire)

**Tester Mode 2 (Description Complète) :**
1. ✅ Aucun fichier image créé
2. ✅ Blocs ```image-description présents
3. ✅ Descriptions contiennent titre + 10 lignes max
4. ✅ Performance acceptable (1 appel LLM par image)

**Sans cette correction, agents devront configurer LLM manuellement !**

---

## ⚠️ Mise à Jour MCP Obligatoire

**CRITIQUE** : Après implémentation, les nouveaux paramètres **DOIVENT** être exposés dans le MCP.

**Fichier à modifier :** `packages/markitdown-mcp/src/markitdown_mcp/__main__.py`

**Actions requises :**

### 1. Exposer les Paramètres BRIEF_02

```python
@mcp.tool()
async def convert_to_markdown(
    uri: str,
    output_images: bool = True,
    image_dir: str = "images",
    skip_background_images: bool = True,
    skip_icon_images: bool = True,
    deduplicate_images: bool = False,
    image_text_description: bool = False,  # ← NEW (opt-in)
    llm_model: str = "gpt-4o",             # ← NEW
    llm_prompt: str = None,                # ← NEW
) -> str:
    """Convert resource to markdown with adaptive LLM image descriptions."""
    kwargs = {
        "output_images": output_images,
        "image_dir": image_dir,
        "skip_background_images": skip_background_images,
        "skip_icon_images": skip_icon_images,
        "deduplicate_images": deduplicate_images,
        "image_text_description": image_text_description,
        "llm_model": llm_model,
        "llm_prompt": llm_prompt,
    }
    return MarkItDown().convert_uri(uri, **kwargs).markdown
```

### 2. Test et Validation

```bash
# Reinstall MCP
pip install -e packages/markitdown-mcp

# Test Mode 1 (alt text enrichment)
@markitdown-ia Convert file:///C:/test/doc.pptx image_text_description=true output_images=true

# Test Mode 2 (full descriptions)
@markitdown-ia Convert file:///C:/test/doc.pptx image_text_description=true output_images=false

# Verify:
# - Mode 1: Images with enriched alt text
# - Mode 2: image-description blocks present
# - Charts excluded (shape.has_chart)
# - LLM calls successful
```

**Sans cette intégration MCP, les descriptions ne seront PAS accessibles !**

---

## 📚 Références

- **Fichier:** [`_pptx_converter.py`](packages/markitdown/src/markitdown/converters/_pptx_converter.py)
- **Module LLM:** [`_llm_caption.py`](packages/markitdown/src/markitdown/converters/_llm_caption.py)
- **ROADMAP:** Fonctionnalité #6
- **Prérequis:** [BRIEF_01_IMAGE_EXTRACTION.md](BRIEF_01_IMAGE_EXTRACTION.md)

---

## 🎯 Questions Ouvertes

1. **Interaction Mode 1 + `keep_data_uris`** :
   - Option A : Ignorer `keep_data_uris` si `image_text_description=True` (extraction prioritaire)
   - Option B : Respecter `keep_data_uris` (base64 + alt text enrichi)
   - **Recommandation:** Option A (cohérent avec logique Mode 1)

2. **Mode 2 avec Charts** :
   - Actuel : Charts exclus (gérés dans BRIEF_03)
   - Alternative : Mode 2 génère aussi descriptions pour charts
   - **Recommandation:** Garder exclusion (évite duplication avec BRIEF_03)

3. **Limite 10 lignes Mode 2** :
   - Hardcodé dans prompt
   - Alternative : paramètre `max_description_lines`
   - **Recommandation:** Hardcodé pour simplicité Tier 1

4. **Limite 100 chars Mode 1** :
   - Hardcodé dans code (`.strip()[:100]`)
   - Alternative : paramètre `max_alt_text_length`
   - **Recommandation:** Hardcodé (standard accessibilité ~100-125 chars)

---

**Prochaine étape:** Voir [MON_ROADMAP.md](MON_ROADMAP.md) pour vision globale et planification des autres fonctionnalités.
