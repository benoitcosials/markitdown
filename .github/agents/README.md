# Agents GitHub Copilot pour MarkItDown

Ce répertoire contient les agents spécialisés qui assistent le développement du projet MarkItDown.

## 🤖 Agents Disponibles

### [markitdown-orchestrator.agent.md](markitdown-orchestrator.agent.md)
**Type** : Orchestrateur Master  
**Rôle** : Gère le workflow complet de développement

**Capacités** :
- Détection automatique de la phase (recherche, plan, implémentation)
- Orchestration des agents spécialisés (task-researcher, task-planner, python-expert)
- Gestion Git (branches, commits, merge)
- Validation des tests
- Gestion des dépendances entre briefs

**Utilisation** :
```
@workspace utilise #file:markitdown-orchestrator.agent.md pour commencer BRIEF_02
@workspace utilise #file:markitdown-orchestrator.agent.md pour continuer
@workspace utilise #file:markitdown-orchestrator.agent.md pour status
```

### [python-expert.agent.md](python-expert.agent.md)
**Type** : Expert Technique Python  
**Rôle** : Assistance spécialisée pour développement Python de qualité

**Expertise** :
- Python 3.10+ (type hints, async/await, decorators)
- Architecture propre (SOLID, design patterns)
- Validation de données (Pydantic, dataclasses)
- Tests (pytest, TDD, mocking)
- Best practices (PEP 8, error handling, performance)

**Utilisation** :
```
@workspace utilise #file:python-expert.agent.md pour implémenter BRIEF_02
@workspace utilise #file:python-expert.agent.md pour revoir le code de _pptx_converter.py
```

**Focus BRIEF_02** :
- Implémentation des modes adaptatifs (Mode 1 & Mode 2)
- Intégration avec OpenAI API
- Gestion d'images (Pillow/io.BytesIO)
- Tests complets des deux modes

## 🎯 Workflow Recommandé

### Approche 1 : Orchestration Complète (Recommandé)
Pour un développement autonome end-to-end :
```
@workspace utilise #file:markitdown-orchestrator.agent.md pour commencer BRIEF_02
```

L'orchestrateur gère automatiquement toutes les phases.

### Approche 2 : Expert Python Manuel
Pour un contrôle fin sur l'implémentation :
```
@workspace utilise #file:python-expert.agent.md pour [tâche spécifique]
```

Utile pour :
- Code reviews
- Refactoring ciblé
- Résolution de bugs
- Optimisations

## 📦 Structure de Suivi

Les agents génèrent des fichiers de tracking dans `.copilot-tracking/` :

```
.copilot-tracking/
├── research/         # Recherche initiale (task-researcher)
├── plans/            # Plans d'implémentation (task-planner)
├── details/          # Détails techniques
├── prompts/          # Prompts d'implémentation
└── changes/          # Journal des changements
```

## 📚 Sources

Ces agents s'inspirent de collections externes :
- **markitdown-orchestrator** : Développé spécifiquement pour ce projet
- **python-expert** : Basé sur `python-mcp-expert` d'awesome-copilot, adapté pour MarkItDown

## 🔄 Maintenance

Pour ajouter un nouvel agent :
1. Créer `nom-agent.agent.md` dans ce répertoire
2. Définir la description, le nom, et les capacités
3. Référencer dans `.github/copilot-instructions.md`
4. Tester avec des commandes réelles

---

**Note** : Ces agents complètent les instructions définies dans `.github/instructions/` et le workflow principal `.github/copilot-instructions.md`.
