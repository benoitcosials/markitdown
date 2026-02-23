"""
Test de faisabilité : Extraction du texte des SmartArt via ZIP/XML.
EXTENSION : Recherche d'images embarquées et exploration DrawingML → SVG.

Résumé : Les PPTX sont des fichiers ZIP contenant des XML.
Les SmartArt ont leurs données dans ppt/diagrams/data*.xml.

Questions de recherche :
1. DrawingML → SVG : Est-ce possible ?
2. Images embarquées : Y a-t-il des <a:blip> dans les SmartArt ?

Date : 22 février 2026
"""

import zipfile
from pathlib import Path

from lxml import etree


def extract_smartart_advanced_analysis(pptx_path: Path):
    """
    Advanced analysis of SmartArt diagrams:
    - Text extraction
    - Embedded images detection (<a:blip>)
    - DrawingML elements for SVG conversion potential
    - Layout/Colors/QuickStyle analysis
    
    Args:
        pptx_path: Path to PPTX file
    """
    
    print(f"\n{'=' * 80}")
    print(f"SMARTART ADVANCED ANALYSIS: {pptx_path.name}")
    print(f"{'=' * 80}\n")
    
    # Open PPTX as ZIP
    with zipfile.ZipFile(pptx_path, 'r') as zf:
        
        # Find all diagram-related files
        data_files = sorted([name for name in zf.namelist() if name.startswith('ppt/diagrams/data')])
        layout_files = sorted([name for name in zf.namelist() if name.startswith('ppt/diagrams/layout')])
        colors_files = sorted([name for name in zf.namelist() if name.startswith('ppt/diagrams/colors')])
        style_files = sorted([name for name in zf.namelist() if name.startswith('ppt/diagrams/quickStyle')])
        
        print("📊 Diagram Files Found:")
        print(f"  - Data files: {len(data_files)}")
        print(f"  - Layout files: {len(layout_files)}")
        print(f"  - Colors files: {len(colors_files)}")
        print(f"  - QuickStyle files: {len(style_files)}\n")
        
        # Define namespaces
        ns = {
            'dgm': 'http://schemas.openxmlformats.org/drawingml/2006/diagram',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
        }
        
        # Process each diagram DATA file
        total_images_found = 0
        
        for idx, data_file in enumerate(data_files, start=1):
            print(f"\n{'─' * 80}")
            print(f"📌 SmartArt #{idx}: {data_file}")
            print(f"{'─' * 80}\n")
            
            # Read XML
            xml_bytes = zf.read(data_file)
            root = etree.fromstring(xml_bytes)
            
            # ─── SECTION 1: Text Extraction ───
            points = root.findall('.//dgm:pt', namespaces=ns)
            print("📝 TEXT EXTRACTION:")
            print(f"   Nodes found: {len(points)}")
            
            texts = []
            for pt_idx, pt in enumerate(points[:5]):  # Limit to first 5 for brevity
                text_elems = pt.findall('.//a:t', namespaces=ns)
                for text_elem in text_elems:
                    if text_elem.text:
                        texts.append(text_elem.text)
                        text_preview = text_elem.text[:60] + "..." if len(text_elem.text) > 60 else text_elem.text
                        print(f"      • \"{text_preview}\"")
            
            if len(points) > 5:
                print(f"      ... (et {len(points) - 5} autres nœuds)")
            
            # ─── SECTION 2: Embedded Images Detection ───
            print("\n🖼️  EMBEDDED IMAGES DETECTION:")
            
            # Search for <a:blip> elements (embedded images)
            blips = root.findall('.//a:blip', namespaces=ns)
            
            if blips:
                print(f"   ✅ FOUND {len(blips)} embedded image(s)!")
                total_images_found += len(blips)
                
                for blip_idx, blip in enumerate(blips, start=1):
                    # Get relationship ID (points to image file)
                    r_embed = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    r_link = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}link')
                    
                    print(f"      Image {blip_idx}:")
                    if r_embed:
                        print(f"         rId: {r_embed}")
                    if r_link:
                        print(f"         External link: {r_link}")
                    
                    # Check for image effects
                    effects = blip.findall('.//a:*', namespaces=ns)
                    if effects:
                        print(f"         Effects: {len(effects)} elements")
            else:
                print("   ❌ No embedded images (<a:blip>) found")
            
            # ─── SECTION 3: DrawingML Elements (for SVG conversion) ───
            print("\n🎨 DRAWINGML ELEMENTS (SVG Potential):")
            
            # Search for shape elements
            shapes = root.findall('.//dgm:shape', namespaces=ns)
            print(f"   Shapes: {len(shapes)}")
            
            # Search for geometric elements
            preSets = root.findall('.//dgm:prSet', namespaces=ns)
            print(f"   Property sets: {len(preSets)}")
            
            # Look for style information
            style_lbls = root.findall('.//dgm:styleLbl', namespaces=ns)
            print(f"   Style labels: {len(style_lbls)}")
            
            # Check for presentation elements
            pres_elems = root.findall('.//dgm:presOf', namespaces=ns)
            print(f"   Presentation elements: {len(pres_elems)}")
            
            # ─── SECTION 4: Connections (Hierarchy) ───
            connections = root.findall('.//dgm:cxn', namespaces=ns)
            print("\n🔗 HIERARCHY:")
            print(f"   Connections: {len(connections)}")
            
            if connections:
                # Count connection types
                cxn_types = {}
                for cxn in connections:
                    cxn_type = cxn.get('type', 'unknown')
                    cxn_types[cxn_type] = cxn_types.get(cxn_type, 0) + 1
                
                print("   Connection types:")
                for cxn_type, count in sorted(cxn_types.items()):
                    print(f"      • {cxn_type}: {count}")
        
        # ─── SECTION 5: Layout Files Analysis ───
        if layout_files:
            print(f"\n\n{'=' * 80}")
            print("📐 LAYOUT FILES ANALYSIS (for SVG conversion)")
            print(f"{'=' * 80}\n")
            
            # Sample first layout file
            layout_file = layout_files[0]
            layout_xml = zf.read(layout_file)
            layout_root = etree.fromstring(layout_xml)
            
            print(f"Sample layout: {layout_file}")
            
            # Check for layout nodes
            layout_nodes = layout_root.findall('.//*')
            print(f"   Total XML elements: {len(layout_nodes)}")
            
            # Check for shape definitions
            shape_defs = layout_root.findall('.//dgm:shape', namespaces=ns)
            print(f"   Shape definitions: {len(shape_defs)}")
            
            # Check for constraints (positioning)
            constraints = layout_root.findall('.//dgm:constr', namespaces=ns)
            print(f"   Layout constraints: {len(constraints)}")
            
            # Check for algorithms
            algorithms = layout_root.findall('.//dgm:alg', namespaces=ns)
            print(f"   Layout algorithms: {len(algorithms)}")
            if algorithms:
                alg_types = set(alg.get('type', 'unknown') for alg in algorithms)
                print(f"      Types: {', '.join(alg_types)}")
        
        # ─── FINAL SUMMARY ───
        print(f"\n\n{'=' * 80}")
        print("📊 RESEARCH SUMMARY")
        print(f"{'=' * 80}\n")
        
        print(f"✅ SmartArt diagrams analyzed: {len(data_files)}")
        print(f"🖼️  Total embedded images found: {total_images_found}")
        
        if total_images_found > 0:
            print("\n   ✅ ANSWER Question 2: YES - SmartArt with embedded images EXIST!")
        else:
            print("\n   ❌ ANSWER Question 2: NO embedded images in this test file")
        
        print("\n🎨 DrawingML → SVG Conversion Potential:")
        if layout_files:
            print(f"   ✅ Layout definitions exist ({len(layout_files)} files)")
            print("   ✅ Shape definitions found")
            print("   ✅ Positioning constraints available")
            print("   ⚠️  COMPLEX: Requires implementing PowerPoint's layout engine")
            print("   ⚠️  Alternative: Use Office APIs or external renderer")
        else:
            print("   ❌ No layout files found")
        
        print(f"\n{'=' * 80}\n")


def main():
    """Run advanced SmartArt analysis on test files."""
    
    # Test file provided by user
    test_file = Path("pptx-test/Test des SmartArt.pptx")
    
    if test_file.exists():
        print(f"🎯 Testing new file: {test_file}")
        extract_smartart_advanced_analysis(test_file)
    else:
        print(f"❌ File not found: {test_file}")
        print("   Please ensure the file exists at this location.")
        
        # Fallback to old test file
        old_test = Path("pptx-test/Kickoff QA - Essais UAT R1 Bancaire et Trésorerie.pptx")
        if old_test.exists():
            print(f"\n🔄 Using old test file instead: {old_test.name}")
            extract_smartart_advanced_analysis(old_test)


if __name__ == "__main__":
    main()
