#!/usr/bin/env python3
"""
Debug script to analyze image extraction issues in PPTX conversion.

This script traces the exact flow of image extraction to identify why
images are not being saved to disk despite output_images=True.
"""

import os
import sys
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "markitdown" / "src"))

from markitdown import MarkItDown


def main():
    # Test file and output paths
    pptx_path = r"C:\Repos\markitdown\.copilot-tracking\pptx\z 015_ARCH-00xx_WS4_Bancaire-b7f2a76a-7655-4a73-a5ab-035aee935269.pptx"
    output_dir = r"C:\Repos\markitdown\.copilot-tracking\tests\debug_images"
    
    # Verify input file exists
    if not os.path.exists(pptx_path):
        print(f"ERROR: PPTX file not found: {pptx_path}")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Initialize converter
    converter = MarkItDown()
    
    # Test 1: Direct conversion with explicit parameters
    print("\n=== TEST 1: Direct convert_local with absolute image_path ===")
    try:
        result = converter.convert_local(
            pptx_path,
            output_images=True,
            image_path=output_dir,
            skip_background_images=True,
            skip_icon_images=False,
        )
        print(f"Markdown length: {len(result.markdown)}")
        
        # Check images in output directory
        images = [f for f in os.listdir(output_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        print(f"Images extracted: {len(images)}")
        for img in images:
            print(f"  - {img}")
            
        # Extract image references from markdown
        import re
        image_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', result.markdown)
        print(f"\nImage references in markdown: {len(image_refs)}")
        for alt, path in image_refs[:10]:  # First 10 only
            print(f"  - [{alt[:30]}...]({path})")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Via URI (like MCP does)
    print("\n=== TEST 2: convert_uri with file:// URI ===")
    file_uri = f"file:///{pptx_path.replace(os.sep, '/')}"
    output_dir_uri = output_dir + "_uri"
    os.makedirs(output_dir_uri, exist_ok=True)
    
    try:
        result = converter.convert_uri(
            file_uri,
            output_images=True,
            image_path=output_dir_uri,
            skip_background_images=True,
            skip_icon_images=False,
        )
        print(f"Markdown length: {len(result.markdown)}")
        
        # Check images
        images = [f for f in os.listdir(output_dir_uri) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        print(f"Images extracted: {len(images)}")
        for img in images:
            print(f"  - {img}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== ANALYSIS ===")
    print("If images are still 0, check:")
    print("1. Shape detection (_is_picture)")
    print("2. Filter conditions (skip_background, skip_icon)")
    print("3. Path issues in _save_image")
    print("4. Silent exceptions in image saving")

if __name__ == "__main__":
    main()
