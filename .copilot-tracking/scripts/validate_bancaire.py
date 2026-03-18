"""Validate Bancaire PPTX conversion — no regressions on SmartArt slides."""

import sys

sys.path.insert(0, "packages/markitdown/src")

from markitdown import MarkItDown  # noqa: E402

md = MarkItDown()
result = md.convert(
    ".copilot-tracking/pptx/z 015_ARCH-00xx_WS4_Bancaire-b7f2a76a-7655-4a73-a5ab-035aee935269.pptx",
    output_images=False,
)

text = result.text_content

# Count slides
slide_count = text.count("<!-- Slide number:")
print(f"Slides converted: {slide_count}")

# Count SmartArt
smartart_count = text.count("<!-- SmartArt")
print(f"SmartArt blocks rendered: {smartart_count}")

# Check no empty SmartArt tables  (headers but no rows)
import re

# Find all SmartArt table blocks and check they have content rows
pattern = r'\| Visual\s+\| Details\s+\|\n\|[-\s|]+\|\n'
empty_tables = []
for m in re.finditer(pattern, text):
    # Check if next line is a table row (starts with |)
    rest = text[m.end():m.end()+200]
    if not rest.strip().startswith('|'):
        # Find which slide this is in
        before = text[:m.start()]
        slide_marker = before.rfind("<!-- Slide number:")
        slide_info = text[slide_marker:slide_marker+40]
        empty_tables.append(slide_info.strip())

if empty_tables:
    print(f"\nWARNING: {len(empty_tables)} empty SmartArt tables found:")
    for s in empty_tables:
        print(f"  {s}")
else:
    print("No empty SmartArt tables (good!)")

# Verify all SmartArt have content
smartart_sections = text.split("<!-- SmartArt")[1:]  # Skip text before first SmartArt
for i, section in enumerate(smartart_sections, 1):
    # Get content until next slide marker or next SmartArt
    end_markers = ["<!-- Slide number:", "<!-- SmartArt"]
    end_pos = len(section)
    for marker in end_markers:
        pos = section.find(marker)
        if pos != -1 and pos < end_pos:
            end_pos = pos
    content = section[:end_pos].strip()
    lines = [l for l in content.split('\n') if l.strip() and not l.startswith('<!--')]
    if len(lines) < 2:
        print(f"  WARNING: SmartArt {i} has very little content: {len(lines)} lines")

print("\nDone! Bancaire PPTX validated.")
