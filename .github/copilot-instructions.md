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

## 📋 Documents de Planification

### Briefs Techniques Disponibles

Trois briefs techniques détaillés sont disponibles à la racine du projet :

1. **[BRIEF_01_IMAGE_EXTRACTION.md](../BRIEF_01_IMAGE_EXTRACTION.md)** (5h) - Priorité CRITIQUE
   - Fonctionnalité : Sauvegarde physique des images PPTX dans un dossier
   - Fichier cible : `packages/markitdown/src/markitdown/converters/_pptx_converter.py`
   - Bug à corriger : Images génèrent des liens cassés (`![](image.jpg)` sans fichier)
   
2. **[BRIEF_02_IMAGE_TEXT_DESCRIPTIONS.md](../BRIEF_02_IMAGE_TEXT_DESCRIPTIONS.md)** (4h) - Priorité MOYENNE
   - Fonctionnalité : Descriptions LLM pour toutes les images (sauf charts)
   - Dépendance : BRIEF_01 doit être implémenté en premier
   - Format : Blocs ```image-description
   
3. **[BRIEF_03_CHART_ASCII_ART.md](../BRIEF_03_CHART_ASCII_ART.md)** (8h) - Priorité MOYENNE
   - Fonctionnalité : ASCII art pour charts statistiques (bar, pie, column, line)
   - Dépendance : BRIEF_01 doit être implémenté en premier
   - Format : Blocs ```ascii-chart avec caractères █ et ░

### Roadmap et Processus

- **[MON_ROADMAP.md](../MON_ROADMAP.md)** : Vision globale des 10+ fonctionnalités planifiées
- **[MON_PROCESS_DE_CONTRIBUTION.md](../MON_PROCESS_DE_CONTRIBUTION.md)** : Guide complet du workflow Git et déploiement

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
  - `task-implementation.instructions.md` pour l'implémentation
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
- L'orchestrateur invoque `task-implementation.instructions.md`
- Implémente progressivement avec validation continue
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
@workspace utilise #file:task-implementation.instructions.md
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
│   ├── 20260210-brief-02-image-descriptions-research.md
│   └── 20260210-brief-03-chart-ascii-research.md
├── plans/
│   ├── 20260210-brief-01-image-extraction-plan.instructions.md
│   ├── 20260210-brief-02-image-descriptions-plan.instructions.md
│   └── 20260210-brief-03-chart-ascii-plan.instructions.md
├── details/
│   ├── 20260210-brief-01-image-extraction-details.md
│   ├── 20260210-brief-02-image-descriptions-details.md
│   └── 20260210-brief-03-chart-ascii-details.md
├── prompts/
│   ├── implement-brief-01-image-extraction.prompt.md
│   ├── implement-brief-02-image-descriptions.prompt.md
│   └── implement-brief-03-chart-ascii.prompt.md
└── changes/
    ├── 20260210-brief-01-image-extraction-changes.md
    ├── 20260210-brief-02-image-descriptions-changes.md
    └── 20260210-brief-03-chart-ascii-changes.md
```

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

## 🚀 Ordre d'Implémentation Recommandé

### Sprint 1 : BRIEF_01 (Critique)
**Priorité** : 🔴 CRITIQUE  
**Estimation** : 5h  
**Objectif** : Corriger le bug des images cassées

**Commandes** :
```bash
git checkout develop
git checkout -b feat/brief-01-image-extraction

# Phase 1 : Recherche
@workspace utilise #file:task-researcher.agent.md pour BRIEF_01

# Phase 2 : Planification
@workspace utilise #file:task-planner.agent.md pour BRIEF_01

# Phase 3 : Implémentation
@workspace utilise #file:task-implementation.instructions.md
```

### Sprint 2 : BRIEF_02 (Dépend de BRIEF_01)
**Priorité** : 🟡 MOYENNE  
**Estimation** : 4h  
**Objectif** : Descriptions LLM pour images

**Prérequis** : BRIEF_01 doit être mergé dans develop

### Sprint 3 : BRIEF_03 (Dépend de BRIEF_01)
**Priorité** : 🟡 MOYENNE  
**Estimation** : 8h  
**Objectif** : ASCII art pour charts

**Prérequis** : BRIEF_01 doit être mergé dans develop

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
@workspace utilise #file:task-implementation.instructions.md
```

### Ouvrir un Brief
```
@workspace ouvre BRIEF_01_IMAGE_EXTRACTION.md
@workspace ouvre BRIEF_02_IMAGE_TEXT_DESCRIPTIONS.md
@workspace ouvre BRIEF_03_CHART_ASCII_ART.md
```

---

**Note** : Ce fichier est automatiquement chargé par GitHub Copilot à chaque session VS Code dans ce workspace.
