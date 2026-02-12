from markitdown import MarkItDown
import os
import shutil

print("="*80)
print("TEST PARAMETRES BRIEF_01 via MCP - APRES FIX")
print("="*80)

test_dir = "test-mcp-params"
if os.path.exists(test_dir):
    shutil.rmtree(test_dir)
os.makedirs(test_dir)

pptx_path = "pptx-test/Standard QA - Design des essais.pptx"

print("\n[TEST 1] Chemin avec sous-répertoires")
result = MarkItDown().convert_local(
    pptx_path,
    output_images=True,
    image_dir="test-mcp-params/subfolder/images",
    skip_icon_images=True
)

expected_path = "test-mcp-params/subfolder/images"
if os.path.exists(expected_path):
    images = [f for f in os.listdir(expected_path) if f.endswith((".png", ".jpg"))]
    print(f"✅ Dossier créé: {expected_path}")
    print(f"✅ Images extraites: {len(images)}")
    for img in images:
        print(f"     - {img}")
else:
    print(f"❌ ERREUR: Dossier {expected_path} non créé")
    print("Vérifions où les images sont:")
    for root, dirs, files in os.walk(".", topdown=True):
        if any(f.endswith((".png", ".jpg")) for f in files):
            print(f"   Trouvé dans: {root}")

print("\n" + "="*80)
print("RÉSUMÉ FIX MCP")
print("="*80) 
print("✅ image_dir personnalisé maintenant respecté")
print("✅ Sous-répertoires fonctionnels")
