import os, json, re
from rembg import remove
from PIL import Image

base = "/Users/gregoryadkins/Documents/Claude"
outdir = os.path.join(base, "papaw-coins", "photos", "cutouts")
data = json.load(open(os.path.join(base, "papaw-coins", "coins.json")))

pub = [c for c in data["coins"] if c.get("pending") and "HOLD" not in c["pending"]]
print("publishing:", [c["id"] for c in pub])
print("holding:", [c["id"] for c in data["coins"] if c.get("pending") and "HOLD" in c["pending"]])

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

# 3) new PLACES (homes already exist; these are the new ones)
new_places = {
 "gary-wedding": '{name:"Gary\'s Wedding — Holston Heights",where:"Holston Heights Dr, Holston Hills, Knoxville",status:"standing",lat:35.99468,lng:-83.85089,story:"On August 30, 1971, Gary — Jack and Chris\'s son, and the father of this archive\'s maker — got married, up at the top of the hill on Holston Heights Drive in the Holston Hills neighborhood of East Knoxville. After the wedding, Jack found a penny in the back of the old Lark, and kept it."}',
 "mildred-troutman": '{name:"Mildred Troutman\'s",where:"Fountain City (exact spot unknown)",status:"standing",lat:36.03203,lng:-83.93741,story:"Mildred Troutman lived somewhere in Fountain City; the family no longer remembers exactly where. Chris found a penny in her driveway in 1995. This pin sits at the heart of Fountain City, a stand-in for a house whose address is lost."}',
 "clinton-highway-market": '{name:"Clinton Highway Market",where:"Clinton Highway (across from Wallace\'s Fruit Market)",status:"standing",lat:36.00710,lng:-84.02930,story:"A market on Clinton Highway, across the street from the beloved Wallace\'s Fruit Market — the hilltop stand whose hand-spun peach ice cream Knoxvillians still talk about. Jack found a dime here in 1985. Wallace\'s exact address lives only in old paper directories now; this pin sits on the documented \\u2018hilltop\\u2019 stretch of Clinton Highway, out toward Powell."}',
 "ambers-restaurant": '{name:"Amber\'s Restaurant",where:"N. Broadway, Knoxville",status:"gone",lat:36.01663,lng:-83.92397,story:"Amber\'s Restaurant once stood on North Broadway, near where The Original Louis\' Drive-In — a Knoxville fixture since 1958 — still serves today. Amber\'s is long gone; Chris found a penny there in 1988. The pin sits by Louis\', the surviving landmark that locates it."}',
 "delmar-haynes": '{name:"Delmar Haynes Pontiac",where:"Airport Motor Mile, Alcoa",status:"gone",lat:35.82113,lng:-83.97851,story:"Delmar Haynes ran the first car dealership on the Airport Motor Mile beside McGhee Tyson Airport in Alcoa, just outside Maryville, from 1971 until the airport bought the land in 2009. In 1974, Jack was driving a loaner car from Haynes\'s lot when he found a penny inside it."}',
 "broadway-shopping-center": '{name:"Broadway Shopping Center",where:"N. Broadway, Knoxville",status:"standing",lat:36.02804,lng:-83.92705,story:"A shopping center off North Broadway in the Broadway Square area — these days right by The Chop House North. Chris found a penny in the lot in 1991."}',
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
