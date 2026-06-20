import os
from rembg import remove
from PIL import Image

base = "/Users/gregoryadkins/Documents/Claude"
outdir = os.path.join(base, "papaw-coins", "photos", "cutouts")
photodir = os.path.join(base, "papaw-coins", "photos")
coins = "/Users/gregoryadkins/Desktop/COINS"

mapping = [
    ("coin-012", "IMG_0144"), ("coin-013", "IMG_0145"), ("coin-014", "IMG_0142"),
    ("coin-015", "IMG_0140"), ("coin-016", "IMG_0137"), ("coin-017", "IMG_0138"),
    ("coin-018", "IMG_0139"), ("coin-019", "IMG_0143"),
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

# place photos -> resized JPGs in photos/
places = [("white-stores.jpg", "white-stores.jpg"),
          ("kmart-clinton.jpg", "kmart-clinton.jpg"),
          ("bavarian-haus-motel.png", "bavarian-haus.jpg")]
for srcname, dstname in places:
    im = Image.open(os.path.join(coins, srcname)).convert("RGB")
    if im.width > 1100:
        h = int(im.height * 1100 / im.width)
        im = im.resize((1100, h), Image.LANCZOS)
    dst = os.path.join(photodir, dstname)
    im.save(dst, "JPEG", quality=82, optimize=True)
    print("place", dstname, im.size, str(os.path.getsize(dst) // 1024) + "KB")
