# Plan d'Implémentation : BRIEF_02 - MCP Sampling avec Refactorisation Modulaire

**Date** : 21 février 2026  
**Estimation** : 7h (2h refactoring + 5h BRIEF_02)  
**Client Principal** : VS Code + GitHub Copilot  
**Standards** : MCP Protocol 2024-11-05

---

## Vue d'Ensemble

Ce plan implémente BRIEF_02 (Descriptions LLM via MCP Sampling) en **2 phases séquentielles** :

1. **Phase 1** : Refactorisation modulaire de `markitdown-mcp` (2h)
2. **Phase 2** : Implémentation MCP Sampling pour analyse d'images (5h)

**Architecture cible** :
```
packages/markitdown-mcp/src/markitdown_mcp/
├── __init__.py              # Package exports
├── __about__.py             # Version metadata (existant)
├── __main__.py              # Entry point (refactoré - 80 lignes)
├── tools.py                 # MCP tool definitions (NEW)
├── vision_enhancement.py    # MCP sampling logic (NEW - BRIEF_02)
├── utils.py                 # Shared utilities (NEW)
└── server.py                # HTTP/SSE server setup (NEW)
```

---

## ✅ PHASE 1 : Refactorisation Modulaire (2h)

**Objectif** : Séparer le monolithe `__main__.py` (176 lignes) en modules distincts par responsabilité.

### Sprint 1.1 : Créer Module Utilities (30 min)

- [ ] **1.1.1** Créer fichier `packages/markitdown-mcp/src/markitdown_mcp/utils.py`
- [ ] **1.1.2** Implémenter `resolve_image_dir_for_file_uri(uri, image_dir, output_images)` :
  - [ ] Parser file:// URIs avec urllib.parse
  - [ ] Extraire parent directory du fichier source
  - [ ] Résoudre image_dir relativement au fichier source
  - [ ] Fallback sur image_dir par défaut en cas d'erreur
  - [ ] Docstring avec type hints complets
- [ ] **1.1.3** Implémenter `check_plugins_enabled()` :
  - [ ] Lire MARKITDOWN_ENABLE_PLUGINS env var
  - [ ] Return bool (true/1/yes → True)
  - [ ] Docstring explicative
- [ ] **1.1.4** Ajouter imports nécessaires (os, urllib.parse, Path)
- [ ] **1.1.5** Ajouter header module `# --- MODULE: Shared Utilities ---`

### Sprint 1.2 : Créer Module Server (30 min)

- [ ] **1.2.1** Créer fichier `packages/markitdown-mcp/src/markitdown_mcp/server.py`
- [ ] **1.2.2** Copier `create_starlette_app(mcp_server, debug)` depuis __main__.py
- [ ] **1.2.3** Copier `handle_sse(request)` async handler
- [ ] **1.2.4** Copier `handle_streamable_http(scope, receive, send)` handler
- [ ] **1.2.5** Copier `lifespan(app)` context manager
- [ ] **1.2.6** Ajouter tous les imports nécessaires :
  - [ ] contextlib, AsyncIterator
  - [ ] mcp.server (Server, SseServerTransport, StreamableHTTPSessionManager)
  - [ ] starlette (Starlette, Request, Mount, Route, Receive, Scope, Send)
- [ ] **1.2.7** Ajouter docstrings et type hints
- [ ] **1.2.8** Header module `# --- MODULE: Server Setup (HTTP/SSE) ---`

### Sprint 1.3 : Créer Module Tools (45 min)

- [ ] **1.3.1** Créer fichier `packages/markitdown-mcp/src/markitdown_mcp/tools.py`
- [ ] **1.3.2** Importer FastMCP et initialiser `mcp = FastMCP("markitdown")`
- [ ] **1.3.3** Importer MarkItDown
- [ ] **1.3.4** Importer helpers depuis utils :
  - [ ] `from .utils import resolve_image_dir_for_file_uri, check_plugins_enabled`
- [ ] **1.3.5** Copier `@mcp.tool() convert_to_markdown()` depuis __main__.py
- [ ] **1.3.6** Ajouter nouveau paramètre `use_client_vision: bool = True`
- [ ] **1.3.7** Utiliser `resolve_image_dir_for_file_uri()` pour adjusted_image_dir
- [ ] **1.3.8** Utiliser `check_plugins_enabled()` pour plugins
- [ ] **1.3.9** Placeholder pour vision enhancement (sera ajouté Phase 2) :
  ```python
  # BRIEF_02: Vision enhancement will be added in Phase 2
  # if use_client_vision:
  #     markdown = await enhance_markdown_with_client_vision(...)
  ```
- [ ] **1.3.10** Mettre à jour docstring avec nouveau paramètre
- [ ] **1.3.11** Header module `# --- MODULE: MCP Tool Definitions ---`

### Sprint 1.4 : Refactorer __main__.py (30 min)

- [ ] **1.4.1** Supprimer tout le code migré vers autres modules
- [ ] **1.4.2** Ajouter imports des nouveaux modules :
  ```python
  from .tools import mcp
  from .server import create_starlette_app
  ```
- [ ] **1.4.3** Garder uniquement `main()` function :
  - [ ] argparse configuration
  - [ ] Logique use_http
  - [ ] Appel create_starlette_app() ou mcp.run()
- [ ] **1.4.4** Garder `if __name__ == "__main__": main()`
- [ ] **1.4.5** Vérifier imports minimum (sys, argparse, uvicorn)
- [ ] **1.4.6** Réduire à ~80 lignes
- [ ] **1.4.7** Header module `# --- MODULE: Entry Point ---`

### Sprint 1.5 : Mettre à Jour Package Exports (15 min)

- [ ] **1.5.1** Éditer `packages/markitdown-mcp/src/markitdown_mcp/__init__.py`
- [ ] **1.5.2** Ajouter imports :
  ```python
  from .__about__ import __version__
  from .tools import mcp
  ```
- [ ] **1.5.3** Définir `__all__ = ["mcp", "__version__"]`
- [ ] **1.5.4** Ajouter docstring package

### Sprint 1.6 : Tests de Régression BRIEF_01 (30 min)

- [ ] **1.6.1** Tester conversion PPTX basique :
  ```python
  result = MarkItDown().convert_uri("file:///path/to/test.pptx", output_images=True)
  ```
- [ ] **1.6.2** Vérifier images extraites dans le bon répertoire (relatif au PPTX)
- [ ] **1.6.3** Vérifier aucune erreur d'import
- [ ] **1.6.4** Tester mode STDIO `markitdown-mcp`
- [ ] **1.6.5** Tester mode HTTP `markitdown-mcp --http`
- [ ] **1.6.6** Utiliser `get_errors` pour vérifier aucune erreur linting
- [ ] **1.6.7** Confirmer ✅ Phase 1 complète avant Phase 2

---

## ✅ PHASE 2 : Implémentation MCP Sampling (5h)

**Objectif** : Implémenter délégation analyse d'images au LLM client via MCP Sampling.

### Sprint 2.1 : Créer Module Vision Enhancement - Infrastructure (1h)

- [ ] **2.1.1** Créer fichier `packages/markitdown-mcp/src/markitdown_mcp/vision_enhancement.py`
- [ ] **2.1.2** Ajouter imports MCP types :
  ```python
  from mcp.server import Server
  from mcp.types import (
      CreateMessageRequest,
      CreateMessageResult,
      SamplingMessage,
      TextContent,
      ImageContent,
  )
  ```
- [ ] **2.1.3** Ajouter imports standard (base64, re, imghdr, Optional, Path)
- [ ] **2.1.4** Header module `# --- MODULE: Vision Enhancement via MCP Sampling (BRIEF_02) ---`
- [ ] **2.1.5** Implémenter `async def enhance_markdown_with_client_vision(markdown, server, output_images)` :
  - [ ] Check sampling support avec `await client_supports_sampling(server)`
  - [ ] Return markdown as-is si sampling non supporté
  - [ ] If output_images → appeler `_enhance_alt_texts()`
  - [ ] Else → appeler `_generate_description_blocks()`
  - [ ] Docstring complète avec args/returns
  - [ ] Type hints complets
- [ ] **2.1.6** Implémenter `async def client_supports_sampling(server)` :
  - [ ] Try/except autour de `server.get_client_capabilities()`
  - [ ] Return `caps.get("sampling", False)`
  - [ ] Fallback False en cas d'erreur
  - [ ] Docstring

### Sprint 2.2 : Helpers et Parsers (30 min)

- [ ] **2.2.1** Implémenter `def parse_markdown_images(markdown)` :
  - [ ] Regex pattern `r'!\[(.*?)\]\((.*?)\)'`
  - [ ] `re.findall(pattern, markdown)`
  - [ ] Return list[tuple[str, str]] (alt_text, image_path)
  - [ ] Docstring avec exemple
- [ ] **2.2.2** Implémenter `def read_image_file(image_path)` :
  - [ ] Try/except FileNotFoundError
  - [ ] Return bytes ou None
  - [ ] Docstring
- [ ] **2.2.3** Implémenter `def detect_image_mime_type(image_data)` :
  - [ ] Utiliser `imghdr.what(None, h=image_data)`
  - [ ] Return `f"image/{image_type or 'png'}"`
  - [ ] Docstring

### Sprint 2.3 : MCP Sampling Core (1h)

- [ ] **2.3.1** Implémenter `async def request_client_image_analysis(server, image_data, prompt, max_tokens)` :
  - [ ] Détecter MIME type avec `detect_image_mime_type()`
  - [ ] Encoder base64 : `base64.b64encode(image_data).decode('utf-8')`
  - [ ] Créer `CreateMessageRequest` :
    - [ ] messages = [SamplingMessage(...)]
    - [ ] content = [TextContent(prompt), ImageContent(base64, mimeType)]
    - [ ] maxTokens = max_tokens
    - [ ] systemPrompt = "You are analyzing images from a PowerPoint presentation."
  - [ ] Try/except autour de `await server.request_sampling(request)`
  - [ ] Return `result.content.text.strip()[:max_tokens]`
  - [ ] Return None en cas d'erreur (fallback gracieux)
  - [ ] Docstring complète avec conformité MCP 2024-11-05
  - [ ] Type hints Optional[str]

### Sprint 2.4 : Mode 1 - Alt Text Enrichi (1h)

- [ ] **2.4.1** Implémenter `async def _enhance_alt_texts(markdown, server)` :
  - [ ] Parser images avec `parse_markdown_images(markdown)`
  - [ ] Boucle sur images
  - [ ] Skip si alt_text existe et non vide (`if alt_text and alt_text.strip()`)
  - [ ] Lire image avec `read_image_file(image_path)`
  - [ ] Skip si lecture échoue
  - [ ] Définir prompt court :
    ```python
    prompt = "Describe this PowerPoint image in 1 concise phrase (max 100 characters):"
    ```
  - [ ] Appeler `await request_client_image_analysis(server, image_data, prompt, max_tokens=100)`
  - [ ] Si description reçue :
    - [ ] `markdown = markdown.replace(f'![{alt_text}]({image_path})', f'![{description}]({image_path})')`
  - [ ] Return markdown enrichi
  - [ ] Docstring Mode 1 spécifique
  - [ ] Type hints

### Sprint 2.5 : Mode 2 - Description Blocks (1h 30)

- [ ] **2.5.1** Implémenter `async def _generate_description_blocks(markdown, server)` :
  - [ ] Parser images avec `parse_markdown_images(markdown)`
  - [ ] Boucle sur TOUTES les images (pas de filter)
  - [ ] Lire image avec `read_image_file(image_path)`
  - [ ] Skip si lecture échoue
  - [ ] Définir prompt détaillé :
    ```python
    prompt = """Analyze this PowerPoint image and provide:
    1. A descriptive title (1 line)
    2. Detailed description (max 10 lines) covering:
       - What is shown
       - Key visual elements
       - Context/purpose
       - Notable details"""
    ```
  - [ ] Appeler `await request_client_image_analysis(server, image_data, prompt, max_tokens=500)`
  - [ ] Si description reçue :
    - [ ] Formater en bloc :
      ```python
      block = f"\n```image-description\n{description}\n```\n"
      ```
    - [ ] Remplacer `![{alt_text}]({image_path})` par bloc
  - [ ] Return markdown avec blocs
  - [ ] Docstring Mode 2 spécifique
  - [ ] Type hints

### Sprint 2.6 : Intégration dans Tools (30 min)

- [ ] **2.6.1** Éditer `packages/markitdown-mcp/src/markitdown_mcp/tools.py`
- [ ] **2.6.2** Ajouter import :
  ```python
  from .vision_enhancement import enhance_markdown_with_client_vision
  ```
- [ ] **2.6.3** Décommenter et activer le code vision :
  ```python
  # BRIEF_02: Enhance with client vision if requested
  if use_client_vision:
      markdown = await enhance_markdown_with_client_vision(
          markdown=markdown,
          server=mcp._server,
          output_images=output_images
      )
  ```
- [ ] **2.6.4** Vérifier que `convert_to_markdown()` est async
- [ ] **2.6.5** Utiliser `get_errors` pour vérifier imports et syntax

### Sprint 2.7 : Tests VS Code + GitHub Copilot (1h)

- [ ] **2.7.1** Tester Mode 1 (Alt Text Enrichi) :
  - [ ] Créer PPTX test avec images sans alt text
  - [ ] Appeler `convert_to_markdown(uri, output_images=True, use_client_vision=True)`
  - [ ] Vérifier alt text enrichis via sampling
  - [ ] Vérifier images sauvegardées
  - [ ] Mesurer temps de traitement (5 images)
- [ ] **2.7.2** Tester Mode 2 (Description Blocks) :
  - [ ] Appeler `convert_to_markdown(uri, output_images=False, use_client_vision=True)`
  - [ ] Vérifier blocs ```image-description présents
  - [ ] Vérifier aucune image sauvegardée
  - [ ] Vérifier format titre + description
- [ ] **2.7.3** Tester images avec alt text existant :
  - [ ] Créer PPTX avec alt text PowerPoint
  - [ ] Vérifier alt text préservé (pas de sampling)
- [ ] **2.7.4** Tester fallback sans sampling :
  - [ ] Simuler client sans sampling capability
  - [ ] Vérifier alt text reste vide (pas d'erreur)

### Sprint 2.8 : Tests Compatibilité Multi-Clients (30 min)

- [ ] **2.8.1** Tester avec Claude Desktop :
  - [ ] Configuration MCP dans claude_desktop_config.json
  - [ ] Tester sampling requests
  - [ ] Vérifier descriptions générées
- [ ] **2.8.2** Tester avec MCP Inspector :
  - [ ] Démarrer inspector `npx @modelcontextprotocol/inspector`
  - [ ] Connecter en SSE mode
  - [ ] Tester tool convert_to_markdown
  - [ ] Inspecter sampling requests
- [ ] **2.8.3** Tester fallback gracieux :
  - [ ] Client sans sampling → alt text vide
  - [ ] Erreur sampling → alt text vide
  - [ ] Aucune exception levée

### Sprint 2.9 : Validation Standards MCP 2024-11-05 (30 min)

- [ ] **2.9.1** Vérifier structure `CreateMessageRequest` :
  - [ ] messages: list[SamplingMessage]
  - [ ] maxTokens: int
  - [ ] systemPrompt (optionnel)
- [ ] **2.9.2** Vérifier `SamplingMessage` :
  - [ ] role: "user"
  - [ ] content: list[TextContent | ImageContent]
- [ ] **2.9.3** Vérifier `ImageContent` :
  - [ ] type: "image"
  - [ ] data: base64 string
  - [ ] mimeType: image/png, image/jpeg, etc.
- [ ] **2.9.4** Tester MIME types variés :
  - [ ] PNG, JPEG, GIF
  - [ ] Vérifier détection correcte avec imghdr

### Sprint 2.10 : Documentation et Qualité Code (30 min)

- [ ] **2.10.1** Vérifier tous les type hints :
  - [ ] Async functions → Awaitable return
  - [ ] Optional pour valeurs nullable
  - [ ] list[tuple[str, str]] pour tuples
- [ ] **2.10.2** Vérifier toutes les docstrings :
  - [ ] Google style
  - [ ] Args, Returns, Raises sections
  - [ ] Exemples si pertinent
- [ ] **2.10.3** Appliquer python.instructions.md :
  - [ ] PEP 8 style (79 chars, 4 espaces)
  - [ ] Imports groupés (standard, external, internal)
  - [ ] Module markers présents
- [ ] **2.10.4** Appliquer self-explanatory-code.instructions.md :
  - [ ] Commenter le WHY, pas le WHAT
  - [ ] Noms variables explicites
  - [ ] Annotations TODO/FIXME si nécessaire
- [ ] **2.10.5** Utiliser `get_errors` sur tous les fichiers modifiés :
  - [ ] tools.py
  - [ ] vision_enhancement.py
  - [ ] utils.py
  - [ ] server.py
  - [ ] __main__.py
- [ ] **2.10.6** Fixer toutes les erreurs détectées

---

## ✅ Conditions d'Acceptation

### Phase 1 (Refactoring)
- [ ] ✅ Structure modulaire créée (7 fichiers total)
- [ ] ✅ __main__.py réduit à ~80 lignes
- [ ] ✅ Tous les tests BRIEF_01 passent (aucune régression)
- [ ] ✅ Aucune erreur linting (`get_errors`)
- [ ] ✅ Mode STDIO et HTTP fonctionnent

### Phase 2 (BRIEF_02)
- [ ] ✅ Mode 1 : Alt text enrichis via sampling
- [ ] ✅ Mode 2 : Blocs description générés
- [ ] ✅ Compatible VS Code + GitHub Copilot (client principal)
- [ ] ✅ Compatible Claude Desktop
- [ ] ✅ Fallback gracieux si sampling non supporté
- [ ] ✅ Conformité MCP Protocol 2024-11-05
- [ ] ✅ Type hints et docstrings complets
- [ ] ✅ Aucune erreur linting

---

## 📊 Estimation Détaillée

| Sprint | Description | Temps |
|--------|-------------|-------|
| **PHASE 1** | **Refactorisation** | **2h** |
| 1.1 | Module Utilities | 30 min |
| 1.2 | Module Server | 30 min |
| 1.3 | Module Tools | 45 min |
| 1.4 | Refactor __main__ | 30 min |
| 1.5 | Package Exports | 15 min |
| 1.6 | Tests Régression | 30 min |
| **PHASE 2** | **MCP Sampling** | **5h** |
| 2.1 | Infrastructure | 1h |
| 2.2 | Helpers/Parsers | 30 min |
| 2.3 | Sampling Core | 1h |
| 2.4 | Mode 1 Alt Text | 1h |
| 2.5 | Mode 2 Descriptions | 1h 30 min |
| 2.6 | Intégration Tools | 30 min |
| 2.7 | Tests VS Code | 1h |
| 2.8 | Tests Multi-Clients | 30 min |
| 2.9 | Validation Standards | 30 min |
| 2.10 | Documentation | 30 min |
| **TOTAL** | | **7h** |

---

## 🚨 Contraintes Critiques

### Architecture
- ✅ **Modifications UNIQUEMENT dans** : `packages/markitdown-mcp/`
- ❌ **AUCUNE modification dans** : `packages/markitdown/` (core)
- ❌ **N'UTILISE PAS** : `_llm_caption.py` (obsolète)

### Workflow
- ✅ **Phase 1 COMPLÈTE avant Phase 2**
- ✅ Tests régression Phase 1 avant de continuer
- ✅ `get_errors` après chaque modification fichier
- ✅ Fix immédiat des erreurs avant de continuer

### Standards
- ✅ MCP Protocol 2024-11-05 strict
- ✅ python.instructions.md compliance
- ✅ self-explanatory-code.instructions.md compliance
- ✅ Type hints obligatoires
- ✅ Docstrings Google style

---

**Prochaine étape** : Invoquer Python Expert pour implémentation progressive avec ce plan.
