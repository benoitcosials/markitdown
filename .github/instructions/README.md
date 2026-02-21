# Instructions Python pour GitHub Copilot

Ce répertoire contient les instructions qui guident GitHub Copilot pour générer du code Python de haute qualité.

## 📋 Instructions Disponibles

### [python.instructions.md](python.instructions.md)
**S'applique à** : `**/*.py`

Conventions Python essentielles :
- PEP 8 (style guide officiel Python)
- Type hints avec le module `typing`
- Docstrings PEP 257
- Gestion des edge cases
- Tests unitaires

### [self-explanatory-code.instructions.md](self-explanatory-code.instructions.md)
**S'applique à** : Tous les fichiers

Principes de code auto-documenté :
- Commenter le **WHY**, pas le **WHAT**
- Annotations (TODO, FIXME, NOTE, SECURITY, etc.)
- Éviter les commentaires évidents/redondants
- Noms de variables/fonctions explicites

## 🚀 Utilisation

Ces instructions sont **automatiquement chargées** par GitHub Copilot dans VS Code pour le workspace MarkItDown.

### Chargement Automatique
GitHub Copilot détecte automatiquement les fichiers `.instructions.md` dans `.github/instructions/` et applique les règles selon le pattern `applyTo`.

### Chargement Manuel (si nécessaire)
Si vous travaillez dans un autre environnement ou voulez forcer le chargement :

```
@workspace charge les instructions Python depuis .github/instructions/
```

## 📚 Sources

Ces instructions proviennent de la collection **awesome-copilot** :
- `python.instructions.md` : Conventions Python standards
- `self-explanatory-code.instructions.md` : Principes de clean code

Pour plus d'informations, consultez [awesome-copilot collections](https://github.com/awesome-copilot).

## 🔄 Mise à Jour

Pour mettre à jour ces instructions :
1. Charger la dernière version depuis awesome-copilot
2. Adapter au contexte MarkItDown si nécessaire
3. Tester avec des exemples de code

---

**Note** : Ces instructions complètent les règles définies dans `.github/copilot-instructions.md` (fichier principal du workflow).
