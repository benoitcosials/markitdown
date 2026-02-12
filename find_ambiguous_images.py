import pptx
from pathlib import Path

# Fichiers PPTX de test
test_dir = Path('pptx-result/test-20260211-182310')

print('=' * 80)
print('IMAGES AVEC TYPE AMBIGU "Espace réservé du contenu" - Test 20260211-182310')
print('=' * 80 + '\n')

# Parcourir les résultats
ambiguous_images = []

pptx_files = sorted(Path('pptx-test').glob('*.pptx'))
pptx_files = [f for f in pptx_files if not f.name.startswith('~$')]

for pptx_file in pptx_files:
    try:
        prs = pptx.Presentation(str(pptx_file))
        
        for slide_num, slide in enumerate(prs.slides, 1):
            image_count = 0
            
            for shape in slide.shapes:
                is_picture = (shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE or 
                             (shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PLACEHOLDER and hasattr(shape, 'image')))
                
                if is_picture and hasattr(shape, 'image'):
                    # Check si c'est un type ambigu
                    if 'Espace réservé du contenu' in shape.name:
                        img = shape.image
                        size_kb = len(img.blob) / 1024
                        
                        # Déterminer catégorie
                        if size_kb < 20:
                            category = 'ICON'
                        else:
                            category = 'PHOTO'
                        
                        # Nom du fichier image extrait
                        ext = '.png'  # Par défaut
                        if img.content_type:
                            if 'jpeg' in img.content_type or 'jpg' in img.content_type:
                                ext = '.jpg'
                            elif 'gif' in img.content_type:
                                ext = '.gif'
                        
                        extracted_filename = f'slide{slide_num}_image{image_count}{ext}'
                        
                        ambiguous_images.append({
                            'pptx': pptx_file.stem,
                            'slide': slide_num,
                            'shape_name': shape.name,
                            'size_kb': size_kb,
                            'category': category,
                            'extracted_file': extracted_filename
                        })
                    
                    # Incrémenter compteur pour toutes les images
                    image_count += 1
                    
    except Exception as e:
        print(f'Erreur {pptx_file.name}: {e}')

# Afficher résultats
if ambiguous_images:
    print(f'Total: {len(ambiguous_images)} images ambiguës trouvées\n')
    
    for img in ambiguous_images:
        print(f'PPTX: {img["pptx"]}')
        print(f'  Slide: {img["slide"]}')
        print(f'  Shape Name: {img["shape_name"]}')
        print(f'  Size: {img["size_kb"]:.1f} KB')
        print(f'  Category: {img["category"]}')
        print(f'  Fichier extrait: {img["extracted_file"]}')
        print()
else:
    print('Aucune image ambiguë trouvée.')

# Vérifier dans les dossiers de résultats
print('\n' + '=' * 80)
print('VÉRIFICATION DANS LES DOSSIERS DE RÉSULTATS')
print('=' * 80 + '\n')

for img in ambiguous_images:
    # Slugify le nom du PPTX
    import re
    import unicodedata
    
    def slugify(text):
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')
        text = text.lower()
        text = re.sub(r'[\s-]+', '_', text)
        text = re.sub(r'[^a-z0-9_]', '', text)
        text = re.sub(r'_+', '_', text)
        text = text.strip('_')
        return text
    
    slugified = slugify(img['pptx'])
    result_dir = test_dir / img['pptx'] / f'{slugified}_images'
    
    if result_dir.exists():
        image_path = result_dir / img['extracted_file']
        if image_path.exists():
            print(f'✅ Trouvé: {result_dir.name}/{img["extracted_file"]}')
            print(f'   Type: {img["category"]} ({img["size_kb"]:.1f} KB)')
        else:
            print(f'❌ Non trouvé: {result_dir.name}/{img["extracted_file"]}')
    else:
        print(f'❌ Dossier non trouvé: {result_dir}')

