"""
Script de conversion batch PPTX vers Markdown.
Utilise l'API MarkItDown develop avec extraction d'images.
"""
import sys
from datetime import datetime
from pathlib import Path

# Workspace root (c:\Repos\markitdown)
WORKSPACE_ROOT = Path(__file__).parent.parent.parent

# Add local package to path
sys.path.insert(0, str(WORKSPACE_ROOT / "packages" / "markitdown" / "src"))

from markitdown import MarkItDown

# Input/output directories relative to workspace
PPTX_DIR = WORKSPACE_ROOT / ".copilot-tracking" / "pptx"
OUTPUT_BASE = WORKSPACE_ROOT / ".copilot-tracking" / "tests"


def convert_all() -> None:
    if not PPTX_DIR.exists():
        print(f"ERROR: PPTX directory not found: {PPTX_DIR}")
        return

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = OUTPUT_BASE / f"convert-pptx-{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    converter = MarkItDown()

    pptx_files = list(PPTX_DIR.glob("*.pptx"))
    print(f"Workspace: {WORKSPACE_ROOT}")
    print(f"Input: {PPTX_DIR}")
    print(f"Found {len(pptx_files)} PPTX files to convert")
    print(f"Output: {output_dir}\n")

    if not pptx_files:
        print("No PPTX files found.")
        return

    for pptx_file in pptx_files:
        print(f"Converting: {pptx_file.name}")

        sub_dir = output_dir / pptx_file.stem
        sub_dir.mkdir(parents=True, exist_ok=True)

        output_path = sub_dir / "content.md"
        image_path = "images"

        try:
            result = converter.convert(
                str(pptx_file),
                source_path=str(pptx_file),
                output_path=str(output_path),
                output_images=True,
                image_path=image_path,
                skip_background_images=True,
                skip_icon_images=False,
            )

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result.markdown)

            images_dir = sub_dir / "images"
            image_count = len(list(images_dir.glob("*"))) if images_dir.exists() else 0
            print(f"  -> OK: {output_path.relative_to(output_dir)} ({image_count} images)")

        except Exception as e:
            print(f"  -> ERROR: {e}")
            import traceback
            traceback.print_exc()

    print(f"\nDone! Results in: {output_dir}")

if __name__ == "__main__":
    convert_all()
