import json
import sys
import os
from datetime import datetime
from src.settings import SAVES_DIR, EXPORTS_DIR

IS_WEB = sys.platform == "emscripten"


def save_local(persistent, filename="character_save.json"):
    """Save character data to the local saves/ directory."""
    if IS_WEB:
        return None
    os.makedirs(SAVES_DIR, exist_ok=True)
    path = os.path.join(SAVES_DIR, filename)
    with open(path, "w") as f:
        json.dump(_build_payload(persistent), f, indent=2)
    return path


def export_downloadable(persistent, filename=None):
    """Export character data to the exports/ directory."""
    if IS_WEB:
        return None
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    if filename is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        species = persistent.get("species", "unknown")
        filename = f"hybris_{species}_{ts}.json"
    path = os.path.join(EXPORTS_DIR, filename)
    with open(path, "w") as f:
        json.dump(_build_payload(persistent), f, indent=2)
    return path


def _build_payload(persistent):
    """Construct the canonical export payload."""
    return {
        "game": "HYBRIS: Create Your Applicant",
        "version": "1.0",
        "character": {
            "species": persistent.get("species"),
            "profile": persistent.get("profile"),
            "profile_label": persistent.get("profile_label"),
            "equipped_accessories": persistent.get("equipped_accessories", {}),
        },
        "stats": persistent.get("stats", {}),
        "applications": persistent.get("applications", []),
        "decisions": persistent.get("decisions", {}),
        "meta": {
            "quiz_answers": persistent.get("quiz_answers", []),
            "cosmetic_tags": persistent.get("cosmetic_tags", {}),
            "tokens_remaining": persistent.get("tokens_remaining", 0),
        },
    }
