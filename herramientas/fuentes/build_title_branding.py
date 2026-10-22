"""Draw the title-screen line "RADICAL CRISTAL" above the copyright line of
gfx/title/nuzlocke_branding.png (160x16, two shades). Run from the source root."""
from pathlib import Path
from PIL import Image

GLYPHS = {
    'R': ['XXXXXX.', 'X.....X', 'X.....X', 'XXXXXX.', 'X...X..', 'X....X.', 'X.....X'],
    'A': ['...X...', '..X.X..', '..X.X..', '.X...X.', '.XXXXX.', 'X.....X', 'X.....X'],
    'D': ['XXXXXX.', 'X.....X', 'X.....X', 'X.....X', 'X.....X', 'X.....X', 'XXXXXX.'],
    'I': ['XXXXX', '..X..', '..X..', '..X..', '..X..', '..X..', 'XXXXX'],
    'C': ['..XXXX.', '.X....X', 'X......', 'X......', 'X......', '.X....X', '..XXXX.'],
    'L': ['X......', 'X......', 'X......', 'X......', 'X......', 'X......', 'XXXXXXX'],
    'S': ['.XXXX..', 'X....X.', 'X......', '.XXXXX.', '......X', 'X.....X', '.XXXXX.'],
    'T': ['XXXXXXX', '...X...', '...X...', '...X...', '...X...', '...X...', '...X...'],
}
TEXT = 'RADICAL CRISTAL'
SPACE = 5
DARK, LIGHT = 85, 255

path = Path('gfx/title/nuzlocke_branding.png')
image = Image.open(path).convert('L')
for y in range(8):
    for x in range(image.width):
        image.putpixel((x, y), LIGHT)
width = sum(SPACE if c == ' ' else len(GLYPHS[c][0]) for c in TEXT) + len(TEXT) - 1
x = (image.width - width) // 2
for char in TEXT:
    if char == ' ':
        x += SPACE + 1
        continue
    for gy, row in enumerate(GLYPHS[char]):
        for gx, bit in enumerate(row):
            if bit == 'X':
                image.putpixel((x + gx, gy), DARK)
    x += len(GLYPHS[char][0]) + 1
image.save(path)
print('title branding: RADICAL CRISTAL, width', width)
