"""
Loads and validates a scenario (an "adventure") from its data files.

A scenario lives in data/<name>/ as a handful of YAML files:
  manifest.yaml - title, description, starting room, intro text
  rooms.yaml     - room templates (description variants, exits)
  items.yaml      - item templates (placement pools, sanity effects)
  events.yaml       - random one-time event templates

Nothing in here is game *logic* - it's purely reading and sanity-checking
the shape of hand-authored content, so a mistake in a data file shows up
as a clear error message at startup instead of a crash mid-playthrough.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import yaml


class ScenarioError(Exception):
    """Raised when a scenario's data files are missing, malformed, or
    internally inconsistent."""


@dataclass
class Scenario:
    name: str
    title: str
    description: str
    start_room: str
    rooms: Dict[str, dict]
    items: Dict[str, dict]
    events: List[dict]
    intro: str = ""


def load_scenario(data_dir: Path) -> Scenario:
    """Load and validate a scenario's data files from `data_dir`
    (e.g. data/manor). Raises ScenarioError on any problem."""
    manifest = _load_yaml(data_dir / "manifest.yaml") or {}
    rooms = _load_yaml(data_dir / "rooms.yaml") or {}
    items = _load_yaml(data_dir / "items.yaml") or {}
    events = _load_yaml(data_dir / "events.yaml") or []

    if "start_room" not in manifest:
        raise ScenarioError(
            f"{data_dir / 'manifest.yaml'}: missing required field 'start_room'"
        )

    scenario = Scenario(
        name=data_dir.name,
        title=manifest.get("title", data_dir.name),
        description=manifest.get("description", ""),
        intro=manifest.get("intro", ""),
        start_room=manifest["start_room"],
        rooms=rooms,
        items=items,
        events=events,
    )

    errors = validate_scenario(scenario)
    if errors:
        formatted = "\n".join(f"  - {e}" for e in errors)
        raise ScenarioError(
            f"Scenario '{scenario.name}' failed validation:\n{formatted}"
        )

    return scenario


def _load_yaml(path: Path):
    if not path.exists():
        raise ScenarioError(f"Missing required file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ScenarioError(f"{path}: invalid YAML - {e}") from e


def validate_scenario(scenario: Scenario) -> List[str]:
    """Return a list of human-readable problems with the scenario's
    content. An empty list means the scenario is valid."""
    errors: List[str] = []
    room_ids = set(scenario.rooms.keys())

    if scenario.start_room not in room_ids:
        errors.append(f"start_room '{scenario.start_room}' is not a defined room")

    for room_id, room in scenario.rooms.items():
        if not room.get("description_variants"):
            errors.append(f"room '{room_id}' has no description_variants")

        for direction, exit_info in room.get("exits", {}).items():
            target = exit_info.get("target")
            requires_all_clues = exit_info.get("requires_all_clues")

            if target is None and not requires_all_clues:
                errors.append(
                    f"room '{room_id}' exit '{direction}' has no target "
                    f"(and isn't a requires_all_clues exit)"
                )
            if target is not None and target not in room_ids:
                errors.append(
                    f"room '{room_id}' exit '{direction}' targets "
                    f"unknown room '{target}'"
                )

            unlock_item = exit_info.get("unlock_item")
            if exit_info.get("locked") and not unlock_item and not requires_all_clues:
                errors.append(
                    f"room '{room_id}' exit '{direction}' is locked but has "
                    f"no unlock_item"
                )
            if unlock_item and unlock_item not in scenario.items:
                errors.append(
                    f"room '{room_id}' exit '{direction}' unlock_item "
                    f"'{unlock_item}' is not a defined item"
                )

    for item_id, item in scenario.items.items():
        if not item.get("valid_rooms"):
            errors.append(f"item '{item_id}' has no valid_rooms")
        for room_id in item.get("valid_rooms", []):
            if room_id not in room_ids:
                errors.append(
                    f"item '{item_id}' valid_rooms references unknown "
                    f"room '{room_id}'"
                )

    for event in scenario.events:
        event_id = event.get("id", "<missing id>")
        if "id" not in event:
            errors.append("an event is missing its 'id' field")
        for room_id in event.get("rooms", []):
            if room_id not in room_ids:
                errors.append(
                    f"event '{event_id}' references unknown room '{room_id}'"
                )

    has_clue = any(item.get("is_clue") for item in scenario.items.values())
    has_win_exit = any(
        exit_info.get("requires_all_clues")
        for room in scenario.rooms.values()
        for exit_info in room.get("exits", {}).values()
    )
    if has_clue and not has_win_exit:
        errors.append("items are marked is_clue, but no exit has requires_all_clues")
    if has_win_exit and not has_clue:
        errors.append("an exit has requires_all_clues, but no item is marked is_clue")

    return errors
