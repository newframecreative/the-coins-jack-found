import os, json, re
from rembg import remove
from PIL import Image

base = "/Users/gregoryadkins/Documents/Claude"
outdir = os.path.join(base, "papaw-coins", "photos", "cutouts")
data = json.load(open(os.path.join(base, "papaw-coins", "coins.json")))

# publish everything pending EXCEPT the held ones (HOLD in pending text)
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

# 3) new PLACES (only those not already in the file)
new_places = {
 "georgia-agrirama": '{name:"Georgia Agrirama",where:"Tifton, Georgia",status:"standing",lat:31.46439,lng:-83.53507,story:"The Georgia Agrirama — the state\'s official agricultural museum — is a 95-acre open-air living-history village in Tifton, off I-75 in deep South Georgia. Opened for the 1976 Bicentennial, it gathered up old farmhouses, a gristmill, a country store and a working steam railroad to recreate an 1870s–90s farm town, staffed in period dress. (It survives today as the Georgia Museum of Agriculture.) Jack found three pennies on a 1993 visit."}',
 "sandy-first-apartment": '{name:"Sandy\'s First Apartment",where:"Cedar Lane, Fountain City",status:"standing",lat:36.01880,lng:-83.96412,story:"Sandy — Jack and Chris\'s daughter — had her very first apartment here, in a complex on Cedar Lane just a minute from the family home on Paula Drive: down Paula, right on Cedar, before you reach Merchant Drive. Jack found a penny out front in 1971."}',
 "sandy-new-home": '{name:"Sandy\'s New Home",where:"Near Nubbin Ridge & Ebenezer, West Knoxville",status:"standing",lat:35.88649,lng:-84.06495,story:"A few years after her first apartment, Sandy moved to a house out in West Knoxville, in a neighborhood near the corner of Nubbin Ridge Road and Ebenezer Road. The exact address is lost to memory, so this pin sits near that corner. Jack turned up a 1982 penny in the kitchen closet in 1987."}',
 "sandy-street": '{name:"Sandy Street",where:"Off N Broadway, Fountain City",status:"standing",lat:36.03504,lng:-83.93286,story:"A find marked only \'Sandy Street,\' somewhere off North Broadway in Fountain City. The exact spot is unknown, so this pin sits by the Fountain City duck pond — the little lake and park that has anchored the neighborhood for generations. Jack found a quarter here in 2004."}',
 "oconnor-senior-center": '{name:"John T. O\'Connor Senior Center",where:"611 Winona St, Knoxville",status:"standing",lat:35.98083,lng:-83.91152,story:"Knoxville\'s first senior center, named for John T. O\'Connor, has welcomed older adults at its Winona Street building just off Broadway since 1978. Chris found coins here more than once in the 1990s."}',
 "casey-jones-village": '{name:"Casey Jones Village",where:"Jackson, Tennessee",status:"standing",lat:35.66048,lng:-88.85620,story:"Casey Jones Village is a roadside Tennessee landmark in Jackson, right off I-40 — built around the home and railroad museum of Casey Jones, the engineer of folk-song fame, with Brooks Shaw\'s Old Country Store and restaurant alongside. A classic stop on the long drive across the state. Chris found a penny in the lot in 1992."}',
 "clinton-highway": '{name:"Clinton Highway",where:"North Knoxville",status:"standing",lat:36.00048,lng:-83.96979,story:"Clinton Highway is the long commercial strip running northwest out of Knoxville — stores, lots and car dealers for miles. One of Jack\'s cards just says \'Clinton Highway,\' with no telling exactly where, so this pin sits along the corridor. He found a nickel somewhere on it in 1973."}',
}

path = os.path.join(base, "papaw-coins", "coins-data.js")
txt = open(path).read()

# insert places before the PLACES-closing "};" (first "};" before const COINS), leading comma
place_lines = []
for k, v in new_places.items():
    assert ('"%s"' % k) not in txt, "place already present: " + k
    place_lines.append(' %s:%s' % (js(k), v))
coins_marker = txt.index("const COINS")
pclose = txt.index("\n};", 0, coins_marker)   # newline before PLACES close
psep = "" if txt[:pclose].rstrip().endswith(",") else ","
txt = txt[:pclose] + psep + "\n" + ",\n".join(place_lines) + txt[pclose:]

# insert coins before COINS-closing "];"
cclose = txt.rindex("\n];")
csep = "" if txt[:cclose].rstrip().endswith(",") else ","
txt = txt[:cclose] + csep + "\n" + ",\n".join(coin_lines) + txt[cclose:]

open(path, "w").write(txt)
print("inserted", len(coin_lines), "coins +", len(place_lines), "places")
