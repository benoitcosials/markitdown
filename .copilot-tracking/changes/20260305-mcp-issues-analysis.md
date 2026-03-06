# Rapport d'Analyse et Corrections MCP - 5 Mars 2026

## Contexte
L'utilisateur a rencontré 3 problèmes majeurs lors de l'utilisation du MCP `mcp_markitdown-ia_convert_to_markdown` :

1. **Format URI non intuitif** - Le MCP rejetait les chemins Windows bruts
2. **Images non extraites** - 0 images extraites malgré `output_images=true` 
3. **Fichier MD non créé** - Le résultat JSON n'a pas été sauvegardé en fichier

---

## Problème 1 : Format URI non intuitif

### Symptôme
```
Error executing tool convert_to_markdown: Unsupported URI scheme: C. 
Supported schemes are: file:, data:, http:, https:
```

### Cause racine
Le MCP `convert_to_markdown` passait le paramètre `uri` directement à `convert_uri()` qui n'accepte que les schémas `file://`, `http://`, `https://`, `data:`. Un chemin Windows comme `C:\path\file.pptx` est interprété avec "C" comme schéma.

### Solution implémentée
Ajout d'une **auto-conversion des chemins locaux** en URI `file://` dans [tools.py](../packages/markitdown-mcp/src/markitdown_mcp/tools.py#L92-L108):

```python
# Step 0: Auto-convert local paths to file:// URIs
if not any(uri.startswith(scheme) for scheme in ['file:', 'http:', 'https:', 'data:']):
    is_windows_path = len(uri) >= 2 and uri[1] == ':' and uri[0].isalpha()
    is_unix_path = uri.startswith('/')
    
    if is_windows_path or is_unix_path:
        normalized = uri.replace('\\', '/')
        if is_windows_path:
            uri = f"file:///{urllib.parse.quote(normalized, safe='/:')}"
        else:
            uri = f"file://{urllib.parse.quote(normalized, safe='/')}"
        logs.append(f"Auto-converted path to URI: {original_uri} -> {uri}")
```

### Documentation mise à jour
La docstring du paramètre `uri` a été améliorée pour clarifier les formats acceptés :
- Chemins locaux : `C:\docs\file.pptx` ou `/home/user/file.pptx`
- URIs file:// : `file:///C:/docs/file.pptx`
- HTTP/HTTPS : `https://example.com/file.docx`
- Data URIs : `data:application/pdf;base64,...`

---

## Problème 2 : Images non extraites (0 images)

### Symptôme
Le log MCP indiquait "Extracted 0 images" mais le Markdown contenait des références d'images.

### Analyse effectuée
Scripts de debug créés :
- [debug_image_extraction.py](debug_image_extraction.py) - Test direct du convertisseur
- [debug_mcp_simulation.py](debug_mcp_simulation.py) - Simulation du flux MCP complet

**Résultat** : Le convertisseur fonctionne correctement et extrait bien 9 images.

### Cause racine probable
Le MCP serveur de VS Code utilisait probablement :
1. Un environnement Python différent avec une ancienne version du code
2. Un cache non rafraîchi du serveur MCP

**Preuve** : Le markdown du premier appel MCP utilisait des noms `Image13.jpg` (format ancien basé sur `shape.name`) tandis que le code actuel génère `slide1_image0.png` (format BRIEF_01).

### Solution appliquée
1. Réinstallation forcée du package MCP en mode editable
2. Ajout de logs plus détaillés pour diagnostic futur

---

## Problème 3 : Fichier MD non créé

### Cause racine
Le MCP retourne un **JSON** contenant le markdown et les métadonnées, mais ne crée pas automatiquement de fichier `.md`. L'agent aurait dû créer le fichier lui-même.

### Solution appliquée
Création du script [convert_and_save.py](convert_and_save.py) qui :
1. Convertit le PPTX avec extraction d'images
2. Sauvegarde le markdown en fichier `.md`
3. Crée un fichier de résumé JSON

**Fichiers créés** :
- `z_015_ARCH-WS4_Bancaire_20260305-173152.md` (102022 caractères)
- 9 images dans le dossier `images/`
- `conversion_summary_20260305-173152.json`

---

## Fichiers modifiés

| Fichier | Modification |
|---------|--------------|
| [tools.py](../../packages/markitdown-mcp/src/markitdown_mcp/tools.py) | Auto-conversion des chemins locaux en URI file:// + documentation améliorée |

## Recommandations

1. **Pour l'utilisateur** : Utiliser indifféremment des chemins locaux ou des URIs file://
2. **Pour le MCP** : Améliorer la gestion d'erreurs avec des messages plus explicites
3. **Pour VS Code** : Vérifier que le MCP serveur utilise l'environnement Python correct avec les packages en mode editable
