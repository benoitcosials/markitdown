"""Debug red cells in slide 2 table."""
import sys

sys.path.insert(0, r"C:\Repos\markitdown\packages\markitdown\src")
import pptx
from pptx.enum.dml import MSO_FILL_TYPE

pptx_path = r".copilot-tracking\tests\pptx\z 015_ARCH-00xx_WS4_Bancaire-b7f2a76a-7655-4a73-a5ab-035aee935269.pptx"
prs = pptx.Presentation(pptx_path)
slide = prs.slides[1]

# Reload converter
for mod in list(sys.modules.keys()):
    if "markitdown" in mod:
        del sys.modules[mod]
        
from markitdown.converters._pptx_converter import PptxConverter

converter = PptxConverter()

for shape in slide.shapes:
    if shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.TABLE:
        table = shape.table
        print("Checking rows 2-10 for colored cells:\n")
        
        for row_idx in range(2, 10):
            row = table.rows[row_idx]
            text_col1 = row.cells[1].text.strip()[:30] if row.cells[1].text else ""
            
            for col_idx in range(2, 5):  # AA, AF, ATI
                cell = row.cells[col_idx]
                fill = cell.fill
                fill_type = fill.type
                
                if fill_type == MSO_FILL_TYPE.SOLID:
                    fore = fill.fore_color
                    if fore.rgb:
                        r, g, b = fore.rgb[0], fore.rgb[1], fore.rgb[2]
                        # Test HSL
                        hsl = converter._rgb_to_hsl(r, g, b)
                        result = converter._rgb_to_color_name(r, g, b)
                        
                        col_name = ["AA", "AF", "ATI"][col_idx - 2]
                        print(f"Row {row_idx} ({text_col1[:20]}) {col_name}:")
                        print(f"  RGB({r},{g},{b}) HSL(H={hsl[0]:.1f}, S={hsl[1]:.2f}, L={hsl[2]:.2f})")
                        print(f"  Result: {result}")
                        print()
        break
