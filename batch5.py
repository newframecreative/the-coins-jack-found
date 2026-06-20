import os
from rembg import remove
from PIL import Image, ImageDraw

base = "/Users/gregoryadkins/Documents/Claude"
outdir = os.path.join(base, "papaw-coins", "photos", "cutouts")
mapping = [
    ("coin-042", "IMG_0169"), ("coin-043", "IMG_0170"), ("coin-044", "IMG_0171"),
    ("coin-045", "IMG_0172"), ("coin-046", "IMG_0173"), ("coin-047", "IMG_0174"),
    ("coin-048", "IMG_0175"), ("coin-049", "IMG_0176"), ("coin-050", "IMG_0177"),
    ("coin-051", "IMG_0178"), ("coin-052", "IMG_0179"), ("coin-053", "IMG_0180"),
    ("coin-054", "IMG_0181"), ("coin-055", "IMG_0182"), ("coin-056", "IMG_0183"),
]
cuts = []
for cid, img in mapping:
    src = Image.open(os.path.join(base, img + ".jpg")).convert("RGBA")
    cut = remove(src); bb = cut.getbbox()
    if bb: cut = cut.crop(bb)
    if cut.width > 1000:
        h = int(cut.height * 1000 / cut.width); cut = cut.resize((1000, h), Image.LANCZOS)
    cut.save(os.path.join(outdir, cid + ".png"), optimize=True)
    ratio = round(cut.height / cut.width, 2)
    cuts.append((cid, cut)); print("cut", cid, cut.size, "ratio", ratio, flush=True)

cols, rows, cw, ch, pad, lh = 3, 5, 300, 200, 10, 18
W = cols * (cw + pad) + pad; H = rows * (ch + lh + pad) + pad
sheet = Image.new("RGB", (W, H), (228, 228, 231)); dr = ImageDraw.Draw(sheet)
for i, (cid, cut) in enumerate(cuts):
    r, c = divmod(i, cols); x = pad + c * (cw + pad); y = pad + r * (ch + lh + pad)
    cc = cut.copy(); cc.thumbnail((cw, ch))
    cell = Image.new("RGBA", (cw, ch), (246, 246, 248, 255)); cell.paste(cc, ((cw - cc.width) // 2, (ch - cc.height) // 2), cc)
    sheet.paste(cell.convert("RGB"), (x, y + lh)); dr.text((x + 4, y + 4), cid, fill=(15, 15, 15))
sheet.save(os.path.join(base, "papaw-coins", "contact5.jpg"), quality=70); print("sheet", sheet.size, flush=True)
