"""
All-in-One Test Suite - Run both Text-Only and Full Images modes.

This script runs both test modes sequentially and generates a comparative report:
1. Text-Only mode (fast, no images)
2. Full Images mode (complete, with images)
3. Comparative analysis report

Usage:
    python run_all_tests.py
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
import json


def run_script(script_name: str) -> tuple[bool, str]:
    """
    Run a Python test script and capture output.
    
    Args:
        script_name: Name of the Python script to run
    
    Returns:
        Tuple (success, output_text)
    """
    print(f"\n{'='*80}")
    print(f"▶️  Exécution: {script_name}")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print(f"\n✅ {script_name} terminé avec succès")
            return True, result.stdout
        else:
            print(f"\n❌ {script_name} a échoué")
            print(result.stderr)
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"\n⏱️  {script_name} timeout (>5 min)")
        return False, "Timeout"
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution de {script_name}: {e}")
        return False, str(e)


def parse_summary_from_output(output: str) -> dict:
    """
    Extract summary statistics from script output.
    
    Looks for lines like:
    - 📊 Total fichiers : 8
    - ✅ Succès : 8
    - 🎯 Total SmartArt : 59
    - 🖼️  Total images : 42
    
    Args:
        output: Script stdout
    
    Returns:
        Dict with parsed statistics
    """
    stats = {
        'files': 0,
        'success': 0,
        'failed': 0,
        'smartart': 0,
        'images': 0,
        'smartart_with_images': 0
    }
    
    for line in output.split('\n'):
        if 'Total fichiers' in line or 'Total files' in line:
            try:
                stats['files'] = int(line.split(':')[1].strip())
            except:
                pass
        elif 'Succès' in line:
            try:
                stats['success'] = int(line.split(':')[1].strip())
            except:
                pass
        elif 'Échecs' in line:
            try:
                stats['failed'] = int(line.split(':')[1].strip())
            except:
                pass
        elif 'Total SmartArt' in line:
            try:
                # Handle both "59" and "59 (25 avec images)" formats
                value_part = line.split(':')[1].strip()
                smartart_count = int(value_part.split()[0])
                stats['smartart'] = smartart_count
                
                # Extract "(X avec images)" if present
                if '(' in value_part:
                    with_images_str = value_part.split('(')[1].split()[0]
                    stats['smartart_with_images'] = int(with_images_str)
            except:
                pass
        elif 'Total images' in line:
            try:
                stats['images'] = int(line.split(':')[1].strip())
            except:
                pass
    
    return stats


def generate_comparative_report(
    text_only_stats: dict,
    full_images_stats: dict,
    text_only_success: bool,
    full_images_success: bool
):
    """
    Generate a comparative Markdown report.
    
    Args:
        text_only_stats: Statistics from text-only mode
        full_images_stats: Statistics from full images mode
        text_only_success: Whether text-only script succeeded
        full_images_success: Whether full images script succeeded
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    pptx_result_dir = Path("pptx-result")
    pptx_result_dir.mkdir(exist_ok=True)
    
    report_file = pptx_result_dir / f"comparative_report_{timestamp}.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Rapport Comparatif - Tests PPTX\n\n")
        f.write(f"**Date/Heure**: {timestamp}\n\n")
        f.write("**Scripts exécutés**:\n")
        f.write("1. `run_text_only_tests.py` - Mode texte seulement\n")
        f.write("2. `run_full_images_tests.py` - Mode extraction complète\n\n")
        
        f.write("---\n\n")
        
        # Execution Status
        f.write("## Statut d'Exécution\n\n")
        f.write(f"- **Text-Only**: {'✅ SUCCESS' if text_only_success else '❌ FAILED'}\n")
        f.write(f"- **Full Images**: {'✅ SUCCESS' if full_images_success else '❌ FAILED'}\n\n")
        
        if not (text_only_success and full_images_success):
            f.write("⚠️ **Attention**: Un ou plusieurs scripts ont échoué. Les statistiques peuvent être incomplètes.\n\n")
        
        # Comparative Statistics
        f.write("## Statistiques Comparatives\n\n")
        f.write("| Métrique | Text-Only | Full Images | Différence |\n")
        f.write("|----------|-----------|-------------|------------|\n")
        
        files_text = text_only_stats['files']
        files_full = full_images_stats['files']
        f.write(f"| **Fichiers testés** | {files_text} | {files_full} | {files_full - files_text:+d} |\n")
        
        success_text = text_only_stats['success']
        success_full = full_images_stats['success']
        f.write(f"| **Conversions réussies** | {success_text} | {success_full} | {success_full - success_text:+d} |\n")
        
        smartart_text = text_only_stats['smartart']
        smartart_full = full_images_stats['smartart']
        f.write(f"| **SmartArt détectés** | {smartart_text} | {smartart_full} | {smartart_full - smartart_text:+d} |\n")
        
        images_text = text_only_stats['images']
        images_full = full_images_stats['images']
        f.write(f"| **Images extraites** | {images_text} | {images_full} | {images_full - images_text:+d} |\n")
        
        smartart_imgs = full_images_stats['smartart_with_images']
        if smartart_imgs > 0:
            percentage = (smartart_imgs / smartart_full * 100) if smartart_full > 0 else 0
            f.write(f"| **SmartArt avec images (Type 2)** | N/A | {smartart_imgs} ({percentage:.0f}%) | - |\n")
        
        f.write("\n")
        
        # Analysis
        f.write("## Analyse\n\n")
        
        if smartart_text == smartart_full:
            f.write("✅ **Cohérence de détection SmartArt**: Les deux modes détectent le même nombre de SmartArt.\n\n")
        else:
            diff = abs(smartart_text - smartart_full)
            f.write(f"⚠️ **Incohérence de détection**: {diff} SmartArt de différence entre les deux modes.\n\n")
        
        if smartart_imgs > 0:
            type1_count = smartart_full - smartart_imgs
            type1_pct = (type1_count / smartart_full * 100) if smartart_full > 0 else 0
            type2_pct = (smartart_imgs / smartart_full * 100) if smartart_full > 0 else 0
            
            f.write("### Répartition Type 1 vs Type 2\n\n")
            f.write(f"- **Type 1 (Liste texte)**: {type1_count} SmartArt ({type1_pct:.0f}%)\n")
            f.write(f"- **Type 2 (Tableau + images)**: {smartart_imgs} SmartArt ({type2_pct:.0f}%)\n\n")
            
            f.write("**Conclusion**: ")
            if type2_pct > 50:
                f.write("La majorité des SmartArt contiennent des images embarquées.\n")
            elif type2_pct > 25:
                f.write("Une proportion significative des SmartArt contiennent des images.\n")
            else:
                f.write("La plupart des SmartArt sont de type texte seulement.\n")
            f.write("\n")
        
        # Image Extraction
        if images_full > 0:
            f.write("### Extraction d'Images\n\n")
            f.write(f"- **Total images extraites**: {images_full}\n")
            if smartart_full > 0:
                avg_images = images_full / smartart_full
                f.write(f"- **Moyenne images/SmartArt**: {avg_images:.1f}\n")
            f.write("\n")
        
        # Performance Comparison
        f.write("## Comparaison de Performance\n\n")
        f.write("| Mode | Avantages | Limitations |\n")
        f.write("|------|-----------|-------------|\n")
        f.write("| **Text-Only** | Rapide, léger, focus texte | Pas d'images, pas de validation Type 2 |\n")
        f.write("| **Full Images** | Complet, valide Type 2, images physiques | Plus lent, fichiers plus volumineux |\n\n")
        
        # Recommendations
        f.write("## Recommandations\n\n")
        f.write("**Quand utiliser Text-Only** :\n")
        f.write("- Debug rapide de la structure SmartArt\n")
        f.write("- Validation de la détection SmartArt\n")
        f.write("- Tests de performance\n\n")
        
        f.write("**Quand utiliser Full Images** :\n")
        f.write("- Validation complète avec images\n")
        f.write("- Tests de Type 2 (SmartArt → tableaux)\n")
        f.write("- Préparation de release\n\n")
        
        # Links to detailed reports
        f.write("## Rapports Détaillés\n\n")
        f.write("Pour plus de détails, consulter les rapports individuels dans `pptx-result/` :\n\n")
        f.write("- **Text-Only** : `pptx-result/text-only-YYYYMMDD-HHMMSS/text_only_report.md`\n")
        f.write("- **Full Images** : `pptx-result/full-images-YYYYMMDD-HHMMSS/full_images_report.md`\n\n")
        
        # Footer
        f.write("---\n\n")
        f.write("*Rapport généré automatiquement par `run_all_tests.py`*\n")
    
    return report_file


def main():
    """Main execution function."""
    print("=" * 80)
    print("🚀 ALL-IN-ONE TEST SUITE - PPTX SMARTART EXTRACTION")
    print("=" * 80)
    print("\nCe script va exécuter séquentiellement:")
    print("  1. run_text_only_tests.py")
    print("  2. run_full_images_tests.py")
    print("  3. Génération d'un rapport comparatif\n")
    
    # Run text-only tests
    text_only_success, text_only_output = run_script("run_text_only_tests.py")
    text_only_stats = parse_summary_from_output(text_only_output)
    
    # Run full images tests
    full_images_success, full_images_output = run_script("run_full_images_tests.py")
    full_images_stats = parse_summary_from_output(full_images_output)
    
    # Generate comparative report
    print("\n" + "=" * 80)
    print("📊 GÉNÉRATION DU RAPPORT COMPARATIF")
    print("=" * 80 + "\n")
    
    report_file = generate_comparative_report(
        text_only_stats,
        full_images_stats,
        text_only_success,
        full_images_success
    )
    
    print(f"✅ Rapport comparatif généré: {report_file}\n")
    
    # Summary
    print("=" * 80)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 80)
    print(f"\n{'Mode':<20} {'Fichiers':<12} {'Succès':<12} {'SmartArt':<12} {'Images':<12}")
    print("-" * 80)
    print(f"{'Text-Only':<20} {text_only_stats['files']:<12} {text_only_stats['success']:<12} {text_only_stats['smartart']:<12} {text_only_stats['images']:<12}")
    print(f"{'Full Images':<20} {full_images_stats['files']:<12} {full_images_stats['success']:<12} {full_images_stats['smartart']:<12} {full_images_stats['images']:<12}")
    print("-" * 80)
    
    if full_images_stats['smartart_with_images'] > 0:
        print(f"\n🎯 SmartArt avec images (Type 2): {full_images_stats['smartart_with_images']}")
    
    print("\n✅ Tests terminés avec succès!")
    print(f"📄 Rapport comparatif: {report_file}")


if __name__ == "__main__":
    main()
