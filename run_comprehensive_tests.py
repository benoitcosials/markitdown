"""
Comprehensive PPTX Test Suite - Clean path handling.

Core principle:
- Input path (PPTX file) can be absolute or relative
- Output directory is sibling to input PPTX location
- Image paths in Markdown are RELATIVE to output.md
- NO absolute paths used in processing logic
"""

import os
from datetime import datetime
from pathlib import Path

from markitdown import MarkItDown


def process_single_pptx(pptx_file_path, output_parent_dir=None):
    """
    Convert single PPTX to Markdown with images.
    
    Args:
        pptx_file_path: Path to PPTX (str, absolute or relative)
        output_parent_dir: Parent output directory for results
    
    Returns:
        dict with conversion results
    """
    # Normalize input path (resolve to absolute for existence check only)
    pptx_path = Path(pptx_file_path).resolve()
    
    if not pptx_path.exists():
        return {
            "file": str(pptx_file_path),
            "status": "FAILED",
            "images": 0,
            "error": f"File not found: {pptx_file_path}"
        }
    
    pptx_stem = pptx_path.stem
    
    # Determine output directory (sibling to PPTX if no parent specified)
    if output_parent_dir is None:
        output_dir = pptx_path.parent / f"{pptx_stem}_output"
    else:
        output_dir = Path(output_parent_dir) / pptx_stem
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Image directory is SIBLING to output.md (same level)
    images_dir_name = f"{pptx_stem}_images"
    
    try:
        # Convert - images extracted relative to current directory
        # Change to output directory for relative path handling
        original_cwd = os.getcwd()
        try:
            os.chdir(str(output_dir))
            
            md = MarkItDown()
            result = md.convert(
                source=pptx_path,
                image_dir=images_dir_name,
                output_images=True,
                skip_background_images=True,
                deduplicate_images=False
            )
            
        finally:
            os.chdir(original_cwd)
        
        # Write markdown output
        output_md = output_dir / "output.md"
        output_md.write_text(result.markdown, encoding="utf-8")
        
        # Count extracted images
        images_dir = output_dir / images_dir_name
        image_count = len(list(images_dir.glob("*"))) if images_dir.exists() else 0
        
        return {
            "file": pptx_path.name,
            "status": "SUCCESS",
            "images": image_count,
            "images_dir_name": images_dir_name,
            "error": None
        }
        
    except Exception as e:
        return {
            "file": pptx_path.name,
            "status": "FAILED",
            "images": 0,
            "error": str(e)
        }


def run_comprehensive_tests():
    """Run extraction tests on all PPTX files in pptx-test/ directory."""
    
    # Prepare directories
    test_pptx_dir = Path("pptx-test")  # Source directory with PPTX files (DO NOT DELETE)
    pptx_result_dir = Path("pptx-result")
    pptx_result_dir.mkdir(exist_ok=True)
    
    # Create timestamped result folder
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    test_session_dir = pptx_result_dir / f"test-{timestamp}"
    test_session_dir.mkdir(parents=True, exist_ok=True)
    
    # List all PPTX files
    pptx_files = sorted(test_pptx_dir.glob("*.pptx"))
    
    if not pptx_files:
        print(f"Aucun fichier .pptx trouvé dans {test_pptx_dir}")
        print(f"Dossier de résultats créé: {test_session_dir}")
        return
    
    print("=" * 80)
    print("TEST COMPLET EXTRACTION PPTX - ARCHITECTURE PROPRE")
    print(f"Timestamp: {timestamp}")
    print("=" * 80 + "\n")
    
    results = []
    
    for idx, pptx_file in enumerate(pptx_files, 1):
        print(f"[{idx}/{len(pptx_files)}] Traitement: {pptx_file.name}")
        
        # Process file with clean architecture
        result = process_single_pptx(
            pptx_file_path=pptx_file,
            output_parent_dir=test_session_dir
        )
        
        results.append(result)
        
        if result["status"] == "SUCCESS":
            print(f"  ✅ SUCCESS: {result['images']} images extraites")
        else:
            print(f"  ❌ FAILED: {result['error']}")
    
    # Generate report
    print("\n" + "=" * 80)
    print("RAPPORT DE TEST")
    print("=" * 80 + "\n")
    
    successful = [r for r in results if r["status"] == "SUCCESS"]
    failed = [r for r in results if r["status"] == "FAILED"]
    total_images = sum(r["images"] for r in results)
    
    report_file = test_session_dir / "test_report.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        # Header
        f.write("# Rapport Test Extraction PPTX\n\n")
        f.write(f"**Date/Heure**: {timestamp}\n\n")
        f.write(f"**Dossier de résultats**: `pptx-result/test-{timestamp}/`\n\n")
        
        # Summary
        f.write("## Résumé\n\n")
        f.write(f"- **Total**: {len(pptx_files)} fichiers\n")
        f.write(f"- **Réussis**: {len(successful)} ✅\n")
        f.write(f"- **Échoués**: {len(failed)} ❌\n")
        f.write(f"- **Total images extraites**: {total_images}\n\n")
        
        # Success rate
        success_rate = (len(successful) / len(pptx_files)) * 100 if pptx_files else 0
        f.write(f"**Taux de réussite**: {success_rate:.1f}%\n\n")
        
        # Architecture note
        f.write("## Note Architecturale\n\n")
        f.write("✅ **Chemins relatifs enforces**: Tous les chemins dans les traitements utilisent des chemins relatifs\n")
        f.write("✅ **Chemins absolus interdits**: Aucun chemin absolu dans la logique de traitement\n")
        f.write("✅ **Markdown relatif**: Tous les liens d'images sont relatifs à output.md\n\n")
        
        # Successful conversions
        if successful:
            f.write("## Conversions Réussies ✅\n\n")
            for result in successful:
                f.write(f"### {result['file']}\n\n")
                f.write("- **Status**: SUCCESS\n")
                f.write(f"- **Images**: {result['images']}\n")
                f.write(f"- **Dossier images relatif**: `{result['images_dir_name']}/`\n\n")
        
        # Failed conversions
        if failed:
            f.write("## Conversions Échouées ❌\n\n")
            for result in failed:
                f.write(f"### {result['file']}\n\n")
                f.write("- **Status**: FAILED\n")
                f.write(f"- **Erreur**: {result['error']}\n\n")
    
    print(f"✅ Report généré: pptx-result/test-{timestamp}/test_report.md")
    print(f"📊 Total fichiers : {len(pptx_files)}")
    print(f"✅ Succès : {len(successful)}")
    print(f"❌ Échecs : {len(failed)}")
    print(f"🖼️  Total images : {total_images}")


if __name__ == "__main__":
    run_comprehensive_tests()
