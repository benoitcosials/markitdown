"""
Full Images PPTX Test Suite - SmartArt with embedded images extraction.

This script converts PPTX files to Markdown in FULL IMAGES mode:
- Physical image extraction enabled (output_images=True)
- All images extracted, including SmartArt embedded images
- Focus on validating SmartArt with images (Type 2 conversion)

Key difference from other test scripts:
- Text-Only: No images extracted (output_images=False)
- Full Images: All images extracted including SmartArt embedded images
- Comprehensive: Similar but without SmartArt-specific analysis
"""

import os
import re
from datetime import datetime
from pathlib import Path

from markitdown import MarkItDown


def extract_smartart_blocks_with_images(markdown_text: str) -> list[dict]:
    """
    Extract SmartArt blocks from Markdown, detecting if they contain images.
    
    Looks for:
    - ### SmartArt N (Slide X) headers
    - Table format (Type 2) with image links
    - List format (Type 1) without images
    
    Args:
        markdown_text: Markdown content to analyze
    
    Returns:
        List of dicts with SmartArt info including image detection
    """
    smartart_blocks = []
    
    # Pattern: ### SmartArt N (Slide X)
    pattern = r'### SmartArt (\d+) \(Slide (\d+)\)'
    
    matches = list(re.finditer(pattern, markdown_text))
    
    for i, match in enumerate(matches):
        smartart_num = int(match.group(1))
        start_pos = match.end()
        
        # Determine end position
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(markdown_text)
        
        content = markdown_text[start_pos:end_pos].strip()
        
        # Detect format type
        has_table = '|' in content and '---' in content
        
        # Count images in content (![...](images/...))
        image_links = re.findall(r'!\[.*?\]\((images/.*?)\)', content)
        
        # Count list items
        list_items = re.findall(r'^\s*[-*]|\d+\.', content, re.MULTILINE)
        
        slide_num = int(match.group(2))
        
        smartart_blocks.append({
            'number': smartart_num,
            'slide': slide_num,
            'title': match.group(0),
            'content': content[:600],  # Preview
            'format_type': 'Type 2 (Table)' if has_table else 'Type 1 (List)',
            'has_images': len(image_links) > 0,
            'image_count': len(image_links),
            'image_paths': image_links[:5],  # First 5 images
            'item_count': len(list_items),
            'full_length': len(content)
        })
    
    return smartart_blocks


def process_single_pptx_full_images(pptx_file_path, output_parent_dir=None):
    """
    Convert single PPTX to Markdown with FULL IMAGE extraction.
    
    Args:
        pptx_file_path: Path to PPTX (str, absolute or relative)
        output_parent_dir: Parent output directory for results
    
    Returns:
        dict with conversion results + SmartArt analysis
    """
    pptx_path = Path(pptx_file_path).resolve()
    
    if not pptx_path.exists():
        return {
            "file": str(pptx_file_path),
            "status": "FAILED",
            "smartart_count": 0,
            "images": 0,
            "error": f"File not found: {pptx_file_path}"
        }
    
    pptx_stem = pptx_path.stem
    
    # Determine output directory
    if output_parent_dir is None:
        output_dir = pptx_path.parent / f"{pptx_stem}_full_images"
    else:
        output_dir = Path(output_parent_dir) / pptx_stem
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    images_dir_name = "images"
    
    try:
        # Change to output directory for relative path handling
        original_cwd = os.getcwd()
        try:
            os.chdir(str(output_dir))
            
            # Convert - FULL IMAGES MODE
            md = MarkItDown()
            result = md.convert(
                source=pptx_path,
                image_dir=images_dir_name,
                output_images=True,  # KEY: Extract all images
                skip_background_images=True
            )
            
        finally:
            os.chdir(original_cwd)
        
        # Write markdown output
        output_md = output_dir / "output_full_images.md"
        output_md.write_text(result.markdown, encoding="utf-8")
        
        # Count extracted images
        images_dir = output_dir / images_dir_name
        image_count = len(list(images_dir.glob("*"))) if images_dir.exists() else 0
        
        # Analyze SmartArt
        smartart_blocks = extract_smartart_blocks_with_images(result.markdown)
        
        # Count SmartArt with images (Type 2)
        smartart_with_images = [s for s in smartart_blocks if s['has_images']]
        smartart_text_only = [s for s in smartart_blocks if not s['has_images']]
        
        return {
            "file": pptx_path.name,
            "status": "SUCCESS",
            "images": image_count,
            "smartart_count": len(smartart_blocks),
            "smartart_with_images": len(smartart_with_images),
            "smartart_text_only": len(smartart_text_only),
            "smartart_blocks": smartart_blocks,
            "markdown_length": len(result.markdown),
            "error": None
        }
        
    except Exception as e:
        return {
            "file": pptx_path.name,
            "status": "FAILED",
            "images": 0,
            "smartart_count": 0,
            "error": str(e)
        }


def run_full_images_tests():
    """Run FULL IMAGES extraction tests on all PPTX files."""
    
    # Prepare directories
    test_pptx_dir = Path("pptx-test")
    pptx_result_dir = Path("pptx-result")
    pptx_result_dir.mkdir(exist_ok=True)
    
    # Create timestamped result folder
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    test_session_dir = pptx_result_dir / f"full-images-{timestamp}"
    test_session_dir.mkdir(parents=True, exist_ok=True)
    
    # List all PPTX files
    pptx_files = sorted(test_pptx_dir.glob("*.pptx"))
    pptx_files = [f for f in pptx_files if not f.name.startswith('~$')]
    
    if not pptx_files:
        print(f"Aucun fichier .pptx trouvé dans {test_pptx_dir}")
        print(f"Dossier de résultats créé: {test_session_dir}")
        return
    
    print("=" * 80)
    print("TEST FULL IMAGES MODE - SMARTART WITH EMBEDDED IMAGES")
    print(f"Timestamp: {timestamp}")
    print(f"Mode: output_images=True (extraction complète)")
    print("=" * 80 + "\n")
    
    results = []
    
    for idx, pptx_file in enumerate(pptx_files, 1):
        print(f"[{idx}/{len(pptx_files)}] Traitement: {pptx_file.name}")
        
        result = process_single_pptx_full_images(
            pptx_file_path=pptx_file,
            output_parent_dir=test_session_dir
        )
        
        results.append(result)
        
        if result["status"] == "SUCCESS":
            print(f"  ✅ SUCCESS: {result['images']} images, {result['smartart_count']} SmartArt ({result['smartart_with_images']} avec images)")
        else:
            print(f"  ❌ FAILED: {result['error']}")
    
    # Generate report
    print("\n" + "=" * 80)
    print("RAPPORT DE TEST FULL IMAGES")
    print("=" * 80 + "\n")
    
    successful = [r for r in results if r["status"] == "SUCCESS"]
    failed = [r for r in results if r["status"] == "FAILED"]
    total_images = sum(r["images"] for r in results)
    total_smartart = sum(r["smartart_count"] for r in results)
    total_smartart_with_images = sum(r.get("smartart_with_images", 0) for r in results)
    
    report_file = test_session_dir / "full_images_report.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        # Header
        f.write("# Rapport Test FULL IMAGES Mode - SmartArt avec Images\n\n")
        f.write(f"**Date/Heure**: {timestamp}\n\n")
        f.write(f"**Dossier de résultats**: `pptx-result/full-images-{timestamp}/`\n\n")
        f.write(f"**Mode de conversion**: `output_images=True` (extraction complète)\n\n")
        
        # Summary
        f.write("## Résumé\n\n")
        f.write(f"- **Total fichiers**: {len(pptx_files)}\n")
        f.write(f"- **Réussis**: {len(successful)} ✅\n")
        f.write(f"- **Échoués**: {len(failed)} ❌\n")
        f.write(f"- **Total images extraites**: {total_images}\n")
        f.write(f"- **Total SmartArt**: {total_smartart}\n")
        f.write(f"- **SmartArt avec images (Type 2)**: {total_smartart_with_images}\n")
        f.write(f"- **SmartArt texte seul (Type 1)**: {total_smartart - total_smartart_with_images}\n\n")
        
        # Success rate
        success_rate = (len(successful) / len(pptx_files)) * 100 if pptx_files else 0
        f.write(f"**Taux de réussite**: {success_rate:.1f}%\n\n")
        
        # Mode explanation
        f.write("## À propos du Mode Full Images\n\n")
        f.write("**Objectif**: Extraire toutes les images, y compris celles embarquées dans les SmartArt.\n\n")
        f.write("**Avantages**:\n")
        f.write("- ✅ Extraction complète de toutes les images\n")
        f.write("- ✅ Validation des SmartArt Type 2 (tableaux avec images)\n")
        f.write("- ✅ Images embarquées SmartArt physiquement sauvegardées\n")
        f.write("- ✅ Liens relatifs dans le Markdown\n\n")
        
        f.write("**Types de conversion SmartArt**:\n")
        f.write("- **Type 1**: Texte seulement → Liste Markdown (SmartArt sans images)\n")
        f.write("- **Type 2**: Avec images → Tableau Markdown 3 colonnes (Image | Texte | Image)\n\n")
        
        # Successful conversions
        if successful:
            f.write("## Conversions Réussies ✅\n\n")
            for result in successful:
                f.write(f"### {result['file']}\n\n")
                f.write("- **Status**: SUCCESS\n")
                f.write(f"- **Images totales**: {result['images']}\n")
                f.write(f"- **SmartArt trouvés**: {result['smartart_count']}\n")
                f.write(f"  - Avec images (Type 2): {result['smartart_with_images']}\n")
                f.write(f"  - Texte seul (Type 1): {result['smartart_text_only']}\n")
                f.write(f"- **Longueur Markdown**: {result['markdown_length']:,} caractères\n")
                f.write(f"- **Fichier de sortie**: [output_full_images.md](./{result['file'].replace('.pptx', '')}/output_full_images.md)\n\n")
                
                # SmartArt details
                if result['smartart_count'] > 0:
                    f.write("#### Détails des SmartArt extraits\n\n")
                    for smartart in result['smartart_blocks']:
                        f.write(f"**{smartart['title']}** - {smartart['format_type']}\n\n")
                        f.write(f"- **Slide**: {smartart['slide']}\n")
                        f.write(f"- **Items de liste**: {smartart['item_count']}\n")
                        f.write(f"- **Images embarquées**: {smartart['image_count']}\n")
                        if smartart['has_images']:
                            f.write("- **Chemins d'images**:\n")
                            for img_path in smartart['image_paths']:
                                f.write(f"  - `{img_path}`\n")
                        f.write(f"- **Longueur contenu**: {smartart['full_length']} caractères\n")
                        f.write("- **Aperçu**:\n\n")
                        f.write("```\n")
                        preview = smartart['content'][:400] + "..." if len(smartart['content']) > 400 else smartart['content']
                        f.write(preview)
                        f.write("\n```\n\n")
                
                f.write("---\n\n")
        
        # Failed conversions
        if failed:
            f.write("## Conversions Échouées ❌\n\n")
            for result in failed:
                f.write(f"### {result['file']}\n\n")
                f.write("- **Status**: FAILED\n")
                f.write(f"- **Erreur**: {result['error']}\n\n")
        
        # Statistics
        f.write("## Statistiques Détaillées\n\n")
        if total_smartart > 0:
            files_with_smartart = [r for r in successful if r['smartart_count'] > 0]
            f.write(f"**SmartArt**:\n")
            f.write(f"- Fichiers avec SmartArt: {len(files_with_smartart)} / {len(successful)}\n")
            if files_with_smartart:
                avg_smartart = total_smartart / len(files_with_smartart)
                f.write(f"- Moyenne SmartArt par fichier: {avg_smartart:.1f}\n")
                type2_percentage = (total_smartart_with_images / total_smartart) * 100
                f.write(f"- Pourcentage Type 2 (avec images): {type2_percentage:.1f}%\n")
            
            f.write(f"\n**Images**:\n")
            f.write(f"- Total images extraites: {total_images}\n")
            if successful:
                avg_images = total_images / len(successful)
                f.write(f"- Moyenne images par fichier: {avg_images:.1f}\n")
        else:
            f.write("Aucun SmartArt détecté dans les fichiers testés.\n")
    
    print(f"✅ Report généré: pptx-result/full-images-{timestamp}/full_images_report.md")
    print(f"📊 Total fichiers : {len(pptx_files)}")
    print(f"✅ Succès : {len(successful)}")
    print(f"❌ Échecs : {len(failed)}")
    print(f"🖼️  Total images : {total_images}")
    print(f"🎯 Total SmartArt : {total_smartart} ({total_smartart_with_images} avec images)")


if __name__ == "__main__":
    run_full_images_tests()
