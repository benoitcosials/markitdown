# Roadmap - Améliorations du Convertisseur PPTX → Markdown

## � Briefs Techniques

Ce ROADMAP est le **document maître** organisant les améliorations du convertisseur PPTX. Chaque fonctionnalité majeure possède un brief technique détaillé :

| # | Fonctionnalité | Brief | Statut | Priorité |
|---|---|---|---|---|
| 0 | Extraction et Sauvegarde Images | [BRIEF_01_IMAGE_EXTRACTION.md](BRIEF_01_IMAGE_EXTRACTION.md) | 📝 Documenté | 🔴 CRITIQUE |
| 6a | Descriptions Textuelles LLM (Images) | [BRIEF_02_IMAGE_TEXT_DESCRIPTIONS.md](BRIEF_02_IMAGE_TEXT_DESCRIPTIONS.md) | 📝 Documenté | 🟡 MOYENNE |
| 6b | ASCII Art pour Charts Statistiques | [BRIEF_03_CHART_ASCII_ART.md](BRIEF_03_CHART_ASCII_ART.md) | 📝 Documenté | 🟡 MOYENNE |
| 1 | Listes à Puces Structurées | — | ⏳ À documenter | ⭐⭐⭐ |
| 2 | Formatage Texte Riche | — | ⏳ À documenter | ⭐⭐⭐ |
| 3 | Hyperlinks | — | ⏳ À documenter | ⭐⭐⭐ |
| 4 | Formes de Texte (Callouts) | — | ⏳ À documenter | ⭐⭐⭐ |
| 5 | Tableaux Avancés | — | ⏳ À documenter | ⭐⭐ |
| 7 | SmartArt | — | ⏳ À documenter | ⭐⭐ |
| 8 | Métadonnées Slides | — | ⏳ À documenter | ⭐⭐ |
| 9 | Audio/Vidéo Embedded | — | ⏳ À documenter | ⭐ |
| 10 | Hiérarchie Visuelle | — | ⏳ À documenter | ⭐ |

**Légende Statut:**
- 📝 **Documenté** : Brief technique complet disponible
- 🚧 **En cours** : Implémentation en cours
- ✅ **Terminé** : Implémenté et testé
- ⏳ **À documenter** : Pas encore de brief technique

---

## �📊 Analyse du Projet

**MarkItDown** est un utilitaire Python léger pour convertir divers formats de fichiers en Markdown, spécialement conçu pour les LLMs. C'est un projet Microsoft bien structuré qui convertit actuellement : PDF, PowerPoint, Word, Excel, Images, Audio, HTML, ZIP, YouTube, EPubs.

### Architecture
```
markitdown/               → Cœur principal
├── converters/           → Convertisseurs pour chaque format
│   └── _pptx_converter.py
├── converter_utils/      → Utilitaires (docx.math, etc.)
└── __main__.py          → Interface CLI

markitdown-mcp/          → Serveur Model Context Protocol
markitdown-sample-plugin/  → Exemple de plugin
```

---

## 🎯 État Actuel du Convertisseur PPTX

### ✅ Fonctionnalités Existantes

- Titres de slides (h1)
- Texte brut et shapes texte
- **Images** ⚠️ (détection + alt-text/descriptions LLM, MAIS voir limitations)
- Tableaux (convertis via HTML)
- Graphiques (basiques - conversion en tableau)
- Notes de slide
- Shapes groupés (recursif)
- Tri des shapes par position (top, left)

### ❌ Limitations Actuelles

**Critique (Images)** 🔴
- **Images ne sont jamais extraites en fichiers** : Le convertisseur génère des liens Markdown cassés par défaut
  - Mode par défaut : `![alt](image.jpg)` → fichier n'existe jamais
  - Mode `keep_data_uris=True` : Crée du base64 énorme et illisible
  - **Manquant** : Sauvegarde réelle des images dans un dossier `images/`

**Standard**
- Pas de support pour les listes à puces structurées
- Pas de gestion des formes de dessin (shapes)
- Pas de support pour les hyperlinks
- Pas de support pour les animations ou transitions
- Pas de formatage du texte (gras, italique, souligné)
- Pas de positions/hiérarchie explicites
- Pas de support multilingue explicite
- Pas de configuration des options des slides (zoom, ratio)
- Pas de support pour les audio/vidéo embedded

---

## � Analyse Approfondie : Extraction d'Images (Problème Critique)

### Situation Actuelle

Le convertisseur PPTX détecte les images et génère du Markdown, **mais sans réellement extraire les fichiers** :

```python
# Mode par défaut (PROBLÉMATIQUE)
filename = re.sub(r"\W", "", shape.name) + ".jpg"
md_content += "\n![" + alt_text + "](" + filename + ")\n"
# Résultat: ![Image](MyImage.jpg) ← fichier n'existe jamais!
```

```python
# Mode keep_data_uris=True (FONCTIONNEL mais limité)
b64_string = base64.b64encode(blob).decode("utf-8")
md_content += f"\n![{alt_text}](data:{content_type};base64,{b64_string})\n"
# Résultat: ![Image](data:image/png;base64,iVBORw0KGgo...) ← base64 ÉNORME
```

| Mode | Sortie Markdown | État | Utilisabilité |
|------|-----------------|------|---|
| **Défaut** | `![alt](image.jpg)` | ❌ Lien cassé | Inutilisable pour LLM |
| **keep_data_uris=True** | `![alt](data:image/png;base64,...)` | ✅ Fonctionne | Énorme (peut dépasser tokens) |
| **Fichiers séparés** (demandé) | `![alt](images/image.jpg)` | ❌ Pas implémenté | Attendu par les utilisateurs |

### Capacités Réelles des Images

✅ **Fonctionne bien:**
- Détection des images dans les slides
- Extraction du contenu binaire (blob)
- Extraction de l'alt-text défini dans le PPTX
- Génération de descriptions via LLM (OpenAI)

❌ **Fonctionne mal / Manquant:**
- Sauvegarde réelle des fichiers image sur le disque
- Gestion des métadonnées d'images (résolution, format original)
- Génération de chemins logiques (`images/slide1_img1.png`)
- Déduplications des images identiques
- Support des formats autre que ce que python-pptx expose

---

## �🚀 Fonctionnalités Recommandées

### Tier 1 : Impact Élevé, Implémentation Modérée ⭐⭐⭐

**À Faire en Priorité:**

#### 0. **[🔴 URGENT] Extraction et Sauvegarde Réelle des Images** → [BRIEF_01](BRIEF_01_IMAGE_EXTRACTION.md)
- **Impact**: Critique - Les images actuellement génèrent des liens cassés
- **Complexité**: Basse-Modérée
- **Statut**: 📝 **Brief complet disponible**
- **Estimation**: 5h (Implémentation: 3h + Tests: 2h)
- **Fonctionnalités**:
  - ✅ Sauvegarde images sur disque (`images/` par défaut)
  - ✅ Nommage cohérent : `slide{N}_image{M}.{ext}`
  - ✅ Dossier personnalisable (`image_dir`)
  - ✅ Déduplication automatique (hash MD5 obligatoire)
  - ✅ Préservation mode Base64 existant
  - ✅ Compatibilité descriptions LLM existantes
- **Paramètres**:
  - `output_images=True` (défaut)
  - `image_dir="images"` (défaut)
- **Voir:** [BRIEF_01_IMAGE_EXTRACTION.md](BRIEF_01_IMAGE_EXTRACTION.md) pour spécifications complètes

#### 1. Support des Listes à Puces Structurées
- **Impact**: Utilisé dans 80% des slides professionnelles
- **Complexité**: Modérée
- **Implémentation**:
  - Détecter `shape.text_frame` avec paragraphes numérotés/pucés
  - Générer Markdown avec indentation correcte
  - Support de listes imbriquées (`-` et `1.`)
- **Exemple**:
  ```
  - Point 1
    - Point 1.1
    - Point 1.2
  - Point 2
  ```

#### 2. Formatage du Texte Riche (gras, italique, souligné)
- **Impact**: Préservation de la structure du document
- **Complexité**: Basse
- **Implémentation**:
  - Parser `run.font.bold`, `run.font.italic`, `run.font.underline`
  - Générer `**bold**`, `*italic*`, `<u>underline</u>`
  - Gérer les couleurs de texte (optionnel)

#### 3. Support des Hyperlinks
- **Impact**: Navigation et référencement
- **Complexité**: Basse
- **Implémentation**:
  - Extraire `shape.text_frame.paragraphs[i].runs[j].hyperlink`
  - Générer `[text](url)` ou `[text](internal-anchor)`
  - Support des liens internes et externes

#### 4. Gestion des Formes de Texte (Callouts, Bulles)
- **Impact**: Mise en évidence de contenu special
- **Complexité**: Modérée
- **Implémentation**:
  - Détecter `MSO_SHAPE_TYPE` et les formes AutoShape
  - Transformer en blockquote `>` ou section spéciale
  - Exemple: `> Callout text`

---

### Tier 2 : Sélectif, Utile pour Cas Spécifiques ⭐⭐

#### 5. Support des Tableaux Imbriqués et Cellules Fusionnées
- **Impact**: Meilleure représentation des données complexes
- **Complexité**: Modérée-Haute
- **Implémentation**:
  - Améliorer la détection des cellules fusionnées
  - Générer HTML/Markdown plus robuste
  - Support des cellules vides

#### 6. Meilleure Gestion des Graphiques → [BRIEF_02](BRIEF_02_CHART_DESCRIPTIONS.md)
- **Impact**: Meilleure compréhension LLM des données visuelles
- **Complexité**: Modérée
- **Statut**: 📝 **Brief complet disponible**
- **Estimation**: 6h (Implémentation: 4.5h + Tests: 1.5h)
- **Dépendances**: BRIEF_01 + `llm_client` configuré
- **Fonctionnalités**:
  - ✅ Détection charts via `shape.has_chart`
  - ✅ Descriptions contextuelles LLM (titre + 10 lignes max)
  - ✅ Remplacement image par bloc ```chart-description
  - ✅ Fallback gracieux (affiche image si LLM absent)
- **Paramètres**:
  - `chart_ascii_art=True` pour activer
  - `llm_client` + `llm_model` requis
  - `llm_prompt` personnalisable
- **Voir:** [BRIEF_02_CHART_DESCRIPTIONS.md](BRIEF_02_CHART_DESCRIPTIONS.md) pour spécifications complètes

#### 7. Support des Diagrammes SmartArt
- **Impact**: Représentation de hierarchies/processus
- **Complexité**: Haute
- **Implémentation**:
  - Extraire structures SmartArt
  - Générer listes/arbres texte avec indentation

#### 8. Métadonnées des Slides
- **Impact**: Contexte et indexation
- **Complexité**: Basse
- **Implémentation**:
  - Titre du document
  - Auteur, date de création
  - Tags/keywords
  - Nombre de slides
  - Format: Ajouter en YAML frontmatter

---

### Tier 3 : Avancé, Cas Niche ⭐

#### 9. Support Audio/Vidéo Embedded
- **Impact**: Contenu multimedia
- **Complexité**: Haute
- **Implémentation**:
  - Détecter et exporter fichiers media
  - Générer liens ou métadonnées

#### 10. Préservation de la Hiérarchie Visuelle
- **Impact**: Structure document complète
- **Complexité**: Haute
- **Implémentation**:
  - Sections master slide
  - Thème/couleurs (optionnel pour LLM)
  - Background images

---

## 📋 Proposition de Plan d'Implémentation

### Phase 1 : Correction Critique + Fondamentaux (Semaine 1-2)
0. **[CRITIQUE] Sauvegarde réelle des images** → [BRIEF_01](BRIEF_01_IMAGE_EXTRACTION.md) (5h)
1. **Listes à puces structurées** → Impact maximal (à documenter)
2. **Formatage texte riche** → Qualité du Markdown (à documenter)
3. **Tests et validation** → Qualité assurance

### Phase 2 : Extensions Courantes (Semaine 3-4)
3. **Hyperlinks** → Interaction (à documenter)
4. **Callouts/Formes texte** → Mise en évidence (à documenter)
6. **Descriptions contextuelles charts** → [BRIEF_02](BRIEF_02_CHART_DESCRIPTIONS.md) (6h)

### Phase 3 : Premium (Semaine 5+)
5. **Tableaux avancés** → Cellules fusionnées (à documenter)
7. **SmartArt** → Diagrammes (à documenter)
8. **Métadonnées** → Indexation/contexte (à documenter)
9. **Multimédia** → Contenu riche (à documenter)

---

## ✨ Avantages Attendus

- ✅ **Couverture**: Augmentation de 60% → 95% des éléments PPTX
- ✅ **Qualité Markdown**: Texte beaucoup mieux structuré
- ✅ **Utilité LLM**: Meilleure compréhension par les modèles
- ✅ **Interopérabilité**: Supports des normes Markdown courantes
- ✅ **Maintenabilité**: Code modulaire et testable

---

## 🔧 Notes Techniques

### Dépendances Existantes
- `python-pptx` : Accès à la structure PPTX
- `openai` (optionnel) : Descriptions LLM d'images
- Tests: `pytest`, `hatch`

### Points d'Extension
- Convertisseur HTML pour réutilisation ([_html_converter.py](packages/markitdown/src/markitdown/converters/_html_converter.py))
- Paramètres kwargs pour options custom
- Support des plugins externe (markitdown-mcp, sample-plugin)

### Guide d'Implémentation : Sauvegarde des Images

**Fichier à modifier:** [_pptx_converter.py](packages/markitdown/src/markitdown/converters/_pptx_converter.py)

**Code actuel problématique (lignes 137-145):**
```python
if kwargs.get("keep_data_uris", False):
    # ... base64 encoding ...
else:
    filename = re.sub(r"\W", "", shape.name) + ".jpg"  # ❌ Lien cassé
    md_content += "\n![" + alt_text + "](" + filename + ")\n"
```

**Modification suggérée:**
```python
# Ajouter avant la conversion
image_count = 0
image_dir = kwargs.get("image_dir", "images")
output_images = kwargs.get("output_images", True)

# Dans la boucle de conversion d'images:
if self._is_picture(shape):
    # ... extraire alt_text comme maintenant ...
    
    if output_images and not kwargs.get("keep_data_uris", False):
        # Créer le dossier
        os.makedirs(image_dir, exist_ok=True)
        
        # Déterminer l'extension
        filename = shape.image.filename
        ext = os.path.splitext(filename)[1] if filename else ".png"
        
        # Générer nom logique
        image_filename = f"slide{slide_num}_image{image_count}.{ext}"
        image_path = os.path.join(image_dir, image_filename)
        
        # Sauvegarder le fichier
        with open(image_path, 'wb') as f:
            f.write(shape.image.blob)
        
        # Générer lien Markdown
        md_content += f"\n![{alt_text}]({image_path})\n"
        image_count += 1
    elif kwargs.get("keep_data_uris", False):
        # Garder l'encodage base64
        ...
```

---

**Prochaines étapes recommandées:** 
1. **[URGENT]** Commencer par l'implémentation de la **sauvegarde réelle des images** qui est actuellement cassée
2. Puis implémenter les **listes à puces** et du **formatage texte** pour maximiser l'impact avec une complexité modérée
