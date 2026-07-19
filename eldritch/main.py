"""
Eldritch - a Lovecraftian terminal adventure.
Entry point / game loop.

The engine itself (this file, plus game/) is generic - all actual story
content (rooms, items, events) lives in data files under data/<scenario>/
and is loaded and validated at startup (see game/content_loader.py).
Pick a scenario with --scenario (defaults to "manor").

Each run generates its own version of the world: room description
variants, item placement, and random events are all resolved from a
seeded RNG at startup (see game/world.py, game/rng.py). Random by
default, so the game plays out differently each time - but a specific
seed can be pinned with --seed for a reproducible run.

A playthrough has real stakes: piece together the scenario's story by
finding all its clues, then reach the exit to win. Sanity bottoming
out, or being caught by the presence that stalks the world, both end
the run.
"""

import argparse
import sys
from pathlib import Path

from game.content_loader import ScenarioError, load_scenario
from game.entities import advance_dread, resolve_evasion
from game.parser import parse
from game.player import Player
from game.rng import make_rng
from game.sanity import distort
from game.world import generate_events, generate_world

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

TURN_CONSUMING_VERBS = {"go", "look", "take", "drop", "use"}

PRESENCE_MANIFEST_TEXT = "\nThe air changes. You are no longer alone in this room."

CAUGHT_TEXT = (
    "\nYou hesitate a moment too long. Something closes the distance "
    "between you, and the world is quiet again.\n\n"
    "You are not found. Not by anyone who could still help."
)

SANITY_BROKEN_TEXT = (
    "\nSomething in you gives way. The walls are breathing now, or you "
    "are - you can no longer tell which.\n\n"
    "You will still be found here, eventually, sitting very still in a "
    "room that makes sense to no one but you."
)

WIN_TEXT = (
    "\nIt fits together now - all of it. What this place was for. What "
    "it cost the people who were here. What is, in some sense, still "
    "here.\n\n"
    "The way out opens without resistance this time, as if it were only "
    "ever waiting for you to understand. You do not look back as you "
    "cross the threshold.\n\n"
    "You made it out."
)


def match_item(target, item_ids, scenario):
    """Find an item id in item_ids matching the player's typed target,
    by full name, item id, or a single word from the name."""
    if not target:
        return None
    for item_id in item_ids:
        name = scenario.items[item_id]["name"]
        if target == name or target == item_id or target in name.split():
            return item_id
    return None


def clue_progress(player: Player, scenario):
    """Return (clues_found, total_clues)."""
    total = sum(1 for t in scenario.items.values() if t.get("is_clue"))
    found = sum(1 for i in player.inventory if scenario.items[i].get("is_clue"))
    return found, total


def has_all_clues(player: Player, scenario) -> bool:
    found, total = clue_progress(player, scenario)
    return total > 0 and found >= total


def describe_room(player: Player, rooms: dict, scenario, rng) -> None:
    room = rooms[player.location]
    text = distort(room["description"], player.sanity, rng)

    print(f"\n{room['name']}")
    print(text)

    exit_labels = []
    for direction, info in room["exits"].items():
        exit_labels.append(f"{direction} (locked)" if info.get("locked") else direction)
    if exit_labels:
        print(f"Exits: {', '.join(exit_labels)}")

    if room["items"]:
        names = [scenario.items[i]["name"] for i in room["items"]]
        print(f"You notice: {', '.join(names)}")


def show_status(player: Player, rooms: dict, scenario) -> None:
    room = rooms[player.location]
    found_clues, total_clues = clue_progress(player, scenario)

    print("\n" + "-" * 40)
    print(f"Location: {room['name']}")
    print(f"Sanity: {player.sanity}/100 ({player.sanity_tier.value})")

    if player.inventory:
        names = [scenario.items[i]["name"] for i in player.inventory]
        print(f"Carrying: {', '.join(names)}")
    else:
        print("Carrying: nothing")

    print(f"Clues found: {found_clues}/{total_clues}")
    print(f"Rooms explored: {len(player.visited)}/{len(rooms)}")
    print("-" * 40)


def check_events(player: Player, rooms: dict, events: list, rng) -> None:
    """Roll for any unfired event tied to the player's current room."""
    room_id = player.location
    for event in events:
        if event["fired"] or room_id not in event["rooms"]:
            continue
        if rng.random() < event["chance"]:
            event["fired"] = True
            print(f"\n{event['text']}")
            effect = event.get("sanity_effect")
            if effect:
                player.adjust_sanity(effect)


def handle_command(cmd, player: Player, rooms: dict, events: list, rng, scenario) -> str:
    """Execute a parsed command. Returns one of:
    'continue', 'quit', 'win', 'caught', 'broken'."""
    room = rooms[player.location]
    just_evaded = False

    # If the presence is active, the only valid responses are to flee to
    # another room or hide - anything else, including looking around or
    # checking your inventory, means you're caught.
    if player.presence_active:
        if cmd.verb == "quit":
            print("\nYou step back from the threshold. Some things are better left unseen.")
            return "quit"

        if cmd.verb == "hide":
            resolve_evasion(player)
            just_evaded = True
            print(
                "\nYou go still and hold your breath. After a long, "
                "silent moment, whatever it was moves on."
            )
            return "continue"

        can_flee = (
            cmd.verb == "go"
            and cmd.direction
            and cmd.direction in room["exits"]
            and not room["exits"][cmd.direction].get("locked")
            and not room["exits"][cmd.direction].get("requires_all_clues")
        )
        if can_flee:
            resolve_evasion(player)
            just_evaded = True
            print("\nYou don't wait to see what it is. You move.")
            # Fall through to the normal 'go' handling below.
        else:
            print(CAUGHT_TEXT)
            return "caught"

    if cmd.verb == "quit":
        print("\nYou step back from the threshold. Some things are better left unseen.")
        return "quit"

    elif cmd.verb == "look":
        describe_room(player, rooms, scenario, rng)

    elif cmd.verb == "go":
        direction = cmd.direction
        if not direction:
            print("Go where?")
        elif direction not in room["exits"]:
            print("You can't go that way.")
        else:
            exit_info = room["exits"][direction]
            if exit_info.get("requires_all_clues"):
                if has_all_clues(player, scenario):
                    print(WIN_TEXT)
                    return "win"
                print(exit_info.get("locked_text", "That way is blocked."))
            elif exit_info.get("locked"):
                print(exit_info.get("locked_text", "That way is locked."))
            else:
                player.location = exit_info["target"]
                player.visited.add(player.location)
                describe_room(player, rooms, scenario, rng)
                check_events(player, rooms, events, rng)

    elif cmd.verb == "inventory":
        if player.inventory:
            names = [scenario.items[i]["name"] for i in player.inventory]
            print("You are carrying: " + ", ".join(names))
        else:
            print("You are carrying nothing.")

    elif cmd.verb == "take":
        if not cmd.target:
            print("Take what?")
        else:
            matched = match_item(cmd.target, room["items"], scenario)
            if not matched:
                print("You don't see that here.")
            else:
                room["items"].remove(matched)
                player.add_item(matched)
                template = scenario.items[matched]
                print(f"You take the {template['name']}.")
                sanity_effect = template.get("on_take_sanity")
                if sanity_effect:
                    player.adjust_sanity(sanity_effect)
                    flavor = template.get("on_take_text")
                    if flavor:
                        print(flavor)

    elif cmd.verb == "drop":
        if not cmd.target:
            print("Drop what?")
        else:
            matched = match_item(cmd.target, player.inventory, scenario)
            if not matched:
                print("You aren't carrying that.")
            else:
                player.remove_item(matched)
                room["items"].append(matched)
                print(f"You set down the {scenario.items[matched]['name']}.")

    elif cmd.verb == "use":
        if not cmd.target:
            print("Use what?")
        else:
            matched = match_item(cmd.target, player.inventory, scenario)
            if not matched:
                print("You aren't carrying that.")
            else:
                unlocked_anything = False
                for info in room["exits"].values():
                    if info.get("locked") and info.get("unlock_item") == matched:
                        info["locked"] = False
                        print(info.get("unlock_text", "Something unlocks."))
                        unlocked_anything = True
                if not unlocked_anything:
                    print("Nothing happens.")

    elif cmd.verb in ("save", "load"):
        print("Saving isn't wired up yet - that's coming in a later step.")

    elif cmd.verb == "status":
        show_status(player, rooms, scenario)

    elif cmd.verb == "hide":
        print("There's nothing to hide from right now.")

    elif cmd.verb == "help":
        print(
            "Commands: look, go <direction>, take <item>, drop <item>, "
            "use <item>, inventory, status, hide, quit"
        )

    elif cmd.verb == "unknown":
        print("You're not sure how to do that.")

    elif cmd.verb == "empty":
        pass

    if cmd.verb in TURN_CONSUMING_VERBS and not player.presence_active and not just_evaded:
        if advance_dread(player, rng):
            print(PRESENCE_MANIFEST_TEXT)

    if player.sanity <= 0:
        print(SANITY_BROKEN_TEXT)
        return "broken"

    return "continue"


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Eldritch - a terminal adventure")
    arg_parser.add_argument(
        "--scenario", default="manor",
        help="Which adventure to load from data/ (default: manor)",
    )
    arg_parser.add_argument(
        "--seed", type=int, default=None,
        help="Pin a specific world seed for a reproducible run",
    )
    arg_parser.add_argument(
        "--show-seed", action="store_true",
        help="Print the seed used this run, for debugging",
    )
    args = arg_parser.parse_args()

    try:
        scenario = load_scenario(DATA_DIR / args.scenario)
    except ScenarioError as e:
        print(f"Could not load scenario '{args.scenario}':\n{e}", file=sys.stderr)
        sys.exit(1)

    rng, seed = make_rng(args.seed)
    rooms = generate_world(scenario, rng)
    events = generate_events(scenario, rng)
    player = Player(location=scenario.start_room)
    player.visited.add(player.location)

    print("=" * 60)
    print("ELDRITCH")
    print(scenario.title)
    print("=" * 60)
    if args.show_seed:
        print(f"[seed: {seed}]")
    if scenario.intro:
        print(f"\n{scenario.intro}")

    describe_room(player, rooms, scenario, rng)

    running = True
    while running:
        try:
            raw = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        cmd = parse(raw)
        outcome = handle_command(cmd, player, rooms, events, rng, scenario)
        running = outcome == "continue"


if __name__ == "__main__":
    main()
