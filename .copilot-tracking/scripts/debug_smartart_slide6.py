"""Debug SmartArt 1 (Slide 6) - Analyze why table rows are empty."""
import zipfile
from pathlib import Path

from lxml import etree

PPTX_PATH = Path(r".copilot-tracking\pptx\Standard QA - Concept de base.pptx")

ns = {
    'dgm': 'http://schemas.openxmlformats.org/drawingml/2006/diagram',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}

with zipfile.ZipFile(PPTX_PATH, 'r') as zf:
    # Find diagram data files
    diagram_files = [f for f in zf.namelist() if 'diagrams/data' in f]
    print(f"Diagram data files: {diagram_files}\n")

    # Check slide 6 relationships to find which diagram it uses
    rels_path = 'ppt/slides/_rels/slide6.xml.rels'
    if rels_path in zf.namelist():
        rels_xml = zf.read(rels_path)
        rels_root = etree.fromstring(rels_xml)
        ns_rel = "http://schemas.openxmlformats.org/package/2006/relationships"
        print("=== Slide 6 relationships ===")
        for rel in rels_root.findall(f'.//{{{ns_rel}}}Relationship'):
            rel_type = rel.get('Type', '')
            if 'diagram' in rel_type.lower():
                print(f"  Id={rel.get('Id')} Type={rel_type.split('/')[-1]} Target={rel.get('Target')}")

    # Analyze each diagram data file
    for dfile in diagram_files:
        print(f"\n{'='*60}")
        print(f"=== Analyzing {dfile} ===")
        print(f"{'='*60}")

        xml_bytes = zf.read(dfile)
        root = etree.fromstring(xml_bytes)

        points = root.findall('.//dgm:pt', namespaces=ns)
        connections = root.findall('.//dgm:cxn', namespaces=ns)

        print(f"\nTotal points: {len(points)}")
        print(f"Total connections: {len(connections)}")

        # Analyze points
        node_types = {}
        data_node_ids = set()
        all_node_ids = set()
        node_texts = {}

        print("\n--- Points ---")
        for pt in points:
            model_id = pt.get('modelId')
            pt_type = pt.get('type', '(none)')
            all_node_ids.add(model_id)
            node_types[model_id] = pt_type

            text_parts = []
            for t in pt.findall('.//a:t', namespaces=ns):
                if t.text:
                    text_parts.append(t.text.strip())
            text = ' '.join(text_parts) if text_parts else ''

            if pt_type in ('(none)', 'node', None) or pt.get('type') is None:
                data_node_ids.add(model_id)
                if text:
                    node_texts[model_id] = text

            # Check for images
            blip = pt.find('.//a:blip', namespaces=ns)
            has_image = blip is not None
            r_embed = blip.get(f'{{{ns["r"]}}}embed') if blip is not None else ''

            actual_type = pt.get('type')
            print(f"  ID={model_id:>4s} type={str(actual_type):>10s} text='{text[:50]}'"
                  f"{'  [HAS IMAGE rId=' + r_embed + ']' if has_image else ''}")

        # Analyze connections
        dest_nodes = set()
        children_map = {}

        print("\n--- Connections (hierarchy only, no type attr) ---")
        for cxn in connections:
            cxn_type = cxn.get('type')
            src_id = cxn.get('srcId')
            dest_id = cxn.get('destId')
            src_ord = cxn.get('srcOrd', '0')
            dest_ord = cxn.get('destOrd', '0')

            child_type = node_types.get(dest_id)
            if child_type in ('parTrans', 'sibTrans', 'pres'):
                continue

            if cxn_type is None:
                if src_id not in children_map:
                    children_map[src_id] = []
                children_map[src_id].append(dest_id)
                dest_nodes.add(dest_id)
                src_type = node_types.get(src_id, '?')
                dst_type = node_types.get(dest_id, '?')
                print(f"  {src_id}({src_type}) -> {dest_id}({dst_type})  "
                      f"srcOrd={src_ord} destOrd={dest_ord}")

        # Root detection (current code: all_node_ids - dest_nodes)
        root_nodes = [nid for nid in all_node_ids if nid not in dest_nodes]
        print("\n--- Root detection ---")
        print(f"  all_node_ids count: {len(all_node_ids)}")
        print(f"  data_node_ids count: {len(data_node_ids)}")
        print(f"  dest_nodes count: {len(dest_nodes)}")
        print(f"  Root nodes (current): {root_nodes}")
        for rn in root_nodes:
            rn_type = node_types.get(rn, '?')
            rn_text = node_texts.get(rn, '(no text)')
            print(f"    Root {rn}: type={rn_type}, text='{rn_text[:50]}'")

        # BFS depth calculation
        depths = {}
        queue = [(rn, 0) for rn in root_nodes]
        while queue:
            nid, d = queue.pop(0)
            if nid in depths:
                depths[nid] = max(depths[nid], d)
            else:
                depths[nid] = d
            for child in children_map.get(nid, []):
                queue.append((child, d + 1))

        print("\n--- Depths for DATA nodes ---")
        for nid in sorted(data_node_ids):
            d = depths.get(nid, '?')
            t = node_texts.get(nid, '(no text)')
            print(f"  Node {nid}: depth={d}, text='{t[:50]}'")

        min_data_depth = min(
            (depths.get(nid, 0) for nid in data_node_ids if nid in depths),
            default=0,
        )
        print(f"\n  >>> Minimum data node depth: {min_data_depth}")
        if min_data_depth > 0:
            print(f"  >>> BUG CONFIRMED: data nodes start at depth {min_data_depth}, "
                  f"not 0. Table grouping requires level-0 nodes!")
