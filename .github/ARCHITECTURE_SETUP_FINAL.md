# 🎯 Architecture Setup - Development & Testing

## 📋 Vue d'Ensemble

**Architecture pragmatique et réaliste** :
- ✅ **Instance VS Code UNIQUE** pour développement et testing en local
- ✅ **MCP Server** para testeurs finaux (conditions réelles)
- ✅ Pas de duplication inutile
- ✅ Tests réalistes avant livraison

---

## 🏗️ Stack Technique

### Votre Poste de Travail (Développeur)

```
C:\Repos\markitdown (BRANCHE: develop)
│
├─ Code Python
│  └─ packages/markitdown/src/
│
├─ Tests en local
│  └─ pytest (C:\Repos\markitdown\.venv\Scripts\pytest)
│
├─ VS Code (Instance unique)
│  ├─ GitHub Copilot
│  ├─ Orchestrateur agent
│  ├─ Ruff (validation)
│  └─ Test runner
│
└─ Git
   └─ Push développé vers origin/develop
```

### Poste des Testeurs (Utilisateurs Finaux)

```
Claude Desktop / Cline
│
└─ MCP Server MarkItDown
   ├─ Source: git+https://github.com/.../markitdown.git@develop
   └─ Utilise VOTRE code en temps réel
```

---

## 🚀 Workflow Complet

### 1️⃣ Développement (Vous)

```bash
# Instance VS Code unique
cd C:\Repos\markitdown
git checkout develop

# Lancer orchestrateur pour BRIEF_01
@workspace utilise #file:markitdown-orchestrator.agent.md pour commencer BRIEF_01
```

**L'orchestrateur**:
1. ✅ Recherche (task-researcher)
2. ✅ Planification (task-planner)
3. ✅ Développement (python-expert)
4. ✅ **Tests locaux** : `pytest tests/ -v`
5. ✅ **Validation** : `get_errors` + Ruff
6. ✅ Commit et push `develop`

### 2️⃣ Après Développement = Prêt pour Testeurs

**BRIEF_01 est prêt ?**

```bash
# Vérifier que tout marche
cd packages/markitdown
pytest tests/ -v  # Tous les tests passent
```

**Communiquer aux testeurs** :
> BRIEF_01 est prêt. Configurez MCP Server avec `@develop` pour tester.

### 3️⃣ Test par Utilisateurs Finaux

**Testeurs configurent** (`claude_desktop_config.json`) :

```json
{
  "mcpServers": {
    "markitdown": {
      "type": "stdio",
      "command": "python",
      "args": [
        "-m",
        "markitdown_mcp",
        "--source",
        "git+https://github.com/benoitcosials/markitdown.git@develop"
      ]
    }
  }
}
```

**Testeurs utilisent** : Claude Desktop → demande à utiliser MarkItDown → **Votre code develop est exécuté** → Feedback immédiat

### 4️⃣ Si Feedback = Itération

**Bug trouvé par testeur** ?

```bash
# Vous recevez feedback
# Créer branche pour fix
git checkout -b fix/brief-01-issue-description

# Fixer le bug
# Tester localement
pytest tests/ -v

# Commit et push
git push origin fix/...
```

**Testeur peut tester** : Mettre à jour sa config MCP avec branche `@fix/...` pour valider le fix immédiatement

---

## 💡 Avantages Architecture

| Aspect | Avantage |
|--------|----------|
| **Efficacité** | Pas de duplication, 1 seule instance VS Code |
| **Réalisme** | Testeurs utilisent votre code Via MCP (conditions réelles) |
| **Feed-back** | Immédiat (testeur utilise code actuel) |
| **Isolation** | Branche de dev isolée de production |
| **Flexibilité** | Testeurs peuvent tester branches différentes |
| **Coût** | Zéro configuration supplémentaire |

---

## 🔄 Cycle Développement & Test

```
Developer (Vous)                 Tester (Utilisateur Final)
│                               │
├─ BRIEF_01 Développement       │
│  ├─ task-researcher           │
│  ├─ task-planner              │
│  ├─ python-expert              │
│  ├─ pytest tests/             │
│  └─ git push develop          │
│                               │
│                               ├─ MCP Config update
│                               │  (@develop)
│                               │
│                               ├─ Claude Desktop usage
│                               │  → Teste BRIEF_01
│                               │
│                               └─ Feedback
│  ← Feedback reçu
│
├─ Créer branche fix/
├─ Appliquer fix
├─ pytest tests/
└─ git push fix/
                                ├─ MCP Config update
                                │  (@fix/...)
                                │
                                └─ Valide fix
```

---

## 📊 Comparaison Approaches

| Approche | Instances VS Code | Tests | Réalisme Testeurs | Complexité |
|----------|-------------------|-------|-------------------|-----------|
| **Ancienne** (non-recommandée) | 2+ | Locaux | Peu | Élevée |
| **Votre Approche** (recommandée) | 1 | Locaux + MCP | Excellent | Faible |
| **Hybrid (optionnel)** | 1 + MCP Server local | Très complets | Très bon | Moyen |

---

## 🎯 Configuration Finale

### Ce Qui Reste

**1 Instance VS Code unique** :
- ✅ `.vscode/settings.json` (Ruff, Claude Sonnet 4.5)
- ✅ `.github/agents/` (Orchestrateur)
- ✅ `.github/copilot-instructions.md` (Auto-chargé)
- ✅ Python `.venv` (mode éditable)
- ✅ Ruff extension (validation)

### Ce Qui Change

**MCP Server pour testeurs** :
- ✅ Configuration fournie aux testeurs
- ✅ Points vers `@develop` (ou branche spécifique)
- ✅ Testeurs utilisent votre code en conditions réelles

---

## 🚀 Prochaines Étapes

### Étape 0 : Valider Développement Local Fonctionne

```bash
# Dans VS Code unique (C:\Repos\markitdown)
cd packages/markitdown
pytest tests/ -v
```

**Tous les tests doivent passer** ✅

### Étape 1 : Lancer Développement BRIEF_01

```
@workspace utilise #file:markitdown-orchestrator.agent.md pour commencer BRIEF_01
```

### Étape 2 : Une Fois BRIEF_01 Prêt

**Donner config MCP aux testeurs** :

```json
{
  "mcpServers": {
    "markitdown-dev": {
      "type": "stdio",
      "command": "python",
      "args": [
        "-m",
        "markitdown_mcp",
        "--source",
        "git+https://github.com/benoitcosials/markitdown.git@develop"
      ]
    }
  }
}
```

**Instructions pour testeurs** :
1. Ajouter config à `claude_desktop_config.json`
2. Redémarrer Claude Desktop
3. Utiliser MarkItDown tool dans une conversation
4. Envoyer feedback

### Étape 3 : Itération sur Feedback

```bash
# Créer branche pour fix
git checkout -b fix/brief-01-feedback

# Fixer le problème
# Tester localement

# Testeur peut mettre à jour config :
"@develop"  # → Pour tester branche principale
# OU
"@fix/brief-01-feedback"  # → Pour tester le fix spécifique
```

---

## ✅ Checklist Avant Démarrage

- ✅ Instance VS Code unique sur `develop`
- ✅ `.venv` prêt avec markitdown en mode éditable
- ✅ `pytest tests/ -v` passe
- ✅ Ruff extension installée (optionnel mais recommandé)
- ✅ Orchestrateur disponible
- ✅ Avez-vous une liste de testeurs finaux ?

---

## 📞 Questions pour Clarifier

**Avant de lancer BRIEF_01** :
1. Avez-vous déjà des testeurs finaux en tête ?
2. Préférez-vous itérer sur feedback régulièrement ou attendre que tout soit fini ?
3. Voulez-vous que je crée un fichier de config MCP à donner aux testeurs ?

---

**Validation achevée !** Vous pouvez maintenant lancer le développement de BRIEF_01 directement. 🚀
