class Character:
    """Stores the player's character state."""

    def __init__(self, species="cat"):
        self.species = species
        self.equipped = {
            "hat": None,
            "glasses": None,
            "neck": None,
            "top": None,
            "bottoms": None,
        }
        self.owned_accessories = set()  # set of accessory IDs

    def equip(self, accessory):
        self.equipped[accessory.slot] = accessory.id
        self.owned_accessories.add(accessory.id)

    def unequip(self, slot):
        self.equipped[slot] = None

    def get_cosmetic_tags(self, accessory_lookup):
        """Sum up hidden tags from all equipped accessories."""
        tags = {"wealth": 0, "striving": 0, "rebellion": 0}
        for slot, acc_id in self.equipped.items():
            if acc_id and acc_id in accessory_lookup:
                acc = accessory_lookup[acc_id]
                for tag, val in acc.tags.items():
                    tags[tag] = tags.get(tag, 0) + val
        return tags
