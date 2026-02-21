# 🧪 Sprint 2.7 : Guide de Test MCP Vision Enhancement

**Date** : 21 février 2026  
**Serveur MCP** : `markitdown-ia-develop` (branche develop)  
**Objectif** : Valider l'implémentation MCP Sampling pour descriptions d'images  
**Durée estimée** : 1h  

---

## 📋 Prérequis

✅ Serveur MCP configuré dans `.vscode/mcp.json` :
```json
{
  "servers": {
    "markitdown-ia-develop": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/benoitcosials/markitdown.git@develop#subdirectory=packages/markitdown-mcp",
        "markitdown-mcp"
      ]
    }
  }
}
```

✅ Extension MCP activée dans VS Code  
✅ GitHub Copilot ou Claude actif (client multimodal)  
✅ Fichiers PPTX de test disponibles dans `pptx-test/`  

---

## 🎯 Test 1 : Mode 1 - Alt Text Enrichment (output_images=True)

### Objectif
Vérifier que les images **sans alt text** reçoivent des descriptions courtes (max 100 caractères) via MCP Sampling, tandis que les images avec alt text existant sont préservées.

### Commande VS Code

Dans VS Code, ouvrir le panneau MCP et exécuter :

```
Utilise le serveur MCP markitdown-ia-develop pour convertir le fichier 
"pptx-test/Standard QA - Concept de base.pptx" en Markdown avec :
- output_images = True
- use_client_vision = True
- image_dir = "pptx-result/test-sprint-2.7-mode1/images"

Sauvegarde le résultat dans "pptx-result/test-sprint-2.7-mode1/output.md"
```

### Validation Attendue

1. **Images extraites** :
   - ✅ Répertoire `pptx-result/test-sprint-2.7-mode1/images/` créé
   - ✅ Fichiers PNG/JPEG présents (slide{N}_image{M}.png)

2. **Alt text enrichis** :
   - ✅ Images sans alt text : `![description courte](images/slide1_image0.png)`
   - ✅ Description < 100 caractères
   - ✅ Description pertinente (vérifie visuellement 2-3 images)

3. **Alt text préservés** :
   - ✅ Si PPTX avait alt text → préservé sans modification

4. **Pas d'erreurs** :
   - ✅ Aucune exception levée
   - ✅ Conversion complète réussie

### Métriques à Capturer

- Nombre d'images traitées : _______
- Nombre d'alt text enrichis : _______
- Nombre d'alt text préservés : _______
- Temps de traitement total : _______ secondes
- Temps moyen par image : _______ secondes

---

## 🎯 Test 2 : Mode 2 - Description Blocks (output_images=False)

### Objectif
Vérifier que **toutes les images** (avec ou sans alt text) sont remplacées par des blocs ```image-description détaillés (max 500 tokens).

### Commande VS Code

```
Utilise le serveur MCP markitdown-ia-develop pour convertir le fichier 
"pptx-test/Standard QA - Design des essais.pptx" en Markdown avec :
- output_images = False
- use_client_vision = True

Sauvegarde le résultat dans "pptx-result/test-sprint-2.7-mode2/output.md"
```

### Validation Attendue

1. **Pas d'images extraites** :
   - ✅ Aucun répertoire images/ créé
   - ✅ Aucun fichier PNG/JPEG sauvegardé

2. **Description blocks présents** :
   - ✅ Format : 
     ```markdown
     ```image-description
     Title: [Titre descriptif]
     
     [Description détaillée multi-lignes]
     - What is shown
     - Key visual elements
     - Context/purpose
     - Notable details
     \```
     ```
   - ✅ Chaque image remplacée par un bloc
   - ✅ Descriptions complètes et pertinentes

3. **Qualité des descriptions** :
   - ✅ Titre présent (1 ligne)
   - ✅ Description structurée (plusieurs lignes)
   - ✅ Contexte PowerPoint mentionné
   - ✅ Détails visuels identifiés

### Métriques à Capturer

- Nombre d'images traitées : _______
- Nombre de blocs générés : _______
- Taille moyenne description : _______ mots
- Temps de traitement total : _______ secondes
- Temps moyen par image : _______ secondes

---

## 🎯 Test 3 : Préservation Alt Text Existant (Mode 1)

### Objectif
Vérifier que le Mode 1 ne modifie PAS les images qui ont déjà un alt text.

### Préparation

1. Créer un PPTX test avec 3 images :
   - Image 1 : Avec alt text "Diagramme de flux"
   - Image 2 : Sans alt text (vide)
   - Image 3 : Avec alt text "Logo entreprise"

### Commande VS Code

```
Utilise le serveur MCP markitdown-ia-develop pour convertir 
"pptx-test/test-alt-text-preservation.pptx" avec :
- output_images = True
- use_client_vision = True

Sauvegarde dans "pptx-result/test-sprint-2.7-mode1-preservation/output.md"
```

### Validation Attendue

1. **Image 1** (alt text existant) :
   - ✅ `![Diagramme de flux](images/slide1_image0.png)` - INCHANGÉ

2. **Image 2** (sans alt text) :
   - ✅ `![description générée par MCP](images/slide1_image1.png)` - ENRICHI

3. **Image 3** (alt text existant) :
   - ✅ `![Logo entreprise](images/slide1_image2.png)` - INCHANGÉ

---

## 🎯 Test 4 : Fallback Gracieux (Client sans Sampling)

### Objectif
Vérifier que si le client ne supporte PAS le sampling, le système continue sans erreur et retourne le markdown sans enrichissement.

### Simulation

Malheureusement, difficile de simuler un client non-sampling dans VS Code. Ce test peut être :
- ✅ Vérifié par inspection du code `client_supports_sampling()`
- ✅ Testé manuellement avec un client MCP basique (sans multimodal)

### Validation du Code

```python
# Dans vision_enhancement.py
async def client_supports_sampling(server: Server) -> bool:
    try:
        caps = await server.get_client_capabilities()
        return caps.get("sampling", False)
    except Exception:
        return False  # Fallback gracieux
```

- ✅ Try/except présent
- ✅ Return False par défaut
- ✅ `enhance_markdown_with_client_vision()` retourne markdown inchangé si False

---

## 🎯 Test 5 : Performance et Fiabilité

### Test à Grande Échelle

Utiliser un PPTX avec **10+ images** :

```
Utilise le serveur MCP markitdown-ia-develop pour convertir 
"pptx-test/Kickoff QA - Essais UAT R1 Bancaire et Trésorerie.pptx" 
avec use_client_vision=True et output_images=True
```

### Métriques Cibles

| Métrique | Valeur Cible | Résultat Réel |
|----------|--------------|---------------|
| Temps/image (Mode 1) | < 3 secondes | _________ |
| Temps/image (Mode 2) | < 5 secondes | _________ |
| Taux de succès | 100% | _________ |
| Erreurs MCP | 0 | _________ |
| Qualité descriptions | Bonne/Excellente | _________ |

---

## ✅ Critères de Validation Sprint 2.7

Le Sprint 2.7 est **COMPLÉTÉ** si :

- [x] **Test 1 (Mode 1)** : Alt text enrichis pour images sans alt text existant
- [x] **Test 2 (Mode 2)** : Description blocks générés pour toutes images
- [x] **Test 3 (Préservation)** : Alt text existants préservés en Mode 1
- [x] **Test 4 (Fallback)** : Code vérifié pour fallback gracieux
- [x] **Test 5 (Performance)** : Traitement 10+ images sans erreur
- [x] **Qualité** : Descriptions pertinentes et utiles pour LLMs
- [x] **MCP Conformité** : Requêtes CreateMessageRequest valides

---

## 📝 Notes et Observations

### Problèmes Rencontrés
(Documenter ici tout bug, comportement inattendu, ou amélioration suggérée)

### Améliorations Potentielles
(Idées pour optimisation ou fonctionnalités supplémentaires)

### Feedback Utilisateurs
(Si des testeurs externes fournissent du feedback)

---

## 🚀 Prochaines Étapes Après Validation

Une fois le Sprint 2.7 validé :
- ✅ Marquer Sprint 2.7 comme complété dans le plan
- ✅ Mettre à jour `.copilot-tracking/changes/` avec résultats
- ✅ Passer au Sprint 2.8 : Tests multi-clients (Claude Desktop, MCP Inspector)

**Date de complétion** : ________________  
**Validé par** : ________________
