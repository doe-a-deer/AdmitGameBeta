from dataclasses import dataclass, field


@dataclass
class Accessory:
    id: str
    display_name: str
    slot: str  # "hat", "glasses", "neck", "top", "bottoms"
    sprite_key: str
    cost: int
    tags: dict = field(default_factory=dict)  # {"wealth": 0, "striving": 0, "rebellion": 0}
    flavor_text: str = ""
