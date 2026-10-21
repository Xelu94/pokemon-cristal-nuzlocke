"""Draw the four item-category labels of the pack as 2bpp-ready art.

Each label is five tiles wide (40x8) like the native "Objetos" / "Balls" labels:
black background, two grey edge columns on each side and white lettering in a
compact 5-pixel-high font. The result is 40x32: label N uses tiles 5N..5N+4.
Run from the root of the source tree.
"""
from pathlib import Path
from PIL import Image

root = Path.cwd()
BLACK, GREY, WHITE = 0, 85, 255

GLYPHS = {
    'A': ['.X.', 'X.X', 'XXX', 'X.X', 'X.X'],
    'B': ['XX.', 'X.X', 'XX.', 'X.X', 'XX.'],
    'C': ['.XX', 'X..', 'X..', 'X..', '.XX'],
    'D': ['XX.', 'X.X', 'X.X', 'X.X', 'XX.'],
    'E': ['XXX', 'X..', 'XX.', 'X..', 'XXX'],
    'I': ['XXX', '.X.', '.X.', '.X.', 'XXX'],
    'M': ['X...X', 'XX.XX', 'X.X.X', 'X...X', 'X...X'],
    'N': ['X..X', 'XX.X', 'X.XX', 'X..X', 'X..X'],
    'O': ['.X.', 'X.X', 'X.X', 'X.X', '.X.'],
    'R': ['XX.', 'X.X', 'XX.', 'X.X', 'X.X'],
    'S': ['.XX', 'X..', '.X.', '..X', 'XX.'],
    'T': ['XXX', '.X.', '.X.', '.X.', '.X.'],
    'Y': ['X.X', 'X.X', '.X.', '.X.', '.X.'],
}
LABELS = ['MEDICINA', 'BAYAS', 'COMBATE', 'OTROS']
TEXT_LEFT, TEXT_WIDTH = 2, 36

image = Image.new('L', (40, 8 * len(LABELS)), BLACK)
for row, label in enumerate(LABELS):
    top = row * 8
    for y in range(8):
        for x in (0, 1, 38, 39):
            image.putpixel((x, top + y), GREY)
    width = sum(len(GLYPHS[c][0]) for c in label) + len(label) - 1
    assert width <= TEXT_WIDTH, (label, width)
    x = TEXT_LEFT + (TEXT_WIDTH - width) // 2
    for char in label:
        glyph = GLYPHS[char]
        for gy, bits in enumerate(glyph):
            for gx, bit in enumerate(bits):
                if bit == 'X':
                    image.putpixel((x + gx, top + 1 + gy), WHITE)
        x += len(glyph[0]) + 1

image.save(root / 'gfx/pack/pack_categories.png')
print('pack category labels: 4 labels, 20 tiles (40x32)')
