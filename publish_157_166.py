import os, json, re
from rembg import remove
from PIL import Image

base = "/Users/gregoryadkins/Documents/Claude"
outdir = os.path.join(base, "papaw-coins", "photos", "cutouts")
data = json.load(open(os.path.join(base, "papaw-coins", "coins.json")))

pub = [c for c in data["coins"] if c.get("pending") and "HOLD" not in c["pending"]]
print("publishing:", [c["id"] for c in pub])

# 1) cutouts
for c in pub:
    cid, img = c["id"], c["photo"]
    src = Image.open(os.path.join(base, img + ".jpg")).convert("RGBA")
    cut = remove(src); bb = cut.getbbox()
    if bb: cut = cut.crop(bb)
    if cut.width > 1000:
        h = int(cut.height * 1000 / cut.width); cut = cut.resize((1000, h), Image.LANCZOS)
    cut.save(os.path.join(outdir, cid + ".png"), optimize=True)
    print("cut", cid, cut.size, flush=True)

# 2) coin JS lines
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
    f = ['id:%s' % js(c["id"]), 'img:%s' % js("photos/cutouts/%s.png" % c["id"]),
         'place:%s' % js(c["place"] if c.get("place") else c["placeKey"]),
         'found:%s' % js(c["dateFound"]), 'raw:%s' % js(c["dateFoundRaw"]),
         'dow:%s' % js(c["dayOfWeek"]), 'finders:[%s]' % ",".join(js(x) for x in c["finders"]),
         'say:%s' % js(c["say"])]
    if c.get("microSpot"): f.append('spot:%s' % js(c["microSpot"]))
    f.append(coins_arr(c))
    if c.get("familyMemory"): f.append('family:%s' % js(c["familyMemory"]))
    f.append('city:%s' % js(c["city"])); f.append('state:%s' % js(c["state"]))
    return " {" + ",".join(f) + "}"
coin_lines = [coin_line(c) for c in pub]

# 3) new PLACES (delmar-haynes & home already exist)
Y = "lat:35.98276,lng:-84.26210"
new_places = {
 "y12-9720-14": '{name:"Y-12 · Building 9720-14",where:"Y-12 Plant, Oak Ridge",status:"standing",'+Y+',story:"Building 9720-14 was one of the warehouses in Y-12\'s 9720 storage complex — the long row of one-story warehouse and container-storage buildings that handled materials inside the secured plant. Jack worked at Y-12 behind the fence; he found a nickel here in 1974. Y-12, in Bear Creek Valley at Oak Ridge, was built during WWII to enrich uranium for the first atomic bomb."}',
 "y12-9720-5": '{name:"Y-12 · Building 9720-5",where:"Y-12 Plant, Oak Ridge",status:"standing",'+Y+',story:"Building 9720-5 is the most storied of Y-12\'s warehouses: built in 1944 with the original Manhattan Project plant, it became — and remains — the complex\'s primary storage warehouse for highly-enriched uranium, and the shipping-and-receiving point for the nation\'s special nuclear material. Jack, who worked inside the fence, found three coins here between 1975 and 1980 — at the \\u2018Floor Carryall,\\u2019 the north dock, and on the warehouse floor."}',
 "y12-9720-8": '{name:"Y-12 · Building 9720-8",where:"Y-12 Plant, Oak Ridge",status:"standing",'+Y+',story:"Building 9720-8 was one of Y-12\'s original 9720-series warehouses — wooden, one-story storage buildings raised on huge concrete pads, the row begun in August 1944 with the Manhattan Project plant. Jack found a dime around back of it on October 29, 1974 — the day before his grandson Greg, who made this archive, was born."}',
 "y12-9720-16": '{name:"Y-12 · Building 9720-16",where:"Y-12 Plant, Oak Ridge",status:"standing",'+Y+',story:"Building 9720-16 was one of Y-12\'s 9720-series buildings — the plant\'s line of warehouses, container-storage units and tank stations, some dating to the 1944 build-out. Its exact role isn\'t in the public record. Jack found a 1958 nickel here in 1976."}',
 "steves-barbershop": '{name:"Steve\'s Barber Shop",where:"Fountain City (exact spot unknown)",status:"standing",lat:36.02819,lng:-83.92823,story:"Steve\'s Barber Shop stood somewhere in Fountain City; the family no longer remembers exactly where, and it isn\'t in any directory now. Jack found a penny outside it in 1999. This pin sits on the Fountain City stretch of North Broadway, where the neighborhood\'s barbershops have long clustered."}',
 "broadway-video-store": '{name:"Broadway Video Store",where:"Fountain City (heart, exact spot unknown)",status:"standing",lat:36.03203,lng:-83.93741,story:"The Broadway Video Store was a Fountain City video-rental shop on North Broadway — exactly where is no longer remembered. Jack found a 1966 penny here in 1989, back when renting a movie meant a trip to the store. This pin sits in the heart of Fountain City."}',
}

path = os.path.join(base, "papaw-coins", "coins-data.js")
txt = open(path).read()

place_lines = []
for k, v in new_places.items():
    assert ('"%s"' % k) not in txt, "place already present: " + k
    place_lines.append(' %s:%s' % (js(k), v))
coins_marker = txt.index("const COINS")
pclose = txt.index("\n};", 0, coins_marker)
psep = "" if txt[:pclose].rstrip().endswith(",") else ","
txt = txt[:pclose] + psep + "\n" + ",\n".join(place_lines) + txt[pclose:]

cclose = txt.rindex("\n];")
csep = "" if txt[:cclose].rstrip().endswith(",") else ","
txt = txt[:cclose] + csep + "\n" + ",\n".join(coin_lines) + txt[cclose:]

open(path, "w").write(txt)
print("inserted", len(coin_lines), "coins +", len(place_lines), "places")
