"""Validate Slide 6 rendering order after X-Y Cut implementation."""

import sys

sys.path.insert(0, "packages/markitdown/src")

from markitdown import MarkItDown  # noqa: E402

md = MarkItDown()
result = md.convert(
    ".copilot-tracking/pptx/Standard QA - Concept de base.pptx",
    output_images=False,
)

text = result.text_content

# Extract Slide 6 content
start = text.find("<!-- Slide number: 6 -->")
end = text.find("<!-- Slide number: 7 -->")
if start == -1 or end == -1:
    print("ERROR: Could not find Slide 6 markers")
    sys.exit(1)

slide6 = text[start:end].strip()
print("=== Slide 6 output ===")
print(slide6)
print()

# Verify ordering: Release management before MANDAT before SmartArt
# before OBJECTIFS before bullets
pos_release = slide6.find("Release management")
pos_mandat = slide6.find("MANDAT")
pos_smartart = slide6.find("SmartArt")
pos_objectifs = slide6.find("OBJECTIFS")
pos_diminuer = slide6.find("Diminuer les erreurs")

checks = [
    ("Release management found", pos_release != -1),
    ("MANDAT found", pos_mandat != -1),
    ("SmartArt found", pos_smartart != -1),
    ("OBJECTIFS found", pos_objectifs != -1),
    ("Bullets found", pos_diminuer != -1),
    ("Release mgmt BEFORE MANDAT", pos_release < pos_mandat),
    ("MANDAT BEFORE SmartArt", pos_mandat < pos_smartart),
    ("SmartArt BEFORE OBJECTIFS", pos_smartart < pos_objectifs),
    ("OBJECTIFS BEFORE bullets", pos_objectifs < pos_diminuer),
]

all_ok = True
for label, ok in checks:
    status = "OK" if ok else "FAIL"
    print(f"  [{status}] {label}")
    if not ok:
        all_ok = False

if all_ok:
    print("\nAll checks passed!")
else:
    print("\nSome checks FAILED!")
    sys.exit(1)
