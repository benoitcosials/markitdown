"""
Comprehensive PPTX Test Suite with organized result storage.

Results structure:
  pptx-result/
    └── test-<YYYYMMDD-HHMMSS>/
        ├── <pptx_name>/
        │   ├── output.md
        │   └── <pptx_name>_images/
        │       ├── slide1_image0.jpg
        │       └── ...
        └── test_report.md
"""

from markitdown import MarkItDown
import os
import shutil
from datetime import datetime
from pathlib import Path


def run_comprehensive_tests():
    """Run extraction tests on all PPTX files in test_pptx/ directory."""
    
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
    print(f"TEST COMPLET EXTRACTION PPTX")
    print(f"Timestamp: {timestamp}")
    print(f"Repertoire: {test_session_dir}")
    print("=" * 80 + "\n")
    
    md = MarkItDown()
    results = []
    
    for idx, pptx_file in enumerate(pptx_files, 1):
        pptx_name = pptx_file.stem
        print(f"[{idx}/{len(pptx_files)}] {pptx_file.name}")
        
        pptx_output_dir = test_session_dir / pptx_name
        pptx_output_dir.mkdir(exist_ok=True)
        
        image_dir = pptx_output_dir / f"{pptx_name}_images"
        
        try:
            result = md.convert(
                str(pptx_file),
                image_dir=str(image_dir),
                output_images=True,
                skip_background_images=True,
                deduplicate_images=False
            )
            
            output_md_file = pptx_output_dir / "output.md"
            with open(output_md_file, "w", encoding="utf-8") as f:
                f.write(result.markdown)
            
            image_count = len(list(image_dir.glob("*"))) if image_dir.exists() else 0
            
            results.append({
                "file": pptx_file.name,
                "status": "SUCCESS",
                "images": image_count,
                "output": str(output_md_file),
                "error": None
            })
            
            print(f"  SUCCESS: {image_count} images")
            
        except Exception as e:
            results.append({
                "file": pptx_file.name,
                "status": "FAILED",
                "images": 0,
                "output": None,
                "error": str(e)
            })
            
            print(f"  FAILED: {str(e)}")
    
    # Generate report
    print("\n" + "=" * 80)
    print("RAPPORT DE TEST")
    print("=" * 80 + "\n")
    
    report_file = test_session_dir / "test_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# Rapport Test PPTX\n\n")
        f.write(f"Date: {datetime.now().strftime(('%Y-%m-%d %H:%M:%S'))}\n")
        f.write(f"Repertoire: `{test_session_dir}`\n\n")
        
        total = len(results)
        success = sum(1 for r in results if r["status"] == "SUCCESS")
        failed = sum(1 for r in results if r["status"] == "FAILED")
        total_images = sum(r["images"] for r in results)
        
        f.write("## Resume\n\n")
        f.write(f"- Total PPTX: {total}\n")
        f.write(f"- Succes: {success}\n")
        f.write(f"- Echecs: {failed}\n")
        f.write(f"- Total images: {total_images}\n\n")
        
        f.write("## Details\n\n")
        for result in results:
            f.write(f"### {result['file']}\n\n")
            
            if result["status"] == "SUCCESS":
                f.write(f"- Status: Success\n")
                f.write(f"- Images: {result['images']}\n")
                f.write(f"- Markdown: {result['output']}\n")
            else:
                f.write(f"- Status: Failed\n")
                f.write(f"- Erreur: {result['error']}\n")
            
            f.write("\n")
    
    print(f"Rapport: {report_file}")
    print(f"Resultats: {test_session_dir}")
    print("=" * 80)


if __name__ == "__main__":
    run_comprehensive_tests()
