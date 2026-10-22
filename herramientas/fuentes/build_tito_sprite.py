"""Compile Tito's native pixel-grid source to PNG and LR35902-ready 2bpp.

The PNG is an editable preview, the textual grid is the source of truth. Do not
rescale the large reference sheet: it drops eyes and contours at 16x16. The
engine requires front/back/LEFT, followed by complete alternate frames.
"""
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / 'gfx/sprites/tito_xeluis.pixels'
frames = {}
name = None
for row in source.read_text(encoding='utf8').splitlines():
    if not row or row.startswith(';'):
        continue
    if row.startswith('['):
        name = row.strip('[]')
        frames[name] = []
    else:
        assert len(row) == 16 and set(row) <= set('.yr#'), (name, row)
        frames[name].append(row)
assert list(frames) == ['front', 'back', 'left']
assert all(len(rows) == 16 for rows in frames.values())

shades = {'.': 255, 'y': 170, 'r': 85, '#': 0}
image = Image.new('L', (16, 96), 255)
def breathe(rows):
    new = list(rows)
    for y in range(11, 0, -1):
        new[y] = rows[y - 1]
    new[0] = '.' * 16
    return new


for index, rows in enumerate(list(frames.values()) + [breathe(r) for r in frames.values()]):
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            image.putpixel((x, index * 16 + y), shades[char])
image.save(root / 'gfx/sprites/tito_xeluis.png')
print('Tito native artwork: front/back/LEFT + three idle frames (head and torso one pixel lower), 16x96.')
