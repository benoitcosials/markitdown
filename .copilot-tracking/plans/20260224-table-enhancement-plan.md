# Plan : Amélioration des Tables PPTX

## Objectif

Améliorer `_convert_table_to_markdown()` pour gérer 3 types de contenu de cellule :
1. **Texte** → Markdown texte
2. **Cellule vide avec couleur** → Emoji couleur ou "(couleur)"
3. **Cellule avec image(s)** → Extraction et insertion `![](path)`

## Décisions de Design

| Question | Décision |
|----------|----------|
| Format couleur | Emoji Unicode (🟢🔴🟡🔵) si disponible, sinon "(couleur)" |
| Images multiples | Extraire toutes les images |
| Texte + Couleur | Afficher les deux : `Texte 🟢` |

## Mapping Couleurs

### Emojis Unicode Disponibles
```
🟢 Vert       🔴 Rouge      🟡 Jaune
🔵 Bleu       🟠 Orange     🟣 Violet/Mauve
⚫ Noir       ⚪ Blanc      🟤 Marron
```

### Algorithme de Proximité
Pour les couleurs non standards, utiliser distance euclidienne RGB vers la couleur nommée la plus proche.

## Fonctions à Créer

### 1. `_get_cell_fill_color(cell) -> tuple[str, str] | None`
- Retourne `(emoji, nom_couleur)` ou `None`
- Accède à `cell.fill.type` et `cell.fill.fore_color`

### 2. `_rgb_to_color_name(r, g, b) -> tuple[str, str]`
- Mapping RGB → (emoji, nom)
- Algorithme de proximité si pas de match exact

### 3. `_get_cell_images(cell, tc_element, rels) -> list[tuple[bytes, str]]`
- Parse XML pour trouver `a:blipFill`
- Résout rId → média
- Retourne liste de (blob, extension)

### 4. `_convert_table_to_markdown()` - REFONTE
- Signature étendue avec slide_num, table_idx, pptx_stream
- Génère Markdown directement (plus de passage par HTML)

## Ordre d'Implémentation

- [ ] 1. Mapping couleurs RGB → emoji/nom
- [ ] 2. Fonction extraction couleur de cellule
- [ ] 3. Fonction extraction images de cellule
- [ ] 4. Refonte `_convert_table_to_markdown()`
- [ ] 5. Intégration dans `get_shape_content()`
- [ ] 6. Tests

## Nommage des Images

Pattern : `slide{N}_table{T}_cell{R}x{C}_img{I}.{ext}`
- N = numéro de slide
- T = index de table dans la slide  
- R = row, C = column
- I = index image si multiple

## Dépendances

- `cell.fill` - API python-pptx native
- `lxml` - Pour parser tcPr/blipFill (déjà installé pour SmartArt)
- `zipfile` - Pour accès média (déjà utilisé)
