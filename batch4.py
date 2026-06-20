import os
from rembg import remove
from PIL import Image, ImageDraw

base = "/Users/gregoryadkins/Documents/Claude"
outdir = os.path.join(base, "papaw-coins", "photos", "cutouts")
mapping = [
    ("coin-034", "IMG_0160"), ("coin-035", "IMG_0161"), ("coin-036", "IMG_0162"),
    ("coin-037", "IMG_0163"), ("coin-038", "IMG_0166"), ("coin-039", "IMG_0167"),
    ("coin-040", "IMG_0165"), ("coin-041", "IMG_0164"),
]
cuts = []
for cid, img in mapping:
    src = Image.open(os.path.join(base, img + ".jpg")).convert("RGBA")
    cut = remove(src); bb = cut.getbbox()
    if bb: cut = cut.crop(bb)
    if cut.width > 1000:
        h = int(cut.height * 1000 / cut.width); cut = cut.resize((1000, h), Image.LANCZOS)
    cut.save(os.path.join(outdir, cid + ".png"), optimize=True)
    cuts.append((cid, cut)); print("cut", cid, cut.size)

cols, rows, cw, ch, pad, lh = 2, 4, 380, 210, 10, 20
W = cols*(cw+pad)+pad; H = rows*(ch+lh+pad)+pad
sheet = Image.new("RGB", (W, H), (228, 228, 231)); d = ImageDraw.Draw(sheet)
for i, (cid, cut) in enumerate(cuts):
    r, c = divmod(i, cols); x = pad+c*(cw+pad); y = pad+r*(ch+lh+pad)
    cc = cut.copy(); cc.thumbnail((cw, ch))
    cell = Image.new("RGBA", (cw, ch), (246, 246, 248, 255)); cell.paste(cc, ((cw-cc.width)//2, (ch-cc.height)//2), cc)
    sheet.paste(cell.convert("RGB"), (x, y+lh)); d.text((x+4, y+6), cid, fill=(15, 15, 15))
sheet.save(os.path.join(base, "papaw-coins", "contact4.jpg"), quality=70); print("sheet", sheet.size)
