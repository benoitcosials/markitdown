"""
Tests unitaires pour vision_enhancement helpers (Sprint 2.7).

Tests les fonctions utilitaires sans nécessiter serveur MCP actif :
- parse_markdown_images
- detect_image_mime_type  
- read_image_file
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from markitdown_mcp.vision_enhancement import (
    detect_image_mime_type,
    parse_markdown_images,
    read_image_file,
)


def test_parse_markdown_images():
    """Test extraction d'images depuis markdown."""
    print("\n🧪 Test: parse_markdown_images")
    
    # Test 1: Images avec alt text
    md1 = "![Photo de chat](cat.png) et ![Logo](logo.jpg)"
    result1 = parse_markdown_images(md1)
    assert result1 == [('Photo de chat', 'cat.png'), ('Logo', 'logo.jpg')], f"Échec Test 1: {result1}"
    print("  ✅ Test 1: Images avec alt text")
    
    # Test 2: Images sans alt text
    md2 = "![](image1.png) texte ![](image2.jpg)"
    result2 = parse_markdown_images(md2)
    assert result2 == [('', 'image1.png'), ('', 'image2.jpg')], f"Échec Test 2: {result2}"
    print("  ✅ Test 2: Images sans alt text")
    
    # Test 3: Mix alt text / sans alt text
    md3 = "![Alt présent](img1.png) ![](img2.png) ![Autre](img3.jpg)"
    result3 = parse_markdown_images(md3)
    assert result3 == [('Alt présent', 'img1.png'), ('', 'img2.png'), ('Autre', 'img3.jpg')], f"Échec Test 3: {result3}"
    print("  ✅ Test 3: Mix alt text présents et vides")
    
    # Test 4: Aucune image
    md4 = "Texte sans images"
    result4 = parse_markdown_images(md4)
    assert result4 == [], f"Échec Test 4: {result4}"
    print("  ✅ Test 4: Markdown sans images")
    
    # Test 5: Chemins avec espaces et caractères spéciaux
    md5 = "![Alt](images/slide 1_image0.png)"
    result5 = parse_markdown_images(md5)
    assert result5 == [('Alt', 'images/slide 1_image0.png')], f"Échec Test 5: {result5}"
    print("  ✅ Test 5: Chemins avec espaces")
    
    print("✅ Tous les tests parse_markdown_images PASSÉS\n")


def test_detect_image_mime_type():
    """Test détection MIME type depuis bytes."""
    print("🧪 Test: detect_image_mime_type")
    
    # Test 1: PNG
    png_header = b'\x89PNG\r\n\x1a\n'
    mime1 = detect_image_mime_type(png_header)
    assert mime1 == 'image/png', f"Échec PNG: {mime1}"
    print("  ✅ Test 1: PNG header → image/png")
    
    # Test 2: JPEG (JFIF)
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF'
    mime2 = detect_image_mime_type(jpeg_header)
    assert mime2 == 'image/jpeg', f"Échec JPEG: {mime2}"
    print("  ✅ Test 2: JPEG header → image/jpeg")
    
    # Test 3: GIF
    gif_header = b'GIF89a'
    mime3 = detect_image_mime_type(gif_header)
    assert mime3 == 'image/gif', f"Échec GIF: {mime3}"
    print("  ✅ Test 3: GIF header → image/gif")
    
    # Test 4: Format inconnu (fallback png)
    unknown = b'\x00\x00\x00\x00unknown'
    mime4 = detect_image_mime_type(unknown)
    assert mime4 == 'image/png', f"Échec fallback: {mime4}"
    print("  ✅ Test 4: Format inconnu → image/png (fallback)")
    
    print("✅ Tous les tests detect_image_mime_type PASSÉS\n")


def test_read_image_file():
    """Test lecture fichiers image."""
    print("🧪 Test: read_image_file")
    
    # Test 1: Fichier inexistant
    result1 = read_image_file("inexistant.png")
    assert result1 is None, f"Échec fichier inexistant: {result1}"
    print("  ✅ Test 1: Fichier inexistant → None")
    
    # Test 2: Chemin vide
    result2 = read_image_file("")
    assert result2 is None, f"Échec chemin vide: {result2}"
    print("  ✅ Test 2: Chemin vide → None")
    
    # Test 3: Fichier réel (si disponible)
    test_image_path = Path("../../../pptx-result/test-20260221-100623/images/slide16_image0.png")
    if test_image_path.exists():
        result3 = read_image_file(str(test_image_path))
        assert result3 is not None, "Échec lecture fichier existant"
        assert isinstance(result3, bytes), f"Type incorrect: {type(result3)}"
        assert len(result3) > 0, "Fichier vide"
        print(f"  ✅ Test 3: Fichier réel → {len(result3)} bytes")
    else:
        print("  ⚠️  Test 3: Fichier test non disponible (skip)")
    
    print("✅ Tous les tests read_image_file PASSÉS\n")


def test_integration_workflow():
    """Test workflow complet de parsing + détection MIME."""
    print("🧪 Test: Workflow d'intégration")
    
    markdown = """
# Slide 1

Voici une image sans alt text :

![](images/slide1_image0.png)

Et une image avec alt text :

![Diagramme de flux](images/slide2_chart0.png)

## Slide 2

Autre image vide :

![](images/slide3_photo1.jpg)
"""
    
    # Étape 1: Parser images
    images = parse_markdown_images(markdown)
    assert len(images) == 3, f"Devrait trouver 3 images, trouvé {len(images)}"
    print(f"  ✅ Étape 1: {len(images)} images trouvées")
    
    # Étape 2: Identifier images sans alt text
    images_without_alt = [(alt, path) for alt, path in images if not alt.strip()]
    assert len(images_without_alt) == 2, f"Devrait avoir 2 images sans alt, trouvé {len(images_without_alt)}"
    print(f"  ✅ Étape 2: {len(images_without_alt)} images sans alt text")
    
    # Étape 3: Identifier images avec alt text
    images_with_alt = [(alt, path) for alt, path in images if alt.strip()]
    assert len(images_with_alt) == 1, f"Devrait avoir 1 image avec alt, trouvé {len(images_with_alt)}"
    assert images_with_alt[0][0] == "Diagramme de flux", f"Alt text incorrect: {images_with_alt[0][0]}"
    print(f"  ✅ Étape 3: {len(images_with_alt)} image avec alt text préservé")
    
    print("✅ Workflow d'intégration VALIDÉ\n")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 Tests Unitaires Vision Enhancement Helpers (Sprint 2.7)")
    print("=" * 70)
    
    try:
        test_parse_markdown_images()
        test_detect_image_mime_type()
        test_read_image_file()
        test_integration_workflow()
        
        print("=" * 70)
        print("✅ TOUS LES TESTS PASSÉS - Helpers fonctionnels")
        print("=" * 70)
        print("\n📌 Prochaine étape : Tester avec serveur MCP actif (voir sprint-2.7-mcp-vision-test-guide.md)")
        
    except AssertionError as e:
        print(f"\n❌ ÉCHEC DE TEST : {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
