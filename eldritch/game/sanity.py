"""
Sanity system for Eldritch.

Sanity isn't just a number on a status screen - as it drops, the game's
own narration becomes unreliable. This module defines the sanity tiers
and the text distortion applied at each level.

This is a first pass focused on narration. Gameplay-altering effects
(false exits, misdirected movement, etc.) will build on this once we
have real rooms to design around.
"""

from enum import Enum
import random


class SanityTier(Enum):
    LUCID = "Lucid"
    UNEASY = "Uneasy"
    FRAYING = "Fraying"
    BROKEN = "Broken"


_THRESHOLDS = (
    (80, SanityTier.LUCID),
    (50, SanityTier.UNEASY),
    (25, SanityTier.FRAYING),
    (0, SanityTier.BROKEN),
)

_INTRUSIVE_THOUGHTS = [
    "(That wasn't there a moment ago. Was it?)",
    "(You've stood in this exact spot before. You're certain of it.)",
    "(Something is keeping count of your footsteps.)",
    "(The proportions of this place are wrong, and getting wronger.)",
    "(You no longer remember which way you came from.)",
]


def tier_for(sanity: int) -> SanityTier:
    """Return the SanityTier for a given sanity value."""
    for threshold, tier in _THRESHOLDS:
        if sanity >= threshold:
            return tier
    return SanityTier.BROKEN


def distort(text: str, sanity: int, rng: random.Random = random) -> str:
    """Apply sanity-based narration distortion to a piece of room text."""
    tier = tier_for(sanity)

    if tier is SanityTier.LUCID:
        return text

    if tier is SanityTier.UNEASY:
        if rng.random() < 0.3:
            text = f"{text} {rng.choice(_INTRUSIVE_THOUGHTS)}"
        return text

    if tier is SanityTier.FRAYING:
        if rng.random() < 0.6:
            text = f"{text} {rng.choice(_INTRUSIVE_THOUGHTS)}"
        if rng.random() < 0.35:
            text = _stutter(text, rng)
        return text

    # BROKEN
    text = f"{text} {rng.choice(_INTRUSIVE_THOUGHTS)}"
    if rng.random() < 0.5:
        text = _stutter(text, rng)
    if rng.random() < 0.4:
        text += " ...or is that not quite what you saw?"
    return text


def _stutter(text: str, rng: random.Random) -> str:
    """Repeat a random word mid-sentence, as if the narrator lost their place."""
    words = text.split(" ")
    if len(words) < 5:
        return text
    idx = rng.randrange(1, len(words) - 1)
    words.insert(idx, words[idx])
    return " ".join(words)
