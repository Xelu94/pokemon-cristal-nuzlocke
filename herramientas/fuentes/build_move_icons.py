"""Draw the three move-category icons (physical, special, status) as 8x8 tiles.

Output: gfx/battle/move_categories.png, 24x8 (three tiles in a row), grayscale
levels 255/170/85/0 = white/light/dark/black like the other 2bpp sources.
Run from the root of the source tree.
"""
from pathlib import Path
from PIL import Image

ICONS = [
    # physical: impact burst
    ['#..##..#',
     '.#.##.#.',
     '..####..',
     '#######.',
     '..####..',
     '.#.##.#.',
     '#..##..#',
     '...##...'],
    # special: spiral
    ['..####..',
     '.#....#.',
     '#..##..#',
     '#.#..#.#',
     '#.#..#.#',
     '#..####.',
     '.#......',
     '..####..'],
    # status: oval with a dot
    ['..####..',
     '.#++++#.',
     '#+....+#',
     '#+.##.+#',
     '#+.##.+#',
     '#+....+#',
     '.#++++#.',
     '..####..'],
]
LEVEL = {'.': 255, '+': 85, '#': 0}
image = Image.new('L', (24, 8), 255)
for n, rows in enumerate(ICONS):
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            image.putpixel((n * 8 + x, y), LEVEL[char])
image.save(Path.cwd() / 'gfx/battle/move_categories.png')
print('move category icons: 3 tiles')
