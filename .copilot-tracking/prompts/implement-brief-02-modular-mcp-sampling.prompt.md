# Prompt d'Implémentation : BRIEF_02 - MCP Sampling avec Refactorisation Modulaire

**Pour** : Python Expert Agent  
**Date** : 21 février 2026  
**Estimation** : 7h (2h Phase 1 + 5h Phase 2)

---

## 🎯 Contexte du Projet

Tu vas implémenter **BRIEF_02** (Descriptions Textuelles LLM via MCP Sampling) pour le projet **MarkItDown**.

**Contexte** :
- **BRIEF_01** est complété ✅ (extraction images PPTX avec alt text fonctionnel)
- **BRIEF_02** ajoute l'analyse d'images via délégation au LLM client (MCP Sampling)
- **Client principal** : VS Code + GitHub Copilot (GPT-4o/Claude multimodal)
- **Standard** : MCP Protocol 2024-11-05 (sampling/createMessage)

**Approche innovante** :
Au lieu de configurer une API externe (OpenAI/Azure), on **délègue l'analyse d'images au LLM qui appelle notre MCP**. Ceci utilise la capacité "sampling" officielle du protocole MCP 2024-11-05.

**Avantages** :
- ✅ **0 configuration** (pas d'API keys)
- ✅ **2× plus rapide** (requests parallèles)
- ✅ **Moitié du coût** (client paie, pas le serveur)
- ✅ **Offline capable** (si client local)

---

## 📋 Documents de Référence

Tu **DOIS lire** ces documents avant de commencer :

1. **Plan d'implémentation (checkboxes)** :
   - Fichier : `.copilot-tracking/plans/20260221-brief-02-modular-mcp-sampling-plan.instructions.md`
   - Contient : Toutes les tâches avec checkboxes Phase 1 + Phase 2

2. **Spécifications techniques détaillées** :
   - Fichier : `.copilot-tracking/details/20260221-brief-02-modular-mcp-sampling-details.md`
   - Contient : Signatures fonctions, architecture, exemples code, standards MCP

3. **Document de recherche** :
   - Fichier : `.copilot-tracking/research/20260220-brief-02-llm-delegated-vision-research.md`
   - Contient : Comparaison OpenAI API vs MCP Sampling, exemples FastMCP

4. **Brief technique original** :
   - Fichier : `BRIEF_02_IMAGE_TEXT_DESCRIPTIONS.md`
   - Contient : Objectifs, modes, formats de sortie

---

## 🏗️ Architecture Cible

Tu vas **refactorer** le monolithe `__main__.py` (176 lignes) en **7 fichiers modulaires** :

```
packages/markitdown-mcp/src/markitdown_mcp/
├── __init__.py              # Package exports (48 lignes)
├── __about__.py             # Version metadata (UNCHANGED)
├── __main__.py              # Entry point (80 lignes) [REFACTORED]
├── tools.py                 # MCP tool definitions (120 lignes) [NEW]
├── vision_enhancement.py    # MCP sampling logic (250 lignes) [NEW - BRIEF_02]
├── utils.py                 # Shared utilities (60 lignes) [NEW]
└── server.py                # HTTP/SSE server setup (110 lignes) [NEW]
```

**Séparation des responsabilités** :
- `utils.py` : Helpers partagés (resolve paths, check env vars)
- `server.py` : Configuration Starlette HTTP/SSE
- `tools.py` : Définition outil MCP `convert_to_markdown`
- `vision_enhancement.py` : Toute la logique MCP Sampling (BRIEF_02)
- `__main__.py` : Entry point CLI uniquement

---

## 🔄 Workflow en 2 Phases OBLIGATOIRES

### ⚠️ PHASE 1 : Refactorisation Modulaire (2h)

**Objectif** : Migrer code existant vers structure modulaire **AVANT** d'ajouter BRIEF_02.

**Validation checkpoint** :
- ✅ Tous les tests BRIEF_01 DOIVENT passer
- ✅ Mode STDIO et HTTP DOIVENT fonctionner
- ✅ Aucune erreur linting (`get_errors`)
- ✅ Aucune régression fonctionnelle

**TU NE PEUX PAS** passer à Phase 2 tant que Phase 1 n'est pas validée.

---

### ✅ PHASE 2 : Implémentation MCP Sampling (5h)

**Objectif** : Ajouter analyse d'images via MCP Sampling dans nouveau module `vision_enhancement.py`.

**Fonctionnalités** :
- **Mode 1** (`output_images=True`) : Enrichir alt text vides avec descriptions courtes (100 chars)
- **Mode 2** (`output_images=False`) : Générer blocs description détaillés pour toutes images (500 tokens)

**Contraintes** :
- ✅ Conformité MCP Protocol 2024-11-05
- ✅ Fallback gracieux si client ne supporte pas sampling
- ✅ Type hints et docstrings complets
- ✅ Aucune modification dans `packages/markitdown/` (core)

---

## 📝 Instructions Spécifiques par Sprint

### Phase 1 - Sprints 1.1 à 1.6

**Sprint 1.1 : Module Utilities (30 min)**

Tu vas créer `packages/markitdown-mcp/src/markitdown_mcp/utils.py` avec :

1. **Function `resolve_image_dir_for_file_uri()`** :
   - Parser file:// URIs et résoudre image_dir relativement au fichier source
   - Fallback sur image_dir par défaut si pas file://
   - Type hints : `(uri: str, image_dir: Optional[str], output_images: bool) -> Optional[str]`
   - Docstring Google style avec exemple

2. **Function `check_plugins_enabled()`** :
   - Lire env var `MARKITDOWN_ENABLE_PLUGINS`
   - Return bool (true/1/yes → True)
   - Type hints : `() -> bool`

**Checklist** :
- [ ] Créer fichier utils.py
- [ ] Implémenter les 2 fonctions
- [ ] Ajouter header `# --- MODULE: Shared Utilities ---`
- [ ] Imports : os, urllib.parse, Path
- [ ] Utiliser `get_errors` pour vérifier

---

**Sprint 1.2 : Module Server (30 min)**

Tu vas créer `packages/markitdown-mcp/src/markitdown_mcp/server.py` en migrant depuis `__main__.py` :

**Code à migrer** :
- `create_starlette_app(mcp_server, debug)` function entière
- `handle_sse(request)` async handler
- `handle_streamable_http(scope, receive, send)` handler
- `lifespan(app)` context manager

**Checklist** :
- [ ] Créer fichier server.py
- [ ] Copier les 4 fonctions depuis __main__.py
- [ ] Ajouter imports nécessaires (starlette.*, mcp.server.*, contextlib)
- [ ] Ajouter docstrings et type hints
- [ ] Header `# --- MODULE: Server Setup (HTTP/SSE) ---`
- [ ] `get_errors` validation

---

**Sprint 1.3 : Module Tools (45 min)**

Tu vas créer `packages/markitdown-mcp/src/markitdown_mcp/tools.py` :

**Contenu** :
```python
from mcp import FastMCP
from markitdown import MarkItDown
from .utils import resolve_image_dir_for_file_uri, check_plugins_enabled

# Initialize FastMCP
mcp = FastMCP("markitdown")

# Initialize converter
converter = MarkItDown()

@mcp.tool()
async def convert_to_markdown(
    uri: str,
    output_images: bool = True,
    image_dir: str = "images",
    use_client_vision: bool = True  # NEW parameter for BRIEF_02
) -> str:
    """
    Convert file to Markdown with optional vision enhancement.
    
    Args:
        uri: File URI or path
        output_images: Save images to separate files
        image_dir: Directory for images (relative to source)
        use_client_vision: Use client's vision for image analysis (BRIEF_02)
    
    Returns:
        Markdown content
    """
    # Step 1: Resolve image_dir
    adjusted_image_dir = resolve_image_dir_for_file_uri(uri, image_dir, output_images)
    
    # Step 2: Check plugins
    enable_plugins = check_plugins_enabled()
    
    # Step 3: Convert file
    result = converter.convert_uri(
        uri=uri,
        image_dir=adjusted_image_dir,
        output_images=output_images,
        enable_plugins=enable_plugins
    )
    markdown = result.text_content
    
    # Step 4: Vision enhancement (BRIEF_02 - will be implemented in Phase 2)
    # For now, add placeholder comment:
    # BRIEF_02: Vision enhancement will be added in Phase 2
    # if use_client_vision:
    #     from .vision_enhancement import enhance_markdown_with_client_vision
    #     markdown = await enhance_markdown_with_client_vision(...)
    
    # Step 5: Return
    return markdown
```

**Checklist** :
- [ ] Créer tools.py
- [ ] Initialiser `mcp = FastMCP("markitdown")`
- [ ] Migrer `@mcp.tool() convert_to_markdown()` depuis __main__.py
- [ ] Ajouter paramètre `use_client_vision: bool = True`
- [ ] Utiliser helpers depuis utils
- [ ] Placeholder commenté pour Phase 2
- [ ] Header module
- [ ] `get_errors` validation

---

**Sprint 1.4 : Refactor __main__.py (30 min)**

Tu vas **RÉDUIRE** `packages/markitdown-mcp/src/markitdown_mcp/__main__.py` à ~80 lignes :

**Garder uniquement** :
```python
import sys
import argparse
from .tools import mcp
from .server import create_starlette_app

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MarkItDown MCP Server")
    parser.add_argument("--http", action="store_true")
    parser.add_argument("--port", type=int, default=3000)
    parser.add_argument("--debug", action="store_true")
    
    args = parser.parse_args()
    
    if args.http:
        import uvicorn
        app = create_starlette_app(mcp._server, debug=args.debug)
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    else:
        mcp.run()

if __name__ == "__main__":
    main()
```

**Checklist** :
- [ ] Supprimer tout le code migré (server, tools, utils)
- [ ] Garder uniquement main() et imports
- [ ] Vérifier ~80 lignes max
- [ ] Header `# --- MODULE: Entry Point ---`
- [ ] `get_errors` validation

---

**Sprint 1.5 : Update __init__.py (15 min)**

**Fichier** : `packages/markitdown-mcp/src/markitdown_mcp/__init__.py`

**Contenu** :
```python
"""
MarkItDown MCP Server

MCP server for file-to-markdown conversion.
"""

from .__about__ import __version__
from .tools import mcp

__all__ = ["mcp", "__version__"]
```

---

**Sprint 1.6 : Tests Régression BRIEF_01 (30 min)**

**CRITIQUE** : Phase 1 DOIT être validée avant Phase 2.

**Checklist** :
- [ ] Tester conversion PPTX basique
- [ ] Vérifier images extraites dans bon répertoire (relatif au PPTX)
- [ ] Tester mode STDIO : `python -m markitdown_mcp`
- [ ] Tester mode HTTP : `python -m markitdown_mcp --http`
- [ ] `get_errors` sur tous fichiers modifiés
- [ ] Tous tests passent ✅

**Si tout OK → Passer Phase 2**  
**Si erreurs → FIX avant de continuer**

---

### Phase 2 - Sprints 2.1 à 2.10

**Sprint 2.1 : Infrastructure Vision Enhancement (1h)**

Tu vas créer `packages/markitdown-mcp/src/markitdown_mcp/vision_enhancement.py` :

**Imports** :
```python
from typing import Optional
from pathlib import Path
import base64
import re
import imghdr

from mcp.server import Server
from mcp.types import (
    CreateMessageRequest,
    CreateMessageResult,
    SamplingMessage,
    TextContent,
    ImageContent,
)
```

**Function principale** :
```python
async def enhance_markdown_with_client_vision(
    markdown: str,
    server: Server,
    output_images: bool
) -> str:
    """
    Enhance Markdown with client vision analysis via MCP Sampling.
    
    Delegates image analysis to calling LLM client (VS Code Copilot, Claude, etc.)
    using MCP Protocol 2024-11-05 sampling capability.
    
    Args:
        markdown: Markdown content to enhance
        server: MCP server instance for sampling
        output_images: Mode 1 (True) = alt text, Mode 2 (False) = description blocks
        
    Returns:
        Enhanced markdown
    """
    # Check sampling support
    if not await client_supports_sampling(server):
        return markdown  # Graceful fallback
    
    # Delegate to mode-specific function
    if output_images:
        return await _enhance_alt_texts(markdown, server)
    else:
        return await _generate_description_blocks(markdown, server)
```

**Function capability check** :
```python
async def client_supports_sampling(server: Server) -> bool:
    """Check if client supports sampling."""
    try:
        caps = await server.get_client_capabilities()
        return caps.get("sampling", False)
    except Exception:
        return False
```

**Checklist** :
- [ ] Créer vision_enhancement.py
- [ ] Ajouter tous imports MCP types
- [ ] Implémenter `enhance_markdown_with_client_vision()`
- [ ] Implémenter `client_supports_sampling()`
- [ ] Header `# --- MODULE: Vision Enhancement via MCP Sampling (BRIEF_02) ---`
- [ ] Docstrings complètes
- [ ] Type hints

---

**Sprint 2.2 : Helpers et Parsers (30 min)**

**Ajouter dans vision_enhancement.py** :

```python
def parse_markdown_images(markdown: str) -> list[tuple[str, str]]:
    """Extract (alt_text, image_path) tuples from markdown."""
    pattern = r'!\[(.*?)\]\((.*?)\)'
    return re.findall(pattern, markdown)

def read_image_file(image_path: str) -> Optional[bytes]:
    """Read image file, return bytes or None."""
    try:
        with open(image_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return None

def detect_image_mime_type(image_data: bytes) -> str:
    """Detect MIME type from image bytes."""
    image_type = imghdr.what(None, h=image_data)
    return f"image/{image_type or 'png'}"
```

**Checklist** :
- [ ] Implémenter les 3 helper functions
- [ ] Docstrings
- [ ] `get_errors` validation

---

**Sprint 2.3 : MCP Sampling Core (1h)**

**Function clé** : `request_client_image_analysis()`

Voir spécifications complètes dans `.copilot-tracking/details/...`.

**Conformité MCP 2024-11-05** :
```python
async def request_client_image_analysis(
    server: Server,
    image_data: bytes,
    prompt: str,
    max_tokens: int
) -> Optional[str]:
    """
    Request image analysis via MCP sampling/createMessage.
    
    Implements MCP Protocol 2024-11-05 specification.
    """
    # Detect MIME
    mime_type = detect_image_mime_type(image_data)
    
    # Encode base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Create request (MCP 2024-11-05)
    request = CreateMessageRequest(
        messages=[
            SamplingMessage(
                role="user",
                content=[
                    TextContent(type="text", text=prompt),
                    ImageContent(
                        type="image",
                        data=image_base64,
                        mimeType=mime_type
                    )
                ]
            )
        ],
        maxTokens=max_tokens,
        systemPrompt="You are analyzing images from a PowerPoint presentation."
    )
    
    try:
        result: CreateMessageResult = await server.request_sampling(request)
        description = result.content.text.strip()
        return description[:max_tokens]
    except Exception:
        return None  # Graceful fallback
```

**Checklist** :
- [ ] Implémenter fonction complète
- [ ] Utiliser types MCP officiels
- [ ] Try/except pour fallback
- [ ] Docstring avec référence spec MCP
- [ ] Type hints Optional[str]

---

**Sprint 2.4 : Mode 1 - Alt Text Enrichi (1h)**

```python
async def _enhance_alt_texts(markdown: str, server: Server) -> str:
    """
    Mode 1: Enrich alt text for images WITHOUT alt text.
    
    Only processes images with empty alt text.
    Requests SHORT descriptions (max 100 chars).
    """
    images = parse_markdown_images(markdown)
    
    for alt_text, image_path in images:
        # Skip if alt text exists
        if alt_text and alt_text.strip():
            continue
        
        # Read image
        image_data = read_image_file(image_path)
        if not image_data:
            continue
        
        # Request short description
        prompt = "Describe this PowerPoint image in 1 concise phrase (max 100 characters):"
        description = await request_client_image_analysis(
            server, image_data, prompt, max_tokens=100
        )
        
        if description:
            # Replace empty alt text
            markdown = markdown.replace(
                f'![{alt_text}]({image_path})',
                f'![{description}]({image_path})'
            )
    
    return markdown
```

**Checklist** :
- [ ] Implémenter fonction
- [ ] Skip images avec alt text existant
- [ ] Prompt court (100 chars)
- [ ] Docstring Mode 1
- [ ] `get_errors`

---

**Sprint 2.5 : Mode 2 - Description Blocks (1h 30)**

```python
async def _generate_description_blocks(markdown: str, server: Server) -> str:
    """
    Mode 2: Generate description blocks for ALL images.
    
    Processes every image. Requests DETAILED descriptions (title + 10 lines).
    Formats as ```image-description blocks.
    """
    images = parse_markdown_images(markdown)
    
    for alt_text, image_path in images:
        image_data = read_image_file(image_path)
        if not image_data:
            continue
        
        # Detailed prompt
        prompt = """Analyze this PowerPoint image and provide:
1. A descriptive title (1 line)
2. Detailed description (max 10 lines) covering:
   - What is shown
   - Key visual elements
   - Context/purpose
   - Notable details"""
        
        description = await request_client_image_analysis(
            server, image_data, prompt, max_tokens=500
        )
        
        if description:
            # Format as block
            block = f"\n```image-description\n{description}\n```\n"
            
            # Replace image with block
            markdown = markdown.replace(
                f'![{alt_text}]({image_path})',
                block
            )
    
    return markdown
```

**Checklist** :
- [ ] Implémenter fonction
- [ ] Traiter TOUTES images (pas de skip)
- [ ] Prompt détaillé (500 tokens)
- [ ] Format ```image-description
- [ ] Docstring Mode 2

---

**Sprint 2.6 : Intégration dans Tools (30 min)**

**Éditer** `packages/markitdown-mcp/src/markitdown_mcp/tools.py` :

**Décommenter et activer** :
```python
# Top of file
from .vision_enhancement import enhance_markdown_with_client_vision

# Inside convert_to_markdown(), replace placeholder comment with:
    # BRIEF_02: Enhance with client vision if requested
    if use_client_vision:
        markdown = await enhance_markdown_with_client_vision(
            markdown=markdown,
            server=mcp._server,
            output_images=output_images
        )
```

**Checklist** :
- [ ] Ajouter import vision_enhancement
- [ ] Décommenter code vision
- [ ] Vérifier convert_to_markdown est async
- [ ] `get_errors` validation

---

**Sprint 2.7 : Tests VS Code + Copilot (1h)**

**Tests critiques** :

1. **Mode 1 (Alt Text)** :
```python
result = await convert_to_markdown(
    uri="file:///C:/test/presentation.pptx",
    output_images=True,
    use_client_vision=True
)
# Vérifier alt text enrichis (max 100 chars)
```

2. **Mode 2 (Description Blocks)** :
```python
result = await convert_to_markdown(
    uri="file:///C:/test/presentation.pptx",
    output_images=False,
    use_client_vision=True
)
# Vérifier ```image-description blocks
```

3. **Préservation Alt Text** :
```python
# PPTX avec alt text PowerPoint → doit être préservé
```

4. **Fallback sans Sampling** :
```python
# Simuler client sans sampling → alt text vides (pas d'erreur)
```

**Checklist** :
- [ ] Tester Mode 1
- [ ] Tester Mode 2
- [ ] Tester préservation alt text
- [ ] Tester fallback gracieux

---

**Sprints 2.8, 2.9, 2.10** : Voir plan détaillé dans `.copilot-tracking/plans/...`

---

## 🚨 Règles CRITIQUES à Respecter

### Qualité Code
- ✅ **`get_errors` après CHAQUE modification de fichier**
- ✅ **Fix immédiat** des erreurs détectées
- ✅ **Type hints** sur toutes fonctions
- ✅ **Docstrings** Google style sur toutes fonctions publiques
- ✅ **PEP 8** strict (79 chars, 4 espaces)

### Architecture
- ✅ **Modifications UNIQUEMENT dans** : `packages/markitdown-mcp/`
- ❌ **AUCUNE modification dans** : `packages/markitdown/` (core)
- ❌ **N'UTILISE PAS** : `_llm_caption.py` (obsolète)

### Workflow
- ✅ **Phase 1 COMPLÈTE** avant Phase 2
- ✅ **Tests régression** après Phase 1
- ✅ **Checkboxes** à cocher dans plan au fur et à mesure
- ✅ **Commits réguliers** avec messages clairs

### Standards
- ✅ **MCP Protocol 2024-11-05** strict
- ✅ **python.instructions.md** compliance
- ✅ **self-explanatory-code.instructions.md** compliance
- ✅ **Fallback gracieux** en cas d'erreur (jamais d'exception non gérée)

---

## 📊 Tracking de Progression

Tu vas mettre à jour le fichier `.copilot-tracking/changes/20260221-brief-02-modular-mcp-sampling-changes.md` après CHAQUE sprint complété avec :

```markdown
## Sprint [X.Y] : [Nom] - [Statut]

**Durée** : [temps réel]  
**Fichiers modifiés** :
- `path/to/file.py` : [description]

**Changements** :
- [Bullet point 1]
- [Bullet point 2]

**Tests** :
- [x] get_errors passé
- [x] Tests unitaires passés

**Problèmes rencontrés** : [Si applicable]
**Résolution** : [Si applicable]

---
```

---

## 🎯 Objectif Final

Après les 2 phases, le système doit :

**Phase 1** :
- ✅ Structure modulaire (7 fichiers)
- ✅ __main__.py réduit à 80 lignes
- ✅ Aucune régression BRIEF_01
- ✅ Modes STDIO et HTTP fonctionnels

**Phase 2** :
- ✅ Mode 1 : Alt text enrichis via sampling
- ✅ Mode 2 : Description blocks détaillés
- ✅ Compatible VS Code + Copilot (client principal)
- ✅ Compatible Claude Desktop
- ✅ Fallback gracieux si pas de sampling
- ✅ Conformité MCP 2024-11-05
- ✅ Code quality standards respectés

---

## 🚀 Commande de Démarrage

Tu commenceras par :

1. **Lire** les 4 documents de référence mentionnés au début
2. **Analyser** le code actuel de `__main__.py`
3. **Commencer Sprint 1.1** (Module Utilities)
4. **Progresser** sprint par sprint
5. **Cocher** les checkboxes dans plan
6. **Utiliser `get_errors`** après chaque modification
7. **Valider Phase 1** avant Phase 2

---

**Tu es prêt ? Commence par lire le plan et les specs, puis démarre Sprint 1.1 !**
