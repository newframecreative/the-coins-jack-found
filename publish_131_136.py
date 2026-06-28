import os, json, re
from rembg import remove
from PIL import Image

base = "/Users/gregoryadkins/Documents/Claude"
outdir = os.path.join(base, "papaw-coins", "photos", "cutouts")
data = json.load(open(os.path.join(base, "papaw-coins", "coins.json")))
pend = [c for c in data["coins"] if c.get("pending")]
print("pending:", [c["id"] for c in pend])

# 1) cutouts
for c in pend:
    cid, img = c["id"], c["photo"]
    src = Image.open(os.path.join(base, img + ".jpg")).convert("RGBA")
    cut = remove(src); bb = cut.getbbox()
    if bb: cut = cut.crop(bb)
    if cut.width > 1000:
        h = int(cut.height * 1000 / cut.width); cut = cut.resize((1000, h), Image.LANCZOS)
    cut.save(os.path.join(outdir, cid + ".png"), optimize=True)
    print("cut", cid, cut.size, flush=True)

# 2) build JS coin lines
def js(s): return json.dumps(s, ensure_ascii=False)
def coins_arr(c):
    if c.get("coins"):
        parts = []
        for x in c["coins"]:
            m = "null" if x["mint"] is None else str(x["mint"])
            parts.append('{den:%s,mint:%s}' % (js(x["den"]), m))
        return "coins:[" + ",".join(parts) + "]"
    m = "null" if c["mintYear"] is None else str(c["mintYear"])
    return "den:%s,mint:%s" % (js(c["denomination"]), m)

def coin_line(c):
    fields = [
        'id:%s' % js(c["id"]),
        'img:%s' % js("photos/cutouts/%s.png" % c["id"]),
        'place:%s' % js(c["place"] if c.get("place") else c["placeKey"]),
        'found:%s' % js(c["dateFound"]),
        'raw:%s' % js(c["dateFoundRaw"]),
        'dow:%s' % js(c["dayOfWeek"]),
        'finders:[%s]' % ",".join(js(f) for f in c["finders"]),
        'say:%s' % js(c["say"]),
    ]
    if c.get("microSpot"): fields.append('spot:%s' % js(c["microSpot"]))
    fields.append(coins_arr(c))
    fields.append('city:%s' % js(c["city"]))
    fields.append('state:%s' % js(c["state"]))
    return " {" + ",".join(fields) + "}"

lines = [coin_line(c) for c in pend]

# new PLACES entry (only fountain-city-auto-clinic is new)
new_place = ' "fountain-city-auto-clinic":{name:"Fountain City Auto Clinic",where:"2823 Woodrow Dr, Knoxville",status:"standing",lat:36.02866,lng:-83.92787,story:"A neighborhood garage on Woodrow Drive in the heart of Fountain City, just off North Broadway and only minutes from Jack\'s house. He turned up two 1999 pennies here in 2006."},\n'

path = os.path.join(base, "papaw-coins", "coins-data.js")
txt = open(path).read()

# insert place before the PLACES-closing "};"
assert "fountain-city-auto-clinic" not in txt
m = re.search(r'\n\};\n', txt)
txt = txt[:m.start()] + "\n" + new_place.rstrip("\n") + txt[m.start():]

# insert coins before COINS closing "]"; last coin currently has no trailing comma
# find the coin-130 line end and the array close
close = re.search(r'(\n\];\s*)$', txt)
if not close:
    close = re.search(r'\n\];', txt[txt.index("const COINS"):])
    idx = txt.index("const COINS") + close.start()
else:
    idx = close.start()
block = ",\n" + ",\n".join(lines)
txt = txt[:idx] + block + txt[idx:]

open(path, "w").write(txt)
print("inserted", len(lines), "coins + 1 place")
