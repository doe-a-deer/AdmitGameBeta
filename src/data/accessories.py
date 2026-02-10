from src.entities.accessory import Accessory

ACCESSORIES = [
    # ---- HAT slot ----
    # Legacy (wealth)
    Accessory(
        "hat_graduation", "Mortarboard", "hat", "hat_graduation",
        cost=1, tags={"wealth": 2, "striving": 0, "rebellion": 0},
        flavor_text="Inherited, naturally. One does not earn a hat like this.",
    ),
    # Meritocrat (striving)
    Accessory(
        "hat_cap", "Baseball Cap", "hat", "hat_cap",
        cost=1, tags={"wealth": 0, "striving": 2, "rebellion": 0},
        flavor_text="Clean lines. Team player energy. Interview-ready.",
    ),
    # Rebellion
    Accessory(
        "hat_beanie", "Slouch Beanie", "hat", "hat_beanie",
        cost=1, tags={"wealth": 0, "striving": 0, "rebellion": 2},
        flavor_text="Pulled low enough to obscure institutional expectations.",
    ),

    # ---- GLASSES slot ----
    # Legacy (wealth)
    Accessory(
        "glasses_wire", "Gold Rounds", "glasses", "glasses_wire",
        cost=1, tags={"wealth": 2, "striving": 0, "rebellion": 0},
        flavor_text="Prescription optional. Prestige mandatory.",
    ),
    # Meritocrat (striving)
    Accessory(
        "glasses_rect", "Square Frames", "glasses", "glasses_rect",
        cost=1, tags={"wealth": 0, "striving": 2, "rebellion": 0},
        flavor_text="Functional. Serious. Seen in every fellowship photo.",
    ),
    # Rebellion
    Accessory(
        "glasses_dark", "Dark Shades", "glasses", "glasses_dark",
        cost=1, tags={"wealth": 0, "striving": 0, "rebellion": 2},
        flavor_text="Sees the cracks in everything, stylishly.",
    ),

    # ---- NECK slot ----
    # Legacy (wealth)
    Accessory(
        "neck_medallion", "Gold Medallion", "neck", "neck_medallion",
        cost=1, tags={"wealth": 2, "striving": 0, "rebellion": 0},
        flavor_text="A family crest, or close enough to one.",
    ),
    # Meritocrat (striving)
    Accessory(
        "neck_bowtie", "The Bowtie", "neck", "neck_bowtie",
        cost=1, tags={"wealth": 0, "striving": 2, "rebellion": 0},
        flavor_text="Tied with the precision of a scholarship application.",
    ),
    # Rebellion
    Accessory(
        "neck_pin", "Safety Pin", "neck", "neck_pin",
        cost=1, tags={"wealth": 0, "striving": 0, "rebellion": 2},
        flavor_text="Holds things together when institutions won't.",
    ),

    # ---- TOP slot ----
    # Legacy (wealth)
    Accessory(
        "top_blazer", "Crimson Blazer", "top", "top_blazer",
        cost=1, tags={"wealth": 2, "striving": 0, "rebellion": 0},
        flavor_text="Understated. Which is the most expensive statement.",
    ),
    # Meritocrat (striving)
    Accessory(
        "top_hoodie", "Grey Hoodie", "top", "top_hoodie",
        cost=1, tags={"wealth": 0, "striving": 2, "rebellion": 0},
        flavor_text="Clean. Simple. Interview-adjacent.",
    ),
    # Rebellion
    Accessory(
        "top_band", "Band Tee", "top", "top_band",
        cost=1, tags={"wealth": 0, "striving": 0, "rebellion": 2},
        flavor_text="The color of things that cannot be ignored.",
    ),

    # ---- BOTTOMS slot ----
    # Legacy (wealth)
    Accessory(
        "bottoms_trousers", "Pressed Trousers", "bottoms", "bottoms_trousers",
        cost=1, tags={"wealth": 2, "striving": 0, "rebellion": 0},
        flavor_text="Pristine. Dry-clean only. Someone else does the cleaning.",
    ),
    # Meritocrat (striving)
    Accessory(
        "bottoms_jeans", "Clean Jeans", "bottoms", "bottoms_jeans",
        cost=1, tags={"wealth": 0, "striving": 2, "rebellion": 0},
        flavor_text="Practical. Durable. Worn to every obligation.",
    ),
    # Rebellion
    Accessory(
        "bottoms_punk", "Plaid Skirt", "bottoms", "bottoms_punk",
        cost=1, tags={"wealth": 0, "striving": 0, "rebellion": 2},
        flavor_text="Tartan by choice, not tradition. There's a difference.",
    ),
]

# Lookup by ID for quick access
ACCESSORY_LOOKUP = {a.id: a for a in ACCESSORIES}

# Group by slot
ACCESSORIES_BY_SLOT = {}
for acc in ACCESSORIES:
    ACCESSORIES_BY_SLOT.setdefault(acc.slot, []).append(acc)
