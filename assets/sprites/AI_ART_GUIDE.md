# AI Sprite Generation Guide for HYBRIS

## Character Dimensions & Body Maps
- **Cat:** 365x587px — body center x=175, eyes at y=225, neck at y=351, torso y=358-460
- **Dog:** 447x548px — body center x=222, eyes at y=178, neck at y=310, torso y=318-430
- **Fox:** 522x609px — body center x=310, eyes at y=228, neck at y=368, torso y=370-500 (tail on LEFT side, body on RIGHT)

## Reference guide images
- `ref_cat_guide.png` — cat with body zones marked
- `ref_dog_guide.png` — dog with body zones marked
- `ref_fox_guide.png` — fox with body zones marked
Red crosshair = eye center, green line = neck, blue box = torso region

## ITEMS NEEDED (15 total)

### BODY-FITTED TOPS (need 1 per species = 3 variants each)
Each top is the SAME canvas size as the character. Only the clothing pixels are drawn, everything else is transparent. The clothing must precisely follow the character's body contours.

1. **Crimson Blazer** (`top_blazer_cat.png`, `top_blazer_dog.png`, `top_blazer_fox.png`, + `top_blazer.png` = copy of fox)
   - Deep crimson/burgundy blazer with gold trim along lapels and cuffs
   - V-neck showing white shirt collar underneath
   - 2-3 gold buttons down the front
   - Structured shoulders, visible sleeve creases
   - Small breast pocket
   - 3-4 shades of red for depth

2. **Grey Hoodie** (`top_hoodie_cat.png`, `top_hoodie_dog.png`, `top_hoodie_fox.png`, + `top_hoodie.png`)
   - Medium gray zip-up hoodie
   - Hood visible behind neck/head
   - Center zipper line
   - Kangaroo pocket
   - Drawstrings hanging from hood
   - Ribbed cuffs and waistband
   - 3 shades of gray

3. **Band Tee** (`top_band_cat.png`, `top_band_dog.png`, `top_band_fox.png`, + `top_band.png`)
   - Black/very dark t-shirt
   - Short sleeves
   - Small red graphic/logo on chest (abstract/lightning bolt)
   - Slightly wrinkled/casual look
   - 2-3 shades of near-black

### BODY-FITTED BOTTOMS (need 1 per species = 3 variants each)
Same rules as tops — full canvas, transparent background, only clothing pixels.

4. **Pressed Trousers** (`bottoms_trousers_cat.png`, etc.)
   - Khaki/tan pressed trousers
   - Belt with small buckle at waist
   - Sharp creases down each leg
   - Clean hemmed bottoms
   - Covers legs down to above the feet
   - 3 shades of tan/khaki

5. **Clean Jeans** (`bottoms_jeans_cat.png`, etc.)
   - Medium blue denim
   - Darker waistband
   - Side seam details
   - Subtle denim texture (slight color variation)
   - Covers legs to above feet
   - 3 shades of blue

6. **Plaid Skirt** (`bottoms_punk_cat.png`, etc.)
   - Red tartan/plaid pattern
   - Dark navy/black cross-stripes making the plaid
   - Shorter length (covers waist to mid-thigh)
   - Slight A-line flare
   - Dark waistband
   - Pleated look

### STANDALONE HATS (1 file each, NOT species-specific)
Small sprites, transparent background. Positioned via code anchors.

7. **Mortarboard** (`hat_graduation.png`) — ~250x130px
   - Classic graduation cap, dark navy/black
   - Flat square board on top
   - Gold tassel hanging from left
   - Cap dome underneath

8. **Baseball Cap** (`hat_cap.png`) — ~230x130px
   - Gray dome with blue brim
   - Curved casual shape
   - Button on top

9. **Slouch Beanie** (`hat_beanie.png`) — ~210x130px
   - Dark charcoal ribbed beanie
   - Slouches to one side
   - Red accent stripe

### STANDALONE GLASSES (1 file each)
Small sprites. Must be wide enough to span between the eyes.

10. **Gold Rounds** (`glasses_wire.png`) — ~180x55px
    - Round gold wire-frame glasses
    - Thin frames, visible lenses
    - Bridge and temple arms

11. **Square Frames** (`glasses_rect.png`) — ~185x50px
    - Dark rectangular frames
    - Professional look

12. **Dark Shades** (`glasses_dark.png`) — ~195x55px
    - Solid dark/opaque sunglasses
    - Wider lenses, cool look
    - Must be fully opaque (no see-through)

### STANDALONE NECK ITEMS (1 file each)

13. **Gold Medallion** (`neck_medallion.png`) — ~170x120px
    - Gold chain in V-shape
    - Round medallion pendant hanging from center

14. **The Bowtie** (`neck_bowtie.png`) — ~170x80px
    - Navy blue butterfly bowtie
    - Center knot

15. **Safety Pin** (`neck_pin.png`) — ~50x80px
    - Silver safety pin
    - Punk aesthetic

## CRITICAL RULES
- ALL sprites must have TRANSPARENT backgrounds (PNG with alpha)
- Pixel art style matching the existing characters (~13px per game-pixel)
- Body-fitted items: canvas size MUST match the character exactly
- Body-fitted items: clothing pixels must align perfectly with the character body
- Use the guide images as reference for positioning
- 3-4 levels of shading per color (highlight, mid, shadow, deep shadow)
- Clean pixel edges, no anti-aliasing
