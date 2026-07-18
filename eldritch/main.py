"""
Eldritch - a Lovecraftian terminal adventure.
Entry point / game loop.

Each run generates its own version of the manor: room description
variants, item placement, and random events are all resolved from a
seeded RNG at startup (see game/world.py, game/rng.py). Random by
default, so the game plays out differently each time - but a specific
seed can be pinned with --seed for a reproducible run.
"""

import argparse

from game.parser import parse
from game.player import Player
from game.rng import make_rng
from game.sanity import distort
from game.world import ITEM_TEMPLATES, START_ROOM, generate_events, generate_world


def match_item(target, item_ids):
    """Find an item id in item_ids matching the player's typed target,
    by full name, item id, or a single word from the name."""
    if not target:
        return None
    for item_id in item_ids:
        name = ITEM_TEMPLATES[item_id]["name"]
        if target == name or target == item_id or target in name.split():
            return item_id
    return None


def describe_room(player: Player, rooms: dict, rng) -> None:
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
        names = [ITEM_TEMPLATES[i]["name"] for i in room["items"]]
        print(f"You notice: {', '.join(names)}")


def show_status(player: Player, rooms: dict) -> None:
    room = rooms[player.location]

    print("\n" + "-" * 40)
    print(f"Location: {room['name']}")
    print(f"Sanity: {player.sanity}/100 ({player.sanity_tier.value})")

    if player.inventory:
        names = [ITEM_TEMPLATES[i]["name"] for i in player.inventory]
        print(f"Carrying: {', '.join(names)}")
    else:
        print("Carrying: nothing")

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


def handle_command(cmd, player: Player, rooms: dict, events: list, rng) -> bool:
    """Execute a parsed command. Returns False if the game should stop."""
    room = rooms[player.location]

    if cmd.verb == "quit":
        print("\nYou step back from the threshold. Some things are better left unseen.")
        return False

    elif cmd.verb == "look":
        describe_room(player, rooms, rng)

    elif cmd.verb == "go":
        direction = cmd.direction
        if not direction:
            print("Go where?")
        elif direction not in room["exits"]:
            print("You can't go that way.")
        else:
            exit_info = room["exits"][direction]
            if exit_info.get("locked"):
                print(exit_info.get("locked_text", "That way is locked."))
            else:
                player.location = exit_info["target"]
                player.visited.add(player.location)
                describe_room(player, rooms, rng)
                check_events(player, rooms, events, rng)

    elif cmd.verb == "inventory":
        if player.inventory:
            names = [ITEM_TEMPLATES[i]["name"] for i in player.inventory]
            print("You are carrying: " + ", ".join(names))
        else:
            print("You are carrying nothing.")

    elif cmd.verb == "take":
        if not cmd.target:
            print("Take what?")
        else:
            matched = match_item(cmd.target, room["items"])
            if not matched:
                print("You don't see that here.")
            else:
                room["items"].remove(matched)
                player.add_item(matched)
                template = ITEM_TEMPLATES[matched]
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
            matched = match_item(cmd.target, player.inventory)
            if not matched:
                print("You aren't carrying that.")
            else:
                player.remove_item(matched)
                room["items"].append(matched)
                print(f"You set down the {ITEM_TEMPLATES[matched]['name']}.")

    elif cmd.verb == "use":
        if not cmd.target:
            print("Use what?")
        else:
            matched = match_item(cmd.target, player.inventory)
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
        show_status(player, rooms)

    elif cmd.verb == "help":
        print(
            "Commands: look, go <direction>, take <item>, drop <item>, "
            "use <item>, inventory, status, quit"
        )

    elif cmd.verb == "unknown":
        print("You're not sure how to do that.")

    elif cmd.verb == "empty":
        pass

    return True


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Eldritch - a terminal adventure")
    arg_parser.add_argument(
        "--seed", type=int, default=None,
        help="Pin a specific world seed for a reproducible run",
    )
    arg_parser.add_argument(
        "--show-seed", action="store_true",
        help="Print the seed used this run, for debugging",
    )
    args = arg_parser.parse_args()

    rng, seed = make_rng(args.seed)
    rooms = generate_world(rng)
    events = generate_events(rng)
    player = Player(location=START_ROOM)
    player.visited.add(player.location)

    print("=" * 60)
    print("ELDRITCH")
    print("a terminal adventure")
    print("=" * 60)
    if args.show_seed:
        print(f"[seed: {seed}]")

    describe_room(player, rooms, rng)

    running = True
    while running:
        try:
            raw = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        cmd = parse(raw)
        running = handle_command(cmd, player, rooms, events, rng)


if __name__ == "__main__":
    main()
