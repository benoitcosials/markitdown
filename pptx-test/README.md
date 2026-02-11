# Structure des Tests PPTX

## 📁 Répertoires

### `pptx-test/` ⚠️ IMPORTANT
**Répertoire SOURCE contenant les fichiers PowerPoint à tester**

- **NE PAS SUPPRIMER** - Ce dossier et ses fichiers sont essentiels pour les tests
- Contient tous les fichiers `.pptx` utilisés comme données d'entrée
- Les fichiers ne doivent pas être modifiés manuellement
- En cas de suppression accidentelle, restaurer depuis Git ou backup

**Fichiers disponibles:**
- Kickoff QA - Essais UAT R1 Bancaire et Trésorerie.pptx
- Méthodologie de livraison et de QA standard.pptx
- Standard QA - Concept de base.pptx
- Standard QA - Design des essais.pptx
- Standard QA - Organisation.pptx
- Standard QA - Stratégie d'essai.pptx
- z 015_ARCH-00xx_WS4_Bancaire-b7f2a76a-7655-4a73-a5ab-035aee935269.pptx


### `pptx-result/` 📊
**Répertoire de RÉSULTATS des tests**

Structure:
```
pptx-result/
└── test-<YYYYMMDD-HHMMSS>/          (Nouvelle session de test)
    ├── test_report.md               (Rapport global en Markdown)
    ├── <nom_du_pptx_1>/
    │   ├── output.md                (Contenu Markdown extrait)
    │   └── <nom_du_pptx_1>_images/  (Dossier images)
    │       ├── slide1_image0.jpeg
    │       └── ...
    ├── <nom_du_pptx_2>/
    │   ├── output.md
    │   └── <nom_du_pptx_2>_images/
    │       ├── slide1_image0.jpeg
    │       └── ...
    └── ...
```

**Caractéristiques:**
- Chaque test génère un nouveau dossier avec timestamp
- Les résultats sont organisés par nom de fichier PPTX
- Les images sont extraites dans des sous-dossiers séparés
- Un rapport global `test_report.md` résume les résultats


## 🧪 Test Complet

### Exécution

```bash
python run_comprehensive_tests.py
```

### Configuration des tests

- **Répertoire source**: `pptx-test/`
- **Répertoire résultats**: `pptx-result/test-<timestamp>/`
- **Images extraites**: Oui (`output_images=True`)
- **Skip backgrounds**: Oui (`skip_background_images=True`)
- **Déduplication**: Non (`deduplicate_images=False`)
- **Format chemins**: Unix/Markdown (`/` au lieu de `\`)

### Sortie attendue

```
================================================================================
TEST COMPLET EXTRACTION PPTX
Timestamp: 20260211-073000
Repertoire: ...
================================================================================

[1/7] Fichier1.pptx
  SUCCESS: 5 images
[2/7] Fichier2.pptx
  SUCCESS: 12 images
...
```


## ⚠️ Règles Importantes

1. **Ne pas supprimer `pptx-test/`**
   - Contient les données source pour les tests
   - Si supprimé accidentellement, restaurer depuis Git

2. **Nettoyage des résultats**
   - Nettoyer régulièrement `pptx-result/` si espace insuffisant
   - Garder les rapports importants (copier ailleurs si nécessaire)

3. **Noms des dossiers résultats**
   - Format: `test-<YYYYMMDD-HHMMSS>`
   - Créé automatiquement à chaque test
   - Timestamp garantit unicité et traçabilité

4. **Chemins des images**
   - Markdown généré utilise `/` (Unix standard)
   - Fonctionne sur Windows, Linux, Mac
   - Images physiquement sauvegardées dans `_images/`


## 📋 Historique des Tests

Consulter `pptx-result/test-<timestamp>/test_report.md` pour:
- Nombre de fichiers traités
- Nombre d'images extraites
- Statut de chaque conversion
- Chemins des fichiers de sortie
