# 🔧 Installation Extension Ruff - Guide Rapide

## 📋 Pourquoi Ruff ?

**Ruff est recommandé pour développement avec agents AI** :
- ✅ **Ultra-rapide** : 10-100x plus rapide que flake8/pylint
- ✅ **Tout-en-un** : Linting + formatting + import sorting
- ✅ **Validation temps réel** : Les agents détectent erreurs immédiatement
- ✅ **Compatible PEP 8** : Respecte les standards Python du projet
- ✅ **Aucune modification du projet upstream** : Configuration locale seulement

---

## 🚀 Installation (2 minutes)

### Méthode 1 : Via VS Code Marketplace (Recommandé)

1. **Ouvrir Extensions** : `Ctrl+Shift+X`
2. **Rechercher** : "Ruff"
3. **Installer** : Extension par **Astral Software** (`charliermarsh.ruff`)
4. **Recharger** : `Ctrl+Shift+P` → "Developer: Reload Window"

### Méthode 2 : Via Commande

```powershell
# Installer Ruff en tant qu'outil Python (optionnel - extension suffit)
pip install ruff
```

### Méthode 3 : Extensions recommandées

**Créer fichier `.vscode/extensions.json`** (déjà configuré) :
```json
{
  "recommendations": [
    "GitHub.copilot",
    "GitHub.copilot-chat",
    "charliermarsh.ruff",
    "ms-python.python",
    "ms-python.vscode-pylance"
  ]
}
```

VS Code proposera automatiquement l'installation.

---

## ✅ Validation Installation

### Test 1 : Vérifier Extension Active

1. **Ouvrir un fichier Python** : `packages/markitdown/src/markitdown/_markitdown.py`
2. **Faire une erreur intentionnelle** :
   ```python
   import os
   x=1+2  # Pas d'espace autour de =
   ```
3. **Vérifier soulignement** : Ruff doit souligner `x=1+2`
4. **Hover sur l'erreur** : Message "Missing whitespace around operator"

### Test 2 : Quick Fix Automatique

1. **Sur l'erreur**, cliquer sur l'ampoule 💡
2. **Sélectionner** : "Ruff: Fix all auto-fixable problems"
3. **Résultat** : `x = 1 + 2` (corrigé automatiquement)

### Test 3 : Validation avec VS Code Tools

**Dans Copilot Chat** :
```
@workspace utilise get_errors pour packages/markitdown/src/markitdown/_markitdown.py
```

**Résultat attendu** : Liste des erreurs détectées par Ruff (si erreurs présentes)

---

## 🤖 Intégration avec les Agents

### Configuration Automatique (Déjà Faite)

**Fichier `.vscode/settings.json`** :
```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": false,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  },
  
  "ruff.enable": true,
  "ruff.lint.enable": true,
  "ruff.lint.run": "onType",  // Validation temps réel
  "ruff.lint.args": [
    "--line-length=79",
    "--extend-ignore=E203,W503,N802,N806"
  ]
}
```

### Workflow Agents (Automatique)

**L'orchestrateur utilise automatiquement `get_errors` tool** :

1. **Agent modifie du code** (ex: ajoute fonction dans `_pptx_converter.py`)
2. **Agent appelle** : `get_errors` pour ce fichier
3. **Si erreurs Ruff détectées** :
   ```
   Error: E501 Line too long (85 > 79 characters)
   Error: F401 'os' imported but unused
   ```
4. **Agent corrige automatiquement** :
   - Casse ligne longue
   - Supprime import inutilisé
5. **Agent re-valide** : `get_errors` → ✅ Aucune erreur
6. **Agent marque tâche complète** : `[x]`

### Commandes Agent (Intégrées dans Orchestrateur)

**Phase Implémentation** :
```
Pour chaque tâche :
1. Faire modification code
2. Appeler get_errors sur fichier modifié
3. Si erreurs : Fix automatiquement
4. Re-appeler get_errors pour vérifier
5. Si aucune erreur : Marquer [x]
```

**Phase Validation Finale** :
```
Avant merge :
1. get_errors sur TOUS les fichiers modifiés
2. Fix toutes les erreurs
3. pytest tests/ -v
4. Si tout OK : merge develop
```

---

## 🎯 Règles Ruff Activées

### Règles Principales (Compatible PEP 8)

| Code | Description | Exemple |
|------|-------------|---------|
| E501 | Line too long | Max 79 caractères |
| E401 | Multiple imports on one line | `import os, sys` → Erreur |
| F401 | Unused import | `import os` sans utilisation |
| F821 | Undefined name | `print(variable_inexistante)` |
| W291 | Trailing whitespace | Espaces en fin de ligne |
| E302 | Expected 2 blank lines | Entre fonctions top-level |

### Règles Ignorées (Projet Specifique)

| Code | Raison |
|------|--------|
| E203 | Whitespace before ':' (conflits avec black) |
| W503 | Line break before binary operator (style préféré) |
| N802 | Function name lowercase (compatibilité API) |
| N806 | Variable lowercase (compatibilité) |

---

## 💡 Utilisation Manuelle (Optionnelle)

### Formater un Fichier

**Option 1 : VS Code**
- `Shift+Alt+F` (format document)
- Ruff formate automatiquement

**Option 2 : Terminal**
```powershell
# Formater un fichier
ruff format packages/markitdown/src/markitdown/_pptx_converter.py

# Formater tout le projet
ruff format packages/markitdown/src/
```

### Linter un Fichier

```powershell
# Check erreurs
ruff check packages/markitdown/src/markitdown/_pptx_converter.py

# Fix automatiquement
ruff check --fix packages/markitdown/src/markitdown/_pptx_converter.py

# Check tout le projet
ruff check packages/markitdown/src/
```

### Organiser Imports

```powershell
# Fix imports
ruff check --select I --fix packages/markitdown/src/markitdown/_pptx_converter.py
```

---

## 🔄 Fallback : Si Ruff Non Installé

**Le projet fonctionne aussi avec flake8** (configuré en fallback dans `.vscode/settings.json`) :

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": [
    "--max-line-length=79",
    "--extend-ignore=E203,W503"
  ]
}
```

**Les agents utilisent toujours `get_errors`** qui fonctionne avec :
- ✅ Ruff (si installé - recommandé)
- ✅ flake8 (fallback automatique)
- ✅ Pylance (toujours actif)

---

## 📊 Comparaison Performance

| Outil | Vitesse | Fonctionnalités | Recommandation |
|-------|---------|-----------------|----------------|
| **Ruff** | ⚡⚡⚡ (10-100x plus rapide) | Linting + Format + Imports | ✅ **OPTIMAL** |
| flake8 | ⚡ | Linting seulement | ⚠️ Fallback OK |
| pylint | 🐌 (très lent) | Linting complet | ❌ Trop lent |
| black | ⚡⚡ | Formatting seulement | ⚠️ Incomplet |

**Pour agents autonomes** : Ruff est **10-100x plus rapide** → Validation quasi instantanée !

---

## ⚠️ Important : Configuration Locale Seulement

### ✅ Ce Qui Est Versionné (OK pour contribution)

- `.vscode/settings.json` - Configuration workspace locale
- `.vscode/extensions.json` - Recommandations extensions

### ❌ Ce Qui N'EST PAS Modifié (Respecte projet upstream)

- `packages/markitdown/pyproject.toml` - **NON modifié** (fichier du projet Microsoft)
- `packages/markitdown/setup.py` - **NON modifié**
- `.pre-commit-config.yaml` - **NON modifié** (si projet utilise autre outil)

**Principe** : Configuration locale pour développement, sans modifier standards du projet upstream.

---

## 🎓 Workflow Complet avec Ruff

### Développement Manuel

```
1. Ouvrir fichier Python dans VS Code
2. Écrire code
3. Ruff valide en temps réel (soulignements rouges)
4. Sauvegarder → Auto-fixes appliqués (si configuré)
5. Avant commit : Vérifier aucune erreur
```

### Développement avec Agents (Automatique)

```
1. Agent écrit code
2. Agent appelle get_errors
3. Ruff détecte erreurs via VS Code
4. Agent lit erreurs et corrige
5. Agent re-valide avec get_errors
6. Si OK : Marque tâche [x]
7. Avant merge : Validation finale get_errors
```

---

## ✅ Checklist Installation

**Avant de commencer développement** :

- ✅ Extension Ruff installée (`charliermarsh.ruff`)
- ✅ VS Code rechargé (`Ctrl+Shift+P` → Reload Window)
- ✅ Fichier Python ouvert → Ruff affiche validations
- ✅ Test erreur intentionnelle → Ruff souligne
- ✅ `get_errors` fonctionne dans Copilot Chat
- ✅ `.vscode/settings.json` commité dans repo

**Si tout est ✅, vous êtes prêt !**

---

## 🚀 Prochaines Étapes

**Avec Ruff installé, les agents vont** :
1. ✅ Détecter erreurs de code en temps réel
2. ✅ Corriger automatiquement via `get_errors` feedback
3. ✅ Respecter PEP 8 à 100%
4. ✅ Valider avant chaque merge

**Lancer développement** :
```
@workspace utilise #file:markitdown-orchestrator.agent.md pour commencer BRIEF_01
```

L'orchestrateur utilisera automatiquement Ruff via `get_errors` ! 🎉

---

## 📞 Troubleshooting

### Problème : "Ruff not found"

**Solution** :
```powershell
# Installer Ruff en tant que package Python
pip install ruff

# Ou réinstaller extension VS Code
Extensions → Ruff → Désinstaller → Réinstaller
```

### Problème : "Errors not showing in VS Code"

**Solution** :
```
1. Ctrl+Shift+P → "Developer: Reload Window"
2. Ouvrir fichier Python
3. Vérifier barre inférieure VS Code : Ruff doit apparaître
```

### Problème : "get_errors returns nothing"

**C'est bon signe !** Aucune erreur détectée. Si vous voulez tester :
```python
# Faire erreur intentionnelle
import os  # Non utilisé
x=1+2  # Espaces manquants
```

---

**Installation terminée !** Ruff est maintenant intégré au workflow des agents. 🚀
