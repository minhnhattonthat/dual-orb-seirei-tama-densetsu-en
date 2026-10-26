"""fontsheet.py VRAM.bin OUT.png [--chr HEX] [--rom ROM]: render every text code (00-DF) as its 8x16 glyph.

The glyph table at ROM $00:B0A2 (file 0x30A2) gives each code a (top tile, bottom tile) word pair; tiles are 2bpp
from VRAM byte offset --chr (BG3 chr base, 0x4000 on the intro and field screens). Labels are the code in hex."""
import argparse
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("vram")
ap.add_argument("out")
ap.add_argument("--chr", default="4000")
ap.add_argument("--rom", default="rom/Dual Orb - Seirei Tama Densetsu (Japan).sfc")
ap.add_argument("--zoom", type=int, default=3)
a = ap.parse_args()
v = open(a.vram, "rb").read()
rom = open(a.rom, "rb").read()
chr_base = int(a.chr, 16)


def tile(n):
    img = Image.new("L", (8, 8))
    o = chr_base + (n & 0x3FF) * 16
    for y in range(8):
        p0, p1 = v[o + 2 * y], v[o + 2 * y + 1]
        for x in range(8):
            c = ((p0 >> (7 - x)) & 1) | (((p1 >> (7 - x)) & 1) << 1)
            img.putpixel((x, y), c * 85)
    return img


cols, cw, ch = 16, 8 * a.zoom + 22, 16 * a.zoom + 4
sheet = Image.new("L", (cols * cw, 14 * ch), 40)
d = ImageDraw.Draw(sheet)
for c in range(0xE0):
    top = rom[0x30A2 + 4 * c] | rom[0x30A3 + 4 * c] << 8
    bot = rom[0x30A4 + 4 * c] | rom[0x30A5 + 4 * c] << 8
    g = Image.new("L", (8, 16))
    g.paste(tile(top), (0, 0))
    g.paste(tile(bot), (0, 8))
    x, y = (c % cols) * cw, (c // cols) * ch
    d.text((x + 1, y + 2), "%02X" % c, fill=255)
    sheet.paste(g.resize((8 * a.zoom, 16 * a.zoom), Image.NEAREST), (x + 20, y + 2))
sheet.save(a.out)
print(a.out)
