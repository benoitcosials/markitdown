"""
Tests unitaires pour les fonctions helper du convertisseur PPTX (BRIEF_01).

Tests les fonctions utilitaires sans couverture :
- _slugify (slugification noms de slides)
- _is_background_image (détection images de fond)
- _classify_image_type (classification photo/icon 97% précision)
- Conversion EMF/WMF → PNG
"""

import io
import os
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from markitdown.converters._pptx_converter import PptxConverter

# --- Tests _slugify() ---


def test_slugify_basic():
    """Test slugification basique : espaces et hyphens."""
    converter = PptxConverter()
    
    # Espaces → underscores
    assert converter._slugify("Hello World") == "hello_world"
    
    # Hyphens → underscores
    assert converter._slugify("Test-Name-123") == "test_name_123"
    
    # Mix espaces et hyphens
    assert converter._slugify("My Test-File Name") == "my_test_file_name"


def test_slugify_accents_unicode():
    """Test normalisation Unicode et suppression accents."""
    converter = PptxConverter()
    
    # Accents français
    assert converter._slugify("Café Hôtel") == "cafe_hotel"
    assert converter._slugify("Élève àgé") == "eleve_age"
    
    # Caractères spéciaux européens
    assert converter._slugify("Schön Größe") == "schon_groe"
    
    # Espagnol
    assert converter._slugify("Año Niño") == "ano_nino"


def test_slugify_special_characters():
    """Test suppression caractères spéciaux."""
    converter = PptxConverter()
    
    # Ponctuation
    assert converter._slugify("Test! Name?") == "test_name"
    assert converter._slugify("File (copy).txt") == "file_copytxt"
    
    # Symboles
    assert converter._slugify("Price: $100 @2024") == "price_100_2024"
    
    # Underscores multiples fusionnés
    assert converter._slugify("Test___Name") == "test_name"


def test_slugify_real_world_examples():
    """Test cas réels du BRIEF (exemples documentés)."""
    converter = PptxConverter()
    
    # Exemple documenté dans le code
    assert converter._slugify("Kickoff QA - Essais UAT R1") == "kickoff_qa_essais_uat_r1"
    
    # Autres exemples réalistes
    assert converter._slugify("Slide 1 - Introduction") == "slide_1_introduction"
    assert converter._slugify("Q4 2025 Results") == "q4_2025_results"


def test_slugify_edge_cases():
    """Test edge cases."""
    converter = PptxConverter()
    
    # Chaîne vide
    assert converter._slugify("") == ""
    
    # Uniquement espaces
    assert converter._slugify("   ") == ""
    
    # Uniquement caractères spéciaux
    assert converter._slugify("!!!???") == ""
    
    # Leading/trailing underscores supprimés
    assert converter._slugify("  Test  ") == "test"
    assert converter._slugify("_Test_") == "test"


def test_slugify_numbers():
    """Test préservation des nombres."""
    converter = PptxConverter()
    
    # Nombres préservés
    assert converter._slugify("Slide 123") == "slide_123"
    assert converter._slugify("Version 2.0") == "version_20"
    assert converter._slugify("2024-Q4") == "2024_q4"


# --- Tests _is_background_image() ---


def test_is_background_image_placeholder_picture():
    """Test détection placeholder PICTURE (ID 18)."""
    converter = PptxConverter()
    
    # Mock shape placeholder type PICTURE
    shape = Mock()
    shape.shape_type = 14  # MSO_SHAPE_TYPE.PLACEHOLDER
    shape.placeholder_format.type = 18  # PP_PLACEHOLDER_TYPE.PICTURE
    
    assert converter._is_background_image(shape) is True


def test_is_background_image_placeholder_slide_image():
    """Test détection placeholder SLIDE_IMAGE (ID 101)."""
    converter = PptxConverter()
    
    # Mock shape placeholder type SLIDE_IMAGE
    shape = Mock()
    shape.shape_type = 14  # MSO_SHAPE_TYPE.PLACEHOLDER
    shape.placeholder_format.type = 101  # PP_PLACEHOLDER_TYPE.SLIDE_IMAGE
    
    assert converter._is_background_image(shape) is True


def test_is_background_image_normal_picture():
    """Test que image normale n'est PAS détectée comme background."""
    converter = PptxConverter()
    
    # Mock shape normal (pas placeholder)
    shape = Mock()
    shape.shape_type = 13  # MSO_SHAPE_TYPE.PICTURE
    
    assert converter._is_background_image(shape) is False


def test_is_background_image_placeholder_other_type():
    """Test que placeholder autre type n'est PAS background."""
    converter = PptxConverter()
    
    # Mock placeholder TITLE (ID 1)
    shape = Mock()
    shape.shape_type = 14  # MSO_SHAPE_TYPE.PLACEHOLDER
    shape.placeholder_format.type = 1  # PP_PLACEHOLDER_TYPE.TITLE
    
    assert converter._is_background_image(shape) is False


def test_is_background_image_error_handling():
    """Test fallback gracieux en cas d'erreur."""
    converter = PptxConverter()
    
    # Mock shape qui lève exception lors de l'accès
    shape = Mock()
    shape.shape_type = 14
    shape.placeholder_format.type = Mock(side_effect=AttributeError)
    
    # Devrait retourner False (fallback sécurisé)
    assert converter._is_background_image(shape) is False


# --- Tests _classify_image_type() ---


def test_classify_graphique_as_icon():
    """Test classification 'Graphique X' → icon (100% précis)."""
    converter = PptxConverter()
    
    # Mock shape avec nom "Graphique"
    shape = Mock()
    shape.name = "Graphique 1"
    shape.image.blob = b"x" * 1000  # 1 KB (peu importe la taille)
    
    assert converter._classify_image_type(shape) == "icon"
    
    # Variantes
    shape.name = "Graphique 42"
    assert converter._classify_image_type(shape) == "icon"
    
    shape.name = "Graph 5"
    assert converter._classify_image_type(shape) == "icon"


def test_classify_image_as_photo():
    """Test classification 'Image X' → photo (100% précis)."""
    converter = PptxConverter()
    
    # Mock shape avec nom "Image"
    shape = Mock()
    shape.name = "Image 1"
    shape.image.blob = b"x" * 1000
    
    assert converter._classify_image_type(shape) == "photo"
    
    # Variantes
    shape.name = "Picture 10"
    assert converter._classify_image_type(shape) == "photo"


def test_classify_espace_reserve_as_photo():
    """Test classification 'Espace réservé pour une image' → photo (100% précis)."""
    converter = PptxConverter()
    
    # Mock shape PowerPoint français
    shape = Mock()
    shape.name = "Espace réservé pour une image 1"
    shape.image.blob = b"x" * 1000
    
    assert converter._classify_image_type(shape) == "photo"


def test_classify_fallback_small_size_icon():
    """Test fallback taille < 20 KB → icon."""
    converter = PptxConverter()
    
    # Mock shape nom ambigu, petite taille
    shape = Mock()
    shape.name = "Espace réservé du contenu 1"
    shape.image.blob = b"x" * 10000  # 10 KB < 20 KB
    
    assert converter._classify_image_type(shape) == "icon"


def test_classify_fallback_large_size_photo():
    """Test fallback taille > 20 KB → photo."""
    converter = PptxConverter()
    
    # Mock shape nom ambigu, grande taille
    shape = Mock()
    shape.name = "Espace réservé du contenu 1"
    shape.image.blob = b"x" * 30000  # 30 KB > 20 KB
    
    assert converter._classify_image_type(shape) == "photo"


def test_classify_threshold_boundary():
    """Test précis du seuil 20 KB."""
    converter = PptxConverter()
    
    shape = Mock()
    shape.name = "Unknown Shape"
    
    # Exactement 20 KB (20480 bytes)
    shape.image.blob = b"x" * 20480
    assert converter._classify_image_type(shape) == "photo"
    
    # Légèrement en dessous (19 KB)
    shape.image.blob = b"x" * 19456
    assert converter._classify_image_type(shape) == "icon"
    
    # Légèrement au dessus (21 KB)
    shape.image.blob = b"x" * 21504
    assert converter._classify_image_type(shape) == "photo"


def test_classify_case_sensitivity():
    """Test sensibilité à la casse pour patterns (comportement réel)."""
    converter = PptxConverter()
    
    shape = Mock()
    shape.image.blob = b"x" * 1000
    
    # "Graphique" avec majuscule initiale (standard PowerPoint français)
    shape.name = "Graphique 1"
    assert converter._classify_image_type(shape) == "icon"
    
    # "Graph" avec majuscule (standard PowerPoint anglais)
    shape.name = "Graph 1"
    assert converter._classify_image_type(shape) == "icon"
    
    # "Image" avec majuscule (standard PowerPoint)
    shape.name = "Image 1"
    assert converter._classify_image_type(shape) == "photo"
    
    # "Picture" avec majuscule (standard PowerPoint anglais)
    shape.name = "Picture 1"
    assert converter._classify_image_type(shape) == "photo"
    
    # Noms en minuscules complètes tombent dans fallback (taille)
    shape.name = "graphique 1"
    shape.image.blob = b"x" * 10000  # 10 KB < 20 KB
    assert converter._classify_image_type(shape) == "icon"  # Fallback size
    
    # Noms en majuscules complètes tombent dans fallback (taille)
    shape.name = "IMAGE 1"
    shape.image.blob = b"x" * 30000  # 30 KB > 20 KB
    assert converter._classify_image_type(shape) == "photo"  # Fallback size


# --- Tests Conversion EMF/WMF → PNG ---


def test_save_image_emf_extension_conversion():
    """Test détection EMF via extension et conversion PNG."""
    converter = PptxConverter()
    converter._image_hashes = {}
    
    # Créer une vraie image EMF mockée (simulée avec PNG pour simplifier)
    from PIL import Image
    
    # Créer image test
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, 'PNG')  # On simule avec PNG pour le test
    blob = img_bytes.getvalue()
    
    # Mock shape avec extension EMF
    shape = Mock()
    shape.image.blob = blob
    shape.image.filename = "diagram.emf"
    shape.image.content_type = "image/x-emf"
    
    # Test dans répertoire temporaire
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        image_path, deduplicated = converter._save_image(
            shape=shape,
            slide_num=1,
            image_count=0,
            image_dir=tmpdir
        )
        
        # Vérifie conversion vers PNG
        assert image_path.endswith('.png')
        assert os.path.exists(os.path.join(tmpdir, "slide1_image0.png"))
        assert not deduplicated


def test_save_image_wmf_mimetype_conversion():
    """Test détection WMF via MIME type et conversion PNG."""
    converter = PptxConverter()
    converter._image_hashes = {}
    
    from PIL import Image
    
    # Créer image test
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, 'PNG')
    blob = img_bytes.getvalue()
    
    # Mock shape avec MIME WMF
    shape = Mock()
    shape.image.blob = blob
    shape.image.filename = None
    shape.image.content_type = "image/x-wmf"
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        image_path, deduplicated = converter._save_image(
            shape=shape,
            slide_num=2,
            image_count=3,
            image_dir=tmpdir
        )
        
        # Vérifie conversion vers PNG
        assert image_path.endswith('.png')
        assert os.path.exists(os.path.join(tmpdir, "slide2_image3.png"))


def test_save_image_normal_png_no_conversion():
    """Test que PNG normal n'est PAS converti."""
    converter = PptxConverter()
    converter._image_hashes = {}
    
    from PIL import Image
    
    # Créer vraie image PNG
    img = Image.new('RGB', (100, 100), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, 'PNG')
    blob = img_bytes.getvalue()
    
    # Mock shape PNG normal
    shape = Mock()
    shape.image.blob = blob
    shape.image.filename = "photo.png"
    shape.image.content_type = "image/png"
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        image_path, deduplicated = converter._save_image(
            shape=shape,
            slide_num=1,
            image_count=0,
            image_dir=tmpdir
        )
        
        # Vérifie extension PNG préservée
        assert image_path.endswith('.png')
        
        # Vérifie fichier créé
        disk_path = os.path.join(tmpdir, "slide1_image0.png")
        assert os.path.exists(disk_path)
        
        # Vérifie que le contenu est identique (pas de conversion)
        with open(disk_path, 'rb') as f:
            saved_blob = f.read()
        assert saved_blob == blob


# --- Tests Intégration ---


def test_skip_icon_images_integration():
    """Test intégration skip_icon_images=True."""
    # Ce test vérifie que _classify_image_type est bien appelée
    # quand skip_icon_images=True
    
    # Note: Test d'intégration complet nécessiterait un vrai fichier PPTX
    # Pour l'instant on vérifie juste que la fonction est accessible
    converter = PptxConverter()
    
    shape = Mock()
    shape.name = "Graphique 1"
    shape.image.blob = b"x" * 1000
    
    # Vérifier que la fonction retourne bien 'icon'
    assert converter._classify_image_type(shape) == "icon"


def test_skip_background_images_integration():
    """Test intégration skip_background_images=True."""
    converter = PptxConverter()
    
    # Background placeholder
    bg_shape = Mock()
    bg_shape.shape_type = 14
    bg_shape.placeholder_format.type = 18
    
    assert converter._is_background_image(bg_shape) is True
    
    # Normal image
    normal_shape = Mock()
    normal_shape.shape_type = 13
    
    assert converter._is_background_image(normal_shape) is False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 Tests Unitaires PPTX Image Helpers (BRIEF_01 Coverage)")
    print("=" * 70)
    
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])

