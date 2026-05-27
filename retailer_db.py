"""
Pre-curated database of top Australian retail websites.
Traffic tiers: High (top ~50 national), Medium (50-300), Low (niche/emerging).
"""

RETAILERS = [
    # ── MARKETPLACES ──────────────────────────────────────────────────────────
    {"domain": "amazon.com.au",        "name": "Amazon AU",          "subvertical": "Marketplace",        "traffic": "High"},
    {"domain": "ebay.com.au",          "name": "eBay AU",            "subvertical": "Marketplace",        "traffic": "High"},
    {"domain": "temu.com",             "name": "Temu",               "subvertical": "Marketplace",        "traffic": "High"},
    {"domain": "mydeal.com.au",        "name": "MyDeal",             "subvertical": "Marketplace",        "traffic": "Medium"},
    {"domain": "catch.com.au",         "name": "Catch",              "subvertical": "Marketplace",        "traffic": "Medium"},
    {"domain": "kogan.com",            "name": "Kogan",              "subvertical": "Marketplace",        "traffic": "Medium"},
    {"domain": "ozbargain.com.au",     "name": "OzBargain",          "subvertical": "Deals / Coupons",    "traffic": "High"},

    # ── GROCERY & SUPERMARKETS ────────────────────────────────────────────────
    {"domain": "woolworths.com.au",    "name": "Woolworths",         "subvertical": "Grocery",            "traffic": "High"},
    {"domain": "coles.com.au",         "name": "Coles",              "subvertical": "Grocery",            "traffic": "High"},
    {"domain": "aldi.com.au",          "name": "ALDI AU",            "subvertical": "Grocery",            "traffic": "Medium"},
    {"domain": "igaonline.com.au",     "name": "IGA Online",         "subvertical": "Grocery",            "traffic": "Medium"},
    {"domain": "costco.com.au",        "name": "Costco AU",          "subvertical": "Grocery",            "traffic": "Medium"},
    {"domain": "harris.farm",          "name": "Harris Farm",        "subvertical": "Grocery",            "traffic": "Low"},
    {"domain": "danmurphys.com.au",    "name": "Dan Murphy's",       "subvertical": "Liquor",             "traffic": "High"},
    {"domain": "bws.com.au",           "name": "BWS",                "subvertical": "Liquor",             "traffic": "Medium"},
    {"domain": "firstchoiceliquor.com.au", "name": "First Choice",   "subvertical": "Liquor",             "traffic": "Low"},

    # ── DEPARTMENT STORES ────────────────────────────────────────────────────
    {"domain": "kmart.com.au",         "name": "Kmart",              "subvertical": "Department Store",   "traffic": "High"},
    {"domain": "bigw.com.au",          "name": "Big W",              "subvertical": "Department Store",   "traffic": "High"},
    {"domain": "target.com.au",        "name": "Target AU",          "subvertical": "Department Store",   "traffic": "Medium"},
    {"domain": "myer.com.au",          "name": "Myer",               "subvertical": "Department Store",   "traffic": "Medium"},
    {"domain": "davidjones.com",       "name": "David Jones",        "subvertical": "Department Store",   "traffic": "Medium"},

    # ── HOME IMPROVEMENT & HARDWARE ───────────────────────────────────────────
    {"domain": "bunnings.com.au",      "name": "Bunnings",           "subvertical": "Home Improvement",   "traffic": "High"},
    {"domain": "mitre10.com.au",       "name": "Mitre 10",           "subvertical": "Home Improvement",   "traffic": "Medium"},
    {"domain": "totaltools.com.au",    "name": "Total Tools",        "subvertical": "Home Improvement",   "traffic": "Low"},

    # ── ELECTRONICS & TECH ───────────────────────────────────────────────────
    {"domain": "jbhifi.com.au",        "name": "JB Hi-Fi",           "subvertical": "Electronics",        "traffic": "High"},
    {"domain": "officeworks.com.au",   "name": "Officeworks",        "subvertical": "Electronics",        "traffic": "High"},
    {"domain": "thegoodguys.com.au",   "name": "The Good Guys",      "subvertical": "Electronics",        "traffic": "Medium"},
    {"domain": "harveynorman.com.au",  "name": "Harvey Norman",      "subvertical": "Electronics",        "traffic": "High"},
    {"domain": "apple.com/au",         "name": "Apple AU",           "subvertical": "Electronics",        "traffic": "High"},
    {"domain": "samsung.com/au",       "name": "Samsung AU",         "subvertical": "Electronics",        "traffic": "Medium"},
    {"domain": "appliancesonline.com.au", "name": "Appliances Online","subvertical": "Electronics",        "traffic": "Medium"},
    {"domain": "bing.lee.com.au",      "name": "Bing Lee",           "subvertical": "Electronics",        "traffic": "Medium"},
    {"domain": "centrecom.com.au",     "name": "Centre Com",         "subvertical": "Electronics",        "traffic": "Low"},
    {"domain": "scorptec.com.au",      "name": "Scorptec",           "subvertical": "Electronics",        "traffic": "Low"},
    {"domain": "pbtech.com.au",        "name": "PB Tech AU",         "subvertical": "Electronics",        "traffic": "Low"},
    {"domain": "umart.com.au",         "name": "Umart",              "subvertical": "Electronics",        "traffic": "Low"},

    # ── FASHION & APPAREL ────────────────────────────────────────────────────
    {"domain": "theiconic.com.au",     "name": "THE ICONIC",         "subvertical": "Fast Fashion",       "traffic": "High"},
    {"domain": "asos.com",             "name": "ASOS",               "subvertical": "Fast Fashion",       "traffic": "High"},
    {"domain": "uniqlo.com/au",        "name": "Uniqlo AU",          "subvertical": "Fast Fashion",       "traffic": "Medium"},
    {"domain": "zara.com/au",          "name": "Zara AU",            "subvertical": "Fast Fashion",       "traffic": "Medium"},
    {"domain": "hm.com/au",            "name": "H&M AU",             "subvertical": "Fast Fashion",       "traffic": "Medium"},
    {"domain": "cotton-on.com",        "name": "Cotton On",          "subvertical": "Fast Fashion",       "traffic": "High"},
    {"domain": "gluestore.com.au",     "name": "Glue Store",         "subvertical": "Fast Fashion",       "traffic": "Low"},
    {"domain": "citybeach.com.au",     "name": "City Beach",         "subvertical": "Fast Fashion",       "traffic": "Medium"},
    {"domain": "supre.com.au",         "name": "Supre",              "subvertical": "Fast Fashion",       "traffic": "Low"},
    {"domain": "factorie.com.au",      "name": "Factorie",           "subvertical": "Fast Fashion",       "traffic": "Low"},
    {"domain": "universalstore.com",   "name": "Universal Store",    "subvertical": "Fast Fashion",       "traffic": "Low"},
    {"domain": "sportsgirl.com.au",    "name": "Sportsgirl",         "subvertical": "Fast Fashion",       "traffic": "Low"},
    {"domain": "minkpink.com",         "name": "MINKPINK",           "subvertical": "Fast Fashion",       "traffic": "Low"},
    {"domain": "witchery.com.au",      "name": "Witchery",           "subvertical": "Fast Fashion",       "traffic": "Low"},
    {"domain": "countryroad.com.au",   "name": "Country Road",       "subvertical": "Fast Fashion",       "traffic": "Medium"},
    {"domain": "marcs.com.au",         "name": "Marcs",              "subvertical": "Fast Fashion",       "traffic": "Low"},
    {"domain": "aliceintheva.com.au",  "name": "Alice in the VA",    "subvertical": "Fast Fashion",       "traffic": "Low"},

    # ── LUXURY FASHION ────────────────────────────────────────────────────────
    {"domain": "mytheresa.com",        "name": "Mytheresa",          "subvertical": "Luxury Fashion",     "traffic": "Medium"},
    {"domain": "net-a-porter.com",     "name": "Net-a-Porter",       "subvertical": "Luxury Fashion",     "traffic": "Medium"},
    {"domain": "farfetch.com",         "name": "Farfetch",           "subvertical": "Luxury Fashion",     "traffic": "Medium"},

    # ── SPORTING GOODS & OUTDOOR ─────────────────────────────────────────────
    {"domain": "rebelsport.com.au",    "name": "Rebel Sport",        "subvertical": "Sporting Goods",     "traffic": "High"},
    {"domain": "decathlon.com.au",     "name": "Decathlon AU",       "subvertical": "Sporting Goods",     "traffic": "Medium"},
    {"domain": "anacondastores.com.au","name": "Anaconda",           "subvertical": "Sporting Goods",     "traffic": "Medium"},
    {"domain": "bcf.com.au",           "name": "BCF",                "subvertical": "Sporting Goods",     "traffic": "Medium"},
    {"domain": "lululemon.com/en-au",  "name": "Lululemon AU",       "subvertical": "Sporting Goods",     "traffic": "Medium"},
    {"domain": "asics.com/au",         "name": "ASICS AU",           "subvertical": "Sporting Goods",     "traffic": "Medium"},
    {"domain": "footlocker.com.au",    "name": "Foot Locker AU",     "subvertical": "Sporting Goods",     "traffic": "Medium"},
    {"domain": "ryderwear.com",        "name": "Ryderwear",          "subvertical": "Sporting Goods",     "traffic": "Low"},
    {"domain": "lskd.com",             "name": "LSKD",               "subvertical": "Sporting Goods",     "traffic": "Low"},

    # ── HEALTH & PHARMACY ────────────────────────────────────────────────────
    {"domain": "chemistwarehouse.com.au","name": "Chemist Warehouse", "subvertical": "Pharmacy",          "traffic": "High"},
    {"domain": "priceline.com.au",     "name": "Priceline",          "subvertical": "Pharmacy",           "traffic": "Medium"},
    {"domain": "terrywhitechemmart.com.au","name": "TerryWhite",      "subvertical": "Pharmacy",          "traffic": "Low"},
    {"domain": "healthylife.com.au",   "name": "Healthy Life",       "subvertical": "Pharmacy",           "traffic": "Medium"},
    {"domain": "iherb.com",            "name": "iHerb",              "subvertical": "Health Supplements", "traffic": "High"},
    {"domain": "vitalstrength.com.au", "name": "Vital Strength",     "subvertical": "Health Supplements", "traffic": "Low"},
    {"domain": "bodybuilding.com",     "name": "Bodybuilding.com",   "subvertical": "Health Supplements", "traffic": "Medium"},

    # ── BEAUTY & COSMETICS ───────────────────────────────────────────────────
    {"domain": "adorebeauty.com.au",   "name": "Adore Beauty",       "subvertical": "Beauty",             "traffic": "Medium"},
    {"domain": "sephora.com.au",       "name": "Sephora AU",         "subvertical": "Beauty",             "traffic": "High"},
    {"domain": "mecca.com",            "name": "Mecca",              "subvertical": "Beauty",             "traffic": "High"},
    {"domain": "lookfantastic.com.au", "name": "Lookfantastic AU",   "subvertical": "Beauty",             "traffic": "Medium"},
    {"domain": "shein.com",            "name": "SHEIN",              "subvertical": "Fast Fashion",       "traffic": "High"},
    {"domain": "ozhairandbeauty.com.au","name": "OZ Hair & Beauty",  "subvertical": "Beauty",             "traffic": "Low"},
    {"domain": "glowrecipe.com",       "name": "Glow Recipe",        "subvertical": "Beauty",             "traffic": "Low"},

    # ── HOME & FURNITURE ─────────────────────────────────────────────────────
    {"domain": "ikea.com/au",          "name": "IKEA AU",            "subvertical": "Furniture & Home",   "traffic": "High"},
    {"domain": "fantasticfurniture.com.au","name": "Fantastic Furniture","subvertical": "Furniture & Home","traffic": "Medium"},
    {"domain": "amart.com.au",         "name": "Amart Furniture",    "subvertical": "Furniture & Home",   "traffic": "Medium"},
    {"domain": "castlery.com",         "name": "Castlery",           "subvertical": "Furniture & Home",   "traffic": "Medium"},
    {"domain": "nick-scali.com.au",    "name": "Nick Scali",         "subvertical": "Furniture & Home",   "traffic": "Low"},
    {"domain": "ooze.com.au",          "name": "Ooze Living",        "subvertical": "Furniture & Home",   "traffic": "Low"},
    {"domain": "temple-webster.com.au","name": "Temple & Webster",   "subvertical": "Furniture & Home",   "traffic": "High"},
    {"domain": "hardtofind.com.au",    "name": "Hard to Find",       "subvertical": "Gifts & Home",       "traffic": "Low"},
    {"domain": "mightape.com.au",      "name": "MightApe",           "subvertical": "Marketplace",        "traffic": "Low"},
    {"domain": "zanui.com.au",         "name": "Zanui",              "subvertical": "Furniture & Home",   "traffic": "Low"},

    # ── PET SUPPLIES ─────────────────────────────────────────────────────────
    {"domain": "petcircle.com.au",     "name": "Pet Circle",         "subvertical": "Pet Supplies",       "traffic": "Medium"},
    {"domain": "petbarn.com.au",       "name": "Petbarn",            "subvertical": "Pet Supplies",       "traffic": "Medium"},
    {"domain": "petzyo.com.au",        "name": "Petzyo",             "subvertical": "Pet Supplies",       "traffic": "Low"},
    {"domain": "lyka.com.au",          "name": "Lyka",               "subvertical": "Pet Supplies",       "traffic": "Low"},

    # ── AUTOMOTIVE ───────────────────────────────────────────────────────────
    {"domain": "supercheapauto.com.au","name": "Supercheap Auto",    "subvertical": "Automotive",         "traffic": "Medium"},
    {"domain": "autobarn.com.au",      "name": "Autobarn",           "subvertical": "Automotive",         "traffic": "Low"},
    {"domain": "repco.com.au",         "name": "Repco",              "subvertical": "Automotive",         "traffic": "Medium"},

    # ── TOYS & BABY ───────────────────────────────────────────────────────────
    {"domain": "toysrus.com.au",       "name": "Toys R Us AU",       "subvertical": "Toys & Baby",        "traffic": "Low"},
    {"domain": "babybunting.com.au",   "name": "Baby Bunting",       "subvertical": "Toys & Baby",        "traffic": "Medium"},
    {"domain": "mothersnest.com.au",   "name": "Mothers Nest",       "subvertical": "Toys & Baby",        "traffic": "Low"},

    # ── BOOKS, MUSIC & ENTERTAINMENT ─────────────────────────────────────────
    {"domain": "booktopia.com.au",     "name": "Booktopia",          "subvertical": "Books & Media",      "traffic": "Medium"},
    {"domain": "angusrobertson.com.au","name": "Angus & Robertson",  "subvertical": "Books & Media",      "traffic": "Low"},

    # ── FOOD DELIVERY & MEAL KITS ────────────────────────────────────────────
    {"domain": "ubereats.com/au",      "name": "Uber Eats AU",       "subvertical": "Food Delivery",      "traffic": "High"},
    {"domain": "doordash.com/au",      "name": "DoorDash AU",        "subvertical": "Food Delivery",      "traffic": "High"},
    {"domain": "menulog.com.au",       "name": "Menulog",            "subvertical": "Food Delivery",      "traffic": "Medium"},
    {"domain": "hellofresh.com.au",    "name": "HelloFresh AU",      "subvertical": "Meal Kits",          "traffic": "Medium"},
    {"domain": "marley-spoon.com.au",  "name": "Marley Spoon",       "subvertical": "Meal Kits",          "traffic": "Low"},
    {"domain": "every-plate.com.au",   "name": "EveryPlate AU",      "subvertical": "Meal Kits",          "traffic": "Low"},

    # ── OFFICE & BUSINESS ────────────────────────────────────────────────────
    {"domain": "staples.com.au",       "name": "Staples AU",         "subvertical": "Office Supplies",    "traffic": "Low"},
    {"domain": "winc.com.au",          "name": "Winc",               "subvertical": "Office Supplies",    "traffic": "Low"},

    # ── JEWELLERY & ACCESSORIES ───────────────────────────────────────────────
    {"domain": "michaelhill.com/au",   "name": "Michael Hill AU",    "subvertical": "Jewellery",          "traffic": "Medium"},
    {"domain": "proudsfinest.com.au",  "name": "Prouds",             "subvertical": "Jewellery",          "traffic": "Low"},
    {"domain": "lovisa.com",           "name": "Lovisa",             "subvertical": "Jewellery",          "traffic": "Medium"},
    {"domain": "strandbags.com.au",    "name": "Strand Bags",        "subvertical": "Accessories",        "traffic": "Low"},

    # ── SUBSCRIPTION & DTC ───────────────────────────────────────────────────
    {"domain": "boody.com.au",         "name": "Boody",              "subvertical": "Sustainable Fashion","traffic": "Low"},
    {"domain": "frank-body.com",       "name": "Frank Body",         "subvertical": "Beauty",             "traffic": "Low"},
    {"domain": "thankyou.co",          "name": "Thankyou",           "subvertical": "Social Enterprise",  "traffic": "Low"},
    {"domain": "koala.com",            "name": "Koala",              "subvertical": "Furniture & Home",   "traffic": "Medium"},
    {"domain": "casper.com/au",        "name": "Casper AU",          "subvertical": "Furniture & Home",   "traffic": "Low"},

    # ── FLORIST & GIFTING ────────────────────────────────────────────────────
    {"domain": "lovethegarden.com",    "name": "Love the Garden",    "subvertical": "Garden",             "traffic": "Low"},
    {"domain": "bloomingdales.com.au", "name": "Bloomingdale's AU",  "subvertical": "Gifts & Flowers",    "traffic": "Low"},
    {"domain": "interflora.com.au",    "name": "Interflora AU",      "subvertical": "Gifts & Flowers",    "traffic": "Low"},
]

SUBVERTICALS = sorted(set(r["subvertical"] for r in RETAILERS))
