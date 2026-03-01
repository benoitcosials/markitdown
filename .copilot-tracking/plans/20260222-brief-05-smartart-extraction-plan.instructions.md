# Plan d'Implémentation BRIEF_05 - Extraction SmartArt PPTX

**Date:** 20260222
**Brief:** BRIEF_05_SMARTART_EXTRACTION
**Phase:** Plan d'Implémentation
**Fichier Cible:** `packages/markitdown/src/markitdown/converters/_pptx_converter.py`
**Dépendances:** BRIEF_01 ✅, lxml (existant)

---

## 📋 Tasks Checklist

### Phase 1: Infrastructure et Imports (4 tasks)

- [x] **Task 1.1** - Ajouter imports ZIP/XML : `import zipfile` et `from lxml import etree` (ligne ~5-10)
- [x] **Task 1.2** - Ajouter compteur SmartArt `smartart_count = 0` dans boucle slides du `convert()`
- [x] **Task 1.3** - Vérifier disponibilité de `lxml` via try/except (gérer absence)
- [x] **Task 1.4** - Validation: Exécuter `get_errors` sur fichier modifié

### Phase 2: Détection SmartArt (5 tasks)

- [x] **Task 2.1** - Créer méthode `_is_smartart(shape)` après `_is_table()` 
- [x] **Task 2.2** - Implémenter détection via XML URI `"diagram"` dans `shape._element.graphic.graphicData`
- [x] **Task 2.3** - Gérer exceptions (AttributeError si pas GraphicFrame)
- [x] **Task 2.4** - Ajouter docstring complète (expliquant absence API python-pptx)
- [x] **Task 2.5** - Validation: Exécuter `get_errors` sur fichier modifié

### Phase 3: Mapping Diagram Files (6 tasks)

- [x] **Task 3.1** - Créer méthode `_get_smartart_diagram_path(pptx_path, slide_index, shape)`
- [x] **Task 3.2** - Parser `ppt/slides/_rels/slide{N}.xml.rels` pour trouver relationship ID
- [x] **Task 3.3** - Extraire GraphicFrame rId depuis `shape._element.graphic.graphicData`
- [x] **Task 3.4** - Résoudre rId → fichier `ppt/diagrams/data{N}.xml` via relationships
- [x] **Task 3.5** - Gérer erreurs (fichier manquant, XML malformé)
- [x] **Task 3.6** - Validation: Exécuter `get_errors` sur fichier modifié

### Phase 4: Extraction Texte SmartArt (8 tasks)

- [x] **Task 4.1** - Créer méthode `_extract_smartart_text(pptx_path, diagram_path)`
- [x] **Task 4.2** - Ouvrir PPTX comme ZIP avec `zipfile.ZipFile()`
- [x] **Task 4.3** - Lire fichier `ppt/diagrams/data{N}.xml` depuis ZIP
- [x] **Task 4.4** - Parser XML avec `lxml.etree.fromstring()`
- [x] **Task 4.5** - Définir namespaces `dgm` et `a` (DrawingML)
- [x] **Task 4.6** - Extraire tous les `<dgm:pt>` nodes
- [x] **Task 4.7** - Pour chaque node, extraire texte via `<a:t>` elements
- [x] **Task 4.8** - Validation: Exécuter `get_errors` sur fichier modifié

### Phase 5: Détection Images Embarquées (7 tasks)

- [x] **Task 5.1** - Créer méthode `_extract_smartart_images(pptx_path, diagram_path)`
- [x] **Task 5.2** - Détecter éléments `<a:blip>` dans data XML
- [x] **Task 5.3** - Extraire relationship IDs (`r:embed` attribute)
- [x] **Task 5.4** - Parser `ppt/diagrams/_rels/data{N}.xml.rels` pour résoudre rIds
- [x] **Task 5.5** - Résoudre chemins → `ppt/media/image{X}.{ext}`
- [x] **Task 5.6** - Extraire images depuis ZIP et sauvegarder via logique BRIEF_01
- [x] **Task 5.7** - Validation: Exécuter `get_errors` sur fichier modifié

### Phase 6: Conversion Markdown (Type 1 - Texte Uniquement) (7 tasks)

- [x] **Task 6.1** - Créer méthode `_convert_smartart_to_markdown(texts, images, smartart_index, slide_number)`
- [x] **Task 6.2** - Détecter Type 1 vs Type 2 (si `images` vide → Type 1)
- [x] **Task 6.3** - **Type 1** : Générer liste Markdown plate (sans hiérarchie pour MVP)
- [x] **Task 6.4** - **Type 1** : Format `- Item 1\n- Item 2\n...`
- [x] **Task 6.5** - Ajouter un titre si SmartArt a un titre (extraire depuis `<dgm:prSet>`)
- [x] **Task 6.6** - Retourner Markdown string complet
- [x] **Task 6.7** - Validation: Exécuter `get_errors` sur fichier modifié

### Phase 7: Conversion Markdown (Type 2 - Avec Images) (6 tasks)

- [x] **Task 7.1** - **Type 2** : Détecter présence d'images embarquées
- [x] **Task 7.2** - **Type 2** : Générer tableau Markdown `| Visual | Details |`
- [x] **Task 7.3** - **Type 2** : Mapper images → textes correspondants (par index node)
- [x] **Task 7.4** - **Type 2** : Format `![](images/slide{N}_smartart{M}_item{K}.{ext})`
- [x] **Task 7.5** - **Type 2** : Gérer SmartArt avec images partielles (fallback Type 1 pour items sans image)
- [x] **Task 7.6** - Validation: Exécuter `get_errors` sur fichier modifié

### Phase 8: Intégration dans convert() (6 tasks)

- [x] **Task 8.1** - Ajouter condition `if self._is_smartart(shape):` dans boucle shapes du `convert()`
- [x] **Task 8.2** - Appeler `_get_smartart_diagram_path()` pour trouver data XML
- [x] **Task 8.3** - Appeler `_extract_smartart_text()` pour obtenir textes
- [x] **Task 8.4** - Appeler `_extract_smartart_images()` pour obtenir images (si présentes)
- [x] **Task 8.5** - Appeler `_convert_smartart_to_markdown()` pour générer output
- [x] **Task 8.6** - Validation: Exécuter `get_errors` sur fichier modifié

### Phase 9: Tests Unitaires (8 tasks)

- [x] **Task 9.1** - Exécuter tests existants: `pytest tests/test_module_vectors.py -v`
- [x] **Task 9.2** - Vérifier régression (tous tests passent) - ✅ 109/109 PASSÉS
- [x] **Task 9.3** - Créer fichier PPTX test avec SmartArt Type 1 (texte uniquement) - ✅ Existant
- [x] **Task 9.4** - Tester extraction Type 1 (vérifier liste Markdown générée) - ✅ 12 SmartArt extraits
- [x] **Task 9.5** - Créer fichier PPTX test avec SmartArt Type 2 (avec images embarquées) - ✅ Existant (2/12 avec images)
- [x] **Task 9.6** - Tester extraction Type 2 (vérifier tableau Markdown + images sauvegardées) - ✅ Fonctionnel
- [x] **Task 9.7** - Tester cas limite (SmartArt vide, sans texte) - ✅ Géré gracefully
- [x] **Task 9.8** - Validation finale: Tous tests passent - ✅ 109/109

### Phase 10: Documentation et Finalisation (5 tasks)

- [x] **Task 10.1** - Ajouter docstrings complètes pour toutes méthodes SmartArt
- [x] **Task 10.2** - Ajouter commentaires expliquant absence API python-pptx (WHY parsing XML)
- [x] **Task 10.3** - Documenter limitations (MVP = liste plate, hiérarchie Phase 2)
- [x] **Task 10.4** - Mettre à jour `.copilot-tracking/changes/20260222-brief-05-smartart-changes.md`
- [x] **Task 10.5** - Validation finale: `get_errors` + tous tests + review code

---

## 📊 Résumé

**Total Tasks:** 62
**Phases:** 10
**Temps Estimé:** 7-9h
**Fichiers Modifiés:** 1 (`_pptx_converter.py`)
**Fichiers Tests:** `test_module_vectors.py` (existant) + nouveaux PPTX

**Dépendances Techniques:**
- ✅ `lxml` (déjà présent dans projet)
- ✅ `zipfile` (Python stdlib)
- ✅ BRIEF_01 logique sauvegarde images (réutilisation)

**Scope MVP:**
- ✅ Type 1 : Listes Markdown plates (texte uniquement)
- ✅ Type 2 : Tableaux Markdown (si images embarquées présentes)
- ⚠️ Hiérarchie complète : Phase 2 (hors MVP)
- ❌ Rendu visuel complet : Non faisable (vectoriel DrawingML)

**Status:** ⏳ En attente d'implémentation

