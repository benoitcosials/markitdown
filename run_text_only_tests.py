"""
Text-Only PPTX Test Suite - Focus on SmartArt extraction without images.

This script converts PPTX files to Markdown in TEXT-ONLY mode:
- NO physical image extraction (output_images=False)
- Focus on text content and SmartArt conversion
- Useful for validating SmartArt text extraction

Key difference from run_comprehensive_tests.py:
- Comprehensive: Extracts images physically with output_images=True
- Text-Only: Pure text conversion, no image files created
"""

import os
import re
from datetime import datetime
from pathlib import Path

from markitdown import MarkItDown


def extract_smartart_blocks(markdown_text: str) -> list[dict]:
    """
    Extract SmartArt blocks from Markdown content.
    
    Searches for patterns like:
    - ### SmartArt N (Slide X)
    - Numbered/bulleted lists following SmartArt headers
    
    Args:
        markdown_text: Markdown content to analyze
    
    Returns:
        List of dicts with SmartArt info (title, content, item_count)
    """
    smartart_blocks = []
    
    # Pattern: ### SmartArt N (Slide X)
    pattern = r'### SmartArt (\d+) \(Slide (\d+)\)'
    
    matches = list(re.finditer(pattern, markdown_text))
    
    for i, match in enumerate(matches):
        smartart_num = int(match.group(1))
        start_pos = match.end()
        
        # Determine end position (next SmartArt or end of text)
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(markdown_text)
        
        # Extract content between current and next SmartArt
        content = markdown_text[start_pos:end_pos].strip()
        
        # Count list items (lines starting with - or 1. 2. etc)
        list_items = re.findall(r'^\s*[-*]|\d+\.', content, re.MULTILINE)
        item_count = len(list_items)
        
        slide_num = int(match.group(2))
        
        smartart_blocks.append({
            'number': smartart_num,
            'slide': slide_num,
            'title': match.group(0),
            'content': content[:500],  # First 500 chars for preview
            'item_count': item_count,
            'full_length': len(content)
        })
    
    return smartart_blocks


def process_single_pptx_text_only(pptx_file_path, output_parent_dir=None):
    """
    Convert single PPTX to Markdown TEXT-ONLY (no images).
    
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
            "error": f"File not found: {pptx_file_path}"
        }
    
    pptx_stem = pptx_path.stem
    
    # Determine output directory
    if output_parent_dir is None:
        output_dir = pptx_path.parent / f"{pptx_stem}_text_only"
    else:
        output_dir = Path(output_parent_dir) / pptx_stem
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Convert - TEXT ONLY MODE
        md = MarkItDown()
        result = md.convert(
            source=pptx_path,
            output_images=False  # KEY: No physical image extraction
        )
        
        # Write markdown output
        output_md = output_dir / "output_text_only.md"
        output_md.write_text(result.markdown, encoding="utf-8")
        
        # Analyze SmartArt in the output
        smartart_blocks = extract_smartart_blocks(result.markdown)
        
        return {
            "file": pptx_path.name,
            "status": "SUCCESS",
            "smartart_count": len(smartart_blocks),
            "smartart_blocks": smartart_blocks,
            "markdown_length": len(result.markdown),
            "error": None
        }
        
    except Exception as e:
        return {
            "file": pptx_path.name,
            "status": "FAILED",
            "smartart_count": 0,
            "error": str(e)
        }


def run_text_only_tests():
    """Run TEXT-ONLY extraction tests on all PPTX files."""
    
    # Prepare directories
    test_pptx_dir = Path("pptx-test")
    pptx_result_dir = Path("pptx-result")
    pptx_result_dir.mkdir(exist_ok=True)
    
    # Create timestamped result folder
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    test_session_dir = pptx_result_dir / f"text-only-{timestamp}"
    test_session_dir.mkdir(parents=True, exist_ok=True)
    
    # List all PPTX files
    pptx_files = sorted(test_pptx_dir.glob("*.pptx"))
    pptx_files = [f for f in pptx_files if not f.name.startswith('~$')]
    
    if not pptx_files:
        print(f"Aucun fichier .pptx trouvé dans {test_pptx_dir}")
        print(f"Dossier de résultats créé: {test_session_dir}")
        return
    
    print("=" * 80)
    print("TEST TEXT-ONLY MODE - FOCUS SMARTART EXTRACTION")
    print(f"Timestamp: {timestamp}")
    print(f"Mode: output_images=False (texte seulement)")
    print("=" * 80 + "\n")
    
    results = []
    
    for idx, pptx_file in enumerate(pptx_files, 1):
        print(f"[{idx}/{len(pptx_files)}] Traitement: {pptx_file.name}")
        
        result = process_single_pptx_text_only(
            pptx_file_path=pptx_file,
            output_parent_dir=test_session_dir
        )
        
        results.append(result)
        
        if result["status"] == "SUCCESS":
            smartart_info = f"{result['smartart_count']} SmartArt trouvés" if result['smartart_count'] else "Aucun SmartArt"
            print(f"  ✅ SUCCESS: {smartart_info}")
        else:
            print(f"  ❌ FAILED: {result['error']}")
    
    # Generate report
    print("\n" + "=" * 80)
    print("RAPPORT DE TEST TEXT-ONLY")
    print("=" * 80 + "\n")
    
    successful = [r for r in results if r["status"] == "SUCCESS"]
    failed = [r for r in results if r["status"] == "FAILED"]
    total_smartart = sum(r["smartart_count"] for r in results)
    
    report_file = test_session_dir / "text_only_report.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        # Header
        f.write("# Rapport Test TEXT-ONLY Mode - SmartArt Focus\n\n")
        f.write(f"**Date/Heure**: {timestamp}\n\n")
        f.write(f"**Dossier de résultats**: `pptx-result/text-only-{timestamp}/`\n\n")
        f.write(f"**Mode de conversion**: `output_images=False` (texte seulement)\n\n")
        
        # Summary
        f.write("## Résumé\n\n")
        f.write(f"- **Total fichiers**: {len(pptx_files)}\n")
        f.write(f"- **Réussis**: {len(successful)} ✅\n")
        f.write(f"- **Échoués**: {len(failed)} ❌\n")
        f.write(f"- **Total SmartArt extraits**: {total_smartart}\n\n")
        
        # Success rate
        success_rate = (len(successful) / len(pptx_files)) * 100 if pptx_files else 0
        f.write(f"**Taux de réussite**: {success_rate:.1f}%\n\n")
        
        # Mode explanation
        f.write("## À propos du Mode Text-Only\n\n")
        f.write("**Objectif**: Valider l'extraction de texte pur, notamment des SmartArt, sans générer de fichiers image.\n\n")
        f.write("**Avantages**:\n")
        f.write("- ✅ Rapide (pas d'extraction d'images)\n")
        f.write("- ✅ Focus sur le contenu textuel\n")
        f.write("- ✅ Idéal pour tester la conversion SmartArt → Markdown\n")
        f.write("- ✅ Aperçu de la structure sans fichiers image\n\n")
        
        f.write("**Limitations**:\n")
        f.write("- ❌ Aucune image physique extraite\n")
        f.write("- ❌ Pas de validation des images embarquées dans SmartArt\n\n")
        
        # Successful conversions with SmartArt details
        if successful:
            f.write("## Conversions Réussies ✅\n\n")
            for result in successful:
                f.write(f"### {result['file']}\n\n")
                f.write("- **Status**: SUCCESS\n")
                f.write(f"- **SmartArt trouvés**: {result['smartart_count']}\n")
                f.write(f"- **Longueur Markdown**: {result['markdown_length']:,} caractères\n")
                f.write(f"- **Fichier de sortie**: [output_text_only.md](./{result['file'].replace('.pptx', '')}/output_text_only.md)\n\n")
                
                # SmartArt details
                if result['smartart_count'] > 0:
                    f.write("#### Détails des SmartArt extraits\n\n")
                    for smartart in result['smartart_blocks']:
                        f.write(f"**{smartart['title']}**\n\n")
                        f.write(f"- **Slide**: {smartart['slide']}\n")
                        f.write(f"- **Items de liste**: {smartart['item_count']}\n")
                        f.write(f"- **Longueur contenu**: {smartart['full_length']} caractères\n")
                        f.write("- **Aperçu**:\n\n")
                        f.write("```\n")
                        preview = smartart['content'][:300] + "..." if len(smartart['content']) > 300 else smartart['content']
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
        f.write("## Statistiques SmartArt\n\n")
        if total_smartart > 0:
            files_with_smartart = [r for r in successful if r['smartart_count'] > 0]
            f.write(f"- **Fichiers avec SmartArt**: {len(files_with_smartart)} / {len(successful)}\n")
            if files_with_smartart:
                avg_smartart = total_smartart / len(files_with_smartart)
                f.write(f"- **Moyenne SmartArt par fichier** (avec SmartArt): {avg_smartart:.1f}\n")
                max_smartart = max(r['smartart_count'] for r in files_with_smartart)
                f.write(f"- **Maximum SmartArt** (un fichier): {max_smartart}\n")
        else:
            f.write("Aucun SmartArt détecté dans les fichiers testés.\n")
    
    print(f"✅ Report généré: pptx-result/text-only-{timestamp}/text_only_report.md")
    print(f"📊 Total fichiers : {len(pptx_files)}")
    print(f"✅ Succès : {len(successful)}")
    print(f"❌ Échecs : {len(failed)}")
    print(f"🎯 Total SmartArt : {total_smartart}")


if __name__ == "__main__":
    run_text_only_tests()
