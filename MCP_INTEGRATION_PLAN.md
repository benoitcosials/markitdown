# Plan d'Intégration MCP - CRITIQUE

## ??? Architecture du Problème

### État Actuel (Depuis commit 4bcfdeb)

**BRIEF_01 Core est COMPLET :**
- ? Images extraites du PPTX
- ? Formats supportés : PNG, JPG, GIF, BMP, WEBP, SVG, TIFF, EMF/WMF
- ? Classification : icon vs photo (97% accuracy)
- ? Filtrage : background et icons suivant les flags
- ? Paramètres exposés au MCP (depuis e3dcb49)

**Mais MCP a un PROBLÈME CRITIQUE :**
- Agent utilise @markitdown-ia avec file:///C:/Users/.../pres.pptx
- MCP reçoit l'URI mais perd le contexte directory
- convert_uri() exécute avec CWD = C:\Users\ledoee\AppData\Roaming\Code\...
- Images créées dans : C:\Users\ledoee\AppData\Roaming\Code\...
- ? Pas dans C:/Users/.../images/ où agent les attend
- Agent doit créer 3 scripts de support workflow (friction !)

### Solution Requise (MCP Level)

**TOUS les briefs dépendent du fix du répertoire MCP.**

## ??? Implémentation Requise

### File: packages/markitdown-mcp/src/markitdown_mcp/__main__.py

**Change**: Modify convert_to_markdown() to detect source directory from file:// URI

Key implementation:
1. Parse file:// URI to extract OS path
2. Get parent directory of source PPTX file
3. Resolve image_dir relative to that parent
4. Pass adjusted absolute path to converter

## ? Validation Checklist

- [ ] MCP detects source directory from file:// URI
- [ ] Images created relative to source PPTX directory, not VS Code temp
- [ ] All BRIEF parameters functional in MCP
- [ ] Agent workflow seamless (no manual scripts needed)
- [ ] Images appear in [source_dir]/images/ automatically

## ?? Success Criteria

- MCP creates images relative to source PPTX, not execution directory
- Agent workflow is seamless without manual intervention
- All BRIEF parameters functional through MCP
