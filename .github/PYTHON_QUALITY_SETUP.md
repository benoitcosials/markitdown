# Instructions et Agents GitHub Copilot - Installation Permanente

**Date d'installation** : 20 février 2026  
**Objectif** : Garantir du code Python de qualité maximale pour BRIEF_02 et projets futurs

## 📦 Fichiers Installés

### Instructions Python (.github/instructions/)
✅ **python.instructions.md**
- Conventions PEP 8
- Type hints (typing module)
- Docstrings PEP 257
- Gestion edge cases et tests
- S'applique à : `**/*.py`

✅ **self-explanatory-code.instructions.md**
- Code auto-documenté (WHY pas WHAT)
- Annotations (TODO, FIXME, NOTE, SECURITY, etc.)
- Éviter commentaires évidents
- S'applique à : tous fichiers

### Agents Experts (.github/agents/)
✅ **python-expert.agent.md**
- Expert Python 3.10+ (type hints, async/await)
- Architecture propre (SOLID, patterns)
- Tests (pytest, TDD, mocking)
- Spécialisé BRIEF_02 (modes adaptatifs LLM)

✅ **markitdown-orchestrator.agent.md** (déjà existant)
- Orchestrateur master pour workflow complet
- Gère recherche → plan → implémentation → tests

### Documentation
✅ **instructions/README.md** - Guide des instructions
✅ **agents/README.md** - Guide des agents

## 🚀 Utilisation

### Chargement Automatique
GitHub Copilot charge automatiquement les instructions depuis `.github/instructions/` lors de l'ouverture du workspace dans VS Code.

### Agents Disponibles

**Pour BRIEF_02 (implémentation complète)** :
```
@workspace utilise #file:python-expert.agent.md pour implémenter BRIEF_02
```

**Pour workflow orchestré (automatique)** :
```
@workspace utilise #file:markitdown-orchestrator.agent.md pour commencer BRIEF_02
```

## 🔄 Comparaison Workflow

### Ancienne Méthode (Awesome-Copilot dynamique)
```
# Charger depuis MCP à chaque session
mcp_awesome-copil_load_instruction python.instructions.md
mcp_awesome-copil_load_instruction python-expert.agent.md
```
❌ Nécessite rechargement manuel  
❌ Dépend de la connexion MCP

### Nouvelle Méthode (Installation permanente)
```
# Instructions chargées automatiquement au démarrage VS Code
# Agents disponibles via #file:
@workspace utilise #file:python-expert.agent.md pour [tâche]
```
✅ Chargement automatique  
✅ Indépendant de MCP  
✅ Disponible offline  
✅ Versionné avec Git

## 📋 Statut Projet

### BRIEF_01 ✅ TERMINÉ (5h)
- Extraction images PPTX
- Alt text vides si absents PowerPoint
- Tests passés : 7/7 fichiers, 23 images

### BRIEF_02 🚧 EN COURS (8h estimés)
- Descriptions LLM adaptatives
- Mode 1 : Alt text enrichi (si absent)
- Mode 2 : Descriptions complètes
- **Agent Python Expert activé** pour qualité maximale

### BRIEF_03 ⏳ À VENIR
- ASCII art pour charts statistiques
- Dépend de BRIEF_01 ✅

## 🎯 Avantages Installation Permanente

1. **Qualité Code Garantie**
   - Standards Python appliqués systématiquement
   - Type hints obligatoires
   - Docstrings PEP 257

2. **Productivité**
   - Pas de rechargement manuel
   - Suggestions Copilot plus pertinentes
   - Agents experts disponibles immédiatement

3. **Maintenance**
   - Instructions versionnées avec Git
   - Modifications trackées
   - Partageables avec équipe

4. **Indépendance**
   - Fonctionne sans MCP
   - Disponible offline
   - Pas de dépendances externes

## 📚 Références

**Source originale** : awesome-copilot collections
- `python.instructions.md` : Standards Python
- `self-explanatory-code.instructions.md` : Clean code
- `python-mcp-expert.agent.md` : Expert Python (adapté pour MarkItDown)

**Documentation projet** :
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Workflow principal
- [.github/instructions/README.md](.github/instructions/README.md) - Guide instructions
- [.github/agents/README.md](.github/agents/README.md) - Guide agents

## ✅ Prochaines Étapes

1. Démarrer BRIEF_02 avec Python Expert
2. Implémenter modes adaptatifs (Mode 1 & Mode 2)
3. Tester exhaustivement les deux modes
4. Valider avec l'orchestrateur
5. Merger dans develop

---

**Note** : Cette installation garantit un code de qualité production pour le reste du projet MarkItDown.
