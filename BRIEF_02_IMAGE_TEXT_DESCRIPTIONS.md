# Brief Technique #02 - Descriptions Textuelles LLM pour Images

**Date:** 10 février 2026  
**Fonctionnalité ROADMAP:** Nouvelle - Remplacement Images par Descriptions Textuelles  
**Statut:** À Implémenter  
**Priorité:** 🟡 MOYENNE (Enhancement)  
**Complexité:** Modérée  
**Estimation:** 4h (Implémentation: 3h + Tests: 1h)  
**Dépendances:** BRIEF_01 (extraction d'images) + `llm_client` configuré

---

## 📋 Résumé Exécutif

### Vision
Améliorer la représentation des **images PPTX** pour les LLMs en **remplaçant l'image par une description contextuelle textuelle** générée par LLM.

### Approche
Au lieu d'afficher `![Image](images/photo.png)`, générer un bloc de texte contextuel :
```
```image-description
Company Office Building - Exterior View

Modern glass and steel building with corporate branding visible on facade.
Surrounded by landscaped gardens with pathway leading to main entrance.
Clear blue sky suggests professional photography for marketing materials.
```
```

### Bénéfices
- ✅ Meilleure compréhension par les LLMs (texte vs image)
- ✅ Accessibilité améliorée
- ✅ Tokens économisés (texte < base64)
- ✅ Fallback gracieux (affiche image si LLM absent)
- ✅ Applicable à **tous types d'images** (photos, logos, screenshots, etc.)

### ⚠️ Note Importante
Cette fonctionnalité génère des **descriptions textuelles LLM** pour **toutes les images**, pas uniquement les charts.
Les **charts statistiques** ont leur propre traitement spécifique (voir [BRIEF_03_CHART_ASCII_ART.md](BRIEF_03_CHART_ASCII_ART.md)).

---

## 🎯 Objectifs Fonctionnels

### Objectif Principal
Détecter les images dans les présentations PPTX et les remplacer par des descriptions contextuelles LLM (titre + max 10 lignes) pour améliorer la lisibilité LLM.

**Scope:** Toutes les images (photos, logos, screenshots, etc.), **SAUF** les charts statistiques qui ont leur propre traitement (BRIEF_03).

### Prérequis
- ✅ BRIEF_01 implémenté (sauvegarde d'images fonctionne)
- ✅ `llm_client` et `llm_model` configurés
- ✅ `_llm_caption()` disponible (déjà existant)

### Nouveaux Éléments
- ⚠️ Paramètre `image_text_description=True`
- ⚠️ Prompt LLM spécifique pour images
- ⚠️ Format bloc ```image-description
- ⚠️ Logique de remplacement (pas d'affichage image)
- ⚠️ Exclusion des charts (traités séparément dans BRIEF_03)

---

## 📝 Cas d'Usage

### Use Case 1 : Image avec Description Contextuelle
```
Input:  presentation.pptx (avec 1 photo de bureau)
Option: image_text_description=True, llm_client=..., llm_model="gpt-4o"

Output:
  - output.md
  - images/slide1_image0.jpg (sauvegardé mais non affiché)

Exemple Markdown:
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
- Image détectée via `_is_picture(shape)`
- **Exclusion** : Si `shape.has_chart == True` → ignorer (traité dans BRIEF_03)
- Image sauvegardée (via BRIEF_01)
- Image **NON affichée** dans Markdown
- Bloc texte généré par LLM (titre + description 10 lignes max)

### Use Case 2 : Image Sans LLM (Fallback)
```
Input:  presentation.pptx (avec 1 image)
Option: image_text_description=True (SANS llm_client)

Output:
  - output.md
  - images/slide1_image0.png

Markdown:
![Company Logo](images/slide1_image0.png)
```

**Comportement:**
- `llm_client` absent → pas de description générée
- Fallback : affiche l'image normalement (comme BRIEF_01)
- Comportement graceful (pas d'erreur)

### Use Case 3 : Mix Images Normales + Charts
```
Input:  presentation.pptx (1 photo + 1 chart)
Option: image_text_description=True, llm_client=..., llm_model="..."

Output:
  - output.md
  - images/slide1_image0.jpg (photo)
  - images/slide2_image0.png (chart)

Markdown:
```image-description
Company Photo: Exterior Building View
...
```

![Sales Chart](images/slide2_image0.png)  ← Chart affiché normalement
```

**Comportement:**
- Photos normales → remplacées par blocs texte (BRIEF_02)
- **Charts (`shape.has_chart`) → affichés comme images** (exclus du traitement BRIEF_02)
- Charts ont leur propre traitement dans BRIEF_03

### Use Case 4 : Chart avec Prompt Personnalisé
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
| `image_text_description` | bool | `False` | Remplacer images par descriptions textuelles LLM | À implémenter |

**Note:** Génère des **descriptions textuelles LLM** pour **toutes les images**, sauf charts (voir BRIEF_03).

### Format de Sortie

**Bloc de Code Markdown:**
```markdown
```chart-description
[Ligne 1: Titre du chart]

[Lignes 2-11: Description contextuelle LLM]
[Maximum 10 lignes de texte]
```
```

**Exemple:**
```markdown
```chart-description
Pie Chart: Market Share Distribution

The pie chart displays the market share distribution across four major competitors.
Company A leads with 42%, followed by Company B at 28%, Company C at 19%, and
Company D at 11%. This indicates a moderately concentrated market with clear
leadership but room for competitive dynamics.
```
```

### Prompt LLM

**Prompt par Défaut:**
```python
image_prompt = (
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

1. **Réutiliser l'existant**
   - ✅ Utiliser `llm_caption()` existant
   - ✅ Pas de nouvelles méthodes nécessaires
   - ✅ Intégration dans `get_shape_content()`

2. **Modularité**
   - ✅ Marqueurs `# --- MODULE: Chart Contextual Description ---`
   - ✅ Code facile à désactiver

3. **Fallback gracieux**
   - ✅ Si `llm_client` absent → affiche image normale
   - ✅ Si génération échoue → affiche image normale

### Fichier à Modifier

**Fichier:** `packages/markitdown/src/markitdown/converters/_pptx_converter.py`

### Modifications Détaillées

#### Modification `get_shape_content()` - Détection Images

**Localisation:** Ligne ~150 (APRÈS le bloc d'extraction d'images de BRIEF_01)

```python
# --- MODULE: Image Text Description (BRIEF_02) ---
if self._is_picture(shape) and not shape.has_chart and kwargs.get("image_text_description", False):
    """
    Images détectées : remplacer image par description contextuelle LLM.
    Nécessite llm_client et llm_model configurés.
    Fallback : affiche image normalement si LLM absent.
    
    IMPORTANT: Exclut les charts (shape.has_chart == True) qui sont traités dans BRIEF_03.
    """
    
    llm_client = kwargs.get("llm_client")
    llm_model = kwargs.get("llm_model")
    output_images = kwargs.get("output_images", True)
    image_dir = kwargs.get("image_dir", "images")
    deduplicate_images = kwargs.get("deduplicate_images", False)
    
    if llm_client and llm_model:
        # Sauvegarder l'image (mais ne pas l'afficher)
        if output_images:
            image_path, _ = self._save_image(
                shape, slide_num, image_count, image_dir, deduplicate_images
            )
            image_count += 1  # Incrémenter même si non affiché
        
        # Générer description contextuelle via LLM
        chart_prompt = kwargs.get("llm_prompt") or (
            "Provide a title for this chart on the first line, "
            "then a contextual description in maximum 10 lines explaining "
            "what the chart shows, key insights, and trends."
        )
        
        try:
            # Préparer stream pour llm_caption
            image_stream = io.BytesIO(shape.image.blob)
            image_stream_info = StreamInfo(
                mimetype=shape.image.content_type,
                extension=os.path.splitext(shape.image.filename or "")[1],
            )
            
            # Appeler llm_caption existant avec prompt spécifique
            chart_description = llm_caption(
                image_stream,
                image_stream_info,
                client=llm_client,
                model=llm_model,
                prompt=chart_prompt
            )
            
            if chart_description:
                # REMPLACER l'image par un bloc de code
                md_content += f"\n```chart-description\n{chart_description}\n```\n"
            else:
                # Fallback : afficher image normalement
                md_content += f"\n![{alt_text}]({image_path})\n"
        
        except Exception as e:
            # Fallback en cas d'erreur : afficher image normalement
            if output_images and image_path:
                md_content += f"\n![{alt_text}]({image_path})\n"
            else:
                # Dernier fallback : lien cassé (mode legacy)
                filename = re.sub(r"\W", "", shape.name) + ".jpg"
                md_content += f"\n![{alt_text}]({filename})\n"
    
    else:
        # Pas de LLM : afficher image normalement (fallback)
        if output_images:
            image_path, deduplicated = self._save_image(
                shape, slide_num, image_count, image_dir, deduplicate_images
            )
            md_content += f"\n![{alt_text}]({image_path})\n"
            if not deduplicated:
                image_count += 1
        else:
            # Legacy mode
            filename = re.sub(r"\W", "", shape.name) + ".jpg"
            md_content += f"\n![{alt_text}]({filename})\n"

# Si ce n'est PAS un chart, continuer avec logique BRIEF_01 normale
elif self._is_picture(shape):
    # Logique BRIEF_01 ici (extraction normale d'images)
    ...
# --- END MODULE ---
```

**Note:** Ce bloc doit être placé **AVANT** le bloc d'extraction normale d'images de BRIEF_01, pour intercepter les charts en premier.

---

## 🧪 Tests

### Test 1 : Chart avec Description LLM
**Input:** PPTX avec 1 bar chart  
**Option:** `chart_text_description=True, llm_client=..., llm_model="gpt-4o"`  
**Expected:**
```
✅ images/slide1_image0.png sauvegardé
✅ Image NON affichée dans Markdown
✅ Bloc chart-description présent
✅ Contient titre (ligne 1) + description (max 10 lignes)
```

### Test 2 : Chart Sans LLM (Fallback)
**Input:** PPTX avec 1 chart  
**Option:** `chart_text_description=True` (SANS llm_client)  
**Expected:**
```
✅ images/slide1_image0.png sauvegardé
✅ Image AFFICHÉE normalement : ![...](images/slide1_image0.png)
✅ Aucun bloc chart-description
✅ Pas d'erreur
```

### Test 3 : Mix Images Normales + Charts
**Input:** PPTX avec 1 photo + 1 chart  
**Option:** `chart_text_description=True, llm_client=..., llm_model="..."`  
**Expected:**
```
✅ Photo : ![...](images/slide1_image0.jpg) (affichée)
✅ Chart : ```chart-description\n...\n``` (bloc texte)
✅ Comportements différents selon has_chart
```

### Test 4 : Prompt Personnalisé
**Input:** PPTX avec chart  
**Option:** `chart_text_description=True, llm_model="...", llm_prompt="Focus on trends"`  
**Expected:**
```
✅ Description générée avec orientation "trends"
✅ Bloc chart-description reflète le prompt custom
```

### Test 5 : Erreur LLM (Fallback)
**Input:** PPTX avec chart  
**Option:** `chart_text_description=True, llm_client=invalid`  
**Expected:**
```
✅ Exception capturée
✅ Fallback : image affichée normalement
✅ Pas de crash
```

### Test 6 : Chart + Mode Base64
**Input:** PPTX avec chart  
**Option:** `chart_text_description=True, keep_data_uris=True, llm_client=..., llm_model="..."`  
**Expected:**
```
✅ Aucun fichier créé
✅ Bloc chart-description généré (base64 ignoré pour charts)
OU
✅ Image base64 affichée (selon préférence design)
```

**Note:** Décision design à valider : chart_text_description + keep_data_uris → lequel prioritaire ?

---

## 📋 Plan d'Implémentation

### Sprint 1 : Détection Charts (1.5h)
- [ ] Ajouter détection `shape.has_chart` dans `get_shape_content()`
- [ ] Tester détection sur différents types de charts
- [ ] Vérifier interaction avec `_is_picture()`

### Sprint 2 : Génération Description (3h)
- [ ] Implémenter prompt LLM contextuel
- [ ] Appeler `llm_caption()` avec prompt chart-specific
- [ ] Générer bloc ```chart-description
- [ ] Remplacer affichage image par bloc texte
- [ ] Tests génération (Use Case 1)

### Sprint 3 : Fallbacks & Tests (1.5h)
- [ ] Implémenter fallback sans LLM (Use Case 2)
- [ ] Implémenter fallback erreur LLM (Test 5)
- [ ] Tests 1-6 validés
- [ ] Vérifier mix images/charts (Test 3)
- [ ] Edge cases

**Estimation Totale:** 6h

---

## ✅ Conditions d'Acceptation

- [ ] Charts détectés via `shape.has_chart`
- [ ] LLM génère description contextuelle (titre + max 10 lignes)
- [ ] Bloc ```chart-description dans Markdown
- [ ] Image sauvegardée mais NON affichée
- [ ] Fallback : affiche image si LLM absent
- [ ] Fallback : affiche image si erreur LLM
- [ ] Prompt personnalisable via `llm_prompt`
- [ ] Mix images normales + charts fonctionne
- [ ] Tests 1-6 passent tous
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

## ⚠️ Mise à Jour MCP Obligatoire

**CRITIQUE** : Après implémentation, les nouveaux paramètres **DOIVENT** être exposés dans le MCP.

**Fichier à modifier :** `packages/markitdown-mcp/src/markitdown_mcp/__main__.py`

**Paramètres à ajouter pour BRIEF_02 :**
- `generate_image_descriptions: bool = False` - Activer descriptions textuelles
- `image_description_prompt: str = None` - Prompt personnalisé (optionnel)

**Action requise :**
1. Ajouter les paramètres à `convert_to_markdown()`
2. Documenter dans la docstring
3. Tester : `pip install -e packages/markitdown-mcp`

**Référence :** Voir commit e3dcb49 (BRIEF_01) pour exemple d'implémentation MCP.

---

## 📚 Références

- **Fichier:** [`_pptx_converter.py`](packages/markitdown/src/markitdown/converters/_pptx_converter.py)
- **Module LLM:** [`_llm_caption.py`](packages/markitdown/src/markitdown/converters/_llm_caption.py)
- **ROADMAP:** Fonctionnalité #6
- **Prérequis:** [BRIEF_01_IMAGE_EXTRACTION.md](BRIEF_01_IMAGE_EXTRACTION.md)

---

## 🎯 Questions Ouvertes

1. **Interaction `chart_text_description` + `keep_data_uris`** :
   - Option A : `chart_text_description` prioritaire (génère bloc texte)
   - Option B : `keep_data_uris` prioritaire (génère base64)
   - **Recommandation:** Option A (cohérent avec objectif BRIEF_02)

2. **Format du bloc** :
   - Actuel : ```chart-description
   - Alternative : ```image-description (réutiliser format BRIEF_01 LLM)
   - **Recommandation:** Garder ```chart-description (distingue charts vs images)

3. **Limite 10 lignes** :
   - Hardcodé dans prompt
   - Alternative : paramètre `max_description_lines`
   - **Recommandation:** Hardcodé pour simplicité Tier 1

---

**Prochaine étape:** Voir [MON_ROADMAP.md](MON_ROADMAP.md) pour vision globale et planification des autres fonctionnalités.
