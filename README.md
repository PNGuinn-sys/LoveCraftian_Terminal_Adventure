# LoveCraftian_Terminal_Adventure
Lovecraft lore based Terminal adventure
# ELDRITCH
### A Lovecraftian Terminal Adventure

> *"The most merciful thing in the world, I think, is the inability of the human mind to correlate all its contents."*

**Status:** 🌑 Early Development — Design Phase
**Working title** — open to renaming once the story takes shape.

---

## About

A text-based, terminal-only horror adventure inspired by the cosmic dread of
H.P. Lovecraft's Mythos. You play an investigator pulled into events that
were never meant to be understood — exploring shadowed locations, gathering
fragments of forbidden knowledge, and trying to survive with your mind
(mostly) intact.

No graphics, no sound — just prose, choices, and the growing sense that you
already know too much.

## Planned Features

- **Room-by-room exploration** via classic text-adventure commands
- **Deep sanity system** — as sanity drops, the game itself becomes an
  unreliable narrator: descriptions warp, exits mislead, items may not be
  what they seem
- **Investigation-first survival** — danger is about avoidance and escape,
  not combat; encounters are things to evade, outwit, or flee, not fight
- **Inventory & item-based puzzles**
- **Multiple endings** shaped by your choices and sanity level
- **Random/triggered events** — entities, omens, things half-glimpsed
- **Save / load** so no one has to finish a descent into madness in one sitting
- **Optional terminal styling** — color and light ASCII art for atmosphere

## Tech Stack

- **Python 3.10+**
- Standard library only to start — no dependencies required to run
- Optional later additions (e.g. `rich` or `colorama` for terminal color)
  if/when we want fancier presentation

## Project Structure (planned)

```
eldritch/
├── main.py                # Entry point — starts the game loop
├── game/
│   ├── __init__.py
│   ├── player.py           # Player state: sanity, health, inventory
│   ├── world.py             # Map graph & room navigation
│   ├── rooms.py               # Room definitions & descriptions
│   ├── items.py                # Item definitions & interactions
│   ├── entities.py              # Monsters, NPCs, encounters
│   ├── sanity.py                 # Sanity effects & narrative triggers
│   ├── parser.py                  # Command input parsing
│   └── save_load.py                # Save/load system
├── data/                   # Room/item/story content (JSON or similar)
├── tests/                  # Unit tests
├── requirements.txt
└── README.md
```

*(Structure is a starting proposal — will evolve as the game does.)*

## Getting Started

### Requirements
- Python 3.10 or later

### Installation
```bash
git clone <repo-url>
cd eldritch
pip install -r requirements.txt   # currently empty — stdlib only
```

### Running the Game
```bash
python main.py
```

## How to Play (planned commands)

| Command            | Effect                          |
|---------------------|----------------------------------|
| `look`               | Describe current surroundings   |
| `go <direction>`      | Move (north/south/east/west/in/out) |
| `take <item>`          | Pick up an item                 |
| `drop <item>`            | Drop an item                    |
| `inventory` / `i`         | List carried items              |
| `examine <object>`         | Look closer at something        |
| `use <item>`                | Use/apply an item               |
| `save` / `load`              | Save or load progress           |
| `quit`                         | Exit the game                   |

## Roadmap

- [ ] Core game loop & command parser
- [ ] World map & room system
- [ ] Sanity mechanic
- [ ] Inventory & puzzle logic
- [ ] First playable chapter
- [ ] Save/load system
- [ ] Polish — styling, pacing, additional endings

## Design Notes

Decisions locked in so far:

- **Setting:** Original/timeless — not tied to a specific real-world era.
  We're free to invent our own locations, factions, and fragments of
  forbidden lore rather than reusing Arkham/Innsmouth-style canon.
- **Sanity mechanic:** Deep. Sanity isn't just a number in a status bar —
  as it drops, the narration itself becomes unreliable. Room descriptions
  may shift or contradict themselves, exits may mislead, and the player
  may not always be able to trust what the game tells them.
- **Danger/combat:** Investigation-focused. There's no combat system —
  threats are survived by avoiding, hiding from, or escaping them. Tension
  comes from evasion, not fighting.

Still open:
- Story premise / inciting incident
- Number & structure of chapters or acts
- How many distinct endings, and what determines them
- Tone calibration (slow-burn dread vs. more frequent scares)

## License

TBD — MIT suggested for a personal/open project.
