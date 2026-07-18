"""
Player state for Eldritch: location, sanity, and inventory.
"""

from dataclasses import dataclass, field
from typing import List, Set

from game.sanity import tier_for, SanityTier

MAX_SANITY = 100
MIN_SANITY = 0


@dataclass
class Player:
    location: str
    sanity: int = MAX_SANITY
    inventory: List[str] = field(default_factory=list)
    visited: Set[str] = field(default_factory=set)

    @property
    def sanity_tier(self) -> SanityTier:
        return tier_for(self.sanity)

    def adjust_sanity(self, amount: int) -> int:
        """Change sanity by `amount` (positive or negative), clamped to
        [MIN_SANITY, MAX_SANITY]. Returns the new sanity value."""
        self.sanity = max(MIN_SANITY, min(MAX_SANITY, self.sanity + amount))
        return self.sanity

    def add_item(self, item_id: str) -> None:
        self.inventory.append(item_id)

    def remove_item(self, item_id: str) -> bool:
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            return True
        return False

    def has_item(self, item_id: str) -> bool:
        return item_id in self.inventory
