# 🔧 Configuration Persistante du Setup AI

## 📋 Vue d'Ensemble

Ce guide explique comment **persister votre configuration AI** entre plusieurs sessions VS Code pour maximiser l'autonomie sur le projet markitdown.

---

## 1️⃣ Instructions Workspace Automatiques

### ✅ Déjà Configuré

Le fichier **`.github/copilot-instructions.md`** est automatiquement chargé par GitHub Copilot à **chaque ouverture de VS Code** dans ce workspace.

**Contient** :
- Contexte du projet
- Références aux 3 briefs techniques
- Workflow Edge AI Tasks complet
- Stratégie Git et branches
- Standards de code Python
- Commandes rapides

**Avantages** :
- ✅ Aucune configuration manuelle par session
- ✅ Commité dans le repo (partageable avec l'équipe)
- ✅ Automatiquement lu par Copilot
- ✅ Synchronisé avec votre fork GitHub

---

## 2️⃣ Agents Awesome-Copilot (Déjà Activés)

### Configuration MCP Awesome-Copilot

Les agents suivants sont **déjà disponibles** via l'extension awesome-copilot installée dans VS Code :

#### Agents Disponibles
1. **task-researcher.agent.md** - Recherche approfondie du codebase
2. **task-planner.agent.md** - Planification structurée avec tracking
3. **task-implementation.instructions.md** - Implémentation autonome progressive

### Comment Utiliser
```
@workspace utilise #file:task-researcher.agent.md pour [description]
@workspace utilise #file:task-planner.agent.md pour [description]
@workspace utilise #file:task-implementation.instructions.md
```

**Persistence** :
- ✅ Agents chargés automatiquement via extension awesome-copilot
- ✅ Disponibles dans toutes les sessions VS Code
- ✅ Pas de configuration par projet nécessaire

---

## 3️⃣ Configuration VS Code (Optionnel)

### Fichier `.vscode/settings.json`

Pour des **paramètres spécifiques au projet** (optionnel) :

```json
{
  "github.copilot.advanced": {
    "debug.overrideEngine": "gpt-4",
    "inlineSuggest.enable": true
  },
  "files.associations": {
    "*.md": "markdown"
  },
  "editor.formatOnSave": false,
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
}
```

**Commiter ce fichier** pour partager avec testeurs.

---

## 4️⃣ Tracking de Progression (.copilot-tracking/)

### Structure Automatique

Le workflow Edge AI Tasks crée automatiquement cette structure :

```
.copilot-tracking/
├── research/           # Résultats de recherche
├── plans/              # Plans avec checkboxes
├── details/            # Détails techniques
├── prompts/            # Prompts d'implémentation
└── changes/            # Tracking des modifications
```

### Persistence

**Option A : Commiter dans le repo** (Recommandé pour votre usage)
```bash
# Ajouter au repo pour synchroniser entre machines
git add .copilot-tracking/
git commit -m "docs: add implementation tracking"
git push origin develop
```

**Option B : Garder local** (Ne pas commiter dans PR finale vers Microsoft)
```bash
# Ajouter à .gitignore si vous voulez garder privé
echo ".copilot-tracking/" >> .gitignore
```

**Recommandation** : 
- ✅ Commiter sur votre branche `develop` pour synchronisation
- ✅ Ne pas inclure dans les PRs vers `microsoft/markitdown`
- ✅ Permet de reprendre exactement où vous étiez à chaque session

---

## 5️⃣ État de Session (Automatique)

### VS Code Sauvegarde Automatiquement

VS Code garde en mémoire :
- ✅ Fichiers ouverts
- ✅ Position du curseur
- ✅ Breakpoints
- ✅ Terminal history
- ✅ Git branch active

**Aucune action requise** - c'est natif VS Code.

---

## 6️⃣ Checklist Démarrage Nouvelle Session

Quand vous ouvrez VS Code pour continuer le travail :

### 🔄 Vérifications Automatiques (0 action)
- ✅ `.github/copilot-instructions.md` chargé automatiquement
- ✅ Agents awesome-copilot disponibles
- ✅ Fichiers de tracking synchronisés (si commités)

### ✅ Vérifications Manuelles (3 commandes)
```bash
# 1. Vérifier branche active
git branch

# 2. Voir derniers commits
git log --oneline -5

# 3. Vérifier fichiers tracking si continuation d'un sprint
ls .copilot-tracking/plans/
```

### 🚀 Reprendre le Travail

**Si nouveau brief** :
```
@workspace utilise #file:task-researcher.agent.md pour BRIEF_01
```

**Si continuation d'un plan existant** :
```
@workspace utilise #file:task-implementation.instructions.md pour continuer le plan
```

L'agent va automatiquement :
- ✅ Lire les fichiers de tracking existants
- ✅ Voir les tâches marquées `[x]`
- ✅ Reprendre à la prochaine tâche non complétée `[ ]`

---

## 7️⃣ Synchronisation Multi-Machines

### Workflow Git Complet

Pour travailler depuis **plusieurs machines** :

#### Machine 1 → Git Push
```bash
# Sauvegarder votre travail
git add .copilot-tracking/ BRIEF_*.md MON_*.md
git commit -m "wip: progress on BRIEF_01"
git push origin develop
```

#### Machine 2 → Git Pull
```bash
# Récupérer votre travail
git checkout develop
git pull origin develop

# Reprendre exactement où vous étiez
@workspace utilise #file:task-implementation.instructions.md
```

**Le workflow reprendra automatiquement** car :
- ✅ Plans avec checkboxes synchronisés
- ✅ Changes files à jour
- ✅ Instructions workspace disponibles

---

## 8️⃣ Configuration MCP (Avancé)

### Pour Testeurs Externes

Si vous voulez que des **testeurs utilisent votre branche** via MCP :

**Fichier à créer** : `docs/iA-markitdown-test-config.json`
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

**Mettre à jour la branche** après chaque push :
```json
"git+https://github.com/benoitcosials/markitdown.git@feat/brief-02-image-descriptions"
```

---

## 9️⃣ Troubleshooting

### Problème : Instructions pas chargées

**Solution** :
```bash
# Recharger la fenêtre VS Code
Ctrl+Shift+P → "Developer: Reload Window"
```

### Problème : Agents awesome-copilot introuvables

**Vérification** :
```
@workspace /extensions
```

**Si manquant** :
```bash
# Réinstaller l'extension
code --install-extension <awesome-copilot-extension-id>
```

### Problème : Tracking files manquants après pull

**Solution** :
```bash
# Vérifier si .copilot-tracking/ est dans .gitignore
cat .gitignore | grep copilot

# Si oui, commenter la ligne ou la retirer
```

---

## 🎯 Résumé : Configuration Persistante

| Élément | Persistence | Configuration Requise |
|---------|-------------|----------------------|
| Instructions Workspace (`.github/copilot-instructions.md`) | ✅ Automatique | ✅ Déjà fait |
| Agents awesome-copilot | ✅ Extension installée | ✅ Déjà fait |
| Tracking files (`.copilot-tracking/`) | ⚠️ Si commité dans Git | ⏳ À décider |
| VS Code state (fichiers ouverts, terminal) | ✅ Automatique | ✅ Natif VS Code |
| Git branches et commits | ✅ Automatique | ✅ Déjà synchro |

**Total Configuration Par Session** : **0 étape** 🎉

Tout est **automatique** dès que vous ouvrez le workspace dans VS Code !

---

## 📝 Commandes Rapides de Synchronisation

### Sauvegarder Progression
```bash
git add .
git commit -m "wip: [description courte]"
git push origin develop
```

### Récupérer Progression
```bash
git pull origin develop
```

### Vérifier État
```bash
git status
git branch -vv
ls .copilot-tracking/plans/
```

---

**✅ Configuration terminée** - Votre setup AI est maintenant **persistant entre toutes les sessions** !
