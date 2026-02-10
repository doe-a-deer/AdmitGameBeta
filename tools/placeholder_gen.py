#!/usr/bin/env python3
"""
Generate placeholder sprites for HYBRIS Game 1.
Creates colored rectangles with text labels for all required assets.
Run from the project root: python tools/placeholder_gen.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()

SPRITE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sprites")


def make_dirs():
    for sub in ["characters", "accessories", "ui"]:
        os.makedirs(os.path.join(SPRITE_DIR, sub), exist_ok=True)


def make_character(name, color, filename):
    """Create a 64x64 character placeholder."""
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    # Body
    pygame.draw.ellipse(s, color, (8, 20, 48, 40))
    # Head
    pygame.draw.circle(s, color, (32, 18), 14)
    # Eyes
    pygame.draw.circle(s, (255, 255, 255), (26, 16), 4)
    pygame.draw.circle(s, (255, 255, 255), (38, 16), 4)
    pygame.draw.circle(s, (20, 20, 30), (26, 16), 2)
    pygame.draw.circle(s, (20, 20, 30), (38, 16), 2)

    if name == "cat":
        # Ears (triangles)
        pygame.draw.polygon(s, color, [(20, 8), (26, 2), (28, 10)])
        pygame.draw.polygon(s, color, [(36, 10), (38, 2), (44, 8)])
        # Whiskers
        pygame.draw.line(s, (200, 200, 200), (16, 22), (8, 20), 1)
        pygame.draw.line(s, (200, 200, 200), (16, 24), (8, 26), 1)
        pygame.draw.line(s, (200, 200, 200), (48, 22), (56, 20), 1)
        pygame.draw.line(s, (200, 200, 200), (48, 24), (56, 26), 1)
    elif name == "dog":
        # Floppy ears
        pygame.draw.ellipse(s, tuple(max(0, c - 30) for c in color), (14, 10, 10, 18))
        pygame.draw.ellipse(s, tuple(max(0, c - 30) for c in color), (40, 10, 10, 18))
        # Nose
        pygame.draw.ellipse(s, (40, 30, 30), (29, 22, 6, 4))
    elif name == "fox":
        # Pointy ears
        pygame.draw.polygon(s, color, [(18, 10), (22, 0), (28, 8)])
        pygame.draw.polygon(s, color, [(36, 8), (42, 0), (46, 10)])
        # White ear tips
        pygame.draw.polygon(s, (255, 255, 255), [(21, 6), (22, 1), (25, 6)])
        pygame.draw.polygon(s, (255, 255, 255), [(39, 6), (42, 1), (43, 6)])
        # Nose
        pygame.draw.polygon(s, (30, 30, 30), [(30, 24), (34, 24), (32, 26)])

    # Label
    font = pygame.font.SysFont("monospace", 8)
    label = font.render(name.upper(), True, (255, 255, 255))
    s.blit(label, (32 - label.get_width() // 2, 52))

    path = os.path.join(SPRITE_DIR, "characters", filename)
    pygame.image.save(s, path)
    print(f"  Created {path}")


def make_accessory(acc_id, slot, tag_type, label_text, filename):
    """Create a 64x64 accessory overlay placeholder."""
    s = pygame.Surface((64, 64), pygame.SRCALPHA)

    tag_colors = {
        "wealth": (200, 180, 60),
        "striving": (60, 140, 200),
        "rebellion": (200, 60, 60),
    }
    color = tag_colors.get(tag_type, (180, 180, 180))

    if slot == "hat":
        pygame.draw.rect(s, (*color, 200), (18, 0, 28, 10))
        pygame.draw.rect(s, (*color, 220), (14, 8, 36, 5))
    elif slot == "glasses":
        pygame.draw.circle(s, (*color, 200), (26, 16), 6, 2)
        pygame.draw.circle(s, (*color, 200), (38, 16), 6, 2)
        pygame.draw.line(s, (*color, 200), (32, 16), (32, 16), 2)
    elif slot == "neck":
        if "bowtie" in acc_id:
            pygame.draw.polygon(s, (*color, 200), [(24, 30), (32, 34), (40, 30), (32, 38)])
        elif "safetypin" in acc_id:
            pygame.draw.line(s, (*color, 220), (28, 32), (36, 38), 2)
            pygame.draw.line(s, (*color, 220), (36, 38), (36, 32), 2)
        else:
            pygame.draw.arc(s, (*color, 200), (20, 28, 24, 16), 0, 3.14, 3)
    elif slot == "pin":
        pygame.draw.circle(s, (*color, 220), (32, 42), 5)
        pygame.draw.circle(s, (*color, 180), (32, 42), 3)
    elif slot == "top":
        pygame.draw.rect(s, (*color, 140), (10, 30, 44, 28))
        # Collar line
        pygame.draw.line(s, (*color, 200), (22, 30), (32, 36), 2)
        pygame.draw.line(s, (*color, 200), (42, 30), (32, 36), 2)

    path = os.path.join(SPRITE_DIR, "accessories", filename)
    pygame.image.save(s, path)
    print(f"  Created {path}")


def main():
    make_dirs()
    print("Generating character sprites...")
    make_character("cat", (220, 160, 80), "cat_base.png")
    make_character("dog", (160, 120, 80), "dog_base.png")
    make_character("fox", (200, 100, 60), "fox_base.png")

    print("Generating accessory sprites...")
    accessories = [
        ("hat_crown", "hat", "wealth", "Crown"),
        ("hat_beanie", "hat", "striving", "Beanie"),
        ("hat_beret", "hat", "rebellion", "Beret"),
        ("glasses_monocle", "glasses", "wealth", "Monocle"),
        ("glasses_round", "glasses", "striving", "Glasses"),
        ("glasses_cracked", "glasses", "rebellion", "Cracked"),
        ("neck_bowtie", "neck", "wealth", "Bowtie"),
        ("neck_scarf", "neck", "striving", "Scarf"),
        ("neck_safetypin", "neck", "rebellion", "SafePin"),
        ("pin_gold_merit", "pin", "wealth", "GoldPin"),
        ("pin_merit", "pin", "striving", "MeritPin"),
        ("pin_tarnished", "pin", "rebellion", "TarnPin"),
        ("top_blazer", "top", "wealth", "Blazer"),
        ("top_hoodie", "top", "striving", "Hoodie"),
        ("top_vest", "top", "rebellion", "Vest"),
    ]
    for acc_id, slot, tag, label in accessories:
        make_accessory(acc_id, slot, tag, label, f"{acc_id}.png")

    print("Done! All placeholder sprites generated.")


if __name__ == "__main__":
    main()
