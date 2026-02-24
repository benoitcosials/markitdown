# Scripts de Test PPTX - Guide d'Utilisation

Ce document explique l'usage des différents scripts de test pour évaluer l'extraction SmartArt et images depuis des fichiers PPTX.

## 📋 Vue d'Ensemble

Quatre scripts de test disponibles, chacun avec un objectif spécifique :

| Script | Mode | Focus | Extraction Images | Use Case |
|--------|------|-------|-------------------|----------|
| `run_text_only_tests.py` | Text-Only | SmartArt texte pur | ❌ Non | Validation texte/structure |
| `run_full_images_tests.py` | Full Images | SmartArt avec images | ✅ Oui | Validation images embarquées |
| `run_comprehensive_tests.py` | Comprehensive | Images globales | ✅ Oui | Test complet architecture |
| `run_all_tests.py` | All-in-One | Comparaison complète | ✅ Les deux | Rapport comparatif automatique |

## ⚡ Démarrage Rapide

**Pour une analyse complète en une commande** :
```bash
python run_all_tests.py
```
Ce script exécute automatiquement les modes Text-Only ET Full Images, puis génère un rapport comparatif.

---

## 🎯 Script 0: All-in-One (Recommandé)

### Objectif
Exécuter **automatiquement** les deux modes de test (Text-Only + Full Images) et générer un **rapport comparatif** unifié.

### Commande
```bash
python run_all_tests.py
```

### Workflow
1. ▶️ Exécute `run_text_only_tests.py`
2. ▶️ Exécute `run_full_images_tests.py`
3. 📊 Parse les résultats des deux modes
4. ✅ Génère un rapport comparatif

### Résultats Générés
```
pptx-result/
├── comparative_report_YYYYMMDD-HHMMSS.md    # 🆕 Rapport comparatif
├── text-only-YYYYMMDD-HHMMSS/               # Résultats Text-Only
│   └── text_only_report.md
└── full-images-YYYYMMDD-HHMMSS/             # Résultats Full Images
    └── full_images_report.md
```

### Contenu du Rapport Comparatif

Le rapport `comparative_report_YYYYMMDD-HHMMSS.md` contient :

#### 1. Statut d'Exécution
```markdown
## Statut d'Exécution

- **Text-Only**: ✅ SUCCESS
- **Full Images**: ✅ SUCCESS
```

#### 2. Statistiques Comparatives
```markdown
| Métrique | Text-Only | Full Images | Différence |
|----------|-----------|-------------|------------|
| Fichiers testés | 8 | 8 | 0 |
| Conversions réussies | 8 | 8 | 0 |
| SmartArt détectés | 59 | 59 | 0 |
| Images extraites | 0 | 42 | +42 |
| SmartArt avec images (Type 2) | N/A | 25 (42%) | - |
```

#### 3. Analyse Automatique
- ✅ **Cohérence de détection** : Validation que les deux modes détectent le même nombre de SmartArt
- 📊 **Répartition Type 1 vs Type 2** : Pourcentage de SmartArt avec/sans images
- 🖼️ **Extraction d'images** : Statistiques sur les images embarquées
- ⚡ **Performance** : Comparaison avantages/limitations

#### 4. Recommandations
Guidance automatique sur quand utiliser chaque mode.

### Avantages
- **Un seul script** : Pas besoin de lancer manuellement deux scripts
- **Rapport unifié** : Vue comparative directe
- **Parsing automatique** : Extraction automatique des statistiques
- **Validation croisée** : Détection d'incohérences entre modes

### Exemple de Sortie Console
```
================================================================================
🚀 ALL-IN-ONE TEST SUITE - PPTX SMARTART EXTRACTION
================================================================================

Ce script va exécuter séquentiellement:
  1. run_text_only_tests.py
  2. run_full_images_tests.py
  3. Génération d'un rapport comparatif

================================================================================
▶️  Exécution: run_text_only_tests.py
================================================================================

[... output du script text-only ...]

================================================================================
▶️  Exécution: run_full_images_tests.py
================================================================================

[... output du script full-images ...]

================================================================================
📊 GÉNÉRATION DU RAPPORT COMPARATIF
================================================================================

✅ Rapport comparatif généré: pptx-result/comparative_report_20260223-083500.md

================================================================================
📋 RÉSUMÉ FINAL
================================================================================

Mode                 Fichiers     Succès       SmartArt     Images      
--------------------------------------------------------------------------------
Text-Only            8            8            59           0           
Full Images          8            8            59           42          
--------------------------------------------------------------------------------

🎯 SmartArt avec images (Type 2): 25

✅ Tests terminés avec succès!
📄 Rapport comparatif: pptx-result/comparative_report_20260223-083500.md
```

### Cas d'Usage
- ✅ **Validation BRIEF_05 complète** : Un seul script pour tout tester
- ✅ **CI/CD** : Intégration dans pipelines automatisés
- ✅ **Démo** : Montrer les deux modes en une seule exécution
- ✅ **Debug** : Comparer rapidement les résultats des deux modes



### Objectif
Convertir les PPTX en Markdown **sans extraction physique d'images**, focus sur le contenu textuel et SmartArt.

### Commande
```bash
python run_text_only_tests.py
```

### Configuration
```python
md.convert(
    source=pptx_path,
    output_images=False  # Pas d'images physiques
)
```

### Résultats Générés
```
pptx-result/text-only-YYYYMMDD-HHMMSS/
├── text_only_report.md          # Rapport global
├── [fichier1]/
│   └── output_text_only.md      # Markdown sans images
├── [fichier2]/
│   └── output_text_only.md
└── ...
```

### Contenu du Rapport
- ✅ Nombre total de SmartArt détectés
- ✅ Détails par SmartArt (slide, items, aperçu)
- ✅ Statistiques globales
- ❌ Aucune image extraite

### Avantages
- **Rapide** : Pas d'I/O image
- **Léger** : Fichiers Markdown seulement
- **Focus texte** : Idéal pour valider la structure SmartArt

### Limitations
- Aucune image physique extraite
- Pas de validation des images embarquées dans SmartArt
- Ne teste pas le mode Type 2 (SmartArt avec images → tableaux)

### Exemple de Sortie Console
```
[7/8] Traitement: Test des SmartArt.pptx
  ✅ SUCCESS: 12 SmartArt trouvés

📊 Total fichiers : 8
✅ Succès : 8
🎯 Total SmartArt : 59
```

---

## 🖼️ Script 2: Full Images Mode

### Objectif
Convertir les PPTX en Markdown **avec extraction complète des images**, y compris celles embarquées dans les SmartArt.

### Commande
```bash
python run_full_images_tests.py
```

### Configuration
```python
md.convert(
    source=pptx_path,
    image_dir="images",
    output_images=True,           # Extraction complète
    skip_background_images=True
)
```

### Résultats Générés
```
pptx-result/full-images-YYYYMMDD-HHMMSS/
├── full_images_report.md        # Rapport global
├── [fichier1]/
│   ├── output_full_images.md    # Markdown avec liens images
│   └── images/                  # Images extraites
│       ├── slide4_image0.png
│       ├── slide6_image1.png
│       └── ...
└── ...
```

### Contenu du Rapport
- ✅ Nombre total d'images extraites
- ✅ SmartArt détectés (Type 1 vs Type 2)
- ✅ Détails images embarquées SmartArt
- ✅ Chemins relatifs des images
- ✅ Format de conversion (Liste vs Tableau)

### Types de SmartArt Détectés
- **Type 1 (List)** : SmartArt sans images → Liste Markdown
- **Type 2 (Table)** : SmartArt avec images → Tableau Markdown 3 colonnes

### Avantages
- **Validation complète** : Images + SmartArt
- **Type 2 testing** : Valide les tableaux avec images embarquées
- **Images physiques** : Fichiers sauvegardés sur disque
- **Liens relatifs** : Architecture propre

### Exemple de Sortie Console
```
[7/8] Traitement: Test des SmartArt.pptx
  ✅ SUCCESS: 19 images, 12 SmartArt (12 avec images)

📊 Total fichiers : 8
✅ Succès : 8
🖼️  Total images : 42
🎯 Total SmartArt : 59 (25 avec images)
```

### Analyse Type 1 vs Type 2
Le rapport indique clairement :
- **SmartArt avec images (Type 2)** : 25 / 59 (42%)
- **SmartArt texte seul (Type 1)** : 34 / 59 (58%)

---

## 🔬 Script 3: Comprehensive Tests (Original)

### Objectif
Test complet de l'architecture d'extraction avec validation des chemins relatifs.

### Commande
```bash
python run_comprehensive_tests.py
```

### Différence avec Full Images
- **Comprehensive** : Focus architecture globale (chemins relatifs, structure)
- **Full Images** : Focus SmartArt et analyse détaillée des images embarquées

### Utilisation
À utiliser pour :
- Tests de non-régression globaux
- Validation de l'architecture (chemins relatifs)
- Préparation de release

---

## 📊 Comparaison des Résultats

### Test Récent (23 février 2026)

| Métrique | Text-Only | Full Images |
|----------|-----------|-------------|
| **Fichiers testés** | 8 | 8 |
| **Succès** | 8 (100%) | 8 (100%) |
| **SmartArt total** | 59 | 59 |
| **SmartArt Type 2** | N/A | 25 (42%) |
| **Images extraites** | 0 | 42 |
| **Temps d'exécution** | ~10s | ~15s |
| **Taille sortie** | Léger | Moyen |

### Répartition SmartArt par Fichier

| Fichier PPTX | SmartArt | Images (Full Mode) |
|--------------|----------|-------------------|
| Test des SmartArt.pptx | 12 | 19 |
| z 015_ARCH...pptx | 15 | 9 |
| Standard QA - Design.pptx | 8 | 4 |
| Kickoff QA.pptx | 6 | 3 |
| Standard QA - Stratégie.pptx | 6 | 0 |
| **TOTAL** | **59** | **42** |

---

## 🚀 Workflow Recommandé

### 1. Développement / Debug
**Script** : `run_text_only_tests.py`  
**Pourquoi** : Rapide, focus sur la structure SmartArt

```bash
python run_text_only_tests.py
# Analyser text_only_report.md
```

### 2. Validation Type 2 (Images Embarquées)
**Script** : `run_full_images_tests.py`  
**Pourquoi** : Valide les SmartArt avec images → tableaux

```bash
python run_full_images_tests.py
# Analyser full_images_report.md
# Vérifier les dossiers images/
```

### 3. Release / Non-Régression
**Script** : `run_comprehensive_tests.py`  
**Pourquoi** : Test complet architecture

```bash
python run_comprehensive_tests.py
# Validation finale avant merge
```

---

## 📁 Structure des Résultats

```
pptx-result/
├── text-only-20260223-083342/
│   ├── text_only_report.md
│   ├── [fichier1]/
│   │   └── output_text_only.md
│   └── ...
├── full-images-20260223-083350/
│   ├── full_images_report.md
│   ├── [fichier1]/
│   │   ├── output_full_images.md
│   │   └── images/
│   │       ├── slide4_image0.png
│   │       └── ...
│   └── ...
└── test-20260223-083400/
    ├── test_report.md
    └── ...
```

---

## 🔍 Analyse des Rapports

### Text-Only Report
Chaque SmartArt affiché avec :
- `### SmartArt N (Slide X)` - Titre détecté
- **Slide** : Numéro de slide
- **Items de liste** : Nombre d'éléments
- **Longueur contenu** : Caractères
- **Aperçu** : Premiers 300-500 caractères

### Full Images Report
Chaque SmartArt affiché avec :
- `### SmartArt N (Slide X)` - Titre
- **Slide** : Numéro de slide
- **Format** : Type 1 (List) ou Type 2 (Table)
- **Images embarquées** : Nombre
- **Chemins d'images** : Liste des images/slideX_imageY.png
- **Aperçu** : Contenu avec format

---

## 🎓 Exemples d'Usage

### Scenario 1 : Nouveau développeur
**Question** : "Comment les SmartArt sont-ils extraits ?"

```bash
python run_text_only_tests.py
# Lire le rapport généré
# Examiner output_text_only.md pour "Test des SmartArt.pptx"
```

### Scenario 2 : Validation BRIEF_05
**Question** : "Les SmartArt avec images utilisent-ils bien Type 2 (tableaux) ?"

```bash
python run_full_images_tests.py
# Rechercher "Type 2 (Table)" dans full_images_report.md
# Vérifier que les images sont bien dans images/
```

### Scenario 3 : Bug Report
**Question** : "Les images SmartArt ne sont pas extraites"

```bash
# 1. Test text-only pour confirmer détection SmartArt
python run_text_only_tests.py

# 2. Test full images pour valider extraction
python run_full_images_tests.py

# 3. Comparer les deux rapports
#    - Si SmartArt détectés en text-only mais pas en full-images → bug extraction
#    - Si pas détectés dans les deux → bug détection
```

---

## 📝 Notes Techniques

### Pattern de Détection SmartArt
Les scripts utilisent le pattern :
```python
pattern = r'### SmartArt (\d+) \(Slide (\d+)\)'
```

Ce format correspond au Markdown généré par `_pptx_converter.py` :
```markdown
### SmartArt 1 (Slide 4)

- Level1
- Level 2
- ...
```

### Formats de Conversion

**Type 1 - Liste** :
```markdown
### SmartArt 1 (Slide 4)

- Item 1
- Item 2
- Item 3
```

**Type 2 - Tableau** :
```markdown
### SmartArt 2 (Slide 6)

| Image | Texte | Image |
|-------|-------|-------|
| ![](images/slide6_image0.png) | Item 1 | |
| | Item 2 | ![](images/slide6_image1.png) |
```

---

## ❓ FAQ

### Q: Pourquoi 3 scripts différents ?
**R** : Chaque script a un objectif différent :
- Text-Only : Rapidité + focus texte
- Full Images : Validation complète images
- Comprehensive : Architecture globale

### Q: Quel script utiliser pour valider BRIEF_05 ?
**R** : `run_full_images_tests.py` pour voir les SmartArt Type 2 avec images.

### Q: Les rapports sont-ils compatibles Git ?
**R** : Oui, mais ajoutez `pptx-result/` au `.gitignore` pour éviter de committer les résultats de test.

### Q: Comment voir seulement les SmartArt d'un fichier spécifique ?
**R** : Ouvrir le rapport Markdown et chercher le nom du fichier, ou ouvrir directement le fichier `output_text_only.md` dans le sous-dossier correspondant.

---

## 🔗 Liens Utiles

- **BRIEF_05** : [BRIEF_05_SMARTART_EXTRACTION.md](BRIEF_05_SMARTART_EXTRACTION.md)
- **Recherche SmartArt** : [.copilot-tracking/research/20260222-brief-05-smartart-capabilities-research.md](.copilot-tracking/research/20260222-brief-05-smartart-capabilities-research.md)
- **Convertisseur PPTX** : [packages/markitdown/src/markitdown/converters/_pptx_converter.py](packages/markitdown/src/markitdown/converters/_pptx_converter.py)

---

**Dernière mise à jour** : 23 février 2026  
**Scripts testés avec** : 8 fichiers PPTX, 59 SmartArt détectés, 100% de réussite
