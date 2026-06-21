import os
from rembg import remove
from PIL import Image, ImageDraw

base = "/Users/gregoryadkins/Documents/Claude"
outdir = os.path.join(base, "papaw-coins", "photos", "cutouts")
mapping = [
    ("coin-058", "IMG_0185"), ("coin-059", "IMG_0186"), ("coin-060", "IMG_0187"),
    ("coin-061", "IMG_0188"), ("coin-062", "IMG_0189"), ("coin-063", "IMG_0190"),
    ("coin-064", "IMG_0191"), ("coin-065", "IMG_0192"), ("coin-066", "IMG_0194"),
    ("coin-067", "IMG_0195"),
]
cuts = []
for cid, img in mapping:
    src = Image.open(os.path.join(base, img + ".jpg")).convert("RGBA")
    cut = remove(src); bb = cut.getbbox()
    if bb: cut = cut.crop(bb)
    if cut.width > 1000:
        h = int(cut.height * 1000 / cut.width); cut = cut.resize((1000, h), Image.LANCZOS)
    cut.save(os.path.join(outdir, cid + ".png"), optimize=True)
    cuts.append((cid, cut)); print("cut", cid, cut.size, "ratio", round(cut.height / cut.width, 2), flush=True)

cols, rows, cw, ch, pad, lh = 3, 4, 300, 200, 10, 18
W = cols * (cw + pad) + pad; H = rows * (ch + lh + pad) + pad
sheet = Image.new("RGB", (W, H), (228, 228, 231)); dr = ImageDraw.Draw(sheet)
for i, (cid, cut) in enumerate(cuts):
    r, c = divmod(i, cols); x = pad + c * (cw + pad); y = pad + r * (ch + lh + pad)
    cc = cut.copy(); cc.thumbnail((cw, ch))
    cell = Image.new("RGBA", (cw, ch), (246, 246, 248, 255)); cell.paste(cc, ((cw - cc.width) // 2, (ch - cc.height) // 2), cc)
    sheet.paste(cell.convert("RGB"), (x, y + lh)); dr.text((x + 4, y + 4), cid, fill=(15, 15, 15))
sheet.save(os.path.join(base, "papaw-coins", "contact6.jpg"), quality=70); print("sheet", sheet.size, flush=True)
