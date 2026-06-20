import os
from rembg import remove
from PIL import Image

base = "/Users/gregoryadkins/Documents/Claude"
outdir = os.path.join(base, "papaw-coins", "photos", "cutouts")

mapping = [
    ("coin-020", "IMG_0146"), ("coin-021", "IMG_0147"), ("coin-022", "IMG_0148"),
    ("coin-023", "IMG_0149"), ("coin-024", "IMG_0150"), ("coin-025", "IMG_0151"),
    ("coin-026", "IMG_0152"), ("coin-027", "IMG_0159"), ("coin-028", "IMG_0158"),
    ("coin-029", "IMG_0154"), ("coin-030", "IMG_0156"), ("coin-031", "IMG_0155"),
    ("coin-032", "IMG_0153"), ("coin-033", "IMG_0157"),
]
for cid, img in mapping:
    src = Image.open(os.path.join(base, img + ".jpg")).convert("RGBA")
    cut = remove(src)
    bb = cut.getbbox()
    if bb:
        cut = cut.crop(bb)
    if cut.width > 1000:
        h = int(cut.height * 1000 / cut.width)
        cut = cut.resize((1000, h), Image.LANCZOS)
    cut.save(os.path.join(outdir, cid + ".png"), optimize=True)
    print("cut", cid, cut.size)
print("DONE", len(mapping))
