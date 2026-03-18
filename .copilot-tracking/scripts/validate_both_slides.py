"""Validate Slide 4 Bancaire ordering + Slide 6 QA still correct."""

import sys

sys.path.insert(0, "packages/markitdown/src")

from markitdown import MarkItDown  # noqa: E402

md = MarkItDown()

# --- Bancaire Slide 4 ---
result = md.convert(
    ".copilot-tracking/pptx/z 015_ARCH-00xx_WS4_Bancaire"
    "-b7f2a76a-7655-4a73-a5ab-035aee935269.pptx",
    output_images=False,
)
text = result.text_content

start = text.find("<!-- Slide number: 4 -->")
end = text.find("<!-- Slide number: 5 -->")
slide4 = text[start:end].strip()
print("=== Bancaire Slide 4 ===")
print(slide4)
print()

# Expected order: Phase 1 → SmartArt 1 → Phase 2 → SmartArt 2
pos_phase1 = slide4.find("Phase 1")
pos_sa1 = slide4.find("SmartArt 1")
pos_phase2 = slide4.find("Phase 2")
pos_sa2 = slide4.find("SmartArt 2")

checks_bancaire = [
    ("Phase 1 found", pos_phase1 != -1),
    ("SmartArt 1 found", pos_sa1 != -1),
    ("Phase 2 found", pos_phase2 != -1),
    ("SmartArt 2 found", pos_sa2 != -1),
    ("Phase 1 BEFORE SmartArt 1", pos_phase1 < pos_sa1),
    ("SmartArt 1 BEFORE Phase 2", pos_sa1 < pos_phase2),
    ("Phase 2 BEFORE SmartArt 2", pos_phase2 < pos_sa2),
]

all_ok = True
for label, ok in checks_bancaire:
    status = "OK" if ok else "FAIL"
    print(f"  [{status}] {label}")
    if not ok:
        all_ok = False

# --- QA Slide 6 ---
print("\n=== QA Slide 6 ===")
result2 = md.convert(
    ".copilot-tracking/pptx/Standard QA - Concept de base.pptx",
    output_images=False,
)
text2 = result2.text_content

start2 = text2.find("<!-- Slide number: 6 -->")
end2 = text2.find("<!-- Slide number: 7 -->")
slide6 = text2[start2:end2].strip()
print(slide6)
print()

pos_release = slide6.find("Release management")
pos_mandat = slide6.find("MANDAT")
pos_smartart = slide6.find("SmartArt")
pos_objectifs = slide6.find("OBJECTIFS")
pos_diminuer = slide6.find("Diminuer les erreurs")

checks_qa = [
    ("Release mgmt BEFORE MANDAT", pos_release < pos_mandat),
    ("MANDAT BEFORE SmartArt", pos_mandat < pos_smartart),
    ("SmartArt BEFORE OBJECTIFS", pos_smartart < pos_objectifs),
    ("OBJECTIFS BEFORE bullets", pos_objectifs < pos_diminuer),
]

for label, ok in checks_qa:
    status = "OK" if ok else "FAIL"
    print(f"  [{status}] {label}")
    if not ok:
        all_ok = False

if all_ok:
    print("\nAll checks passed!")
else:
    print("\nSome checks FAILED!")
    sys.exit(1)
