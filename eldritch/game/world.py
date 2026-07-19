"""
World generation for Eldritch.

Given a loaded Scenario (see game/content_loader.py), resolves its
templates into one concrete world for a single playthrough: picks a
description variant per room, and places each item in one randomly
chosen room from its valid pool. Content itself lives entirely in the
scenario's data files - this module only knows how to assemble it.
"""

from typing import Dict, List


def generate_world(scenario, rng) -> Dict[str, dict]:
    rooms = {}
    for room_id, template in scenario.rooms.items():
        rooms[room_id] = {
            "name": template["name"],
            "description": rng.choice(template["description_variants"]),
            "exits": {d: dict(info) for d, info in template.get("exits", {}).items()},
            "items": [],
        }

    for item_id, template in scenario.items.items():
        room_id = rng.choice(template["valid_rooms"])
        rooms[room_id]["items"].append(item_id)

    return rooms


def generate_events(scenario, rng) -> List[dict]:
    """Return a fresh copy of the scenario's event table, each tagged as
    not-yet-fired. `rng` is accepted for symmetry with generate_world and
    in case future events need setup-time randomness."""
    return [dict(event, fired=False) for event in scenario.events]
