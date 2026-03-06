#!/usr/bin/env python3
"""
Convert the PPTX to Markdown and save the result.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "markitdown" / "src"))

from markitdown import MarkItDown


def main():
    pptx_path = r"C:\Repos\markitdown\.copilot-tracking\pptx\z 015_ARCH-00xx_WS4_Bancaire-b7f2a76a-7655-4a73-a5ab-035aee935269.pptx"
    output_dir = r"C:\Repos\markitdown\.copilot-tracking\tests"
    
    # Create output directory and images subdirectory
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    print(f"Converting: {pptx_path}")
    print(f"Output dir: {output_dir}")
    print(f"Images dir: {images_dir}")
    
    # Convert
    converter = MarkItDown()
    result = converter.convert_local(
        pptx_path,
        output_images=True,
        image_path=images_dir,
        skip_background_images=True,
        skip_icon_images=False,
    )
    
    # Save markdown file
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    md_filename = f"z_015_ARCH-WS4_Bancaire_{timestamp}.md"
    md_path = os.path.join(output_dir, md_filename)
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(result.markdown)
    
    print(f"\nMarkdown saved: {md_path}")
    print(f"Markdown length: {len(result.markdown)} chars")
    
    # Count images
    images = [f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    print(f"Images extracted: {len(images)}")
    
    # Save summary
    summary = {
        "source": pptx_path,
        "markdown_file": md_path,
        "markdown_length": len(result.markdown),
        "images_dir": images_dir,
        "images_count": len(images),
        "converted_at": datetime.now().isoformat(),
    }
    
    summary_path = os.path.join(output_dir, f"conversion_summary_{timestamp}.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary saved: {summary_path}")
    
    return md_path, images_dir

if __name__ == "__main__":
    main()
