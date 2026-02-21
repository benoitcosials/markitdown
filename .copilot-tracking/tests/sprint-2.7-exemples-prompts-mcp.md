# 📝 Exemples de Prompts pour Tester MCP Vision Enhancement

**Serveur MCP** : `markitdown-ia-develop`  
**Objectif** : Test rapide des deux modes avec vraies conversions  
**Usage** : Copier-coller dans VS Code avec extension MCP active

---

## 🎯 Prompt 1 : Test Mode 1 (Alt Text Enrichment)

**À copier dans VS Code Copilot Chat** :

```
@workspace Utilise le serveur MCP markitdown-ia-develop pour convertir le fichier PPTX suivant en Markdown :

Fichier source : pptx-test/Standard QA - Concept de base.pptx

Paramètres de conversion :
- output_images = True
- use_client_vision = True  
- image_dir = "pptx-result/test-mode1-vision/images"

Actions attendues :
1. Extraire toutes les images dans le répertoire spécifié
2. Pour chaque image SANS alt text PowerPoint :
   - Analyser l'image via MCP Sampling
   - Générer une description courte (max 100 caractères)
   - Remplacer ![](path) par ![description](path)
3. Pour chaque image AVEC alt text PowerPoint :
   - Préserver l'alt text existant sans modification

Sauvegarde le markdown résultant dans :
pptx-result/test-mode1-vision/output.md

Après conversion, affiche-moi :
- Nombre total d'images traitées
- Nombre d'alt text enrichis (nouvellement générés)
- Nombre d'alt text préservés (existants)
- Exemple de 2-3 descriptions générées
```

**Résultat attendu** :
- Fichier `output.md` avec images extraites et alt text enrichis
- Répertoire `images/` avec fichiers PNG/JPEG physiques
- Alt text générés pertinents et < 100 caractères

---

## 🎯 Prompt 2 : Test Mode 2 (Description Blocks Détaillés)

**À copier dans VS Code Copilot Chat** :

```
@workspace Utilise le serveur MCP markitdown-ia-develop pour convertir le fichier PPTX suivant en Markdown avec descriptions détaillées :

Fichier source : pptx-test/Standard QA - Design des essais.pptx

Paramètres de conversion :
- output_images = False
- use_client_vision = True

Actions attendues :
1. Ne PAS extraire les images physiquement (pas de sauvegarde fichiers)
2. Pour CHAQUE image PowerPoint :
   - Analyser l'image via MCP Sampling
   - Générer une description détaillée (max 500 tokens) incluant :
     * Titre descriptif (1 ligne)
     * Description complète (plusieurs lignes)
     * Éléments visuels clés
     * Contexte et objectif de l'image
   - Remplacer ![alt](path) par un bloc :
     ```image-description
     Title: [Titre]
     
     [Description détaillée multi-lignes]
     ```

Sauvegarde le markdown résultant dans :
pptx-result/test-mode2-vision/output.md

Après conversion, affiche-moi :
- Nombre total d'images traitées
- Nombre de blocs description générés
- Exemple complet d'un bloc description (avec titre et détails)
```

**Résultat attendu** :
- Fichier `output.md` avec blocs ```image-description
- Aucun répertoire images/ créé
- Descriptions riches et structurées pour toutes les images

---

## 🎯 Prompt 3 : Comparaison Mode 1 vs Mode 2 (Même fichier)

**À copier dans VS Code Copilot Chat** :

```
@workspace Compare les deux modes de vision enhancement du serveur MCP markitdown-ia-develop sur le même fichier PPTX.

Fichier test : pptx-test/Standard QA - Organisation.pptx

**Conversion 1 - Mode 1** :
- output_images = True
- use_client_vision = True
- image_dir = "pptx-result/comparison/mode1/images"
- Sauvegarde : pptx-result/comparison/mode1-output.md

**Conversion 2 - Mode 2** :
- output_images = False
- use_client_vision = True
- Sauvegarde : pptx-result/comparison/mode2-output.md

Après les deux conversions, affiche-moi un tableau comparatif :

| Critère | Mode 1 (Alt Text) | Mode 2 (Blocks) |
|---------|-------------------|-----------------|
| Images extraites physiquement | ? | ? |
| Format descriptions | ? | ? |
| Longueur moyenne description | ? | ? |
| Niveau de détail | ? | ? |
| Utilité pour LLMs | ? | ? |

Recommandation : Quel mode utiliser selon le cas d'usage ?
```

**Résultat attendu** :
- Deux fichiers markdown distincts
- Comparaison claire des approches
- Recommandation d'usage contextuel

---

## 🎯 Prompt 4 : Test Préservation Alt Text (Mode 1)

**Test de non-régression** :

```
@workspace Vérifie que le Mode 1 préserve correctement les alt text existants dans PowerPoint.

Fichier test : pptx-test/Kickoff QA - Essais UAT R1 Bancaire et Trésorerie.pptx

Paramètres :
- output_images = True
- use_client_vision = True
- image_dir = "pptx-result/test-preservation/images"

Analyse spécifique requise :
1. Identifie quelles images du PPTX original ont déjà un alt text PowerPoint
2. Après conversion en Markdown, vérifie que :
   - Ces alt text sont EXACTEMENT préservés
   - Aucune modification n'a été apportée
3. Pour les images sans alt text PowerPoint :
   - Vérifie qu'un nouvel alt text a été généré via MCP Sampling

Affiche un rapport avec :
- Images avec alt text préservé : [nombre] (liste des 3 premiers)
- Images avec alt text généré : [nombre] (liste des 3 premiers)
- Anomalies détectées : [si un alt text existant a été modifié]

Sauvegarde : pptx-result/test-preservation/output.md
```

**Validation critique** :
- ✅ Alt text existants NON modifiés
- ✅ Seulement images vides enrichies
- ❌ Aucune surcharge des alt text PowerPoint existants

---

## 🎯 Prompt 5 : Test Performance (10+ Images)

**Test à grande échelle** :

```
@workspace Teste la performance du serveur MCP markitdown-ia-develop avec un fichier PPTX contenant de nombreuses images.

Fichier test : pptx-test/Kickoff QA - Essais UAT R1 Bancaire et Trésorerie.pptx

Paramètres :
- output_images = True
- use_client_vision = True

Métriques à mesurer :
1. Temps de traitement total
2. Temps moyen par image
3. Nombre d'images traitées avec succès
4. Nombre d'échecs (si sampling échoue)
5. Taille du markdown final

Benchmark cible :
- Temps/image : < 3 secondes
- Taux de succès : 100%
- Aucune erreur MCP

Sauvegarde : pptx-result/test-performance/output.md

Après conversion, affiche un rapport de performance :
```
📊 Rapport de Performance MCP Vision Enhancement
================================================
Images traitées : X
Succès : X (XX%)
Échecs : X
Temps total : XX.XX secondes
Temps moyen/image : X.XX secondes
Taille output : XX KB
```

**Objectif** : Valider la robustesse à grande échelle

---

## 🧪 Prompt 6 : Test Cas Limite (Edge Cases)

**Test de robustesse** :

```
@workspace Teste les cas limites du vision enhancement MCP :

**Cas 1** : PPTX sans images
- Fichier fictif ou créer un PPTX vide
- Vérifier : Conversion réussie, pas d'erreur, markdown sans images

**Cas 2** : PPTX avec images corrompues/cachées
- Si disponible dans pptx-test/
- Vérifier : Graceful fallback, pas de crash

**Cas 3** : PPTX avec très grande image (> 5 MB)
- Si disponible
- Vérifier : Traitement correct ou timeout gracieux

**Cas 4** : PPTX multilingue (caractères spéciaux dans alt text)
- Vérifier : Encodage UTF-8 préservé

Pour chaque cas, documente :
- Comportement observé
- Erreurs (si présentes)
- Suggestions d'amélioration
```

**Validation** : Le système gère tous les edge cases sans crash

---

## 📌 Checklist de Validation Sprint 2.7

Après avoir exécuté ces prompts, valider :

- [ ] **Prompt 1** : Mode 1 fonctionne (alt text enrichis)
- [ ] **Prompt 2** : Mode 2 fonctionne (description blocks)
- [ ] **Prompt 3** : Comparaison claire entre modes
- [ ] **Prompt 4** : Alt text existants préservés
- [ ] **Prompt 5** : Performance acceptable (< 3s/image)
- [ ] **Prompt 6** : Cas limites gérés gracieusement

**Si tous validés** ✅ → Sprint 2.7 COMPLÉTÉ

---

## 🚀 Utilisation Rapide

**Pour tester rapidement** :
1. Ouvrir VS Code dans workspace markitdown
2. Activer l'onglet Copilot Chat
3. Copier Prompt 1 ou Prompt 2
4. Coller et exécuter
5. Vérifier les fichiers générés dans `pptx-result/`

**Serveur MCP actif ?**
- Vérifier `.vscode/mcp.json` configuré
- Le serveur démarre automatiquement à la première requête
- Logs MCP visibles dans Output > MCP (si extension supporte)

**Debugging** :
Si le serveur ne répond pas :
```bash
# Test manuel du serveur
uvx --from "git+https://github.com/benoitcosials/markitdown.git@develop#subdirectory=packages/markitdown-mcp" markitdown-mcp
```

---

**Date de création** : 21 février 2026  
**Version serveur** : develop (commit après Phase 2 Sprints 2.1-2.6)  
**Prochaine étape** : Sprint 2.8 - Tests multi-clients (Claude Desktop, MCP Inspector)
