#!/usr/bin/env python3
"""
Debug script to analyze MCP image extraction issue.

This script simulates exactly what the MCP does to understand
why it reports 0 images while the converter extracts them correctly.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "markitdown" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "markitdown-mcp" / "src"))

from markitdown import MarkItDown
from markitdown_mcp.utils import (
    check_plugins_enabled,
    resolve_image_path_for_file_uri,
)


def main():
    # Exact parameters used in MCP call
    uri = "file:///C:/Repos/markitdown/.copilot-tracking/pptx/z%20015_ARCH-00xx_WS4_Bancaire-b7f2a76a-7655-4a73-a5ab-035aee935269.pptx"
    output_images = True
    image_path = "C:/Repos/markitdown/.copilot-tracking/tests"
    skip_background_images = True
    skip_icon_images = False
    
    logs = []
    
    print("=== MCP SIMULATION ===")
    print(f"Input URI: {uri}")
    print(f"Input image_path: {image_path}")
    print(f"Output images: {output_images}")
    
    # Step 1: Resolve image_path (what MCP does)
    adjusted_image_path = resolve_image_path_for_file_uri(
        uri, image_path, output_images
    )
    logs.append(f"Resolved image_path: {adjusted_image_path}")
    print(f"\nStep 1 - Resolved image_path: {adjusted_image_path}")
    
    # Step 2: Test write access
    can_write_to_target = False
    fallback_temp_dir = None
    final_image_dir = None
    
    if output_images and adjusted_image_path:
        try:
            target_dir = Path(adjusted_image_path)
            target_dir.mkdir(parents=True, exist_ok=True)
            
            test_file = target_dir / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            
            can_write_to_target = True
            final_image_dir = str(target_dir)
            logs.append(f"Write access confirmed: {target_dir}")
            print(f"Step 2 - Write access confirmed: {target_dir}")
        except (PermissionError, OSError) as e:
            logs.append(f"Cannot write to {adjusted_image_path}: {e}")
            fallback_temp_dir = tempfile.mkdtemp(prefix="markitdown_images_")
            adjusted_image_path = fallback_temp_dir
            final_image_dir = fallback_temp_dir
            print(f"Step 2 - Using fallback: {fallback_temp_dir}")
    
    # Step 3: Check plugins
    enable_plugins = check_plugins_enabled()
    print(f"Step 3 - Plugins enabled: {enable_plugins}")
    
    # Step 4: Prepare conversion kwargs
    kwargs = {
        "output_images": output_images,
        "image_path": adjusted_image_path,
        "skip_background_images": skip_background_images,
        "skip_icon_images": skip_icon_images,
    }
    print(f"Step 4 - kwargs: {kwargs}")
    
    # Step 5: Perform conversion
    print("\nStep 5 - Converting...")
    converter = MarkItDown(enable_plugins=enable_plugins)
    result = converter.convert_uri(uri, **kwargs)
    print(f"  Markdown length: {len(result.markdown)}")
    
    # Step 6: Collect extracted images (what MCP does)
    extracted_images = []
    print(f"\nStep 6 - Checking final_image_dir: {final_image_dir}")
    print(f"  os.path.isdir(final_image_dir): {os.path.isdir(final_image_dir) if final_image_dir else 'N/A'}")
    
    if output_images and final_image_dir and os.path.isdir(final_image_dir):
        all_files = os.listdir(final_image_dir)
        print(f"  All files in dir: {all_files}")
        
        for filename in all_files:
            filepath = os.path.join(final_image_dir, filename)
            if os.path.isfile(filepath):
                extracted_images.append({
                    "name": filename,
                    "path": filepath,
                    "size": os.path.getsize(filepath)
                })
        logs.append(f"Extracted {len(extracted_images)} images to {final_image_dir}")
        print(f"  Extracted {len(extracted_images)} images")
    
    # Analysis
    print("\n=== ANALYSIS ===")
    print(f"Images found by MCP logic: {len(extracted_images)}")
    
    # Check if images are in a different location
    import re
    image_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', result.markdown)
    print(f"Image refs in markdown: {len(image_refs)}")
    
    # Get unique paths from markdown
    unique_paths = set(path for _, path in image_refs)
    print("Unique image paths in markdown:")
    for p in list(unique_paths)[:5]:
        print(f"  - {p}")
        
    # Check where images actually are
    if unique_paths:
        sample_path = list(unique_paths)[0]
        # Try to find the actual file
        possible_locations = [
            sample_path,
            os.path.join(os.getcwd(), sample_path),
            os.path.join(final_image_dir, os.path.basename(sample_path)) if final_image_dir else None,
        ]
        print(f"\nLooking for sample image: {sample_path}")
        for loc in possible_locations:
            if loc and os.path.exists(loc):
                print(f"  FOUND at: {loc}")
                break
        else:
            print("  NOT FOUND in expected locations!")

if __name__ == "__main__":
    main()
