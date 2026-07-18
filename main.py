"""
Eldritch - a Lovecraftian terminal adventure.
Entry point / game loop.

This is an early engine scaffold: the parser, player state, and sanity
system are wired together against a tiny placeholder world (see
game/world.py) so the core loop can be tested end to end. Real story
content, items, and encounters will replace the placeholder world once
the setting is designed.
"""

from game.parser import parse
from game.player import Player
from game.sanity import distort
from game.world import ROOMS, ITEMS, START_ROOM


def match_item(target, item_ids):
    """Find an item id in item_ids matching the player's typed target,
    by full name, item id, or a single word from the name."""
    if not target:
        return None
    for item_id in item_ids:
        name = ITEMS[item_id]["name"]
        if target == name or target == item_id or target in name.split():
            return item_id
    return None


def describe_room(player: Player) -> None:
    room = ROOMS[player.location]
    text = distort(room["description"], player.sanity)

    print(f"\n{room['name']}")
    print(text)

    exits = list(room["exits"].keys())
    if exits:
        print(f"Exits: {', '.join(exits)}")

    if room["items"]:
        names = [ITEMS[i]["name"] for i in room["items"]]
        print(f"You notice: {', '.join(names)}")


def handle_command(cmd, player: Player) -> bool:
    """Execute a parsed command. Returns False if the game should stop."""
    room = ROOMS[player.location]

    if cmd.verb == "quit":
        print("\nYou step back from the threshold. Some things are better left unseen.")
        return False

    elif cmd.verb == "look":
        describe_room(player)

    elif cmd.verb == "go":
        direction = cmd.direction
        if not direction:
            print("Go where?")
        elif direction not in room["exits"]:
            print("You can't go that way.")
        else:
            player.location = room["exits"][direction]
            describe_room(player)

    elif cmd.verb == "inventory":
        if player.inventory:
            names = [ITEMS[i]["name"] for i in player.inventory]
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
                print(f"You take the {ITEMS[matched]['name']}.")
                sanity_effect = ITEMS[matched].get("on_take_sanity")
                if sanity_effect:
                    player.adjust_sanity(sanity_effect)
                    flavor = ITEMS[matched].get("on_take_text")
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
                print(f"You set down the {ITEMS[matched]['name']}.")

    elif cmd.verb == "use":
        print("Nothing happens - item interactions aren't wired up yet.")

    elif cmd.verb in ("save", "load"):
        print("Saving isn't wired up yet - that's coming in a later step.")

    elif cmd.verb == "status":
        print(f"Sanity: {player.sanity}/100 ({player.sanity_tier.value})")

    elif cmd.verb == "help":
        print(
            "Commands: look, go <direction>, take <item>, drop <item>, "
            "inventory, status, quit"
        )

    elif cmd.verb == "unknown":
        print("You're not sure how to do that.")

    elif cmd.verb == "empty":
        pass

    return True


def main() -> None:
    player = Player(location=START_ROOM)

    print("=" * 60)
    print("ELDRITCH")
    print("a terminal adventure  (engine test build)")
    print("=" * 60)
    describe_room(player)

    running = True
    while running:
        try:
            raw = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        cmd = parse(raw)
        running = handle_command(cmd, player)


if __name__ == "__main__":
    main()
