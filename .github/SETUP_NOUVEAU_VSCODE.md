# 🔧 Configuration Nouveau VS Code - Guide Rapide

## 📋 Vue d'Ensemble

Ce guide explique comment configurer **un nouveau VS Code** pour utiliser votre fork `benoitcosials/markitdown` et tester l'orchestrateur avant de commencer les modifications.

---

## 🚀 Configuration Initiale (5 minutes)

### Étape 1 : Cloner le Repository

```powershell
# Dans un nouveau terminal PowerShell
cd C:\Repos  # Ou votre dossier de projets

# Cloner votre fork (avec la branche develop)
git clone https://github.com/benoitcosials/markitdown.git markitdown-test

# Entrer dans le dossier
cd markitdown-test

# Vérifier que develop existe
git branch -a

# Basculer sur develop
git checkout develop

# Vérifier l'état
git log --oneline -5
```

**Résultat attendu** :
- Dossier `C:\Repos\markitdown-test` créé
- Branche `develop` active
- Commit `4b47fab` visible (orchestrateur master)

---

### Étape 2 : Ouvrir dans un Nouveau VS Code

#### Option A : Nouvelle fenêtre VS Code
```powershell
# Depuis C:\Repos\markitdown-test
code .
```

#### Option B : Workspace séparé
```powershell
# Ouvrir VS Code depuis le menu Démarrer
# Fichier > Ouvrir le dossier > C:\Repos\markitdown-test
```

---

### Étape 3 : Vérifier Extensions Nécessaires

**Extensions OBLIGATOIRES** :

1. ✅ **GitHub Copilot** (`GitHub.copilot`)
   - Menu : Extensions → Rechercher "GitHub Copilot" → Installer
   
2. ✅ **Awesome Copilot** (pour les agents)
   - Menu : Extensions → Rechercher "Awesome Copilot" → Installer
   
3. ✅ **Python** (`ms-python.python`)
   - Menu : Extensions → Rechercher "Python" → Installer

**Extensions RECOMMANDÉES** :
- Python Debugger (`ms-python.debugpy`)
- Pylance (`ms-python.vscode-pylance`)
- Git Graph (`mhutchie.git-graph`)

**Vérification** :
```
Ctrl+Shift+P → "Extensions: Show Installed Extensions"
```

---

### Étape 4 : Configuration Automatique

**Les fichiers suivants sont déjà dans le repo** :

✅ **`.vscode/settings.json`** - Configuration optimale du workspace
- Modèle Claude Sonnet 4.5
- Python PEP 8 standards
- Git auto-fetch
- Associations fichiers agent.md

✅ **`.github/copilot-instructions.md`** - Instructions auto-chargées
- Contexte projet
- Référence aux 3 briefs
- Workflow orchestrateur
- Standards de code

✅ **`.github/agents/markitdown-orchestrator.agent.md`** - Orchestrateur master

**Aucune configuration manuelle nécessaire !** 🎉

---

### Étape 5 : Installer Environnement Python

```powershell
# Vérifier Python 3.10+
python --version  # Doit afficher 3.10 ou supérieur

# Créer environnement virtuel
python -m venv .venv

# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Installer les dépendances en mode éditable
pip install -e "packages/markitdown[all]"
pip install -e packages/markitdown-mcp

# Installer pytest pour les tests
pip install pytest pytest-cov
```

**Résultat attendu** :
- `.venv` créé dans le dossier
- Toutes les dépendances installées sans erreur
- `markitdown` installé en mode éditable

---

## ✅ Validation de l'Installation

### Test 1 : Copilot Instructions Auto-Chargées

**Ouvrir Copilot Chat** (`Ctrl+Shift+I` ou clic sur l'icône chat)

**Taper** :
```
@workspace ouvre BRIEF_01_IMAGE_EXTRACTION.md
```

**Résultat attendu** : Le fichier BRIEF_01 s'ouvre automatiquement.

---

### Test 2 : Orchestrateur Disponible

**Dans Copilot Chat, taper** :
```
@workspace utilise #file:markitdown-orchestrator.agent.md pour status
```

**Résultat attendu** :
- L'agent analyse l'état du projet
- Affiche la branche actuelle (develop)
- Indique qu'aucune recherche/plan n'existe pour BRIEF_01
- Propose de commencer la phase de recherche

---

### Test 3 : Tests Existants Passent

```powershell
# Depuis le terminal VS Code (avec .venv activé)
cd packages/markitdown
pytest tests/ -v
```

**Résultat attendu** :
- Tous les tests existants passent ✅
- Aucune erreur de dépendances
- Temps d'exécution < 1 minute

---

### Test 4 : Git Configuration Correcte

```powershell
# Vérifier les remotes
git remote -v
```

**Résultat attendu** :
```
origin  https://github.com/benoitcosials/markitdown.git (fetch)
origin  https://github.com/benoitcosials/markitdown.git (push)
```

**Si vous voulez ajouter upstream** :
```powershell
git remote add upstream https://github.com/microsoft/markitdown.git
git fetch upstream
```

---

## 🎯 État Après Configuration

**Vous devriez avoir** :
- ✅ VS Code ouvert sur `C:\Repos\markitdown-test`
- ✅ Branche `develop` active
- ✅ Extensions installées (Copilot + Awesome Copilot + Python)
- ✅ Environnement Python `.venv` créé et activé
- ✅ Dépendances installées en mode éditable
- ✅ Tests existants qui passent
- ✅ Copilot instructions auto-chargées
- ✅ Orchestrateur disponible via `#file:markitdown-orchestrator.agent.md`

---

## 🚀 Lancer le Développement (Test)

**Une fois validé, vous pouvez lancer** :

```
@workspace utilise #file:markitdown-orchestrator.agent.md pour commencer BRIEF_01
```

**L'orchestrateur va** :
1. Analyser l'état du projet (Git + tracking files)
2. Déterminer qu'aucune recherche n'existe
3. Invoquer `task-researcher.agent.md` automatiquement
4. Créer `.copilot-tracking/research/20260210-brief-01-image-extraction-research.md`
5. Passer automatiquement à la planification
6. Et continuer jusqu'à l'implémentation complète

**IMPORTANT** : Ceci est un **test en lecture seule** dans la nouvelle instance. Aucune modification ne sera poussée vers GitHub depuis cette instance tant que vous ne faites pas de `git push`.

---

## 🔄 Workflow Recommandé

### Instance 1 (C:\Repos\markitdown) - PRODUCTION
- **Branche** : develop
- **Usage** : Développement principal, commits, push vers GitHub
- **Orchestrateur** : Active pour implémentation réelle

### Instance 2 (C:\Repos\markitdown-test) - TEST
- **Branche** : develop (lecture seule ou branche test)
- **Usage** : Validation, expérimentation, tests isolés
- **Orchestrateur** : Active pour simulation

**Synchronisation** :
```powershell
# Dans markitdown-test, pour récupérer les derniers changements
cd C:\Repos\markitdown-test
git fetch origin
git pull origin develop
```

---

## ⚠️ Troubleshooting

### Problème : "Python not found"
**Solution** :
```powershell
# Vérifier Python installé
python --version

# Ou utiliser py launcher
py -3.10 -m venv .venv
```

### Problème : "No module named 'markitdown'"
**Solution** :
```powershell
# Réinstaller en mode éditable
pip install -e "packages/markitdown[all]"
```

### Problème : "Git push rejected"
**C'est normal !** Instance test ne devrait pas push. Si vous voulez push :
```powershell
# Vérifier remote
git remote -v

# Devrait pointer vers benoitcosials/markitdown
```

### Problème : "Copilot instructions not loaded"
**Solution** :
```powershell
# Recharger la fenêtre VS Code
Ctrl+Shift+P → "Developer: Reload Window"
```

### Problème : "Orchestrator file not found"
**Solution** :
```powershell
# Vérifier que le fichier existe
ls .github/agents/markitdown-orchestrator.agent.md

# Si absent, pull depuis origin
git pull origin develop
```

---

## 📊 Comparaison Instance 1 vs Instance 2

| Aspect | Instance PRODUCTION | Instance TEST |
|--------|---------------------|---------------|
| Chemin | `C:\Repos\markitdown` | `C:\Repos\markitdown-test` |
| Branche | `develop` | `develop` (ou `test-branch`) |
| Commits | ✅ Autorisés | ⚠️ Locaux seulement |
| Push GitHub | ✅ Actif | ❌ Éviter |
| Usage | Développement réel | Validation/Expérimentation |
| Config partagée | ✅ Sync auto Git | ✅ Sync auto Git |

---

## 🎓 Prochaines Étapes

**Après validation complète dans l'instance TEST** :

1. ✅ Retourner à l'instance PRODUCTION (`C:\Repos\markitdown`)
2. ✅ Lancer l'orchestrateur pour BRIEF_01 :
   ```
   @workspace utilise #file:markitdown-orchestrator.agent.md pour commencer BRIEF_01
   ```
3. ✅ L'orchestrateur gère automatiquement tout le workflow
4. ✅ Les modifications seront commitées et pushées vers GitHub

---

**Questions ou problèmes ?** L'orchestrateur peut vous aider à diagnostiquer :
```
@workspace utilise #file:markitdown-orchestrator.agent.md pour status
```
