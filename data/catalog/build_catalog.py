#!/usr/bin/env python3
"""Atelier Nilaya catalogue builder.
Reads rates.json, generates products with prices CALCULATED from today's metal rates,
and writes products.json, products.csv, collections.json.
Re-run after changing rates.json to refresh every price:  python build_catalog.py
Weights, making % and stone values are market-typical ESTIMATES. Replace them with your real
inventory data (actual net weight, actual stone cost) before publishing a piece.
"""
import json, csv, hashlib, os, re, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "rates.json"), encoding="utf-8"))
RATE, STONE, GST = R["metal_rates_per_g"], R["stone_rates_inr_per_ct"], R["gst_pct"]

def frac(k): return int(hashlib.md5(k.encode()).hexdigest()[:8], 16) / 0xffffffff
def between(k, lo, hi, nd=2): return round(lo + frac(k) * (hi - lo), nd)
def slugify(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
def cyc(l, i): return l[i % len(l)]

METALS = {  # code: (label, purity, rate key, group, tone)
 "G22": ("22K Yellow Gold", "22K / 916", "gold_22k", "gold", "yellow"),
 "G22A": ("22K Antique Gold", "22K / 916", "gold_22k", "gold", "antique"),
 "G18Y": ("18K Yellow Gold", "18K / 750", "gold_18k", "gold", "yellow"),
 "G18W": ("18K White Gold", "18K / 750", "gold_18k", "gold", "white"),
 "G18R": ("18K Rose Gold", "18K / 750", "gold_18k", "gold", "rose"),
 "PT": ("950 Platinum", "Pt 950", "platinum_950", "platinum", "white"),
 "AG": ("925 Sterling Silver", "925", "silver_925", "silver", "white"),
}
DIA = {"melee", "dia_s", "dia_m", "dia_l"}
GEM = {"ruby", "emerald", "sapphire", "gem_semi"}
STONE_LABEL = {"melee": "Natural diamonds (melee)", "dia_s": "Natural diamonds (small)", "dia_m": "Natural diamond (centre)",
 "dia_l": "Natural diamond (large centre)", "polki": "Uncut polki diamonds", "blackdia": "Black diamonds", "ruby": "Natural ruby",
 "emerald": "Natural emerald", "sapphire": "Natural blue sapphire", "gem_semi": "Semi-precious gemstone", "onyx": "Black onyx"}

P = []
def add(code, form, name, metal, wt, mk, stones=(), styles=(), occ=(), gender="women", tags=(), pers=None, mto=False, ptype="fixed", comps=None):
    P.append(dict(code=code, form=form, name=name, metal=metal, wt=wt, mk=mk, stones=list(stones), styles=list(dict.fromkeys(styles)),
                  occ=list(occ), gender=gender, tags=list(tags), pers=pers, mto=mto, ptype=ptype, comps=comps))

TRAD = ["Lakshmi Coin", "Peacock", "Mango Paisley", "Lotus Bloom", "Nakashi Floral", "Vine & Leaf", "Gajra Floral", "Antique Filigree",
        "Royal Navratna", "Maharani Floral", "Kamal Petal", "Rani Paisley"]
MT = {"Lakshmi Coin": ["lakshmi"], "Peacock": ["peacock"], "Mango Paisley": ["south-indian", "floral"], "Lotus Bloom": ["floral", "lakshmi"],
      "Nakashi Floral": ["floral"], "Vine & Leaf": ["floral"], "Gajra Floral": ["floral"], "Antique Filigree": ["imperial"],
      "Royal Navratna": ["imperial"], "Maharani Floral": ["imperial", "floral"], "Kamal Petal": ["floral", "lakshmi"],
      "Rani Paisley": ["south-indian", "imperial"], "Kasu": ["south-indian", "lakshmi"], "Navratna Kasu": ["south-indian", "imperial"]}
TEMPLE_OK = {"Royal Navratna", "Maharani Floral", "Antique Filigree", "Lakshmi Coin", "Peacock", "Lotus Bloom", "Nakashi Floral", "Kamal Petal", "Mango Paisley", "Kasu", "Navratna Kasu", "Rani Paisley"}

def trad(code, form, suffix, metal, wt, mk, stones, styles, occ, motifs, temple=False, tags=(), gender="women"):
    for m in motifs:
        st = list(styles) + (["temple"] if temple and m in TEMPLE_OK else [])
        add(code, form, f"{m} {suffix}", metal, wt, mk, stones, st, occ, gender, MT.get(m, []) + list(tags))

KUNDAN = lambda a, b: [("flat", a, b, "Kundan stones")]
PEARL = lambda a, b: [("flat", a, b, "Cultured pearls")]
CZ = lambda a, b: [("flat", a, b, "Cubic zirconia")]
WYR = ["G18W", "G18Y", "G18R"]

# ---------------- NECKLACES ----------------
trad("NK", "choker_set", "Gold Choker Set", "G22", (30, 52), 13, [], ["traditional"], ["festive", "wedding"], TRAD[:8])
trad("NK", "choker_set", "Antique Choker Set", "G22A", (32, 58), 17, [], ["antique", "traditional"], ["wedding", "festive"], TRAD[2:10], temple=True)
trad("NK", "choker_set", "Kundan Choker Set", "G22", (28, 50), 16, KUNDAN(18000, 32000), ["kundan", "traditional"], ["wedding", "festive", "party-wear"], TRAD[1:9])
trad("NK", "choker_set", "Polki Choker Set", "G22", (35, 60), 16, [("polki", 3, 6)], ["polki", "traditional"], ["wedding", "festive"], TRAD[3:11])
for m in ["Floral Cluster", "Cascade", "Infinity Bloom", "Marquise Leaf", "Starburst", "Halo Drop", "Ribbon Vine", "Petal Cascade"]:
    add("NK", "choker_set", f"{m} Diamond Choker Set", "G18W", (20, 34), 15, [("melee", 2.2, 4.5)], ["contemporary", "statement"], ["engagement", "wedding", "party-wear"])
for m in ["Cultured Pearl", "Layered Pearl", "Seed Pearl", "Baroque Pearl", "Pearl & Kundan", "Pearl & Polki", "Pearl Cascade", "Pearl Vine"]:
    add("NK", "choker_set", f"{m} Choker Set", "G22", (22, 40), 14, PEARL(22000, 48000), ["pearl", "traditional"], ["wedding", "festive", "party-wear"])
trad("NK", "long", "Gold Rani Haar", "G22", (45, 95), 12, [], ["traditional"], ["wedding", "festive"], TRAD[:8])
trad("NK", "long", "Temple Long Haar", "G22A", (50, 110), 18, [], ["temple", "antique", "traditional"], ["festive", "wedding"],
     ["Lakshmi Coin", "Peacock", "Kamal Petal", "Nakashi Floral", "Mango Paisley", "Kasu", "Lotus Bloom", "Navratna Kasu"], tags=["south-indian"])
trad("NK", "long", "Polki Long Haar", "G22", (40, 80), 16, [("polki", 5, 9)], ["polki", "traditional"], ["wedding"], TRAD[4:10])
trad("NK", "long", "Kundan Long Haar", "G22", (38, 70), 16, KUNDAN(24000, 45000), ["kundan", "traditional"], ["wedding", "festive"], TRAD[5:11])
for m in ["Single-Line Pearl Mala", "Triple-Line Pearl Mala", "Pearl & Gold Bead Mala", "Pearl Rani Haar", "Five-Line Pearl Mala"]:
    add("NK", "long", m, "G22", (30, 60), 12, PEARL(30000, 90000), ["pearl", "traditional"], ["festive", "wedding"])
for m in ["Rivière", "Floral Cascade", "Leaf Drop", "Marquise Drop", "Starlight", "Bar Cascade"]:
    add("NK", "long", f"{m} Diamond Long Necklace", "G18W", (14, 26), 15, [("melee", 3, 6.5)], ["contemporary", "statement"], ["party-wear", "wedding"])
for g in ["Emerald", "Ruby", "Blue Sapphire"]:
    add("NK", "long", f"{g} Drop Long Haar", "G22", (35, 65), 14, [(g.split()[-1].lower(), 6, 12)], ["traditional"], ["wedding", "festive"])
add("NK", "long", "Navratna Long Haar", "G22", (40, 70), 15, [("ruby", 2, 4), ("emerald", 2, 4), ("sapphire", 2, 4)], ["traditional"], ["wedding", "festive"], tags=["imperial"])
for m in ["Om", "Floral", "Peacock Feather", "Evil Eye", "Lotus", "Heart", "Leaf", "Tree of Life", "Sun Motif", "Coin"]:
    add("NK", "pendant", f"{m} Pendant with Chain", "G22", (4, 9), 12, [], ["minimal", "traditional"], ["daily-wear", "gifting"])
for i, m in enumerate(["Solitaire Bezel", "Y-Drop", "Halo", "Heart", "Infinity", "Floral", "Evil Eye", "Bar", "Teardrop", "Marquise Cluster", "Round Cluster", "Leaf"]):
    big = m in ("Solitaire Bezel", "Y-Drop")
    add("NK", "pendant", f"{m} Diamond Pendant", cyc(WYR, i), (3, 6), 15, [("dia_m", 0.4, 1.1)] if big else [("dia_s", 0.12, 0.55)],
        ["minimal", "contemporary"] + (["solitaire"] if big else []), ["gifting", "daily-wear", "engagement"])
for m in ["Solitaire Bezel", "Heart", "Infinity", "Evil Eye", "Bar", "Halo", "Teardrop", "Floral"]:
    add("NK", "pendant", f"Platinum {m} Diamond Pendant with Chain", "PT", (4, 9), 18, [("dia_s", 0.1, 0.4)], ["minimal", "contemporary"] + (["solitaire"] if "Solitaire" in m else []), ["gifting", "daily-wear"])
for m in ["Rope", "Box", "Cable", "Curb", "Wheat", "Snake"]:
    add("NK", "chain", f"Platinum {m} Chain", "PT", (8, 18), 14, [], ["minimal"], ["daily-wear", "gifting"])
for m in ["Lotus", "Evil Eye", "Heart", "Infinity", "Moon & Star", "Leaf", "Peacock", "Initial Bar", "Tree of Life", "Butterfly"]:
    add("NK", "pendant", f"Sterling Silver {m} Pendant with Chain", "AG", (4, 12), 25, CZ(500, 1800), ["minimal"], ["daily-wear", "gifting"])
for m in ["Rope", "Box", "Cable", "Curb", "Snake", "Figaro"]:
    add("NK", "chain", f"Sterling Silver {m} Chain", "AG", (8, 24), 22, [], ["minimal"], ["daily-wear", "gifting"])
for g in ["Emerald", "Ruby", "Blue Sapphire"]:
    for s in ["Halo", "Drop"]:
        add("NK", "pendant", f"{g} {s} Pendant with Chain", "G18Y", (3.5, 7), 16, [(g.split()[-1].lower(), 0.6, 1.8), ("melee", 0.1, 0.3)], ["contemporary", "minimal"], ["gifting", "party-wear"])
for m in ["Single Pearl Drop", "Pearl & Diamond", "Pearl Floral", "Pearl Bar", "Twin Pearl"]:
    add("NK", "pendant", f"{m} Pendant with Chain", "G18Y", (3, 6), 14, PEARL(3000, 9000), ["pearl", "minimal"], ["daily-wear", "gifting"])
for m, t in [("Goddess Lakshmi", ["lakshmi"]), ("Lord Ganesha", []), ("Peacock Nakashi", ["peacock"]), ("Krishna with Flute", []), ("Lotus Kamal", ["floral", "lakshmi"]),
             ("Shankh & Chakra", []), ("Tirupati Balaji", ["south-indian"]), ("Radha Krishna", []), ("Kamakshi", ["south-indian"]), ("Meenakshi", ["south-indian"])]:
    add("TP", "pendant", f"{m} Temple Pendant", "G22A", (8, 22), 17, [], ["temple", "antique", "traditional"], ["festive", "daily-wear", "gifting"], tags=t)
for m in ["Lakshmi Coin", "Peacock", "Kamal Petal", "Nakashi Floral", "Mango Paisley", "Kasu"]:
    add("TP", "pendant", f"{m} Temple Pendant Set with Earrings", "G22A", (14, 30), 17, [], ["temple", "antique", "traditional"], ["festive", "wedding", "gifting"], tags=MT.get(m, []))
for m in ["Rope", "Box", "Singapore", "Cable", "Wheat", "Figaro", "Curb", "Byzantine"]:
    add("NK", "chain", f"{m} Gold Chain", "G22", (8, 24), 9, [], ["minimal", "traditional"], ["daily-wear", "gifting"])
for m in ["Geometric Collar", "Layered Bar", "Sculpted Leaf Collar", "Cascade Bib", "Wave Collar", "Orbit Collar"]:
    add("NK", "statement", f"{m} Statement Necklace", cyc(["G18Y", "G22"], len(m)), (18, 38), 14, [], ["contemporary", "statement"], ["party-wear", "gifting"])
for m in ["Cluster Bib", "Floral Bib"]:
    add("NK", "statement", f"{m} Diamond Statement Necklace", "G18W", (22, 40), 15, [("melee", 2, 4)], ["contemporary", "statement"], ["party-wear", "wedding"])
add("NK", "chain", "Rose Gold Cable Chain", "G18R", (6, 12), 12, [], ["minimal"], ["daily-wear", "gifting"])
add("NK", "chain", "White Gold Box Chain", "G18W", (6, 12), 12, [], ["minimal"], ["daily-wear", "gifting"])

# ---------------- EARRINGS ----------------
J = ["Classic Dome", "Peacock", "Lotus Bell", "Floral Bell", "Filigree Dome", "Mango", "Lakshmi Coin", "Kamal", "Nakashi Floral", "Maharani"]
JT = lambda m: [t for k, t in MT.items() if k.split()[0] == m.split()[0]][:1][0] if any(k.split()[0] == m.split()[0] for k in MT) else []
for m in J[:8]: add("ER", "jhumka", f"{m} Gold Jhumka", "G22", (7, 18), 13, [], ["traditional"], ["festive", "everyday"], tags=JT(m))
for m in J[:8]: add("ER", "jhumka", f"{m} Antique Jhumka", "G22A", (9, 20), 17, [], ["antique", "temple", "traditional"], ["festive", "bridal"], tags=JT(m))
for m in J[:8]: add("ER", "jhumka", f"{m} Kundan Jhumka", "G22", (8, 16), 16, KUNDAN(6000, 14000), ["kundan", "traditional"], ["bridal", "festive", "party-wear"], tags=JT(m))
for m in J[:7]: add("ER", "jhumka", f"{m} Polki Jhumka", "G22", (9, 18), 16, [("polki", 1.5, 3.5)], ["polki", "traditional"], ["bridal", "festive"], tags=JT(m))
for m in ["Classic Dome", "Floral Bell", "Filigree Dome", "Lotus Bell", "Maharani"]:
    add("ER", "jhumka", f"{m} Pearl Drop Jhumka", "G22", (7, 14), 14, PEARL(5000, 16000), ["pearl", "traditional"], ["festive", "party-wear", "bridal"])
for m in ["Floral", "Round Bead", "Peacock Feather", "Leaf", "Star", "Flower Petal", "Knot", "Sunburst"]:
    add("ER", "stud", f"{m} Gold Stud Earrings", "G22", (2, 5), 11, [], ["minimal", "traditional"], ["everyday", "gifting"])
for i, m in enumerate(["Round Solitaire", "Princess-Cut Solitaire", "Halo", "Cluster", "Flower", "Square Bezel", "Pear Halo", "Starburst", "Infinity"]):
    sol = "Solitaire" in m
    add("ER", "stud", f"{m} Diamond Stud Earrings", cyc(WYR, i), (1.8, 4), 15, [("dia_m", 0.4, 0.9)] if sol else [("dia_s", 0.2, 0.7)],
        ["minimal"] + (["solitaire"] if sol else []), ["everyday", "gifting", "party-wear"] + (["bridal"] if "Halo" in m else []))
for m in ["Round Solitaire", "Halo", "Cluster", "Bezel", "Flower"]:
    add("ER", "stud", f"Platinum {m} Diamond Stud Earrings", "PT", (2.5, 5), 18, [("dia_s", 0.2, 0.6)], ["minimal", "contemporary"] + (["solitaire"] if "Solitaire" in m else []), ["everyday", "gifting", "party-wear"])
for m in ["Floral", "Round CZ", "Peacock", "Heart", "Moon & Star", "Butterfly", "Leaf", "Flower CZ"]:
    add("ER", "stud", f"Sterling Silver {m} Stud Earrings", "AG", (2, 5), 28, CZ(300, 900), ["minimal"], ["everyday", "gifting"])
for g in ["Ruby", "Emerald", "Blue Sapphire"]:
    add("ER", "stud", f"{g} Halo Stud Earrings", "G18Y", (2.5, 4.5), 15, [(g.split()[-1].lower(), 0.5, 1.2), ("melee", 0.1, 0.3)], ["contemporary", "minimal"], ["everyday", "party-wear", "gifting"])
for m in ["Classic Round", "Twisted Rope", "Textured", "Hammered", "Bali", "Flat Band"]:
    add("ER", "hoop", f"{m} Gold Hoops", "G22", (4, 10), 11, [], ["minimal", "contemporary"], ["everyday", "gifting", "party-wear"])
for i, m in enumerate(["Pavé", "Huggie", "Half-Eternity", "Twisted Pavé", "Mini Pavé", "Marquise Pavé"]):
    add("ER", "hoop", f"{m} Diamond Hoops", cyc(WYR, i), (3, 7), 16, [("melee", 0.6, 1.4)], ["contemporary", "statement"], ["party-wear", "gifting", "everyday"])
for m in ["Classic", "Twisted", "Chunky", "Mini Huggie", "Textured"]:
    add("ER", "hoop", f"Sterling Silver {m} Hoops", "AG", (3, 9), 26, [], ["minimal", "contemporary"], ["everyday", "gifting"])
for m in ["Classic", "Twisted", "Huggie", "Pavé Huggie", "Mini"]:
    add("ER", "hoop", f"Platinum {m} Hoops", "PT", (4, 9), 18, [("melee", 0.3, 0.8)] if "Pav" in m else [], ["minimal", "contemporary"], ["everyday", "gifting"])
for m, st in [("Classic", ["traditional"]), ("Floral", ["traditional"]), ("Peacock", ["traditional"]), ("Filigree", ["traditional"]), ("Lotus", ["traditional"]), ("Royal", ["traditional"])]:
    add("ER", "chandbali", f"{m} Gold Chandbali", "G22", (10, 22), 14, [], st, ["festive", "bridal"])
for m in ["Classic", "Floral", "Peacock", "Lotus", "Royal", "Crescent"]:
    add("ER", "chandbali", f"{m} Kundan Chandbali", "G22", (10, 20), 16, KUNDAN(8000, 18000), ["kundan", "traditional"], ["bridal", "party-wear", "festive"])
for m in ["Classic", "Floral", "Peacock", "Lotus", "Royal"]:
    add("ER", "chandbali", f"{m} Polki Chandbali", "G22", (11, 22), 16, [("polki", 2, 4.5)], ["polki", "traditional"], ["bridal", "festive"])
for m in ["Classic", "Peacock", "Lotus", "Filigree"]:
    add("ER", "chandbali", f"{m} Antique Chandbali", "G22A", (12, 24), 17, [], ["antique", "temple", "traditional"], ["bridal", "festive"])
for m in ["Classic", "Pearl Fringe", "Floral", "Crescent"]:
    add("ER", "chandbali", f"{m} Pearl Chandbali", "G22", (9, 18), 14, PEARL(8000, 22000), ["pearl", "traditional"], ["bridal", "party-wear"])
for m in ["Floral", "Marquise", "Starburst", "Crescent"]:
    add("ER", "chandbali", f"{m} Diamond Chandbali", "G18W", (7, 14), 15, [("melee", 1.2, 2.6)], ["contemporary", "statement"], ["party-wear", "bridal"])
for i, m in enumerate(["Teardrop", "Marquise", "Cascade", "Bar", "Pear Halo", "Floral Cluster", "Starlight"]):
    add("ER", "drop", f"{m} Diamond Drop Earrings", cyc(WYR, i), (3, 8), 15, [("melee", 0.6, 2.0)], ["contemporary", "minimal"], ["party-wear", "bridal", "gifting"])
for g in ["Emerald", "Ruby", "Blue Sapphire"]:
    add("ER", "drop", f"{g} Drop Earrings", "G22", (5, 10), 15, [(g.split()[-1].lower(), 2, 5)], ["traditional", "contemporary"], ["festive", "party-wear", "bridal"])
    add("ER", "drop", f"{g} & Diamond Drop Earrings", "G18Y", (5, 10), 15, [(g.split()[-1].lower(), 1.5, 3.5), ("melee", 0.3, 0.8)], ["contemporary", "statement"], ["party-wear", "bridal", "gifting"])
for m in ["Single Pearl", "Pearl & Gold Bead", "Pearl Cluster", "Pearl & Diamond", "Baroque Pearl"]:
    add("ER", "drop", f"{m} Drop Earrings", cyc(["G18Y", "G22"], len(m)), (3, 8), 14, PEARL(3000, 12000), ["pearl", "minimal"], ["everyday", "party-wear", "gifting"])
for m in ["Leaf", "Teardrop", "Floral", "Geometric"]:
    add("ER", "drop", f"{m} Gold Drop Earrings", "G22", (4, 9), 12, [], ["minimal", "contemporary"], ["everyday", "gifting"])
for m in ["Solitaire", "Bar", "Teardrop", "Marquise", "Halo"]:
    add("ER", "drop", f"Platinum {m} Drop Earrings", "PT", (3, 6), 18, [("dia_s", 0.2, 0.7)], ["minimal", "contemporary"] + (["solitaire"] if m == "Solitaire" else []), ["party-wear", "gifting"])
for m in ["Leaf", "Teardrop", "Moon", "Floral", "Dangle Bead"]:
    add("ER", "drop", f"Sterling Silver {m} Drop Earrings", "AG", (3, 8), 26, CZ(300, 900), ["minimal"], ["everyday", "gifting"])
for m in ["Lakshmi Coin", "Peacock", "Kamal Petal", "Nakashi Floral", "Mango Paisley", "Lotus Bloom"]:
    add("ER", "drop", f"{m} Temple Earrings", "G22A", (6, 14), 17, [], ["temple", "antique", "traditional"], ["festive", "bridal"], tags=MT.get(m, []))

# ---------------- RINGS ----------------
ENG_M = ["PT", "G18W", "G18R", "G18Y"]
for i, shape in enumerate(["Round", "Oval", "Cushion", "Pear", "Emerald-Cut", "Princess-Cut", "Marquise", "Radiant"]):
    for j, setting in enumerate(["Solitaire", "Halo", "Three-Stone", "Pavé Band"]):
        mc = cyc(ENG_M, i + j)
        st = [("dia_m", 0.3, 1.2)] + ([] if setting == "Solitaire" else [("melee", 0.08, 0.3)])
        add("RG", "engagement", f"{shape} {setting} Engagement Ring in {METALS[mc][0]}", mc, (3.6, 6.2) if mc == "PT" else (2.6, 4.8), 20 if mc == "PT" else 16, st,
            ["solitaire", "minimal"] if setting in ("Solitaire", "Pavé Band") else ["statement"], ["engagement"])
BAND = ["Classic Plain", "Milgrain Edge", "Twisted Rope", "Channel-Set Diamond", "Half-Eternity Diamond", "Full-Eternity Diamond", "Pavé Curve", "Knife-Edge", "Matte Finish", "Stackable Thin", "Wave Contour", "Diamond-Accent Court"]
for i, m in enumerate(BAND):
    for k in range(2):
        mc = cyc(["G18Y", "PT", "G18W", "G18R", "G22"], i * 2 + k)
        d = "Diamond" in m or "Pav" in m
        add("RG", "band", f"{m} Wedding Band in {METALS[mc][0]}", mc, (3, 6) if mc == "PT" else (2, 5.5), 20 if mc == "PT" else 14,
            [("melee", 0.1, 0.5)] if d else [], ["minimal"] + (["traditional"] if mc == "G22" else []), ["wedding"])
CP = ["Classic Plain", "Milgrain", "Twisted Rope", "Diamond-Accent", "Matte", "Contour", "Beveled Edge", "Hammered"]
for i, m in enumerate(CP):
    for k in range(3):
        mc = cyc(["PT", "G18Y", "G22", "G18R"], i + k)
        add("RG", "couple", f"{m} Couple Band Set in {METALS[mc][0]}", mc, (9, 15) if mc == "PT" else (7, 13), 20 if mc == "PT" else 15,
            [("melee", 0.05, 0.3)] if "Diamond" in m else [], ["minimal"], ["wedding", "engagement"])
for m in ["Classic Plain", "Twisted Rope", "Cz Accent", "Hammered"]:
    add("RG", "couple", f"Sterling Silver {m} Couple Band Set", "AG", (8, 14), 30, CZ(300, 800) if "Cz" in m else [], ["minimal"], ["gifting"])
for m, extra in [("Floral Jaali", ["floral"]), ("Peacock", []), ("Lotus", ["floral"]), ("Mango", []), ("Lakshmi Coin", []), ("Filigree", []), ("Nakashi", ["floral"]), ("Bead & Wire", []), ("Plain Dome", [])]:
    add("RG", "ring", f"{m} Gold Ring", "G22", (3.5, 8), 12, [], ["traditional"] + extra, [])
add("RG", "ring", "Navratna Gold Ring", "G22", (4, 8), 13, [("ruby", 0.3, 0.6), ("emerald", 0.3, 0.6), ("sapphire", 0.3, 0.6)], ["traditional", "gemstone"], [])
add("RG", "ring", "Kundan Floral Gold Ring", "G22", (4, 8), 14, KUNDAN(5000, 11000), ["traditional", "floral"], [])
for i, m in enumerate(["Twisted Knot", "Leaf Wrap", "Crossover", "Bypass", "Textured Stack", "Wave Stack"]):
    add("RG", "ring", f"{m} Gold Ring in 18K", cyc(["G18Y", "G18R"], i), (2.5, 5), 14, [], ["minimal"] + (["floral"] if "Leaf" in m else []), [])
for m in ["Plain", "Milgrain", "Twisted", "Textured", "Hammered", "Beaded"]:
    add("RG", "ring", f"Slim {m} Gold Band", "G22", (1.4, 2.2), 11, [], ["minimal"], [])
for i, m in enumerate(["Floral", "Bar", "Heart", "Infinity", "Evil Eye", "Leaf", "Crown", "Knot", "Star", "Wave", "Sunburst", "Trinity"]):
    add("RG", "ring", f"{m} Diamond Ring", cyc(WYR, i), (1.6, 3.2), 15, [("dia_s", 0.06, 0.25)], ["minimal"] + (["floral"] if m in ("Floral", "Leaf") else []), [])
for i, m in enumerate(["Cluster Cocktail", "Marquise Cluster", "Cocktail Halo", "Wide Pavé Band", "Cigar Band Pavé", "Floral Cluster Cocktail"]):
    add("RG", "ring", f"{m} Diamond Statement Ring", cyc(WYR, i), (4, 7), 15, [("melee", 0.8, 1.8)], ["statement"] + (["floral"] if "Floral" in m else []), [])
for g in ["Emerald", "Ruby", "Blue Sapphire"]:
    add("RG", "cocktail", f"{g} Halo Cocktail Ring", "G18Y", (4, 7), 15, [(g.split()[-1].lower(), 1.5, 3.5), ("melee", 0.2, 0.6)], ["statement", "gemstone"], [])
    add("RG", "cocktail", f"{g} Cluster Cocktail Ring in 22K Gold", "G22", (5, 9), 14, [(g.split()[-1].lower(), 1.2, 3)], ["statement", "gemstone", "traditional"], [])
for g in ["Amethyst", "Citrine", "Blue Topaz", "Garnet", "Peridot", "Moonstone", "Turquoise"]:
    add("RG", "cocktail", f"{g} Cocktail Ring in 18K Gold", cyc(["G18Y", "G18R"], len(g)), (4, 7), 15, [("gem_semi", 3, 8)], ["statement", "gemstone"], [])
    add("RG", "cocktail", f"{g} Cocktail Ring in Sterling Silver", "AG", (4, 8), 28, [("gem_semi", 3, 8)], ["statement", "gemstone"], [])
add("RG", "cocktail", "Floral Ruby Cocktail Ring in 22K Gold", "G22", (5, 9), 14, [("ruby", 1.2, 2.5)], ["statement", "gemstone", "floral"], [])
add("RG", "cocktail", "Floral Emerald Cocktail Ring in 22K Gold", "G22", (5, 9), 14, [("emerald", 1.5, 3)], ["statement", "gemstone", "floral"], [])
for m in ["Solitaire CZ", "Stackable Band", "Floral CZ", "Adjustable Leaf", "Twisted Rope Band", "Infinity", "Heart CZ", "Evil Eye", "Moonstone Bezel", "Eternity CZ", "Crown", "Knot",
          "Open Wrap", "Butterfly", "Lotus", "Peacock", "Beaded Band", "Hammered Band", "Sunburst CZ", "Trinity", "Wave Band", "Bar"]:
    add("RG", "ring", f"Sterling Silver {m} Ring", "AG", (2.5, 7), 30, CZ(300, 1200) if "CZ" in m or "Cz" in m else [], ["minimal"] + (["floral"] if any(w in m for w in ("Floral", "Lotus", "Butterfly")) else []), [])
SIG = ["Classic Round Signet", "Oval Signet", "Cushion Signet", "Engraved Crest Signet", "Heritage Seal Signet", "Octagon Signet", "Rectangle Signet", "Hammered Signet"]
for i, s in enumerate(SIG):
    for k, mc in enumerate(["G22", "G22A"]):
        add("RG", "mens_ring", f"{s} Ring in {METALS[mc][0]}", mc, (9, 22), 11 if mc == "G22" else 14, [], ["traditional"], [], "men", ["signet"], pers={"monogram": (i + k) % 2 == 0, "engraving": True})
    add("RG", "mens_ring", f"{s} Ring in {METALS['G18Y'][0]}" if i % 2 == 0 else f"{s} Ring in {METALS['PT'][0]}", "G18Y" if i % 2 == 0 else "PT", (8, 18), 14 if i % 2 == 0 else 20, [], ["minimal"], [], "men", ["signet"], pers={"monogram": True, "engraving": True})
for i, m in enumerate(["Black Onyx Signet", "Black Onyx Bezel", "Onyx Square", "Onyx Oval"]):
    for mc in ["G22", "PT"]:
        add("RG", "mens_ring", f"{m} Ring in {METALS[mc][0]}", mc, (8, 18), 11 if mc == "G22" else 20, [("onyx", 4, 9)], ["statement"], [], "men", ["signet", "onyx"], pers={"monogram": mc == "G22", "engraving": True})
for m in ["Round Solitaire", "Bezel Solitaire", "Square Solitaire"]:
    for mc in ["PT", "G18Y"]:
        add("RG", "mens_ring", f"Men's {m} Ring in {METALS[mc][0]}", mc, (7, 14), 20 if mc == "PT" else 15, [("dia_m", 0.3, 0.9)], ["solitaire"], [], "men", ["solitaire"])
for m in ["Black Diamond Solitaire", "Black Diamond Signet"]:
    for mc in ["PT", "G22"]:
        add("RG", "mens_ring", f"Men's {m} Ring in {METALS[mc][0]}", mc, (8, 16), 20 if mc == "PT" else 13, [("blackdia", 0.3, 0.8)], ["solitaire" if "Solitaire" in m else "statement"], [], "men", ["signet" if "Signet" in m else "solitaire", "black-diamond"])
for m in ["Brushed Comfort-Fit", "Wide Matte", "Beveled Edge", "Textured Carbon"]:
    for mc in ["PT", "G22"]:
        add("RG", "band", f"Men's {m} Wedding Band in {METALS[mc][0]}", mc, (6, 12), 20 if mc == "PT" else 11, [], ["minimal"], ["wedding"], "men", ["band"])
BR_R = [("Kundan Floral Bridal Ring", "G22", KUNDAN(6000, 12000), ["kundan", "traditional", "floral"]), ("Polki Cocktail Bridal Ring", "G22", [("polki", 1.2, 2.4)], ["polki", "traditional", "statement"]),
        ("Temple Lotus Bridal Ring", "G22A", [], ["temple", "antique", "traditional", "floral"]), ("Diamond Halo Bridal Ring", "G18W", [("dia_s", 0.3, 0.7), ("melee", 0.1, 0.3)], ["statement"]),
        ("Pearl & Polki Bridal Ring", "G22", [("polki", 0.8, 1.6), ("flat", 3000, 8000, "Cultured pearls")], ["polki", "pearl", "traditional"]), ("Antique Peacock Bridal Ring", "G22A", [], ["antique", "traditional"]),
        ("Ruby Cocktail Bridal Ring", "G22", [("ruby", 1.5, 3)], ["statement", "gemstone", "traditional"]), ("Emerald Cocktail Bridal Ring", "G22", [("emerald", 1.5, 3)], ["statement", "gemstone", "traditional"]),
        ("Maharani Floral Bridal Ring", "G22", KUNDAN(7000, 14000), ["kundan", "traditional", "floral"]), ("Cluster Diamond Bridal Ring", "G18Y", [("melee", 0.8, 1.6)], ["statement"]),
        ("Navratna Bridal Ring", "G22", [("ruby", 0.3, 0.6), ("emerald", 0.3, 0.6), ("sapphire", 0.3, 0.6)], ["traditional", "gemstone"]), ("Marquise Diamond Bridal Ring", "G18W", [("dia_s", 0.3, 0.7)], ["statement"])]
for n, mc, stn, st in BR_R:
    add("BR", "bridal_ring", n, mc, (4, 9), 15, stn, st, ["wedding"], tags=["bridal-ring"])

# ---------------- BANGLES ----------------
BG_G = ["Plain Polished", "Machine-Cut", "Faceted Diamond-Cut", "Rope Twist", "Nakashi Floral", "Filigree Jaali", "Lakshmi Coin", "Peacock Motif", "Mango Pattern", "Lotus Petal", "Beaded Edge", "Twisted Wire"]
for m in BG_G: add("BG", "bangle", f"{m} Gold Bangle Pair", "G22", (22, 44), 10, [], ["traditional"], ["festive"])
for m in BG_G[:10]: add("BG", "bangle", f"Lightweight {m} Daily Wear Bangles", "G22", (10, 18), 12, [], ["minimal", "traditional"], ["daily-wear", "gifting"])
for m in ["Plain", "Twisted", "Beaded", "Hammered", "Textured", "Faceted"]: add("BG", "bangle", f"Slim {m} Gold Bangle", "G22", (2.6, 5), 12, [], ["minimal"], ["daily-wear", "gifting"])
for i, m in enumerate(["Geometric Cuff", "Wave Cuff", "Bar Link", "Open Twist Cuff", "Sculpted Cuff", "Mesh Link"]):
    add("BG", "bangle", f"{m} Designer Gold Bangle", cyc(["G18Y", "G22"], i), (14, 28), 14, [], ["designer", "contemporary"], ["party-wear", "gifting"])
for m, stn in [("Ruby Studded", [("ruby", 2, 4)]), ("Emerald Studded", [("emerald", 2, 4)]), ("Navratna Studded", [("ruby", 1, 2), ("emerald", 1, 2), ("sapphire", 1, 2)]),
               ("Kundan Studded", KUNDAN(14000, 26000)), ("Polki Studded", [("polki", 2, 4)]), ("CZ Studded", CZ(4000, 9000))]:
    add("BG", "bangle", f"{m} Gold Bangle Pair", "G22", (24, 40), 14, stn, ["stone-studded", "traditional"], ["festive", "wedding"])
for m in ["Floral Engraved", "Peacock Engraved", "Geometric Engraved", "Calligraphy Engraved", "Mandala Engraved", "Initial Engraved"]:
    add("BG", "bangle", f"{m} Gold Bangle", "G22", (12, 26), 13, [], ["engraved", "traditional"], ["gifting", "festive"], pers={"engraving": True} if "Initial" in m or "Calligraphy" in m else None)
for i, m in enumerate(["Pavé Open Cuff", "Tennis-Style", "Floral Cluster", "Half-Eternity", "Station Diamond", "Twist Pavé", "Marquise Pavé", "Starburst Pavé"]):
    mc = cyc(["G18W", "G18Y", "G18R", "PT"], i)
    add("BG", "bangle", f"{m} Diamond Bangle in {METALS[mc][0]}", mc, (10, 22), 20 if mc == "PT" else 15, [("melee", 1.2, 3.2)], ["contemporary", "stone-studded"], ["gifting", "festive"])
for m in ["Slim Polished", "Twisted", "Matte", "Beaded", "Hammered", "Knife-Edge"]:
    add("BG", "bangle", f"Platinum {m} Bangle", "PT", (6, 12), 20, [], ["minimal"], ["gifting", "daily-wear"])
for m in ["Plain Polished", "Twisted", "Antique Oxidised", "Kundan Stone", "Floral Engraved", "Peacock Oxidised", "Beaded", "Temple Oxidised"]:
    add("BG", "bangle", f"Sterling Silver {m} Bangle Pair", "AG", (28, 60), 18, KUNDAN(800, 2500) if "Kundan" in m else [],
        (["antique"] if "Antique" in m else []) + (["engraved"] if "Engraved" in m else []) + (["stone-studded"] if "Kundan" in m else []) + ["traditional"], ["daily-wear", "festive"])
for m in ["Antique Temple", "Peacock Oxidised", "Bridal Chooda-Style", "Rope Heavy", "Floral Jaali", "Lakshmi Coin"]:
    add("BG", "bangle", f"Sterling Silver {m} Bangle Pair (Heavy)", "AG", (80, 140), 16, [], ["antique", "traditional"] if "Antique" in m else ["traditional"], ["festive"])
for i, m in enumerate(TRAD[:5]): add("BG", "bridal_bangle", f"{m} Kundan Bridal Bangle Set", "G22", (48, 90), 15, KUNDAN(22000, 40000), ["kundan", "traditional"], ["wedding", "festive"], tags=MT.get(m, []))
for m in TRAD[5:9]: add("BG", "bridal_bangle", f"{m} Polki Bridal Bangle Set", "G22", (50, 92), 16, [("polki", 4, 7)], ["polki", "traditional"], ["wedding"], tags=MT.get(m, []))
for m in ["Lakshmi Coin", "Peacock", "Kamal Petal", "Nakashi Floral"]: add("BG", "bridal_bangle", f"{m} Temple Bridal Bangle Set", "G22A", (55, 95), 18, [], ["temple", "antique", "traditional"], ["wedding", "festive"], tags=MT.get(m, []))
for m in ["Floral Cluster", "Marquise Leaf", "Starburst"]: add("BG", "bridal_bangle", f"{m} Diamond Bridal Bangle Set", "G18W", (30, 50), 15, [("melee", 3, 6)], ["contemporary", "stone-studded"], ["wedding", "party-wear"])
for m in ["Classic Gold", "Filigree Gold", "Twisted Gold", "Faceted Gold"]: add("BG", "bridal_bangle", f"{m} Bridal Bangle Set", "G22", (50, 90), 11, [], ["traditional"], ["wedding", "festive"])
for m in ["Plain Polished", "Hammered", "Twisted Rope", "Nakashi Floral", "Peacock Motif", "Lakshmi Coin", "Geometric Engraved", "Beaded Edge"]:
    add("BG", "kada", f"{m} Gold Kada", "G22", (22, 48), 10, [], ["traditional"] + (["engraved"] if "Engraved" in m else []), ["gifting", "festive"], "unisex")
for m in ["Antique Temple", "Antique Peacock", "Antique Lakshmi", "Antique Floral"]:
    add("BG", "kada", f"{m} Gold Kada", "G22A", (28, 55), 16, [], ["antique", "temple", "traditional"], ["festive", "wedding"], "unisex", ["lakshmi"] if "Lakshmi" in m else [])
for m in ["Polished", "Brushed", "Twisted", "Hammered"]: add("BG", "kada", f"Platinum {m} Kada", "PT", (20, 40), 16, [], ["minimal"], ["gifting"], "unisex")
for m in ["Plain", "Oxidised Floral", "Rope", "Hammered", "Peacock Oxidised"]: add("BG", "kada", f"Sterling Silver {m} Kada", "AG", (35, 70), 20, [], ["antique"] if "Oxidised" in m else ["minimal"], ["gifting", "daily-wear"], "unisex")
for m in ["Lakshmi Coin", "Peacock", "Kamal Petal", "Nakashi Floral", "Mango Paisley", "Lotus Bloom", "Kasu", "Navratna Kasu"]:
    add("BG", "bangle", f"{m} Temple Bangle Pair", "G22A", (28, 55), 17, [], ["temple", "antique", "traditional"], ["festive", "wedding"], tags=MT.get(m, []))

# ---------------- BRIDAL: sets, tikka, nath ----------------
def sets(label, motifs, metal, wt, mk, stn, styles, tags=(), comps=("Necklace", "Earrings", "Maang Tikka"), temple=False):
    for m in motifs:
        st = list(styles) + (["temple"] if temple and m in TEMPLE_OK else [])
        add("BR", "bridal_set", f"{m} {label} Bridal Set", metal, wt, mk, stn, st, ["wedding"], tags=MT.get(m, []) + list(tags), comps=list(comps))
sets("Kundan", TRAD[:8], "G22", (90, 160), 15, KUNDAN(60000, 120000), ["kundan", "traditional"])
sets("Polki", TRAD[2:10], "G22", (100, 190), 16, [("polki", 10, 18)], ["polki", "traditional"])
TM = ["Lakshmi Coin", "Peacock", "Kamal Petal", "Nakashi Floral", "Mango Paisley", "Lotus Bloom", "Kasu", "Navratna Kasu"]
sets("Temple", TM, "G22A", (110, 210), 18, [], ["temple", "antique", "traditional"], comps=("Long Haar", "Choker", "Earrings"))
sets("South Indian Temple", TM, "G22A", (120, 220), 18, [], ["temple", "antique", "traditional"], tags=["south-indian"], comps=("Long Haar", "Choker", "Earrings", "Maang Tikka", "Bangles"))
for i, m in enumerate(TRAD[:6]): add("BR", "bridal_set", f"{m} Antique Bridal Set", "G22A", (95, 170), 17, [], ["antique", "traditional"] + (["temple"] if m in TEMPLE_OK and i % 2 == 0 else []), ["wedding"], tags=MT.get(m, []), comps=["Necklace", "Earrings", "Maang Tikka"])
DS = ["Floral Cascade", "Marquise Leaf", "Rivière", "Starburst", "Halo Bloom", "Ribbon Vine", "Petal Cascade", "Infinity Bloom"]
for m in DS:
    for c in (("Necklace", "Earrings"), ("Necklace", "Earrings", "Maang Tikka")):
        add("BR", "bridal_set", f"{m} Diamond Bridal Set" + (" with Maang Tikka" if len(c) == 3 else ""), "G18W", (45, 85), 15, [("melee", 6, 12)], ["contemporary", "statement"], ["wedding", "engagement", "party-wear"], comps=list(c))
sets("Traditional Gold", TRAD[:8], "G22", (100, 180), 12, [], ["traditional"])
for m in TRAD[:5]: add("BR", "tikka", f"{m} Kundan Maang Tikka", "G22", (6, 16), 16, KUNDAN(8000, 18000), ["kundan", "traditional"], ["wedding", "festive"], tags=MT.get(m, []))
for m in TRAD[:4]: add("BR", "tikka", f"{m} Polki Maang Tikka", "G22", (6, 16), 16, [("polki", 1.5, 3)], ["polki", "traditional"], ["wedding"], tags=MT.get(m, []))
for m in ["Lakshmi Coin", "Peacock", "Kamal Petal", "Nakashi Floral"]: add("BR", "tikka", f"{m} Temple Maang Tikka", "G22A", (6, 16), 18, [], ["temple", "antique", "traditional"], ["wedding", "festive"], tags=MT.get(m, []))
for m in ["Floral", "Marquise", "Starburst", "Halo"]: add("BR", "tikka", f"{m} Diamond Maang Tikka", "G18W", (5, 10), 15, [("melee", 0.8, 1.8)], ["contemporary"], ["wedding", "party-wear"])
for m in ["Pearl Drop", "Pearl Fringe", "Pearl & Kundan"]: add("BR", "tikka", f"{m} Maang Tikka", "G22", (6, 14), 14, PEARL(6000, 16000), ["pearl", "traditional"], ["wedding", "festive"])
for n, stn, st in [("Maharashtrian Pearl", PEARL(5000, 14000), ["pearl", "traditional"]), ("Kundan Floral", KUNDAN(5000, 11000), ["kundan", "traditional"]), ("Polki Peacock", [("polki", 0.8, 1.6)], ["polki", "traditional"]),
                   ("Temple Lakshmi", [], ["temple", "antique", "traditional"]), ("Diamond Floral", [("melee", 0.3, 0.7)], ["contemporary"]), ("Pearl & Polki", [("polki", 0.5, 1.0), ("flat", 3000, 8000, "Cultured pearls")], ["polki", "pearl", "traditional"]),
                   ("Antique Peacock", [], ["antique", "traditional"]), ("Classic Gold Hoop", [], ["traditional"]), ("Kundan Pearl Fringe", KUNDAN(5000, 10000) + PEARL(3000, 8000), ["kundan", "pearl", "traditional"]),
                   ("Royal Pearl Cluster", PEARL(8000, 20000), ["pearl", "traditional"]), ("Kamal Petal", [], ["traditional"]), ("Mango Paisley", [], ["traditional"]), ("Marquise Diamond", [("melee", 0.3, 0.7)], ["contemporary"]),
                   ("Lotus Kundan", KUNDAN(5000, 10000), ["kundan", "traditional"]), ("Filigree Gold", [], ["traditional"]), ("Ruby Drop", [("ruby", 0.5, 1)], ["traditional", "gemstone"])]:
    add("BR", "nath", f"{n} Nath", "G18W" if "Diamond" in n else "G22", (4, 12), 18, stn, st, ["wedding"])

# ---------------- DIAMOND bracelets ----------------
for i, m in enumerate(["Classic Tennis", "Station Diamond", "Bezel Station", "Floral Cluster", "Pavé Link", "Marquise Link", "Evil Eye Chain", "Heart Link", "Infinity Chain", "Mini Bar",
                       "Adjustable Solitaire Chain", "Starlight Chain", "Leaf Vine", "Pavé Cuff", "Bolo Slider", "Butterfly Chain", "Twisted Tennis", "Clover Chain"]):
    mc = cyc(["G18W", "G18Y", "G18R", "PT"], i)
    add("DM", "bracelet", f"{m} Diamond Bracelet in {METALS[mc][0]}", mc, (4, 11), 20 if mc == "PT" else 15, [("melee", 2, 4)] if "Tennis" in m else [("melee", 0.4, 1.6)],
        ["contemporary", "minimal"] + (["statement"] if "Tennis" in m or "Cuff" in m else []), ["gifting", "daily-wear", "party-wear"])

# ---------------- MEN'S ----------------
MK = ["Classic Polished", "Hammered", "Twisted Rope", "Engraved Crest", "Faceted", "Brushed Matte", "Wide Flat", "Bead Edge"]
for i, m in enumerate(MK):
    for mc in ["G22", "PT", "G22A"]:
        if mc == "PT" and i % 2: continue
        add("MN", "mens_kada", f"{m} Men's Kada in {METALS[mc][0]}", mc, (30, 60) if mc == "PT" else (32, 70), 16 if mc == "PT" else 10 if mc == "G22" else 14, [], ["traditional"], [], "men", pers={"monogram": "Engraved" in m, "engraving": True})
CH = ["Rope", "Franco", "Box", "Curb", "Figaro", "Byzantine", "Singapore", "Wheat", "Cable", "Snake", "Anchor", "Herringbone"]
for i, m in enumerate(CH):
    ln = cyc(["20-inch", "22-inch", "24-inch"], i)
    w = {"20-inch": (18, 32), "22-inch": (24, 44), "24-inch": (30, 56)}[ln]
    add("MN", "mens_chain", f"{m} Chain, {ln}, 22K Gold", "G22", w, 9, [], ["traditional"], [], "men")
for m in ["Curb", "Rope", "Franco", "Box"]:
    add("MN", "mens_chain", f"Platinum {m} Chain, 22-inch", "PT", (20, 36), 14, [], ["minimal"], [], "men")
for i, g in enumerate(["Black Onyx", "Tiger Eye", "Lapis Lazuli", "Ruby", "Emerald", "Blue Sapphire", "Garnet", "Carnelian", "Green Aventurine", "Amethyst"]):
    for mc in (["AG", "G22"] if i < 8 else ["AG"]):
        stn = [(g.split()[-1].lower(), 1, 2)] if g in ("Ruby", "Emerald", "Blue Sapphire") else ([("onyx", 4, 9)] if g == "Black Onyx" else [("gem_semi", 4, 9)])
        add("MN", "cufflinks", f"{g} Gemstone Cufflinks in {METALS[mc][0]}", mc, (8, 16) if mc == "AG" else (10, 18), 26 if mc == "AG" else 14, stn, ["statement"], [], "men",
            ["onyx"] if g == "Black Onyx" else [], pers={"monogram": mc == "AG", "engraving": True})
for m, stn in [("Kundan", KUNDAN(6000, 14000)), ("Pearl", PEARL(4000, 12000)), ("Polki", [("polki", 0.6, 1.4)]), ("Diamond", [("melee", 0.3, 0.8)]), ("Onyx", [("onyx", 3, 6)]),
               ("Ruby", [("ruby", 0.6, 1.2)]), ("Emerald", [("emerald", 0.6, 1.2)]), ("Antique Gold", []), ("Navratna", [("ruby", 0.2, 0.4), ("emerald", 0.2, 0.4), ("sapphire", 0.2, 0.4)]),
               ("Plain Gold Ball", []), ("Filigree", []), ("Peacock", [])]:
    add("MN", "kurta_buttons", f"{m} Kurta Button Set", "G22A" if "Antique" in m else "G22", (6, 14), 13, stn, ["traditional"], [], "men", ["onyx"] if m == "Onyx" else [])
for m, stn in [("Peacock", []), ("Lotus", []), ("Kundan Floral", KUNDAN(6000, 14000)), ("Pearl Cluster", PEARL(5000, 12000)), ("Diamond Bar", [("melee", 0.3, 0.8)]),
               ("Antique Crest", []), ("Onyx Crest", [("onyx", 3, 6)]), ("Navratna Sherwani", [("ruby", 0.3, 0.5), ("emerald", 0.3, 0.5), ("sapphire", 0.3, 0.5)])]:
    add("MN", "brooch", f"{m} Sherwani Brooch", "G22A" if "Antique" in m else "G22", (6, 14), 13, stn, ["traditional"], [], "men", ["onyx"] if "Onyx" in m else [])
for m in ["Black Diamond Signet Pendant", "Onyx Inlay Kada", "Black Diamond Cufflinks", "Onyx & Black Diamond Kurta Buttons", "Black Diamond Chain Pendant", "Black Diamond Band", "Onyx Bead Bracelet"]:
    add("MN", "mens_kada" if "Kada" in m or "Bracelet" in m else ("cufflinks" if "Cuff" in m else "kurta_buttons" if "Kurta" in m else "mens_chain"), m, "PT" if "Black Diamond" in m else "G22", (10, 40), 16, [("blackdia", 0.3, 0.9)] if "Black Diamond" in m else [("onyx", 6, 14)], ["statement"], [], "men", ["black-diamond", "onyx"])
add("MN", "mens_kada", "Monogram Engraved Kada in Antique Brushed Gold", "G22A", (35, 70), 14, [], ["traditional"], [], "men", pers={"monogram": True, "engraving": True})
add("MN", "mens_kada", "Monogram Signet Kada in 950 Platinum", "PT", (30, 60), 16, [], ["minimal"], [], "men", pers={"monogram": True, "engraving": True})

# ---------------- PERSONALISED (made to order) ----------------
PM = ["G18Y", "G18R", "G22", "AG", "G18W", "PT"]
def pers(code, form, names, wt, mk, key, extra=None, minc=16):
    n = 0
    for i, s in enumerate(names):
        for k in range(2):
            if n >= minc: break
            mc = cyc(PM, i * 2 + k)
            add(code, form, f"{s} in {METALS[mc][0]}", mc, wt, 30 if mc == "AG" else 20 if mc == "PT" else mk, [("melee", 0.05, 0.2)] if "Diamond" in s else [], ["minimal"], ["gifting", "daily-wear"],
                "unisex", [], pers=dict({key: True}, **(extra or {})), mto=True, ptype="starting_from")
            n += 1
pers("PS", "custom_name", ["Cursive Name Necklace", "Block Name Necklace", "Serif Name Necklace", "Lowercase Minimal Name Necklace", "Gujarati Script Name Necklace", "Devanagari Script Name Necklace", "Heart-Frame Name Necklace", "Bar Nameplate Necklace"], (3, 8), 18, "name_text", {"max_chars": 12})
pers("PS", "initial", ["Classic Serif Initial Pendant", "Block Initial Pendant", "Cursive Initial Pendant", "Diamond-Set Initial Pendant", "Heart Initial Pendant", "Bar Initial Pendant", "Tiny Initial Pendant", "Floral Wreath Initial Pendant"], (2, 5), 18, "initial_letter", {"letters": "A-Z"})
pers("PS", "pers_ring", ["Engraved Signet Ring", "Name Ring", "Birthstone Stack Ring", "Initial Signet Ring", "Engraved Band", "Roman Numeral Date Ring", "Coordinates Band", "Infinity Name Ring"], (3, 9), 14, "engraving", {"max_chars": 16})
pers("PS", "engraved_bracelet", ["Engraved ID Bracelet", "Engraved Cuff Bracelet", "Men's Engraved Kada", "Women's Engraved Kada", "Name Bar Bracelet", "Initial Charm Bracelet", "Engraved Baby Bracelet", "Engraved Link Bracelet"], (6, 40), 12, "engraving", {"max_chars": 20})
for i, m in enumerate(["Kundan", "Polki", "Temple", "Antique", "Diamond", "Pearl & Polki", "Navratna", "Traditional Gold"]):
    for k, t in enumerate(["Bespoke Bridal Set", "Bespoke Bridal Set with Family Gifts"]):
        add("PS", "custom_bridal", f"{m} {t}", "G18W" if m == "Diamond" else "G22A" if m in ("Temple", "Antique") else "G22", (90, 220), 16, [("melee", 6, 12)] if m == "Diamond" else [], ["traditional"], ["wedding"],
            "women", [], pers={"design_consultation": True, "reference_photos": True}, mto=True, ptype="starting_from", comps=["Necklace", "Earrings", "Maang Tikka"] + (["Gifts for family"] if k else []))
for i, m in enumerate(["Bespoke Solitaire Ring", "Bespoke Pendant", "Bespoke Earrings", "Bespoke Bangle", "Bespoke Necklace", "Bespoke Kada", "Bespoke Cufflinks", "Bespoke Bracelet"]):
    for k in range(2):
        mc = cyc(["G18Y", "G22", "PT", "G18W"], i + k)
        add("PS", "design_own", f"{m} in {METALS[mc][0]}", mc, (3, 30), 20 if mc == "PT" else 15, [], ["minimal"], ["gifting"], "unisex", [], pers={"design_consultation": True, "reference_photos": True}, mto=True, ptype="starting_from")

# ---------------- GIFT SETS ----------------
for i, m in enumerate(["Pendant & Stud Gift Set", "Chain & Pendant Gift Set", "Earrings & Pendant Gift Set", "Couple Pendant Gift Set", "Mother-Daughter Pendant Set", "Bracelet & Stud Gift Set", "Evil Eye Gift Set", "Initial Pendant & Earring Set"]):
    for k in range(2):
        mc = cyc(["G22", "AG", "G18Y", "G18R"], i + k)
        add("GF", "gift_set", f"{m} in {METALS[mc][0]}", mc, (6, 14), 30 if mc == "AG" else 15, [("dia_s", 0.1, 0.3)] if mc.startswith("G18") else [], ["minimal"], ["gifting"], "women", [], comps=["Gift box", "Authenticity card"])


# ---------------- COVERAGE TOP-UPS (keep every subcategory at its minimum) ----------------
trad("NK", "choker_set", "Kundan Choker Set", "G22", (28, 50), 16, KUNDAN(18000, 32000), ["kundan", "traditional"], ["wedding", "festive", "party-wear"], TRAD[9:12])
trad("NK", "choker_set", "Polki Choker Set", "G22", (35, 60), 16, [("polki", 3, 6)], ["polki", "traditional"], ["wedding", "festive"], ["Rani Paisley", "Lakshmi Coin", "Peacock"])
for m in ["Franco", "Figaro", "Byzantine"]:
    add("NK", "chain", f"Platinum {m} Chain", "PT", (8, 18), 14, [], ["minimal"], ["daily-wear", "gifting"])
for g in ["Emerald", "Ruby", "Blue Sapphire"]:
    add("NK", "choker_set", f"{g} Choker Set", "G22", (25, 45), 15, [(g.split()[-1].lower(), 6, 12)], ["traditional"], ["wedding", "festive"])
    add("NK", "statement", f"{g} Beaded Necklace", "G18Y", (14, 24), 14, [(g.split()[-1].lower(), 10, 20)], ["contemporary", "statement"], ["party-wear", "gifting"])
for m in ["Floral", "Round", "Leaf"]:
    add("ER", "stud", f"{m} Kundan Stud Earrings", "G22", (3, 6), 14, KUNDAN(2500, 6000), ["kundan", "traditional"], ["festive", "bridal"])
for m in ["Floral", "Round", "Peacock", "Lotus"]:
    add("ER", "stud", f"{m} Polki Stud Earrings", "G22", (3, 6), 15, [("polki", 0.6, 1.4)], ["polki", "traditional"], ["festive", "bridal"])
for m in ["Classic", "Halo", "Floral"]:
    add("ER", "stud", f"Cultured Pearl {m} Stud Earrings", "G18Y", (2, 4), 14, PEARL(2000, 7000), ["pearl", "minimal"], ["everyday", "gifting"])
for g in ["Ruby", "Emerald", "Blue Sapphire"]:
    add("ER", "jhumka", f"{g} Gold Jhumka", "G22", (8, 16), 15, [(g.split()[-1].lower(), 2, 5)], ["traditional"], ["festive", "bridal"])
add("ER", "chandbali", "Navratna Chandbali", "G22", (11, 22), 15, [("ruby", 1, 2), ("emerald", 1, 2), ("sapphire", 1, 2)], ["traditional"], ["festive", "bridal"])
for g in ["Amethyst", "Citrine", "Blue Topaz"]:
    add("ER", "hoop", f"{g} Gold Hoop Earrings", "G18Y", (4, 8), 14, [("gem_semi", 2, 6)], ["contemporary"], ["party-wear", "gifting"])
for i, m in enumerate(["Daisy", "Blossom", "Petal Wrap", "Rose Bud", "Marigold"]):
    add("RG", "ring", f"{m} Floral Ring in 18K Gold", cyc(["G18R", "G18Y"], i), (2.5, 4.5), 14, [], ["minimal", "floral"], [])
for i, m in enumerate(["Plain", "Milgrain", "Twisted", "Beaded", "Hammered", "Knife-Edge", "Mini Bar", "Mini Star", "Mini Heart", "Mini Leaf", "Wishbone", "Chevron", "Tiny Crown", "Tiny Knot"]):
    add("RG", "ring", f"{m} 18K Stackable Ring", cyc(["G18Y", "G18W", "G18R"], i), (1.2, 1.9), 14, [], ["minimal"], [])
for m in ["Slim Plain", "Slim Milgrain", "Slim Twisted", "Slim Beaded", "Slim Knife-Edge", "Slim Hammered"]:
    add("RG", "band", f"{m} Platinum Wedding Band", "PT", (2.6, 3.4), 20, [], ["minimal"], ["wedding"])
for m in ["Plain", "Twisted", "Beaded", "Hammered", "Oxidised", "Floral CZ", "Peacock", "Textured", "Rope", "Antique", "Leaf", "Wave"]:
    add("BG", "bangle", f"Sterling Silver {m} Slim Bangle (Single)", "AG", (12, 30), 20, CZ(300, 900) if "CZ" in m else [], ["minimal"] + (["antique"] if "Antique" in m else []), ["daily-wear", "gifting"])
for m in ["Nakashi", "Kundan Stone", "Oxidised Rope", "Temple"]:
    add("BG", "bangle", f"Sterling Silver {m} Bangle Pair (Heavy)", "AG", (80, 140), 16, KUNDAN(1500, 3500) if "Kundan" in m else [], ["traditional"] + (["stone-studded"] if "Kundan" in m else []), ["festive"])
for m in ["Rope", "Nakashi", "Floral", "Peacock", "Faceted Cut", "Engraved", "Beaded Edge", "Wave"]:
    add("BG", "bangle", f"Slim {m} Gold Bangle (Single)", "G22", (2.0, 3.4), 12, [], ["minimal"] + (["engraved"] if m == "Engraved" else []), ["daily-wear", "gifting"])
for m in BG_G[:8]:
    add("BG", "bangle", f"{m} Gold Bangle (Single)", "G22", (5, 8), 10, [], ["traditional"], ["festive", "gifting"])
for i, m in enumerate(["Floral Pavé", "Leaf Pavé", "Bar Station", "Infinity Pavé", "Cluster Cuff", "Wave Pavé"]):
    mc = cyc(["G18W", "G18Y", "G18R", "PT"], i)
    add("BG", "bangle", f"{m} Diamond Bangle in {METALS[mc][0]}", mc, (10, 22), 20 if mc == "PT" else 15, [("melee", 1.2, 3.2)], ["contemporary", "stone-studded"], ["gifting", "festive"])
for i, m in enumerate(["Orbit Cuff", "Bamboo Texture", "Ribbon Twist", "Braided Link", "Sculpted Leaf", "Hammered Wave", "Beveled Cuff", "Chain Link", "Open Spiral"]):
    add("BG", "bangle", f"{m} Designer Gold Bangle", cyc(["G18Y", "G22", "G18R"], i), (12, 26), 14, [], ["designer", "contemporary"], ["party-wear", "gifting"])
for m in ["Vine Engraved", "Paisley Engraved", "Lotus Engraved", "Peacock Feather Engraved", "Gujarati Motif Engraved", "Chevron Engraved", "Sun-Ray Engraved"]:
    add("BG", "bangle", f"{m} Gold Bangle", "G22", (12, 26), 13, [], ["engraved", "traditional"], ["gifting", "festive"])
for m in ["Fluted", "Brushed Matte", "Diamond-Cut Facet", "Mesh"]:
    add("BG", "bangle", f"Platinum {m} Bangle", "PT", (6, 12), 20, [], ["minimal"], ["gifting", "daily-wear"])


IMP = ["Royal Navratna", "Maharani Floral", "Antique Filigree"]
TPL = ["temple", "antique", "traditional"]
trad("NK", "long", "Temple Long Haar", "G22A", (55, 100), 18, [], TPL, ["festive", "wedding"], IMP, temple=True)
trad("ER", "drop", "Temple Earrings", "G22A", (6, 14), 17, [], TPL, ["festive", "bridal"], IMP, temple=True)
trad("BG", "bangle", "Temple Bangle Pair", "G22A", (28, 55), 17, [], TPL, ["festive", "wedding"], IMP, temple=True)
trad("TP", "pendant", "Temple Pendant", "G22A", (8, 22), 17, [], TPL, ["festive", "daily-wear", "gifting"], IMP, temple=True)
sets("Imperial Temple", IMP, "G22A", (115, 215), 18, [], TPL, comps=("Long Haar", "Choker", "Earrings"), temple=True)
for m in BG_G[8:12]:
    add("BG", "bangle", f"{m} Gold Bangle (Single)", "G22", (5, 8), 10, [], ["traditional"], ["festive", "gifting"])
for m in ["Classic Polished", "Machine-Cut", "Rope Twist", "Peacock Motif"]:
    add("BG", "bangle", f"Heavy {m} Gold Bangle (Single)", "G22", (6, 8.5), 10, [], ["traditional"], ["festive", "gifting"])

# ---------------- MENU MEMBERSHIPS ----------------
NECK = {"choker_set", "long", "pendant", "chain", "statement"}
def is_dia(p): return any(s[0] in DIA for s in p["stones"])
def has(p, kinds): return any(s[0] in kinds for s in p["stones"])
def is_pearl(p): return any(s[0] == "flat" and "pearl" in s[3].lower() for s in p["stones"])
def band(price, pre):
    return f"{pre}-price-" + ("under-10k" if price < 10000 else "10k-25k" if price < 25000 else "25k-50k" if price < 50000 else "50k-1l" if price < 100000 else "above-1l")

def menus(p, price):
    m, f, g, S, O, T = [], p["form"], METALS[p["metal"]][3], set(p["styles"]), set(p["occ"]), set(p["tags"])
    mg = g
    mat = lambda pre: ([f"{pre}-material-gold"] if g == "gold" else []) + ([f"{pre}-material-diamond"] if is_dia(p) else []) + ([f"{pre}-material-platinum"] if g == "platinum" else []) + \
        ([f"{pre}-material-silver"] if g == "silver" else []) + ([f"{pre}-material-pearl"] if is_pearl(p) else []) + ([f"{pre}-material-gemstone"] if has(p, GEM) else [])
    if f in NECK:
        m += ["necklaces-all"] + (["necklaces-gold"] if g == "gold" else []) + (["necklaces-diamond"] if is_dia(p) else []) + (["necklaces-bridal", "bridal-necklaces"] if "wedding" in O and f in ("choker_set", "long") else []) \
            + (["necklaces-temple"] if "temple" in S else []) + (["necklaces-choker-sets"] if f == "choker_set" else []) + (["necklaces-long"] if f == "long" else []) + (["necklaces-pendant"] if f == "pendant" else [])
        m += [f"necklaces-style-{s}" for s in S if s in {"traditional", "contemporary", "antique", "minimal", "kundan", "polki", "pearl", "statement"}]
        m += [f"necklaces-occasion-{o}" for o in O if o in {"wedding", "engagement", "festive", "daily-wear", "party-wear", "gifting"}] + mat("necklaces")
        if f == "pendant" and is_dia(p): m.append("diamond-pendants")
        if is_dia(p): m.append("diamond-necklaces")
        if "temple" in S and f == "pendant": m.append("temple-pendants")
        if "temple" in S: m.append("temple-necklaces")
    if f in ("jhumka", "stud", "hoop", "chandbali", "drop"):
        m += ["earrings-all", f"earrings-{ {'jhumka':'jhumkas','stud':'stud','hoop':'hoop','chandbali':'chandbalis','drop':'drop'}[f] }"] + (["earrings-traditional"] if "traditional" in S else []) + (["earrings-diamond", "diamond-earrings"] if is_dia(p) else [])
        m += [f"earrings-style-{s}" for s in S if s in {"antique", "temple", "kundan", "polki", "pearl", "minimal", "contemporary"}]
        m += [f"earrings-occasion-{o}" for o in O if o in {"bridal", "festive", "everyday", "party-wear", "gifting"}]
        m += [x for x in mat("earrings") if not x.endswith("pearl")]
        if "bridal" in O: m.append("bridal-earrings")
        if "temple" in S: m.append("temple-earrings")
    if f in ("engagement", "band", "couple", "ring", "cocktail", "mens_ring", "bridal_ring"):
        m += ["rings-all"] + (["rings-engagement"] if f == "engagement" else []) + (["rings-wedding-bands"] if f == "band" else []) + (["rings-diamond", "diamond-rings"] if is_dia(p) else []) + (["rings-gold"] if g == "gold" else []) \
            + (["rings-cocktail"] if f == "cocktail" else []) + (["rings-couple"] if f == "couple" else []) + (["rings-mens"] if f == "mens_ring" or p["gender"] == "men" else []) + [band(price, "rings")]
        m += [f"rings-style-{s}" for s in S if s in {"solitaire", "floral", "traditional", "minimal", "statement", "gemstone"}] + [x for x in mat("rings") if not x.endswith("pearl")]
        if f in ("bridal_ring", "engagement"): m.append("bridal-rings")
        if f == "mens_ring" and ("signet" in T or "solitaire" in T): m.append("mens-signet-solitaire")
    if f in ("bangle", "kada", "bridal_bangle"):
        m += ["bangles-all"] + (["bangles-gold"] if g == "gold" else []) + (["bangles-diamond"] if is_dia(p) else []) + (["bangles-bridal", "bridal-bangles"] if f == "bridal_bangle" or "wedding" in O and f == "bridal_bangle" else []) \
            + (["bangles-kadas"] if f == "kada" else []) + (["bangles-temple", "temple-bangles"] if "temple" in S else []) + (["bangles-daily"] if "daily-wear" in O else []) + (["bangles-antique"] if "antique" in S else []) + [band(price, "bangles")]
        m += [f"bangles-style-{s}" for s in S if s in {"traditional", "contemporary", "minimal", "designer", "stone-studded", "engraved"}] + [x for x in mat("bangles") if not x.endswith(("pearl", "gemstone"))]
    if f == "bracelet": m += ["diamond-bracelets"]
    if f == "bridal_set": m += ["bridal-sets"] + (["temple-bridal-sets"] if "temple" in S else []) + (["diamond-bridal-sets"] if is_dia(p) else [])
    if f == "tikka": m += ["bridal-maang-tikka"]
    if f == "nath": m += ["bridal-nath"]
    if "temple" in S: m += ["temple-all"]
    if "temple" in S or p["metal"] == "G22A":
        if p["metal"] == "G22A" or "antique" in S: m.append("temple-motif-antique-finish") if "temple" in S else None
    if "temple" in S:
        for tg, slug in [("lakshmi", "temple-motif-lakshmi"), ("peacock", "temple-motif-peacock-floral"), ("floral", "temple-motif-peacock-floral"), ("south-indian", "temple-motif-south-indian-royal"), ("imperial", "temple-motif-imperial-heritage")]:
            if tg in T: m.append(slug)
    if is_dia(p):
        if "solitaire" in S: m.append("diamond-style-solitaire")
        if "daily-wear" in O or "everyday" in O: m.append("diamond-style-everyday")
        if "statement" in S: m.append("diamond-style-statement")
        if "contemporary" in S: m.append("diamond-style-modern")
        if "gifting" in O: m.append("diamond-style-gifts")
        mm = p["metal"]
        m.append({"G18W": "diamond-metal-white-gold", "G18Y": "diamond-metal-yellow-gold", "G22": "diamond-metal-yellow-gold", "G22A": "diamond-metal-yellow-gold", "G18R": "diamond-metal-rose-gold", "PT": "diamond-metal-platinum"}.get(mm, "diamond-metal-other"))
    if f == "mens_kada": m.append("mens-kadas")
    if f == "mens_chain": m.append("mens-chains")
    if f == "cufflinks": m.append("mens-cufflinks")
    if f in ("kurta_buttons", "brooch"): m.append("mens-kurta-brooches")
    if p["code"] == "MN" or p["gender"] == "men":
        if p["metal"] == "G22": m.append("mens-finish-22k-yellow-gold")
        if p["metal"] == "PT": m.append("mens-finish-950-platinum")
        if p["metal"] == "G22A": m.append("mens-finish-antique-brushed-gold")
        if "black-diamond" in T or "onyx" in T or has(p, {"blackdia", "onyx"}): m.append("mens-finish-black-diamonds-onyx")
        if p["pers"] and p["pers"].get("monogram"): m.append("mens-finish-bespoke-monogramming")
    for k, slug in {"custom_name": "pers-custom-name-necklace", "initial": "pers-initial-pendants", "pers_ring": "pers-personalised-rings", "engraved_bracelet": "pers-engraved-bracelets-kadas",
                    "custom_bridal": "pers-custom-bridal-sets", "design_own": "pers-design-your-own"}.items():
        if f == k: m.append(slug)
    if f == "gift_set": m.append("gift-sets")
    # bridal collections & occasions
    inb = any(x.startswith("bridal-") for x in m) or "necklaces-bridal" in m or "bridal" in O and f in ("jhumka", "chandbali", "drop")
    if inb:
        for s, slug in [("kundan", "bridal-coll-kundan"), ("polki", "bridal-coll-polki"), ("temple", "bridal-coll-temple"), ("antique", "bridal-coll-antique"), ("traditional", "bridal-coll-traditional")]:
            if s in S: m.append(slug)
        if is_dia(p): m.append("bridal-coll-diamond")
        occs = {"wedding"} if f != "engagement" else {"engagement"}
        if is_dia(p) or "polki" in S: occs.add("reception")
        if is_dia(p) and f in ("bridal_set", "bridal_ring", "engagement", "tikka", "choker_set"): occs.add("engagement")
        if "kundan" in S or "pearl" in S: occs.update(["sangeet"])
        if "pearl" in S or ("kundan" in S and f in ("tikka", "nath", "jhumka", "chandbali", "bridal_ring")): occs.add("mehendi")
        m += [f"bridal-occasion-{o}" for o in occs]
    # new & featured (editorial / rule based)
    if "festive" in O: m.append("nf-festive")
    if "wedding" in O or inb: m.append("nf-wedding")
    if "daily-wear" in O or "everyday" in O: m.append("nf-everyday")
    if inb: m.append("feat-bridal-collection")
    if "temple" in S or "antique" in S or "imperial" in T: m.append("feat-heritage")
    if is_dia(p): m.append("feat-diamond")
    if "temple" in S: m.append("feat-temple")
    if S & {"designer", "statement", "contemporary"}: m.append("feat-designer")
    if O & {"wedding", "engagement", "party-wear", "bridal"}: m.append("feat-special-occasion")
    if p["mto"]: m.append("nf-exclusive")
    return list(dict.fromkeys(m))

# ---------------- BUILD ----------------
SHOTS = {"ring": ["Top-down front view", "Side profile", "Close-up of setting and hallmark", "On hand", "36-frame turntable"],
         "default": ["Front view", "Side or angled view", "Close-up detail and hallmark stamp", "Worn on model or bust", "36-frame turntable"]}
rows, seen, ctr = [], set(), collections.Counter()
today = datetime.date.today().isoformat()
for p in P:
    assert p["name"] not in seen, "duplicate name: " + p["name"]; seen.add(p["name"])
    mlabel, purity, rk, grp, tone = METALS[p["metal"]]
    wt = p["wt"] if not isinstance(p["wt"], tuple) else round(between(p["name"] + "w", *p["wt"], 1), 1)
    sv, stones_out = 0, []
    for s in p["stones"]:
        if s[0] == "flat":
            v = round(between(p["name"] + s[3], s[1], s[2], 0) / 100) * 100; stones_out.append({"type": s[3], "carat": None, "estimated_value_inr": v}); sv += v
        else:
            ct = between(p["name"] + s[0], s[1], s[2], 2); v = round(ct * STONE[s[0]] / 100) * 100
            stones_out.append({"type": STONE_LABEL[s[0]], "carat": ct, "estimated_value_inr": v}); sv += v
    mv = round(wt * RATE[rk]); mk = round(mv * p["mk"] / 100); sub = mv + mk + sv; gst = round(sub * GST / 100); price = int(round((sub + gst) / 10) * 10)
    ctr[p["code"]] += 1; sku = f"NIL-{p['code']}-{ctr[p['code']]:04d}"; mid = [x for x in menus(p, price)]
    rows.append(dict(sku=sku, slug=slugify(p["name"]) + "-" + sku[-4:].lower(), name=p["name"], form=p["form"], gender=p["gender"], metal={"label": mlabel, "purity": purity, "group": grp, "tone": tone},
        net_weight_g=wt, making_charge_pct=p["mk"], stones=stones_out,
        price={"metal_value": mv, "making_charge": mk, "stone_value": sv, "subtotal": sub, "gst_pct": GST, "gst": gst, "total_inr": price, "type": p["ptype"],
               "rates_as_of": R["as_of"], "basis": "estimated weight/stones; metal at published rate"},
        styles=p["styles"], occasions=p["occ"], tags=p["tags"], set_contains=p["comps"], made_to_order=p["mto"], personalisation=p["pers"],
        made_to_order_details={"making_days": 21, "advance_pct": 50} if p["mto"] else None, menus=mid,
        flags={"is_new": False, "is_bestseller": False, "is_customer_favourite": False, "is_trending": False},
        media={"front": f"products/{sku}/front.webp", "side": f"products/{sku}/side.webp", "detail": f"products/{sku}/detail.webp", "model": f"products/{sku}/model.webp",
               "view360": {"folder": f"products/{sku}/360", "frames": 36, "pattern": "frame_{n:02d}.webp"}},
        shot_list=SHOTS["ring"] if "ring" in p["form"] or p["form"] in ("engagement", "band", "couple", "cocktail") else SHOTS["default"],
        status="needs_photos", published=False, added_on=today))
# New arrivals / latest collections: seed the 6 most recently added items per family code (admin can change)
bycode = collections.defaultdict(list)
for r in rows: bycode[r["sku"].split("-")[1]].append(r)
for code, l in bycode.items():
    for r in l[-5:]:
        r["flags"]["is_new"] = True
for r in rows:
    if r["flags"]["is_new"]: r["menus"] += ["nf-new-arrivals", "nf-latest-collections"]
# collections definitions
LAB = {}
def L(slug, label, top, group, minn=15): LAB[slug] = dict(slug=slug, label=label, top_menu=top, group=group, min_required=minn)
for s, l in [("all", "All Necklaces"), ("gold", "Gold Necklaces"), ("diamond", "Diamond Necklaces"), ("bridal", "Bridal Necklaces"), ("temple", "Temple Necklaces"), ("choker-sets", "Choker Sets"), ("long", "Long Necklaces"), ("pendant", "Pendant Necklaces")]: L("necklaces-" + s, l, "Necklaces", "Category")
for s in ["traditional", "contemporary", "antique", "minimal", "kundan", "polki", "pearl", "statement"]: L("necklaces-style-" + s, s.title(), "Necklaces", "Style")
for s in ["wedding", "engagement", "festive", "daily-wear", "party-wear", "gifting"]: L("necklaces-occasion-" + s, s.replace("-", " ").title(), "Necklaces", "Occasion")
for s in ["gold", "diamond", "platinum", "silver", "pearl", "gemstone"]: L("necklaces-material-" + s, s.title(), "Necklaces", "Material")
for s, l in [("all", "All Earrings"), ("jhumkas", "Jhumkas"), ("stud", "Stud Earrings"), ("hoop", "Hoop Earrings"), ("chandbalis", "Chandbalis"), ("drop", "Drop Earrings"), ("traditional", "Traditional Earrings"), ("diamond", "Diamond Earrings")]: L("earrings-" + s, l, "Earrings", "Category")
for s in ["antique", "temple", "kundan", "polki", "pearl", "minimal", "contemporary"]: L("earrings-style-" + s, s.title(), "Earrings", "Style")
for s in ["bridal", "festive", "everyday", "party-wear", "gifting"]: L("earrings-occasion-" + s, s.replace("-", " ").title(), "Earrings", "Occasion")
for s in ["gold", "diamond", "silver", "platinum", "gemstone"]: L("earrings-material-" + s, s.title(), "Earrings", "Material")
for s, l in [("all", "All Rings"), ("engagement", "Engagement Rings"), ("wedding-bands", "Wedding Bands"), ("diamond", "Diamond Rings"), ("gold", "Gold Rings"), ("cocktail", "Cocktail Rings"), ("couple", "Couple Rings"), ("mens", "Men's Rings")]: L("rings-" + s, l, "Rings", "Category", 20)
for s in ["solitaire", "floral", "traditional", "minimal", "statement", "gemstone"]: L("rings-style-" + s, s.title(), "Rings", "Style", 20)
for s, l in [("under-10k", "Under ₹10,000"), ("10k-25k", "₹10,000–₹25,000"), ("25k-50k", "₹25,000–₹50,000"), ("50k-1l", "₹50,000–₹1,00,000"), ("above-1l", "Above ₹1,00,000")]: L("rings-price-" + s, l, "Rings", "Price", 20); L("bangles-price-" + s, l, "Bangles", "Price")
for s in ["gold", "diamond", "platinum", "silver", "gemstone"]: L("rings-material-" + s, s.title(), "Rings", "Material", 20)
for s, l in [("all", "All Bangles"), ("gold", "Gold Bangles"), ("diamond", "Diamond Bangles"), ("bridal", "Bridal Bangles"), ("kadas", "Kadas"), ("temple", "Temple Bangles"), ("daily", "Daily Wear Bangles"), ("antique", "Antique Bangles")]: L("bangles-" + s, l, "Bangles", "Category")
for s in ["traditional", "contemporary", "minimal", "designer", "stone-studded", "engraved"]: L("bangles-style-" + s, s.replace("-", " ").title(), "Bangles", "Style")
for s in ["gold", "diamond", "platinum", "silver"]: L("bangles-material-" + s, s.title(), "Bangles", "Material")
for s, l in [("sets", "Complete Bridal Sets"), ("necklaces", "Bridal Necklaces"), ("earrings", "Bridal Earrings"), ("bangles", "Bridal Bangles"), ("maang-tikka", "Maang Tikka"), ("nath", "Nath"), ("rings", "Bridal Rings")]: L("bridal-" + s, l, "Bridal Jewellery", "Category")
for s in ["kundan", "polki", "temple", "antique", "diamond", "traditional"]: L("bridal-coll-" + s, s.title() + " Bridal", "Bridal Jewellery", "Collection")
for s in ["engagement", "wedding", "reception", "mehendi", "sangeet"]: L("bridal-occasion-" + s, s.title(), "Bridal Jewellery", "Occasion")
for s, l in [("all", "All Temple Jewellery"), ("necklaces", "Temple Necklaces"), ("earrings", "Temple Earrings"), ("bangles", "Temple Bangles"), ("pendants", "Temple Pendants"), ("bridal-sets", "Temple Bridal Sets")]: L("temple-" + s, l, "Temple Jewellery", "Category")
for s, l in [("antique-finish", "Antique Finish"), ("lakshmi", "Goddess Lakshmi Designs"), ("peacock-floral", "Traditional Peacock & Floral Motifs"), ("south-indian-royal", "South Indian Royal Collection"), ("imperial-heritage", "Imperial Heritage Collection")]: L("temple-motif-" + s, l, "Temple Jewellery", "Heritage Motifs")
for s, l in [("necklaces", "Diamond Necklaces"), ("rings", "Diamond Rings"), ("earrings", "Diamond Earrings"), ("bracelets", "Diamond Bracelets"), ("pendants", "Diamond Pendants"), ("bridal-sets", "Diamond Bridal Sets")]: L("diamond-" + s, l, "Diamond Jewellery", "Category")
for s, l in [("solitaire", "Solitaire"), ("everyday", "Everyday Diamonds"), ("statement", "Statement Diamonds"), ("modern", "Modern Designs"), ("gifts", "Diamond Gifts")]: L("diamond-style-" + s, l, "Diamond Jewellery", "Style")
for s, l in [("white-gold", "White Gold"), ("yellow-gold", "Yellow Gold"), ("rose-gold", "Rose Gold"), ("platinum", "Platinum")]: L("diamond-metal-" + s, l, "Diamond Jewellery", "Precious Metal")
for s, l in [("kadas", "Gold & Platinum Kadas"), ("chains", "Imperial Gold Chains"), ("signet-solitaire", "Signet & Solitaire Rings"), ("cufflinks", "Gemstone Cufflinks"), ("kurta-brooches", "Kurta Buttons & Brooches")]: L("mens-" + s, l, "Men's Jewellery", "Category")
for s, l in [("22k-yellow-gold", "22K Yellow Gold"), ("950-platinum", "950 Platinum"), ("antique-brushed-gold", "Antique Brushed Gold"), ("black-diamonds-onyx", "Black Diamonds & Onyx"), ("bespoke-monogramming", "Bespoke Monogramming")]: L("mens-finish-" + s, l, "Men's Jewellery", "Metals & Finishes")
for s, l in [("custom-name-necklace", "Custom Name Necklace"), ("initial-pendants", "Initial Pendants"), ("personalised-rings", "Personalised Rings"), ("engraved-bracelets-kadas", "Engraved Bracelets & Kadas"), ("custom-bridal-sets", "Custom Bridal Sets"), ("design-your-own", "Design Your Own Jewellery")]: L("pers-" + s, l, "New & Featured", "Personalised Jewellery")
for s, l in [("new-arrivals", "New Arrivals"), ("festive", "Festive Jewellery"), ("wedding", "Wedding Jewellery"), ("everyday", "Everyday Jewellery"), ("exclusive", "Exclusive Designs"), ("latest-collections", "Latest Collections")]: L("nf-" + s, l, "New & Featured", "Category")
L("gift-sets", "Gift Sets", "New & Featured", "Category")
for s, l in [("bridal-collection", "Bridal Collection"), ("heritage", "Heritage Collection"), ("diamond", "Diamond Collection"), ("temple", "Temple Jewellery"), ("designer", "Designer Jewellery"), ("special-occasion", "Special Occasion Jewellery")]: L("feat-" + s, l, "New & Featured", "Featured")
for s, l in [("bestsellers", "Bestsellers"), ("customer-favourites", "Customer Favourites"), ("trending", "Trending Jewellery")]:
    d = dict(slug="sales-" + s, label=l, top_menu="New & Featured", group="Sales-driven", min_required=0, rule="Fill automatically from real order data after launch. Left empty on purpose so no piece shows a Best Seller or Favourite badge it has not earned.")
    LAB["sales-" + s] = d
cnt = collections.Counter(x for r in rows for x in r["menus"])
for s, d in LAB.items(): d["product_count"] = cnt.get(s, 0)
fails = [(s, d["product_count"], d["min_required"]) for s, d in LAB.items() if d["product_count"] < d["min_required"]]
unknown = sorted(set(cnt) - set(LAB))
print("products:", len(rows), "| collections:", len(LAB), "| below minimum:", len(fails), "| unmapped slugs:", unknown)
for f in fails: print("  SHORT", f)
json.dump({"meta": {"generated": today, "rates": R, "currency": "INR", "notes": ["Prices are calculated from rates.json. Weights, making % and stone values are estimates: replace with your real inventory data.",
           "No piece is published until its 4 angle photos and 36 turntable frames exist (run check_media.py)."]}, "collections": list(LAB.values()), "products": rows},
          open(os.path.join(HERE, "catalog.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(list(LAB.values()), open(os.path.join(HERE, "collections.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, "products.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh); w.writerow(["sku", "name", "form", "gender", "metal", "purity", "net_weight_g", "making_charge_pct", "stones", "metal_value", "making_charge", "stone_value", "gst", "price_inr", "price_type", "styles", "occasions", "collections", "made_to_order", "front", "side", "detail", "model", "view360_folder", "published"])
    for r in rows:
        w.writerow([r["sku"], r["name"], r["form"], r["gender"], r["metal"]["label"], r["metal"]["purity"], r["net_weight_g"], r["making_charge_pct"], "; ".join(f'{s["type"]} {s["carat"] or ""}'.strip() for s in r["stones"]),
                    r["price"]["metal_value"], r["price"]["making_charge"], r["price"]["stone_value"], r["price"]["gst"], r["price"]["total_inr"], r["price"]["type"], "|".join(r["styles"]), "|".join(r["occasions"]), "|".join(r["menus"]),
                    r["made_to_order"], r["media"]["front"], r["media"]["side"], r["media"]["detail"], r["media"]["model"], r["media"]["view360"]["folder"], r["published"]])
