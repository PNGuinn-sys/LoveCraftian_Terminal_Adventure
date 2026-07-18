"""
Smoke tests for the parser, sanity system, and world generation.

Run directly with: python tests/test_engine.py
(No pytest dependency required yet - kept stdlib-only for now.)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from game.parser import parse
from game.rng import make_rng
from game.sanity import SanityTier, distort, tier_for
from game.world import ITEM_TEMPLATES, generate_world


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


def test_world_generation_is_deterministic_for_a_seed():
    rng1, _ = make_rng(12345)
    world1 = generate_world(rng1)

    rng2, _ = make_rng(12345)
    world2 = generate_world(rng2)

    assert world1 == world2


def test_items_are_placed_in_a_valid_room():
    rng, _ = make_rng(42)
    world = generate_world(rng)

    for item_id, template in ITEM_TEMPLATES.items():
        rooms_containing_item = [
            room_id for room_id, room in world.items() if item_id in room["items"]
        ]
        assert len(rooms_containing_item) == 1
        assert rooms_containing_item[0] in template["valid_rooms"]


def test_cellar_starts_locked():
    rng, _ = make_rng(7)
    world = generate_world(rng)
    assert world["corridor"]["exits"]["down"]["locked"] is True


def test_visited_rooms_tracked_on_movement():
    import io
    from contextlib import redirect_stdout

    import main as game_main
    from game.player import Player
    from game.world import START_ROOM, generate_events, generate_world

    rng, _ = make_rng(1)
    rooms = generate_world(rng)
    events = generate_events(rng)
    player = Player(location=START_ROOM)
    player.visited.add(player.location)

    with redirect_stdout(io.StringIO()):
        game_main.handle_command(parse("go north"), player, rooms, events, rng)

    assert player.location == "corridor"
    assert player.visited == {"foyer", "corridor"}


def test_status_output_includes_key_fields():
    import io
    from contextlib import redirect_stdout

    import main as game_main
    from game.player import Player
    from game.world import START_ROOM, generate_world

    rng, _ = make_rng(1)
    rooms = generate_world(rng)
    player = Player(location=START_ROOM)
    player.visited.add(player.location)
    player.add_item("brass_key")

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        game_main.show_status(player, rooms)
    output = buffer.getvalue()

    assert rooms[START_ROOM]["name"] in output
    assert "Sanity: 100/100" in output
    assert "brass key" in output
    assert "Rooms explored: 1/" in output


def run_all():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed.")


if __name__ == "__main__":
    run_all()
