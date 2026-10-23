"""Builds gfx/pokemon/dark_lugia/front.png and back.png.

front.png: the user-supplied animated Dark Lugia sprite (video, 280x280 = 56x56 pixels scaled by 5).
Frame 0 is the idle pose, frames 1-3 are the wing-flap poses. Colours are reduced to the four
colours of the Dark Lugia palette. back.png is not generated here: it is the back view supplied by the
project author (56x56 pixel art cropped to its central 48x48 with the same four colours, red mark removed).
Usage: build_dark_lugia_sprite.py <frames_dir> <idle> <flap> <flap> <flap>   (frame numbers in frames_dir)"""
import sys
from collections import Counter
from pathlib import Path
from PIL import Image

PALETTE = [(255, 255, 255), (99, 82, 140), (66, 41, 90), (0, 0, 0)]
REF = [(255, 255, 255), (100, 79, 136), (62, 44, 90), (0, 0, 0)]


def nearest(c):
    return min(range(4), key=lambda i: sum((c[k] - REF[i][k]) ** 2 for k in range(3)))


def shrink(path):
    im = Image.open(path).convert('RGB')
    out = Image.new('RGB', (56, 56))
    for y in range(56):
        for x in range(56):
            block = Counter(nearest(im.getpixel((x * 5 + i, y * 5 + j))) for i in range(5) for j in range(5))
            out.putpixel((x, y), PALETTE[block.most_common(1)[0][0]])
    return out


def main():
    frames_dir = Path(sys.argv[1])
    numbers = [int(n) for n in sys.argv[2:]]
    sheet = Image.new('RGB', (56, 56 * len(numbers)))
    for i, n in enumerate(numbers):
        sheet.paste(shrink(frames_dir / ('f%03d.png' % n)), (0, 56 * i))
    out = Path('gfx/pokemon/dark_lugia')
    sheet.save(out / 'front.png')


main()
