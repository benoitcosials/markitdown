# Plan d'Implémentation BRIEF_01 - Extraction Images PPTX

**Date:** 20260210
**Brief:** BRIEF_01_IMAGE_EXTRACTION
**Phase:** Plan d'Implémentation
**Fichier Cible:** `packages/markitdown/src/markitdown/converters/_pptx_converter.py`

---

## 📋 Tasks Checklist

### Phase 1: Infrastructure (5 tasks)

- [ ] **Task 1.1** - Ajouter import `hashlib` (ligne ~5)
- [ ] **Task 1.2** - Ajouter `self._image_hashes = {}` dans `__init__()` (ligne ~38)
- [ ] **Task 1.3** - Ajouter initialisation configuration dans `convert()` (ligne ~80)
- [ ] **Task 1.4** - Ajouter compteur `image_count = 0` dans boucle slides
- [ ] **Task 1.5** - Validation: Exécuter `get_errors` sur fichier modifié

### Phase 2: Méthodes Utilitaires (6 tasks)

- [ ] **Task 2.1** - Créer méthode `_get_image_extension()` après `_is_table()`
- [ ] **Task 2.2** - Implémenter mapping MIME → extension dans `_get_image_extension()`
- [ ] **Task 2.3** - Implémenter logique fallback `.png` dans `_get_image_extension()`
- [ ] **Task 2.4** - Créer méthode `_save_image()` après `_get_image_extension()`
- [ ] **Task 2.5** - Implémenter logique déduplication MD5 dans `_save_image()`
- [ ] **Task 2.6** - Validation: Exécuter `get_errors` sur fichier modifié

### Phase 3: Intégration Images (7 tasks)

- [ ] **Task 3.1** - Modifier bloc images dans `get_shape_content()` (ligne ~147-154)
- [ ] **Task 3.2** - Préserver bloc Base64 existant (lignes 147-151) SANS MODIFICATION
- [ ] **Task 3.3** - Ajouter condition `elif output_images:` pour nouveau mode
- [ ] **Task 3.4** - Appeler `_save_image()` dans nouveau bloc
- [ ] **Task 3.5** - Générer Markdown avec chemin image retourné
- [ ] **Task 3.6** - Incrémenter `image_count` si image non dédupliquée
- [ ] **Task 3.7** - Validation: Exécuter `get_errors` sur fichier modifié

### Phase 4: Tests Unitaires (6 tasks)

- [ ] **Task 4.1** - Exécuter tests existants: `pytest tests/test_module_vectors.py -v`
- [ ] **Task 4.2** - Vérifier que tous les tests passent (régression check)
- [ ] **Task 4.3** - Créer fichier PPTX de test avec 2 images
- [ ] **Task 4.4** - Tester extraction standard (vérifier fichiers créés)
- [ ] **Task 4.5** - Tester mode Base64 (vérifier aucun changement)
- [ ] **Task 4.6** - Tester déduplication (vérifier fichier unique)

### Phase 5: Documentation & Finalisation (4 tasks)

- [ ] **Task 5.1** - Ajouter docstrings pour `_get_image_extension()`
- [ ] **Task 5.2** - Ajouter docstrings pour `_save_image()`
- [ ] **Task 5.3** - Mettre à jour fichier changes avec résumé
- [ ] **Task 5.4** - Validation finale: `get_errors` + tous tests

---

## 📊 Résumé

**Total Tasks:** 28
**Phases:** 5
**Temps Estimé:** 3-5h
**Fichiers Modifiés:** 1 (`_pptx_converter.py`)
**Fichiers Tests:** `test_module_vectors.py` (existant)

**Status:** ⏳ En attente d'implémentation
