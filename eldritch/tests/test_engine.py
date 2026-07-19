"""
Smoke tests for the parser, sanity system, world generation, and the
scenario loader/validator.

Run directly with: python tests/test_engine.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from game.content_loader import Scenario, load_scenario, validate_scenario
from game.parser import parse
from game.rng import make_rng
from game.sanity import SanityTier, distort, tier_for
from game.world import generate_events, generate_world

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANOR_SCENARIO = load_scenario(PROJECT_ROOT / "data" / "manor")


# --- Parser ----------------------------------------------------------------

def test_parser_basic_verbs():
    assert parse("look").verb == "look"
    assert parse("l").verb == "look"
    assert parse("").verb == "empty"
    assert parse("asdkjhaskjd").verb == "unknown"


def test_parser_movement():
    cmd = parse("go north")
    assert cmd.verb == "go" and cmd.direction == "north"

    cmd = parse("n")
    assert cmd.verb == "go" and cmd.direction == "north"


def test_parser_target():
    cmd = parse("take brass key")
    assert cmd.verb == "take"
    assert cmd.target == "brass key"


# --- Sanity ------------------------------------------------------------------

def test_sanity_tiers():
    assert tier_for(100) == SanityTier.LUCID
    assert tier_for(80) == SanityTier.LUCID
    assert tier_for(79) == SanityTier.UNEASY
    assert tier_for(50) == SanityTier.UNEASY
    assert tier_for(49) == SanityTier.FRAYING
    assert tier_for(25) == SanityTier.FRAYING
    assert tier_for(24) == SanityTier.BROKEN
    assert tier_for(0) == SanityTier.BROKEN


def test_distort_lucid_unchanged():
    text = "The room is quiet."
    assert distort(text, 100) == text


# --- Scenario loading & validation --------------------------------------------

def test_manor_scenario_loads_and_validates():
    assert MANOR_SCENARIO.start_room in MANOR_SCENARIO.rooms
    assert len(MANOR_SCENARIO.rooms) == 7
    assert validate_scenario(MANOR_SCENARIO) == []


def test_validator_catches_bad_exit_target():
    scenario = Scenario(
        name="broken", title="Broken", description="", start_room="a",
        rooms={"a": {
            "name": "Room A",
            "description_variants": ["A room."],
            "exits": {"north": {"target": "nowhere"}},
        }},
        items={}, events=[],
    )
    errors = validate_scenario(scenario)
    assert any("unknown room 'nowhere'" in e for e in errors)


def test_validator_catches_locked_exit_without_unlock_item():
    scenario = Scenario(
        name="broken", title="Broken", description="", start_room="a",
        rooms={
            "a": {
                "name": "Room A",
                "description_variants": ["A room."],
                "exits": {"north": {"target": "b", "locked": True}},
            },
            "b": {
                "name": "Room B",
                "description_variants": ["Another room."],
                "exits": {},
            },
        },
        items={}, events=[],
    )
    errors = validate_scenario(scenario)
    assert any("no unlock_item" in e for e in errors)


def test_validator_catches_clue_without_win_exit():
    scenario = Scenario(
        name="broken", title="Broken", description="", start_room="a",
        rooms={"a": {
            "name": "Room A",
            "description_variants": ["A room."],
            "exits": {},
        }},
        items={"clue_1": {"name": "a clue", "valid_rooms": ["a"], "is_clue": True}},
        events=[],
    )
    errors = validate_scenario(scenario)
    assert any("requires_all_clues" in e for e in errors)


def test_validator_catches_item_in_unknown_room():
    scenario = Scenario(
        name="broken", title="Broken", description="", start_room="a",
        rooms={"a": {
            "name": "Room A",
            "description_variants": ["A room."],
            "exits": {},
        }},
        items={"thing": {"name": "a thing", "valid_rooms": ["nowhere"]}},
        events=[],
    )
    errors = validate_scenario(scenario)
    assert any("unknown room 'nowhere'" in e for e in errors)


# --- World generation ------------------------------------------------------------

def test_world_generation_is_deterministic_for_a_seed():
    rng1, _ = make_rng(12345)
    world1 = generate_world(MANOR_SCENARIO, rng1)

    rng2, _ = make_rng(12345)
    world2 = generate_world(MANOR_SCENARIO, rng2)

    assert world1 == world2


def test_items_are_placed_in_a_valid_room():
    rng, _ = make_rng(42)
    world = generate_world(MANOR_SCENARIO, rng)

    for item_id, template in MANOR_SCENARIO.items.items():
        rooms_containing_item = [
            room_id for room_id, room in world.items() if item_id in room["items"]
        ]
        assert len(rooms_containing_item) == 1
        assert rooms_containing_item[0] in template["valid_rooms"]


def test_cellar_starts_locked():
    rng, _ = make_rng(7)
    world = generate_world(MANOR_SCENARIO, rng)
    assert world["corridor"]["exits"]["down"]["locked"] is True


# --- Engine integration (via main.handle_command) -------------------------------

def test_visited_rooms_tracked_on_movement():
    import io
    from contextlib import redirect_stdout

    import main as game_main
    from game.player import Player

    rng, _ = make_rng(1)
    rooms = generate_world(MANOR_SCENARIO, rng)
    events = generate_events(MANOR_SCENARIO, rng)
    player = Player(location=MANOR_SCENARIO.start_room)
    player.visited.add(player.location)

    with redirect_stdout(io.StringIO()):
        game_main.handle_command(parse("go north"), player, rooms, events, rng, MANOR_SCENARIO)

    assert player.location == "corridor"
    assert player.visited == {"foyer", "corridor"}


def test_status_output_includes_key_fields():
    import io
    from contextlib import redirect_stdout

    import main as game_main
    from game.player import Player

    rng, _ = make_rng(1)
    rooms = generate_world(MANOR_SCENARIO, rng)
    player = Player(location=MANOR_SCENARIO.start_room)
    player.visited.add(player.location)
    player.add_item("brass_key")

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        game_main.show_status(player, rooms, MANOR_SCENARIO)
    output = buffer.getvalue()

    assert rooms[MANOR_SCENARIO.start_room]["name"] in output
    assert "Sanity: 100/100" in output
    assert "brass key" in output
    assert "Rooms explored: 1/" in output


def test_advance_dread_manifests_at_threshold():
    from game.entities import DREAD_THRESHOLD, advance_dread
    from game.player import Player

    class AlwaysHitsRandom:
        def random(self):
            return 0.0  # always below any chance threshold

    player = Player(location="foyer")
    rng_stub = AlwaysHitsRandom()

    manifested = False
    for _ in range(DREAD_THRESHOLD):
        manifested = advance_dread(player, rng_stub)

    assert manifested is True
    assert player.presence_active is True
    assert player.dread == DREAD_THRESHOLD


def test_reaching_out_with_all_clues_wins():
    import main as game_main
    from game.player import Player

    rng, _ = make_rng(5)
    rooms = generate_world(MANOR_SCENARIO, rng)
    events = generate_events(MANOR_SCENARIO, rng)

    player = Player(location="foyer")
    player.visited.add(player.location)
    for item_id, template in MANOR_SCENARIO.items.items():
        if template.get("is_clue"):
            player.add_item(item_id)

    outcome = game_main.handle_command(parse("go out"), player, rooms, events, rng, MANOR_SCENARIO)
    assert outcome == "win"


def test_reaching_out_without_all_clues_is_blocked():
    import main as game_main
    from game.player import Player

    rng, _ = make_rng(5)
    rooms = generate_world(MANOR_SCENARIO, rng)
    events = generate_events(MANOR_SCENARIO, rng)

    player = Player(location="foyer")
    player.visited.add(player.location)

    outcome = game_main.handle_command(parse("go out"), player, rooms, events, rng, MANOR_SCENARIO)
    assert outcome == "continue"
    assert player.location == "foyer"


def test_caught_if_not_evading_when_presence_active():
    import main as game_main
    from game.player import Player

    rng, _ = make_rng(9)
    rooms = generate_world(MANOR_SCENARIO, rng)
    events = generate_events(MANOR_SCENARIO, rng)

    player = Player(location="foyer")
    player.presence_active = True

    outcome = game_main.handle_command(parse("look"), player, rooms, events, rng, MANOR_SCENARIO)
    assert outcome == "caught"


def test_fleeing_resolves_presence():
    import main as game_main
    from game.player import Player

    rng, _ = make_rng(11)
    rooms = generate_world(MANOR_SCENARIO, rng)
    events = generate_events(MANOR_SCENARIO, rng)

    player = Player(location="foyer")
    player.visited.add(player.location)
    player.presence_active = True
    player.dread = 3

    outcome = game_main.handle_command(parse("go north"), player, rooms, events, rng, MANOR_SCENARIO)
    assert outcome == "continue"
    assert player.presence_active is False
    assert player.dread == 0
    assert player.location == "corridor"


def test_hiding_resolves_presence():
    import main as game_main
    from game.player import Player

    rng, _ = make_rng(13)
    rooms = generate_world(MANOR_SCENARIO, rng)
    events = generate_events(MANOR_SCENARIO, rng)

    player = Player(location="foyer")
    player.presence_active = True
    player.dread = 3

    outcome = game_main.handle_command(parse("hide"), player, rooms, events, rng, MANOR_SCENARIO)
    assert outcome == "continue"
    assert player.presence_active is False
    assert player.dread == 0


def test_sanity_reaching_zero_ends_game():
    import main as game_main
    from game.player import Player

    rng, _ = make_rng(21)
    rooms = generate_world(MANOR_SCENARIO, rng)
    events = generate_events(MANOR_SCENARIO, rng)

    player = Player(location="foyer")
    player.visited.add(player.location)
    player.adjust_sanity(-97)  # sanity now 3
    player.adjust_sanity(-10)  # clamped to 0

    outcome = game_main.handle_command(parse("status"), player, rooms, events, rng, MANOR_SCENARIO)
    assert outcome == "broken"
    assert player.sanity == 0


def run_all():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed.")


if __name__ == "__main__":
    run_all()
