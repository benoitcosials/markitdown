# Scripts de Test PPTX - Index Rapide

## 🎯 Quel script utiliser ?

### Je veux...

#### **Tester tout en une seule commande** → `run_all_tests.py` ⭐
```bash
python run_all_tests.py
```
✅ Lance Text-Only + Full Images + rapport comparatif automatique

---

#### **Voir les SmartArt extraits (texte seulement, rapide)** → `run_text_only_tests.py`
```bash
python run_text_only_tests.py
```
✅ Mode texte seulement, aucune image extraite  
✅ Résultats dans `pptx-result/text-only-YYYYMMDD-HHMMSS/`

---

#### **Valider les SmartArt avec images embarquées** → `run_full_images_tests.py`
```bash
python run_full_images_tests.py
```
✅ Extraction complète des images  
✅ Détecte SmartArt Type 2 (tableaux avec images)  
✅ Résultats dans `pptx-result/full-images-YYYYMMDD-HHMMSS/`

---

#### **Tester l'architecture complète** → `run_comprehensive_tests.py`
```bash
python run_comprehensive_tests.py
```
✅ Test global de l'architecture  
✅ Validation chemins relatifs  
✅ Résultats dans `pptx-result/test-YYYYMMDD-HHMMSS/`

---

## 📊 Résumé Rapide

| Script | Temps | Images | SmartArt | Usage |
|--------|-------|--------|----------|-------|
| `run_all_tests.py` | ~20s | ✅ | ✅ | **Recommandé** - Comparaison complète |
| `run_text_only_tests.py` | ~10s | ❌ | ✅ | Debug rapide structure |
| `run_full_images_tests.py` | ~15s | ✅ | ✅ | Validation images |
| `run_comprehensive_tests.py` | ~15s | ✅ | ❌ | Test architecture |

---

## 📁 Résultats Générés

Tous les résultats sont dans `pptx-result/` :

```
pptx-result/
├── comparative_report_YYYYMMDD-HHMMSS.md    # Rapport comparatif (run_all_tests.py)
├── text-only-YYYYMMDD-HHMMSS/               # Résultats Text-Only
├── full-images-YYYYMMDD-HHMMSS/             # Résultats Full Images
└── test-YYYYMMDD-HHMMSS/                    # Résultats Comprehensive
```

---

## 💡 Exemples d'Usage

### Scenario 1 : Je développe et veux tester rapidement
```bash
python run_text_only_tests.py
# Voir pptx-result/text-only-*/text_only_report.md
```

### Scenario 2 : Je valide BRIEF_05 avant merge
```bash
python run_all_tests.py
# Voir pptx-result/comparative_report_*.md
```

### Scenario 3 : Je veux vérifier que les images SmartArt sont bien extraites
```bash
python run_full_images_tests.py
# Vérifier pptx-result/full-images-*/[fichier]/images/
```

---

## 📚 Documentation Complète

Pour plus de détails, voir [README_TEST_SCRIPTS.md](README_TEST_SCRIPTS.md).

---

**Dernière mise à jour** : 23 février 2026
