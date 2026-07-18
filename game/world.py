"""
Placeholder world data, used to test-drive the engine (parser, player,
sanity system) end to end. This will be replaced once the real setting
and story are designed - nothing here is canon.
"""

START_ROOM = "start"

ROOMS = {
    "start": {
        "name": "A Room Without a Name",
        "description": (
            "You are standing in a bare stone chamber. The air is cold "
            "and smells faintly of salt, though you are certain you are "
            "nowhere near the sea. A narrow doorway leads north."
        ),
        "exits": {"north": "corridor"},
        "items": ["brass_key"],
    },
    "corridor": {
        "name": "The Long Corridor",
        "description": (
            "A corridor stretches ahead, longer than the room it came "
            "from should reasonably allow. The walls seem to lean "
            "inward as you walk."
        ),
        "exits": {"south": "start"},
        "items": [],
    },
}

ITEMS = {
    "brass_key": {
        "name": "brass key",
        "description": "An old brass key, warm to the touch despite the cold.",
        # Optional hooks - a taste of sanity being affected by the world,
        # not just by fixed encounters.
        "on_take_sanity": -40,
        "on_take_text": (
            "The moment your fingers close around it, the key pulses "
            "faintly - like something breathing. The cold of the room "
            "no longer seems to reach you."
        ),
    },
}
