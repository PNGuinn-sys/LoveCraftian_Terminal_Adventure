"""
The presence - an unseen threat stalking the manor.

This isn't a monster to fight; it's built entirely around avoidance.
Dread quietly accumulates while the player explores, building faster
the further their sanity has slipped. Once dread crosses a threshold,
the presence manifests in the player's current room, and their very
next action has to be an evasion (fleeing to another room, or hiding)
or they're caught.
"""

from game.sanity import SanityTier

DREAD_THRESHOLD = 3

_DREAD_CHANCE_BY_TIER = {
    SanityTier.LUCID: 0.12,
    SanityTier.UNEASY: 0.22,
    SanityTier.FRAYING: 0.35,
    SanityTier.BROKEN: 0.50,
}


def advance_dread(player, rng) -> bool:
    """Roll for the presence's dread to build by one step, based on the
    player's current sanity tier. Returns True if it just manifested in
    the player's room this turn (setting player.presence_active)."""
    if player.presence_active:
        return False

    chance = _DREAD_CHANCE_BY_TIER[player.sanity_tier]
    if rng.random() < chance:
        player.dread += 1

    if player.dread >= DREAD_THRESHOLD:
        player.presence_active = True
        return True

    return False


def resolve_evasion(player) -> None:
    """Call once the player successfully evades (flees or hides)."""
    player.presence_active = False
    player.dread = 0
