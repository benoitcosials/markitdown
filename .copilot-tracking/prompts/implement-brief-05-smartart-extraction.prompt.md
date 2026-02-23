# Prompt d'Implémentation BRIEF_05 - SmartArt Extraction

**Date:** 20260222
**Agent Cible:** `#file:python-expert.agent.md`

---

## 🎯 Mission

Implémenter l'extraction et la conversion de **SmartArt PPTX en Markdown** selon BRIEF_05, en suivant le plan d'implémentation progressif avec **validation continue via get_errors**.

## 📋 Contexte

**Brief**: `BRIEF_05_SMARTART_EXTRACTION.md`  
**Recherche**: `.copilot-tracking/research/20260222-brief-05-smartart-capabilities-research.md` ✅ COMPLÉTÉE  
**Plan**: `.copilot-tracking/plans/20260222-brief-05-smartart-extraction-plan.instructions.md` (62 tasks)  
**Détails**: `.copilot-tracking/details/20260222-brief-05-smartart-extraction-details.md`

**Fichier cible**: `packages/markitdown/src/markitdown/converters/_pptx_converter.py`

**Dépendances**:
- ✅ BRIEF_01 implémenté (logique sauvegarde images disponible)
- ✅ `lxml` disponible (déjà dans projet)
- ✅ `zipfile` (Python stdlib)

## 🔬 Découvertes de Recherche Critiques

**⚠️ python-pptx : AUCUNE API SmartArt**
- Pas de `MSO_SHAPE_TYPE.SMART_ART`
- Pas d'attribut `shape.smart_art`
- **Solution** : Parsing XML manuel avec lxml

**✅ Détection SmartArt**
- Via XML URI : `"http://schemas.openxmlformats.org/drawingml/2006/diagram"`
- Dans `shape._element.graphic.graphicData`
- Fiabilité : 100% (19 SmartArt testés)

**✅ Extraction Texte**
- Fichiers : `ppt/diagrams/data{N}.xml` dans ZIP
- Nœuds : `<dgm:pt>` contenant `<a:t>` elements
- Résultats : 21-94 nœuds par SmartArt extraits avec succès

**✅ Images Embarquées**
- Éléments : `<a:blip r:embed="rId1">` dans data XML
- Résolution : Via `ppt/diagrams/_rels/data{N}.xml.rels`
- Statistiques : 7 images trouvées dans 2/13 SmartArt testés (15% taux)

**❌ Rendu Visuel Complet**
- SmartArt sont **vectoriels** (DrawingML XML)
- Conversion DrawingML → SVG : 200-300h (hors scope MVP)
- Seules images EMBARQUÉES extractibles, pas icônes dessinés

**Scope MVP Ajusté**
- ✅ Type 1 : Listes Markdown plates (texte uniquement)
- ✅ Type 2 : Tableaux Markdown (si images embarquées présentes)
- ⚠️ Hiérarchie complète : Phase 2 (hors MVP)

## 📂 Structure d'Implémentation

### Nouvelles Méthodes à Créer

1. **_is_smartart(shape) -> bool**
   - Détection via XML URI
   - Position : Après `_is_table()` (~ligne 120)

2. **_get_smartart_diagram_path(pptx_path, slide_index, shape) -> Optional[str]**
   - Résolution relationship ID → data{N}.xml
   - Parser `ppt/slides/_rels/slide{N}.xml.rels`

3. **_extract_smartart_text(pptx_path, diagram_path) -> List[str]**
   - Lecture ZIP + parsing lxml
   - Extraction `<dgm:pt>` → `<a:t>` textes

4. **_extract_smartart_images(pptx_path, diagram_path, slide_number, smartart_index, kwargs) -> List[str]**
   - Détection `<a:blip>` nodes
   - Résolution rId → media paths
   - Sauvegarde via logique BRIEF_01

5. **_convert_smartart_to_markdown(texts, images, smartart_index, slide_number) -> str**
   - Type 1 : Liste Markdown plate
   - Type 2 : Tableau 2 colonnes (Visual | Details)

### Intégration dans convert()

Dans boucle shapes, ajouter bloc :
```python
if self._is_smartart(shape):
    # Extract and convert SmartArt
    # Increment smartart_count
    continue
```

## 🛠️ Instructions d'Implémentation

### 1. Lire les Documents de Référence

**TU DOIS** d'abord lire :
- `.copilot-tracking/plans/20260222-brief-05-smartart-extraction-plan.instructions.md` (plan complet)
- `.copilot-tracking/details/20260222-brief-05-smartart-extraction-details.md` (structures de code)

### 2. Suivre le Plan Progressivement

**TU DOIS** implémenter phase par phase (10 phases, 62 tasks) :
- ✅ Cocher `[x]` chaque task complétée
- ✅ Appeler **get_errors** après CHAQUE modification de code
- ✅ Corriger tous les linting/syntax errors AVANT de continuer
- ✅ Ne JAMAIS passer à la tâche suivante si errors présentes

### 3. Workflow de Validation MANDATORY

**POUR CHAQUE TASK** :
```
1. Implémenter code pour la task
2. Appeler get_errors sur _pptx_converter.py
3. Si errors détectées :
   a. Corriger immédiatement
   b. Re-appeler get_errors
   c. Répéter jusqu'à zéro error
4. Si aucune error :
   a. Marquer task [x]
   b. Mettre à jour changes file
   c. Continuer task suivante
```

### 4. Standards de Code Python

**TU DOIS** respecter :
- ✅ Type hints pour toutes méthodes
- ✅ Docstrings Google Style complètes
- ✅ PEP 8 (79 chars max, 4 espaces)
- ✅ Imports : stdlib avant externes
- ✅ Error handling : try/except autour XML parsing
- ✅ Commentaires : WHY pas WHAT

### 5. Namespaces XML Critiques

**TU DOIS** utiliser ces namespaces exacts :
```python
ns = {
    'dgm': 'http://schemas.openxmlformats.org/drawingml/2006/diagram',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'
}
```

### 6. Gestion d'Erreurs

**TU DOIS** :
- ✅ Ne JAMAIS crasher la conversion complète
- ✅ Retourner résultats partiels si possible
- ✅ Log errors pour debugging
- ✅ Skip gracefully si lxml manquant

### 7. Tests Requis

**TU DOIS** :
- ✅ Exécuter `pytest tests/test_module_vectors.py -v` après chaque phase
- ✅ Vérifier ZÉRO régression (tous tests existants passent)
- ✅ Créer PPTX de test pour Type 1 (texte uniquement)
- ✅ Créer PPTX de test pour Type 2 (avec images embarquées)
- ✅ Valider extraction complète end-to-end

### 8. Documentation Changes

**TU DOIS** mettre à jour :
- `.copilot-tracking/changes/20260222-brief-05-smartart-changes.md` après CHAQUE phase
- Docstrings complètes pour toutes méthodes
- Commentaires expliquant limitations python-pptx

## ⚠️ Contraintes Critiques

**TU NE DOIS JAMAIS** :
- ❌ Implémenter sans lire plan et détails d'abord
- ❌ Marquer task [x] si errors présentes dans get_errors
- ❌ Passer à phase suivante si tests régressent
- ❌ Crasher conversion complète (toujours try/except)
- ❌ Implémenter hiérarchie complète (hors scope MVP)
- ❌ Tenter conversion DrawingML → SVG (trop complexe)

**TU DOIS TOUJOURS** :
- ✅ Valider avec get_errors après CHAQUE modification
- ✅ Fixer errors IMMÉDIATEMENT avant continuer
- ✅ Réutiliser logique BRIEF_01 pour sauvegarde images
- ✅ Documenter WHY pas WHAT dans commentaires
- ✅ Tester progressivement (ne pas attendre fin)

## 🚀 Commande de Lancement

```
@workspace utilise #file:python-expert.agent.md pour implémenter BRIEF_05 selon le plan .copilot-tracking/plans/20260222-brief-05-smartart-extraction-plan.instructions.md avec validation get_errors continue
```

## 📊 Résumé Scope MVP

**Inclus** :
- ✅ Détection SmartArt via XML URI
- ✅ Extraction texte via ZIP + lxml parsing
- ✅ Extraction images embarquées (si présentes)
- ✅ Conversion Markdown Type 1 (liste) + Type 2 (tableau)
- ✅ Intégration dans convert() sans régression

**Exclu (Phase 2)** :
- ⚠️ Reconstruction hiérarchie complète via `<dgm:cxn>`
- ⚠️ Tri topologique pour multi-niveaux
- ❌ Rendu visuel complet (DrawingML → SVG)
- ❌ Icônes vectoriels (seules images embarquées)

**Estimation** : 7h implémentation + 2h tests = 9h total

---

**Status**: ⏳ Prêt pour implémentation - Recherche ✅ complétée, Plan ✅ créé

