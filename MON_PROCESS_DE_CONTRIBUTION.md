# 📋 Mon Process de Contribution - Guide Complet

## 🎯 Objectif
Contribuer au projet **markitdown** en toute confiance en déployant votre branche à des utilisateurs de test **avant le merge** vers la branche principale.

---

## 📚 Table des matières
1. [Setup Initial](#setup-initial)
2. [Stratégie de Branching](#stratégie-de-branching)
3. [Créer votre Branche de Développement](#créer-votre-branche-de-développement)
4. [Développer votre Contribution](#développer-votre-contribution)
5. [Tester Localement](#tester-localement)
6. [Déployer aux Testeurs Réels](#déployer-aux-testeurs-réels)
7. [Créer une Pull Request](#créer-une-pull-request)

---

## 1. Setup Initial {#setup-initial}

### 1.1 Forker le projet sur GitHub

1. Allez sur https://github.com/microsoft/markitdown
2. Cliquez sur le bouton **"Fork"** en haut à droite
3. GitHub crée une copie du projet sur votre compte : `https://github.com/benoitcosials/markitdown`

### 1.2 Cloner votre fork localement

```bash
git clone https://github.com/benoitcosials/markitdown.git
cd markitdown
```

### 1.3 Ajouter le remote upstream (optionnel mais recommandé)

Cela vous permet de rester à jour avec le projet original :

```bash
git remote add upstream https://github.com/microsoft/markitdown.git
git fetch upstream
```

Vérifiez vos remotes :
```bash
git remote -v
```

Vous devriez voir :
```
origin    https://github.com/benoitcosials/markitdown.git (fetch)
origin    https://github.com/benoitcosials/markitdown.git (push)
upstream  https://github.com/microsoft/markitdown.git (fetch)
upstream  https://github.com/microsoft/markitdown.git (push)
```

---

## 2. Stratégie de Branching {#stratégie-de-branching}

### 2.1 Structure des Branches

Nous utilisons une approche **develop + feature branches** :

```
main (sync avec upstream/microsoft)
  └── develop (branche d'intégration)
       ├── feat/brief-01-image-extraction
       ├── feat/brief-02-image-descriptions
       └── feat/brief-03-chart-ascii-art
```

### 2.2 Avantages de cette Approche

✅ **Isolation des fonctionnalités** : Chaque brief = 1 branche = 1 PR éventuelle  
✅ **Tests progressifs** : Tester BRIEF_01 seul, puis intégrer BRIEF_02, etc.  
✅ **Rollback facile** : Si un brief pose problème, revenir à `develop`  
✅ **PRs ciblées** : Microsoft peut review/merger une fonctionnalité à la fois  
✅ **Déploiement testeurs** : Donner accès à une branche spécifique

### 2.3 Workflow avec develop

```bash
# 1. Créer develop depuis main
git checkout main
git checkout -b develop

# 2. Commit vos docs de préparation sur develop
git add BRIEF_*.md MON_ROADMAP.md MON_PROCESS_DE_CONTRIBUTION.md
git commit -m "docs: add technical briefs and contribution roadmap"

# 3. Push develop vers votre fork
git push -u origin develop

# 4. Créer branche pour BRIEF_01
git checkout -b feat/brief-01-image-extraction

# 5. Implémenter BRIEF_01...
# ... commits réguliers ...
git add .
git commit -m "feat(pptx): implement image extraction"

# 6. Push vers votre fork
git push -u origin feat/brief-01-image-extraction

# 7. Tests + Feedback testeurs ✅

# 8. Merger dans develop une fois validé
git checkout develop
git merge feat/brief-01-image-extraction
git push origin develop

# 9. Créer branche pour BRIEF_02 (qui dépend de BRIEF_01)
git checkout -b feat/brief-02-image-descriptions

# ... et ainsi de suite
```

### 2.4 Note sur les Dépendances

Dans notre cas, **BRIEF_02 et BRIEF_03 dépendent de BRIEF_01** (extraction d'images), donc la branche `develop` est essentielle pour intégrer progressivement les fonctionnalités.

---

## 3. Créer votre Branche de Développement {#créer-votre-branche-de-développement}

### 3.1 Sync avec le repo principal (recommandé)

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

### 3.2 Créer une branche descriptive

```bash
# Depuis develop, créer une branche pour un brief
git checkout develop
git checkout -b feat/brief-01-image-extraction

# Ou pour un bug fix :
git checkout -b fix/pptx-table-formatting
```

**Format recommandé** : `type/brief-XX-description` ou `type/description-courte`
- `feat/` → nouvelle fonctionnalité
- `fix/` → correction de bug
- `docs/` → documentation
- `refactor/` → refactorisation

**Exemples pour nos briefs** :
- `feat/brief-01-image-extraction`
- `feat/brief-02-image-descriptions`
- `feat/brief-03-chart-ascii-art`

### 3.3 Vérifiez que vous êtes sur la bonne branche

```bash
git branch
# Affiche : * feat/brief-01-image-extraction
```

---

## 4. Développer votre Contribution {#développer-votre-contribution}

### 4.1 Installer les dépendances en mode développement

```bash
cd c:\Repos\markitdown

# Installer en mode "editable" : vos modifications sont immédiatement réfléchies
pip install -e ".[all]"  # Pour markitdown
# ou
pip install -e packages/markitdown-mcp  # Pour le serveur MCP
```

### 4.2 Faire vos modifications

Modifiez les fichiers nécessaires avec VS Code. Exemples :
- `packages/markitdown/src/markitdown/converters/_pptx_converter.py`
- `packages/markitdown-mcp/src/markitdown_mcp/__main__.py`

### 4.3 Commit fréquemment et proprement

```bash
# Voir vos changements
git status
git diff

# Ajouter les fichiers modifiés
git add src/markitdown/converters/_pptx_converter.py
# ou tout ajouter :
git add .

# Commiter avec un message descriptif
git commit -m "feat(pptx): ajout extraction images vers dossier"

# Messages recommandés :
# feat(module): description
# fix(module): description
# docs: description
```

### 4.4 Push régulièrement vers votre fork

```bash
# Push de votre branche feature
git push origin feat/brief-01-image-extraction

# Ou si première fois :
git push -u origin feat/brief-01-image-extraction
```

---

## 5. Tester Localement {#tester-localement}

### 5.1 Exécuter les tests existants

```bash
cd c:\Repos\markitdown\packages\markitdown

# Voir les tests disponibles
ls tests/test_*.py

# Exécuter tous les tests
pytest tests/

# Exécuter un test spécifique
pytest tests/test_module_vectors.py -v

# Exécuter avec coverage
pytest tests/ --cov=src/markitdown
```

### 5.2 Tester manuellement votre convertisseur

```python
# Créez un fichier test_contrib.py
from markitdown import markitdown

# Tester votre nouveau code
result = markitdown.markitdown("mon_fichier.pptx")
print(result)
```

### 5.3 Utiliser le CLI

```bash
# Mode interactif depuis votre terminal
python -m markitdown mon_fichier.pptx

# Ou avec options
python -m markitdown mon_fichier.pptx --output mon_fichier.md
```

---

## 6. Déployer aux Testeurs Réels {#déployer-aux-testeurs-réels}

**C'est ici que vous divergez du processus standard !**

Les testeurs vont utiliser votre branche directement depuis GitHub via MCP, sans attendre un merge.

### 6.1 Pousser votre branche finale vers GitHub

Assurez-vous que votre branche est complète et testée :

```bash
# Exemple avec BRIEF_01
git push origin feat/brief-01-image-extraction
```

Vérifiez sur GitHub : https://github.com/benoitcosials/markitdown/tree/feat/brief-01-image-extraction

### 6.2 Configurer MCP dans VS Code pour les testeurs

Les testeurs vont configurer VS Code pour utiliser votre branche directement. Créez un fichier de documentation qu'ils peuvent partager :

**`iA-markitdown-test-config.json`** (à la racine de votre repo ou dans un dossier `docs/`)

**Configuration pour VS Code** (avec l'extension Claude ou une extension MCP) :

```json
{
  "mcpServers": {
    "iA-markitdown-test": {
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

Ou si vous avez un fichier de configuration spécifique à VS Code :

```json
{
  "mcpServers": {
    "iA-markitdown-test": {
      "type": "stdio",
      "command": "python",
      "args": [
        "-m",
        "markitdown_mcp"
      ],
      "env": {
        "GITHUB_BRANCH": "feat/brief-01-image-extraction",
        "GITHUB_REPO": "benoitcosials/markitdown"
      }
    }
  }
}
```

### 6.3 Instructions pour vos testeurs

Partagez ce guide court avec vos testeurs :

```markdown
## Instructions de Test - Branche feat/brief-01-image-extraction

### Setup VS Code avec la branche de test

1. **Cloner votre fork** (ou utiliser un clone existant) :
   ```bash
   git clone https://github.com/benoitcosials/markitdown.git
   cd markitdown
   git checkout feat/brief-01-image-extraction
   ```

2. **Installer en mode développement** :
   ```bash
   pip install -e ".[all]"
   pip install -e packages/markitdown-mcp
   ```

3. **Configurer VS Code** pour utiliser le MCP de test :
   
   Selon votre setup MCP/extension VS Code, ajouter cette configuration (fichier config MCP ou settings.json) :
   
   ```json
   "mcpServers": {
     "iA-markitdown-test": {
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
   ```

4. **Redémarrer VS Code** et recharger l'extension MCP

5. **Tester** en ouvrant des fichiers PPTX et confirmer que :
   - ✅ Les images sont extraites correctement
   - ✅ Le Markdown est bien formaté
   - ✅ Les tableaux sont lisibles
   - ✅ Les notes de slide sont incluses

6. **Rapporter les bugs** : email ou GitHub Issues avec des détails

7. **Revert** quand terminé :
   ```bash
   git checkout main
   pip install -e ".[all]"  # Revenir à la version stable
   ```
```

### 6.4 (Avancé) Publier une version pré-release sur PyPI

Si vous voulez que les testeurs installent plus facilement sans éditer la config :

```bash
# Mettre à jour la version en pre-release
# Fichier: packages/markitdown-mcp/src/markitdown_mcp/__about__.py
# Changez: __version__ = "0.0.1a5"  (au lieu de "0.0.1a4")

# Publier sur PyPI (nécessite un compte et un token)
cd packages/markitdown-mcp
pip install build twine
python -m build
twine upload dist/*

# Les testeurs peuvent alors simplement faire :
# pip install markitdown-mcp==0.0.1a5
```

---

## 7. Créer une Pull Request {#créer-une-pull-request}

### 7.1 Préparer votre PR

Avant de créer la PR, assurez-vous que :

- ✅ Tous les tests locaux passent : `pytest tests/`
- ✅ Votre code respecte la style : `black src/` (si utilisé)
- ✅ Les types sont correctes : `mypy src/` (si utilisé)
- ✅ Vous avez synchronisé avec `upstream/main` :

```bash
git fetch upstream
git rebase upstream/main
# Si conflits : résolvez-les et continuez
git rebase --continue
```

### 7.2 Créer la PR sur GitHub

1. Allez sur votre fork : https://github.com/benoitcosials/markitdown
2. Cliquez sur **"Compare & pull request"** (GitHub détecte votre branche récemment pushée)
3. Remplissez le formulaire :

   **Titre** :
   ```
   feat(pptx): Add image extraction to local folder
   ```

   **Description** (détaillée) :
   ```markdown
   ## Description
   Ajoute l'extraction automatique des images PPTX vers un dossier `images/`

   ## Motivation
   Les utilisateurs LLM ont besoin que les images soient accessibles physiquement

   ## Context
   This contribution was developed while working at Industrielle Alliance (iA).
   Special thanks to the iA innovation team for their support.

   ## Tests
   - ✅ Testé sur 10 fichiers PPTX différents
   - ✅ Tous les tests existants passent
   - ✅ Images extraites correctement

   ## Fichiers modifiés
   - `_pptx_converter.py` : Logique d'extraction
   - `test_pptx_*.py` : Tests unitaires
   
   ## Feedback des testeurs
   - @testeur1 : Images correctement intégrées ✅
   - @testeur2 : Performance acceptable ✅

   Closes #ISSUE_NUMBER (si applicable)
   ```

4. Sélectionnez :
   - **Base repository** : `microsoft/markitdown`
   - **Base branch** : `main`
   - **Head repository** : `benoitcosials/markitdown`
   - **Head branch** : `feat/brief-01-image-extraction`

5. Cliquez sur **"Create pull request"**

### 7.3 Répondre aux commentaires

- Les mainteneurs peuvent demander des changements
- Continuez à commiter sur votre branche locale
- Pushez vers GitHub : les changements apparaissent automatiquement dans la PR

```bash
# Modification après feedback
git add .
git commit -m "fix: incorporate feedback from review"
git push origin feat/brief-01-image-extraction
```

---

## 📊 Flux Complet Résumé

```
┌─── Fork sur GitHub
│
├─── Clone localement
│
├─── Ajouter remotes (origin + upstream)
│
├─── Créer branche `develop`
│
├─── Commit docs de préparation sur develop
│
├─── Créer branche `feat/brief-XX-...` depuis develop
│
├─── Développer + Commit réguliers
│
├─── Tests locaux ✅
│
├─── Push vers fork
│
├─── ⭐ DÉPLOYER AUX TESTEURS (votre branche directe)
│    │
│    ├─── Testeurs téléchargent via git+https://...
│    │
│    └─── Feedback recueilli ✅
│
├─── Appliquer feedback
│
├─── Merger dans develop
│
├─── Push final
│
└─── Créer Pull Request sur microsoft/markitdown
     │
     └─── Review + Merge dans main ✅
```

---

## 🆘 Troubleshooting

### Conflits lors du rebase
```bash
# Résoudre les conflits dans VS Code, puis :
git add .
git rebase --continue
```

### Ma branche est trop en retard
```bash
git fetch upstream
git rebase upstream/main
# Ou fusionner :
git merge upstream/main
```

### Les changements ne s'affichent pas chez les testeurs
- Vérifiez que vous avez pushé : `git push origin feat/...`
- Testeurs doivent redémarrer Claude Desktop
- Vérifiez l'URL GitHub dans la config MCP

### Tests qui échouent

```bash
# Voir les logs détaillés
pytest tests/ -vv -s

# Tester un fichier spécifique
pytest tests/test_pptx.py -v
```

---

## ✅ Checklist Avant de Demander une Review

- [ ] Branche créée et pushée
- [ ] Tous les tests passent localement
- [ ] Code propre et commenté
- [ ] Testeurs réels ont validé la contribution
- [ ] PR décrit clairement les changements
- [ ] Pas de conflits avec `main`
- [ ] Documentation mise à jour (si applicable)

---

**Bonne contribution ! 🚀**
