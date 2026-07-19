"""
World content for Eldritch: an old manor.

This module holds *templates*, not a fixed world - each room has a few
description variants, each item has a pool of rooms it might spawn in,
and a small table of random one-time events. `generate_world()` resolves
all of that into one concrete manor for a single playthrough, using the
session's seeded RNG, so the same hand-authored content plays out a bit
differently each time.
"""

from typing import Dict, List


START_ROOM = "foyer"


# --- Room templates ----------------------------------------------------

ROOM_TEMPLATES = {
    "foyer": {
        "name": "The Foyer",
        "description_variants": [
            "Dust sheets cover most of the furniture, pale shapes in the "
            "gloom. A grand staircase curls up into darkness. The front "
            "door has already swung shut behind you.",
            "Your footsteps echo off a floor of cracked black-and-white "
            "tile. Somewhere above, something settles - old wood, you "
            "tell yourself - and goes quiet.",
        ],
        "exits": {
            "north": {"target": "corridor"},
            "east": {"target": "drawing_room"},
            "west": {"target": "study"},
            "out": {
                "requires_all_clues": True,
                "locked_text": (
                    "The front door won't budge. Whatever is happening "
                    "in this house, you haven't understood it yet."
                ),
            },
        },
    },
    "drawing_room": {
        "name": "The Drawing Room",
        "description_variants": [
            "Faded velvet armchairs face a cold hearth. A portrait above "
            "the mantel is too soot-stained to make out the face.",
            "The smell of old smoke lingers, though the fireplace has "
            "clearly been unused for years. Something about the room "
            "feels arranged, like a stage set waiting for its cast.",
        ],
        "exits": {"west": {"target": "foyer"}},
    },
    "study": {
        "name": "The Study",
        "description_variants": [
            "Shelves of ledgers line the walls, their spines swollen "
            "with damp. A heavy desk sits centered, its drawers slightly "
            "open, as if someone left in a hurry.",
            "Papers are scattered across the desk, covered in a cramped "
            "hand you don't recognize and can't quite stop trying to read.",
        ],
        "exits": {"east": {"target": "foyer"}},
    },
    "corridor": {
        "name": "The Upstairs Corridor",
        "description_variants": [
            "A long hallway, lined with doors that don't quite match "
            "the house's exterior proportions. A narrow stair leads "
            "down into darkness.",
            "The runner carpet is worn thin down the center of the "
            "hall, as though something paced here for a very long time.",
        ],
        "exits": {
            "south": {"target": "foyer"},
            "north": {"target": "library"},
            "down": {
                "target": "cellar",
                "locked": True,
                "unlock_item": "brass_key",
                "locked_text": "A heavy door blocks the stairs down. It's locked.",
                "unlock_text": "The key turns with a reluctant, grinding click.",
            },
        },
    },
    "library": {
        "name": "The Library",
        "description_variants": [
            "Floor-to-ceiling shelves, most of them empty. The few "
            "remaining books have titles in no alphabet you know.",
            "A reading table holds a single open book, its pages "
            "filled with diagrams that hurt to look at directly.",
        ],
        "exits": {
            "south": {"target": "corridor"},
            "up": {"target": "attic"},
        },
    },
    "attic": {
        "name": "The Attic",
        "description_variants": [
            "Low rafters force you to stoop. Trunks and broken furniture "
            "are stacked in shapes that seem almost deliberate.",
            "Light filters through a single grimy window. Dust hangs "
            "motionless in the air, as if the room is holding its breath.",
        ],
        "exits": {"down": {"target": "library"}},
    },
    "cellar": {
        "name": "The Cellar",
        "description_variants": [
            "The air is colder here, and wetter. Something has been "
            "dragged across the dirt floor, more than once.",
            "Shelves of preserves line one wall, jars gone black with "
            "age. You'd rather not look closely at what's floating in them.",
        ],
        "exits": {"up": {"target": "corridor"}},
    },
}


# --- Item templates ------------------------------------------------------

ITEM_TEMPLATES = {
    "brass_key": {
        "name": "brass key",
        "description": "An old brass key, warm to the touch despite the cold.",
        "valid_rooms": ["study", "drawing_room", "library"],
        "on_take_sanity": -10,
        "on_take_text": (
            "It's warmer than a piece of metal has any right to be. "
            "You pocket it anyway."
        ),
    },
    "old_journal": {
        "name": "old journal",
        "description": "A water-damaged journal, its later pages illegible.",
        "valid_rooms": ["study", "foyer", "drawing_room"],
        "on_take_sanity": -15,
        "on_take_text": (
            "Most of it is ruined, but one entry survives: 'It listens "
            "when we speak of leaving. We have stopped speaking of "
            "leaving.'"
        ),
        "is_clue": True,
    },
    "torn_letter": {
        "name": "torn letter",
        "description": "Half a letter, the rest burned away at the edges.",
        "valid_rooms": ["study", "library", "corridor"],
        "on_take_sanity": -10,
        "on_take_text": (
            "'...told them not to dig beneath the cellar. They didn't "
            "listen. None of us have felt quite whole since.'"
        ),
        "is_clue": True,
    },
    "childs_drawing": {
        "name": "child's drawing",
        "description": "A crayon drawing, curling at the corners.",
        "valid_rooms": ["attic", "drawing_room", "foyer"],
        "on_take_sanity": -10,
        "on_take_text": (
            "A child's crayon drawing of this house - and of a tall, "
            "thin shape standing in every window at once."
        ),
        "is_clue": True,
    },
    "family_photograph": {
        "name": "family photograph",
        "description": "A formal portrait, slightly out of focus.",
        "valid_rooms": ["cellar", "library", "corridor"],
        "on_take_sanity": -10,
        "on_take_text": (
            "A family of five, posed stiffly. You count them twice, "
            "certain you're miscounting. There are six chairs."
        ),
        "is_clue": True,
    },
}


# --- Random events ---------------------------------------------------------

EVENT_TEMPLATES = [
    {
        "id": "creaking_floor",
        "rooms": ["corridor", "library", "attic"],
        "chance": 0.35,
        "text": "A floorboard creaks behind you. When you turn, nothing is there.",
        "sanity_effect": -5,
    },
    {
        "id": "portrait_eyes",
        "rooms": ["drawing_room"],
        "chance": 0.5,
        "text": "For a moment, you'd swear the portrait's eyes had moved to follow you.",
        "sanity_effect": -10,
    },
    {
        "id": "distant_voice",
        "rooms": ["cellar", "attic"],
        "chance": 0.3,
        "text": "A voice, too far away to place, says something that sounds like your name.",
        "sanity_effect": -10,
    },
]


# --- World generation --------------------------------------------------------

def generate_world(rng) -> Dict[str, dict]:
    """Resolve room/item templates into one concrete world for this
    playthrough: pick a description variant per room, and place each
    item in one randomly chosen room from its valid pool."""
    rooms = {}
    for room_id, template in ROOM_TEMPLATES.items():
        rooms[room_id] = {
            "name": template["name"],
            "description": rng.choice(template["description_variants"]),
            "exits": {d: dict(info) for d, info in template["exits"].items()},
            "items": [],
        }

    for item_id, template in ITEM_TEMPLATES.items():
        room_id = rng.choice(template["valid_rooms"])
        rooms[room_id]["items"].append(item_id)

    return rooms


def generate_events(rng) -> List[dict]:
    """Return a fresh copy of the event table for this playthrough, each
    tagged as not-yet-fired. `rng` is accepted for symmetry with
    generate_world and in case future events need setup-time randomness."""
    return [dict(event, fired=False) for event in EVENT_TEMPLATES]
