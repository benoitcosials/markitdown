# GitHub Copilot - Workflow Instructions MarkItDown

## 🎯 Contexte du Projet

Vous travaillez sur **markitdown**, un projet Microsoft Python pour convertir divers formats (PPTX, PDF, DOCX, etc.) en Markdown optimisé pour LLMs.

**Repository** : `benoitcosials/markitdown` (fork de `microsoft/markitdown`)
**Branche principale** : `develop`
**Python** : 3.10+
**Framework** : Standard library + python-pptx, mammoth, etc.

**⚠️ ENVIRONNEMENT DE DÉVELOPPEMENT CRITIQUE :**
- **IDE cible** : Visual Studio Code (VS Code)
- **Agent IA utilisé** : GitHub Copilot (dans VS Code)
- **NE PAS développer dans** : Claude Desktop, Claude Web, ou autres environnements
- **Workflow MCP** : Tests uniquement, développement dans VS Code

## 🔒 Règles de Permissions (OBLIGATOIRE)

**⚠️ CRITIQUE : L'Agent DOIT respecter ces règles strictement !**

### Zones Autorisées (modifications libres)

L'Agent peut créer/modifier des fichiers **SANS permission** uniquement dans :

| Dossier | Usage |
|---------|-------|
| `.copilot-tracking/` | Recherche, plans, scripts, tests, fichiers temporaires |
| `.github/` | Instructions, agents, documentation workflow |

### Zones Protégées (permission requise)

**TOUTE modification hors des zones autorisées nécessite une permission explicite de l'utilisateur :**

- ❌ `packages/` - Code source du projet
- ❌ Racine du projet (`/`) - Fichiers de configuration
- ❌ `images/` - Assets du projet
- ❌ Tout autre dossier

**Avant de modifier une zone protégée, l'Agent DOIT :**
1. Décrire la modification proposée
2. Attendre la confirmation de l'utilisateur
3. Ne procéder qu'après approbation explicite

### Exceptions

- Les commits Git sont autorisés après implémentation approuvée
- Les commandes de lecture (`git status`, `ls`, `cat`) sont toujours autorisées

## 🎓 Instructions & Agents de Qualité

### Instructions Python Disponibles

Pour garantir un code Python de haute qualité, les instructions suivantes sont automatiquement chargées :

1. **[python.instructions.md](.github/instructions/python.instructions.md)** ✅
   - Conventions Python (PEP 8, type hints, docstrings)
   - Gestion des erreurs et edge cases
   - Tests et validation
   - S'applique à : `**/*.py`

2. **[self-explanatory-code.instructions.md](.github/instructions/self-explanatory-code.instructions.md)** ✅
   - Principes de code auto-documenté
   - Commenter le WHY pas le WHAT
   - Annotations (TODO, FIXME, NOTE, SECURITY, etc.)
   - S'applique à : tous les fichiers

### Agents Experts Disponibles

Agents spécialisés pour assistance durant le développement :

1. **[python-expert.agent.md](.github/agents/python-expert.agent.md)** 🤖
   - Expert Python 3.10+ avec focus sur qualité et architecture
   - Type hints, async/await, best practices
   - Utilisation : `@workspace utilise #file:python-expert.agent.md pour [tâche]`

2. **[markitdown-orchestrator.agent.md](.github/agents/markitdown-orchestrator.agent.md)** 🎯
   - Orchestrateur master pour workflow complet
   - Gère recherche, planification, implémentation, tests
   - Utilisation : `@workspace utilise #file:markitdown-orchestrator.agent.md pour commencer [feature]`

## 📋 Documents de Planification

### Fonctionnalités Implémentées

**Fonctionnalités actuellement disponibles dans `develop` :**

1. **Image Extraction** ✅ TERMINÉ
   - Sauvegarde physique des images PPTX dans un dossier
   - Fichier : `packages/markitdown/src/markitdown/converters/_pptx_converter.py`
   - Options : `output_images`, `image_dir`, `skip_background_images`, `skip_icon_images`

2. **SmartArt Extraction** ✅ TERMINÉ (Phase 1)
   - Extraction texte SmartArt avec hiérarchie BFS
   - Support des assistants (organigrammes)
   - Détection de cycles
   - Association images ↔ nœuds via presAssocID

### Roadmap et Processus

- **[MON_ROADMAP.md](MON_ROADMAP.md)** : Vision globale des 10+ fonctionnalités planifiées
- **[MON_PROCESS_DE_CONTRIBUTION.md](MON_PROCESS_DE_CONTRIBUTION.md)** : Guide complet du workflow Git et déploiement

## 🤖 Workflow d'Implémentation Autonome Recommandé

### Architecture : Master Orchestrator + Edge AI Tasks

Pour un **codage autonome maximal**, utiliser l'agent orchestrateur master qui gère tout le cycle de développement :

#### 🎯 Point d'Entrée Unique : Master Orchestrator

```
@workspace utilise #file:markitdown-orchestrator.agent.md pour [commande]
```

**Commandes disponibles** :
- `commencer BRIEF_01` - Démarre le développement (détection automatique de la phase)
- `continuer` - Reprend le développement où il était
- `status` - Affiche l'état actuel du projet
- `brief suivant` - Passe au brief suivant (après complétion)

**L'orchestrateur va** :
- ✅ Analyser automatiquement l'état du projet (Git, tracking files)
- ✅ Déterminer la phase nécessaire (recherche, plan, implémentation)
- ✅ Orchestrer les agents spécialisés selon la phase :
  - `task-researcher.agent.md` pour la recherche
  - `task-planner.agent.md` pour la planification
  - `python-expert.agent.md` pour l'implémentation (qualité Python maximale)
- ✅ Gérer le workflow Git (branches, commits, merge)
- ✅ Valider les tests et respecter les standards
- ✅ Gérer les dépendances entre briefs
- ✅ Fournir des rapports de progression concis

#### 🔄 Workflow Automatique (Orchestré)

**Phase 1 : Recherche** (orchestrée automatiquement)
- L'orchestrateur invoque `task-researcher.agent.md`
- Crée `.copilot-tracking/research/YYYYMMDD-[brief]-research.md`

**Phase 2 : Planification** (orchestrée automatiquement)
- L'orchestrateur invoque `task-planner.agent.md`
- Crée 3 fichiers :
  - `.copilot-tracking/plans/YYYYMMDD-[brief]-plan.instructions.md` (checkboxes)
  - `.copilot-tracking/details/YYYYMMDD-[brief]-details.md` (détails techniques)
  - `.copilot-tracking/prompts/implement-[brief].prompt.md` (prompt d'implémentation)

**Phase 3 : Implémentation** (orchestrée automatiquement)
- L'orchestrateur invoque `python-expert.agent.md`
- Implémente progressivement avec qualité Python maximale (type hints, clean architecture)
- Met à jour `.copilot-tracking/changes/YYYYMMDD-[brief]-changes.md`

**Phase 4 : Tests & Merge** (orchestrée automatiquement)
- L'orchestrateur exécute les tests
- Merge dans develop si tous les tests passent
- Push vers GitHub

#### 🆚 Ancienne vs Nouvelle Méthode

**Ancienne (3 commandes manuelles)** :
```bash
@workspace utilise #file:task-researcher.agent.md pour BRIEF_01
@workspace utilise #file:task-planner.agent.md pour BRIEF_01  
@workspace utilise #file:python-expert.agent.md pour implémenter BRIEF_01
```

**Nouvelle (1 commande orchestrée)** :
```bash
@workspace utilise #file:markitdown-orchestrator.agent.md pour commencer BRIEF_01
```

L'orchestrateur gère automatiquement les 3 phases + Git + tests + merge !

### Structure Générée

```
.copilot-tracking/
├── research/
│   ├── 20260210-brief-01-image-extraction-research.md
│   └── ...
├── plans/
│   ├── 20260210-brief-01-image-extraction-plan.instructions.md
│   └── ...
├── details/
│   ├── 20260210-brief-01-image-extraction-details.md
│   └── ...
├── prompts/
│   ├── implement-brief-01-image-extraction.prompt.md
│   └── ...
├── changes/
│   ├── 20260210-brief-01-image-extraction-changes.md
│   └── ...
├── tests/
│   └── pptx/           # Fichiers PPTX de test
│       ├── presentation-sample.pptx
│       └── ...
├── scripts/            # Scripts de debug/analyse temporaires
│   ├── debug_smartart.py
│   └── ...
└── temp/               # Fichiers temporaires divers
    └── ...
```

### 📁 Règle d'Isolation du Projet

**⚠️ CRITIQUE : Ne pas polluer l'arborescence du projet !**

Tout fichier temporaire créé par l'agent doit être stocké dans `.copilot-tracking/` :

| Type de fichier | Emplacement |
|-----------------|-------------|
| Documentation de recherche | `.copilot-tracking/research/` |
| Plans d'implémentation | `.copilot-tracking/plans/` |
| Détails techniques | `.copilot-tracking/details/` |
| Prompts générés | `.copilot-tracking/prompts/` |
| Logs de changements | `.copilot-tracking/changes/` |
| **Fichiers de test (PPTX, etc.)** | `.copilot-tracking/tests/` |
| **Scripts de debug/analyse** | `.copilot-tracking/scripts/` |
| **Fichiers temporaires** | `.copilot-tracking/temp/` |
| **Versions extraites (comparaison)** | `.copilot-tracking/versions/` |

**Interdit à la racine du projet :**
- ❌ Scripts de debug (`debug_*.py`, `test_*.py` hors `packages/*/tests/`)
- ❌ Fichiers PPTX/DOCX de test
- ❌ Documentation temporaire
- ❌ Résultats de conversion (utiliser `pptx-result/` si nécessaire pour tests manuels)

**Seuls fichiers autorisés à la racine :**
- ✅ `README.md`, `LICENSE`, `SECURITY.md`, etc. (documentation officielle)
- ✅ Fichiers de configuration (`.gitignore`, `pyproject.toml`, etc.)

## 🌳 Stratégie Git

### Structure des Branches
```
main (sync avec upstream/microsoft)
  └── develop (branche d'intégration - benoitcosials/markitdown)
       ├── feat/brief-01-image-extraction
       ├── feat/brief-02-image-descriptions
       └── feat/brief-03-chart-ascii-art
```

### Workflow Git Standard
```bash
# 1. Sync avec upstream
git fetch upstream
git checkout main
git merge upstream/main

# 2. Créer branche feature depuis develop
git checkout develop
git checkout -b feat/brief-01-image-extraction

# 3. Développer + commits réguliers
git add .
git commit -m "feat(pptx): implement image extraction to folder"

# 4. Push vers fork
git push -u origin feat/brief-01-image-extraction

# 5. Merger dans develop après tests
git checkout develop
git merge feat/brief-01-image-extraction
git push origin develop

# 6. Créer PR vers microsoft/markitdown quand prêt
```

## 📝 Standards de Code Python

### Conventions MarkItDown
- **Python** : 3.10+ avec type hints
- **Style** : PEP 8 (79 chars max, 4 espaces)
- **Imports** : Standard library en premier, puis dépendances externes
- **Tests** : pytest dans `packages/markitdown/tests/`
- **Modules** : Marqueurs `# --- MODULE: [Name] (BRIEF_XX) ---` pour nouveau code
- **Validation** : **Ruff recommandé** (linter ultra-rapide) - voir [INSTALLATION_RUFF.md](.github/INSTALLATION_RUFF.md)

### Validation Automatique avec get_errors

**CRITIQUE pour agents** : Utiliser `get_errors` tool après chaque modification de code :

```
1. Modifier fichier Python
2. Appeler get_errors sur fichier modifié
3. Si erreurs détectées → Fix immédiatement
4. Re-appeler get_errors pour vérifier
5. Seulement si aucune erreur → Continuer
```

**L'orchestrateur fait cela automatiquement !**

### Exemple de Structure de Module
```python
# packages/markitdown/src/markitdown/converters/_pptx_converter.py

# --- MODULE: Image Extraction (BRIEF_01) ---
def _save_image_to_folder(self, image_bytes, shape_name, slide_number, kwargs):
    """
    Save PPTX image to local folder.
    
    Args:
        image_bytes: Raw image data
        shape_name: Name of shape
        slide_number: Slide index
        kwargs: Converter options
    
    Returns:
        str: Relative path to saved image
    """
    # Implementation
    pass
# --- END MODULE ---
```

## 🧪 Tests et Validation

### Commandes de Test
```bash
cd packages/markitdown

# Tous les tests
pytest tests/

# Test spécifique
pytest tests/test_module_vectors.py -v

# Avec coverage
pytest tests/ --cov=src/markitdown
```

### Validation Avant Commit
- ✅ Tous les tests passent
- ✅ Code suit les conventions du projet
- ✅ Pas d'erreurs dans `get_errors` VS Code
- ✅ Documentation/commentaires à jour

## 🚀 État du Développement

### Fonctionnalités Complétées

| Feature | Status | Description |
|---------|--------|-------------|
| Image Extraction | ✅ TERMINÉ | Sauvegarde images PPTX vers dossier |
| SmartArt Phase 1 | ✅ TERMINÉ | Extraction texte avec hiérarchie BFS |

### Workflow pour Nouvelles Fonctionnalités

Pour développer une nouvelle fonctionnalité :

```bash
# 1. Créer une branche feature depuis develop
git checkout develop
git checkout -b feat/[nom-feature]

# 2. Utiliser l'orchestrateur pour le workflow complet
@workspace utilise #file:markitdown-orchestrator.agent.md pour commencer [description]

# 3. Après implémentation et tests, merger dans develop
git checkout develop
git merge feat/[nom-feature]
git push origin develop
```

## 🔧 Configuration MCP et Tests

### Test Local avec MCP
```bash
# Installer en mode développement
pip install -e ".[all]"
pip install -e packages/markitdown-mcp

# Tester le convertisseur
python -m markitdown test.pptx
```

### Configuration pour Testeurs (après implémentation)
Les testeurs pourront utiliser votre branche directement :
```json
{
  "mcpServers": {
    "markitdown-test": {
      "type": "stdio",
      "command": "python",
      "args": [
        "-m",
        "markitdown_mcp",
        "--source",
        "git+https://github.com/benoitcosials/markitdown.git@feat/brief-01-image-extraction"
      ]
    }
  }
}
```

## 📚 Références Rapides

### Fichiers Clés du Projet
- `packages/markitdown/src/markitdown/converters/_pptx_converter.py` - Convertisseur PPTX principal
- `packages/markitdown/src/markitdown/_llm_caption.py` - LLM descriptions existantes
- `packages/markitdown-mcp/src/markitdown_mcp/__main__.py` - Interface MCP
- `packages/markitdown/tests/test_module_vectors.py` - Tests principaux

### Remotes Git
- **origin** : `https://github.com/benoitcosials/markitdown.git` (votre fork)
- **upstream** : `https://github.com/microsoft/markitdown.git` (Microsoft original)

### Dépendances Principales
- `python-pptx` : Parsing PPTX
- `mammoth` : Conversion DOCX
- `pdfminer.six` : Parsing PDF
- `FastMCP` : Serveur MCP (markitdown-mcp)

## 💡 Commandes Rapides

### Démarrage Session
```bash
# Vérifier branche
git branch

# Vérifier status
git status

# Voir dernier commit
git log --oneline -5
```

### Commandes Orchestrateur (RECOMMANDÉ)
```
# Démarrer le développement (détection automatique)
@workspace utilise #file:markitdown-orchestrator.agent.md pour commencer BRIEF_01

# Reprendre après interruption
@workspace utilise #file:markitdown-orchestrator.agent.md pour continuer

# Vérifier l'état actuel
@workspace utilise #file:markitdown-orchestrator.agent.md pour status

# Passer au brief suivant
@workspace utilise #file:markitdown-orchestrator.agent.md pour brief suivant
```

### Agents Spécialisés (Si orchestration manuelle nécessaire)
```
@workspace utilise #file:task-researcher.agent.md pour [tâche]
@workspace utilise #file:task-planner.agent.md pour [tâche]
@workspace utilise #file:python-expert.agent.md pour implémenter [tâche]
```

---

**Note** : Ce fichier est automatiquement chargé par GitHub Copilot à chaque session VS Code dans ce workspace.
