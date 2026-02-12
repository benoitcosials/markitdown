# Guide de Réinstallation MCP avec BRIEF_01

## Problème Identifié
Le MCP n''exposait pas les nouveaux paramètres du BRIEF_01 (output_images, image_dir, skip_icon_images, etc.).

## Solution Implémentée
Modification de `convert_to_markdown()` dans `packages/markitdown-mcp/src/markitdown_mcp/__main__.py`

## Nouveaux Paramètres MCP Disponibles

```python
convert_to_markdown(
    uri: str,
    output_images: bool = True,           # Extraire les images
    image_dir: str = "images",            # Dossier de destination
    skip_background_images: bool = True,  # Ignorer backgrounds PPTX
    skip_icon_images: bool = True,        # Ignorer icons (photos seulement)
    deduplicate_images: bool = False      # Déduplication MD5
)
```

## Étapes de Réinstallation

### 1. Réinstaller markitdown-mcp en mode développement

```powershell
# Désinstaller l''ancienne version
pip uninstall markitdown-mcp -y

# Installer depuis le repo local en mode éditable
pip install -e packages/markitdown-mcp
```

### 2. Vérifier l''installation

```powershell
python -c "from markitdown_mcp import __main__; print(''MCP installé'')"
```

### 3. Tester avec un fichier PPTX local

```powershell
# Test basique (utilise les défauts)
python -m markitdown_mcp

# Dans un autre terminal, utiliser le MCP avec les nouveaux paramètres
```

## Test Rapide (Python Script)

Créer un fichier `test_mcp_params.py` :

```python
from markitdown import MarkItDown

# Test avec les nouveaux paramètres
pptx_path = "pptx-test/Standard QA - Design des essais.pptx"

result = MarkItDown().convert_local(
    pptx_path,
    output_images=True,
    image_dir="test-mcp-output",
    skip_icon_images=True,
    skip_background_images=True,
    deduplicate_images=False
)

print(f"Conversion terminée")
print(f"Longueur Markdown: {len(result.markdown)} chars")

# Vérifier que les images sont extraites
import os
if os.path.exists("test-mcp-output"):
    images = os.listdir("test-mcp-output")
    print(f"Images extraites: {len(images)}")
    for img in images:
        print(f"  - {img}")
else:
    print("ERREUR: Dossier test-mcp-output non créé!")
```

Exécuter :
```powershell
python test_mcp_params.py
```

## Configuration Claude Desktop (MCP)

Modifier `%APPDATA%\Claude\claude_desktop_config.json` :

```json
{
  "mcpServers": {
    "markitdown-dev": {
      "type": "stdio",
      "command": "python",
      "args": [
        "-m",
        "markitdown_mcp"
      ],
      "env": {
        "PYTHONPATH": "C:\\Repos\\markitdown\\packages\\markitdown-mcp\\src"
      }
    }
  }
}
```

Redémarrer Claude Desktop après modification.

## Test MCP avec Claude

Dans Claude Desktop, essayer :

```
@markitdown-dev Convert this PPTX with icon filtering:
file:///C:/Repos/markitdown/pptx-test/Standard%20QA%20-%20Design%20des%20essais.pptx

Parameters:
- output_images: true
- skip_icon_images: true
- image_dir: "test-output"
```

## Vérification des Paramètres

Les nouveaux paramètres sont visibles dans la documentation du tool MCP :

```python
# Depuis Python
from markitdown_mcp.__main__ import mcp

# Lister les tools
print(mcp._tools)

# Inspecter convert_to_markdown
tool = mcp._tools["convert_to_markdown"]
print(tool.__doc__)
```

## Troubleshooting

### Les paramètres ne sont pas reconnus
→ Réinstaller en mode éditable : `pip install -e packages/markitdown-mcp`

### Images non extraites
→ Vérifier que `output_images=True` (défaut)
→ Vérifier les permissions du dossier `image_dir`

### Icons toujours extraits
→ Vérifier que `skip_icon_images=True` (défaut)
→ Classification basée sur noms de shapes (97% précision)

---

**Commit:** e3dcb49 - feat(mcp): expose BRIEF_01 parameters in MCP tool
**Status:** ✅ BRIEF_01 maintenant accessible via MCP
