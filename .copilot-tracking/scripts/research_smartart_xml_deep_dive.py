"""
Deep dive XML exploration for SmartArt diagram parts.

This script focuses on extracting text from SmartArt by navigating
the diagram parts relationships.

Date: 22 février 2026
"""

from pathlib import Path

import pptx
from lxml import etree


def find_smartart_in_pptx(pptx_path: Path):
    """Find first SmartArt in PPTX and explore its XML structure deeply."""
    
    print(f"\n{'=' * 80}")
    print(f"SMARTART XML DEEP DIVE: {pptx_path.name}")
    print(f"{'=' * 80}\n")
    
    presentation = pptx.Presentation(pptx_path)
    
    for slide_idx, slide in enumerate(presentation.slides, start=1):
        for shape_idx, shape in enumerate(slide.shapes):
            
            #Check if SmartArt via XML
            try:
                if not hasattr(shape._element, 'graphic'):
                    continue
                    
                graphic_data = shape._element.graphic.graphicData
                uri = graphic_data.get('uri', '')
                
                if 'diagram' not in uri:
                    continue
                
                # SmartArt found!
                print(f"✅ SmartArt found: Slide {slide_idx}, Shape {shape_idx}")
                print(f"   Name: {shape.name}")
                print(f"   URI: {uri}\n")
                
                # Deep exploration
                explore_smartart_xml_parts(shape, slide, slide_idx)
                
                # Only explore first SmartArt
                return True
                
            except:
                pass
    
    print("❌ No SmartArt found in this file.\n")
    return False


def explore_smartart_xml_parts(shape, slide, slide_idx):
    """Deep XML exploration of SmartArt parts."""
    
    print("--- PART STRUCTURE EXPLORATION ---\n")
    
    # 1. Get slide part
    slide_part = slide.part
    print(f"1. Slide Part: {slide_part}")
    print(f"   Part name: {slide_part.partname}\n")
    
    # 2. Get shape element XML
    shape_elem = shape._element
    print("2. Shape Element:")
    print(f"   Tag: {shape_elem.tag}")
    
    # Try to get relationship IDs from shape XML
    # SmartArt references diagram parts via relationship IDs
    print("\n3. Looking for Relationship IDs in shape XML...")
    
    # Parse shape XML to find rIds
    for elem in shape_elem.iter():
        for attr_name, attr_value in elem.attrib.items():
            if 'id' in attr_name.lower() and attr_value.startswith('rId'):
                print(f"   Found rId: {attr_name} = {attr_value}")
                
                # Try to resolve this relationship
                try:
                    related_part = slide_part.related_part(attr_value)
                    print(f"      → Resolves to: {related_part.partname}")
                    
                    # Check if it's a diagram part
                    if 'diagram' in str(related_part.partname).lower():
                        print("      🎯 This is a diagram part!")
                        explore_diagram_part(related_part, attr_value)
                        
                except Exception as e:
                    print(f"      Error resolving: {e}")
    
    # 3. List ALL related parts of the slide
    print("\n4. All Related Parts of Slide:")
    for rel_id, related_part in slide_part.related_parts.items():
        part_name = related_part.partname
        print(f"   {rel_id}: {part_name}")
        
        # Check for diagram parts
        if 'diagram' in str(part_name).lower():
            print("      🎯 Found diagram part via related_parts!")
            explore_diagram_part(related_part, rel_id)


def explore_diagram_part(diagram_part, rel_id):
    """Explore diagram part to extract nodes and text."""
    
    print(f"\n   --- DIAGRAM PART EXPLORATION ({rel_id}) ---")
    
    try:
        # Get diagram XML content
        diagram_xml_bytes = diagram_part.blob
        print(f"   XML Size: {len(diagram_xml_bytes)} bytes")
        
        # Parse with lxml
        root = etree.fromstring(diagram_xml_bytes)
        print("   ✅ Successfully parsed XML")
        print(f"   Root tag: {root.tag}")
        
        # Define namespaces
        # dgm = DrawingML Diagram
        # a = DrawingML Main
        nsmap = {
            'dgm': 'http://schemas.openxmlformats.org/drawingml/2006/diagram',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        }
        
        # Find all points (nodes) in diagram
        print("\n   🔍 Searching for <dgm:pt> nodes...")
        
        points = root.findall('.//dgm:pt', namespaces=nsmap)
        print(f"   ✅ Found {len(points)} <dgm:pt> nodes")
        
        if len(points) == 0:
            # Try without namespace
            points_no_ns = root.findall('.//pt')
            print(f"   ℹ️ Found {len(points_no_ns)} <pt> nodes (no namespace)")
            points = points_no_ns
        
        # Extract text from nodes
        print("\n   📝 Extracting text from nodes:")
        nodes_with_text = []
        
        for idx, pt in enumerate(points):
            # Get node type
            node_type = pt.get('type', 'unknown')
            model_id = pt.get('modelId', 'no-id')
            
            # Find text element <a:t>
            text_elems = pt.findall('.//a:t', namespaces=nsmap)
            if not text_elems:
                # Try without namespace
                text_elems = pt.findall('.//t')
            
            if text_elems:
                for text_elem in text_elems:
                    text = text_elem.text
                    if text:
                        print(f"      Node {idx} (type={node_type}): \"{text}\"")
                        nodes_with_text.append({
                            'index': idx,
                            'type': node_type,
                            'id': model_id,
                            'text': text
                        })
        
        if not nodes_with_text:
            print("      ⚠️ No text found in nodes")
        
        # Find connections (hierarchy)
        print("\n   🔗 Searching for <dgm:cxn> connections...")
        connections = root.findall('.//dgm:cxn', namespaces=nsmap)
        if not connections:
            connections = root.findall('.//cxn')
        
        print(f"   ✅ Found {len(connections)} <dgm:cxn> connections")
        
        if connections:
            print("\n   📊 Connection hierarchy:")
            for idx, cxn in enumerate(connections[:10]):  # First 10
                cxn_type = cxn.get('type', 'unknown')
                src_id = cxn.get('srcId', '')
                dest_id = cxn.get('destId', '')
                print(f"      Connection {idx} ({cxn_type}): {src_id} → {dest_id}")
        
        # Summary
        print("\n   ✅ EXTRACTION SUMMARY:")
        print(f"      Total nodes: {len(points)}")
        print(f"      Nodes with text: {len(nodes_with_text)}")
        print(f"      Connections: {len(connections)}")
        
        if nodes_with_text:
            print("\n   🎯 TEXT EXTRACTION SUCCESSFUL!")
            print("      Sample texts:")
            for node in nodes_with_text[:5]:
                print(f"         - \"{node['text']}\"")
        
        return nodes_with_text, connections
        
    except Exception as e:
        print(f"   ❌ Error exploring diagram part: {e}")
        import traceback
        traceback.print_exc()
        return [], []


def main():
    """Test XML exploration on PPTX files."""
    
    # Test file with known SmartArt
    test_file = "pptx-test/Kickoff QA - Essais UAT R1 Bancaire et Trésorerie.pptx"
    
    path = Path(test_file)
    if path.exists():
        found = find_smartart_in_pptx(path)
        
        if found:
            print("\n" + "=" * 80)
            print("CONCLUSION:")
            print("✅ SmartArt text extraction is FEASIBLE via XML parsing!")
            print("=" * 80)
        else:
            print("\n⚠️ No SmartArt found to test")
    else:
        print(f"❌ Test file not found: {test_file}")


if __name__ == "__main__":
    main()
