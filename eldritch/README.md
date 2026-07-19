# ELDRITCH
### A Lovecraftian Terminal Adventure

> *"The most merciful thing in the world, I think, is the inability of the human mind to correlate all its contents."*

**Status:** 🏚️ First playable chapter — "The Manor" (win/lose both work end to end)
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

## Features

- **Room-by-room exploration** via classic text-adventure commands ✅
- **Deep sanity system** — as sanity drops, room narration becomes
  unreliable (intrusive asides, stuttering text), and it also raises the
  odds of the presence finding you ✅
- **Investigation-first survival** — no combat; an unseen presence stalks
  the manor, and getting caught by it or losing your sanity entirely
  both end the run ✅
- **Randomized per playthrough** — item locations, room description
  flavor, and which random events fire are all reshuffled by a seeded RNG
  each run (`--seed` to reproduce a specific one) ✅
- **A real win condition** — piece together the manor's story by finding
  all its scattered clues, then reach the front door ✅
- **Inventory & a locked-door puzzle** ✅
- Multiple/varied endings, more puzzles, a bigger manor — planned
- **Save / load** — not wired up yet
- **Optional terminal styling** — color and light ASCII art — not started

## Tech Stack

- **Python 3.10+**
- **PyYAML** — the only dependency. Adventure content (rooms, items,
  events) lives in hand-authored YAML data files rather than Python code.

## Project Structure

```
eldritch/
├── main.py                # Entry point — loads a scenario, runs the game loop
├── game/                  # The engine - generic, has no story content in it
│   ├── __init__.py
│   ├── content_loader.py   # Loads + validates a scenario's YAML files
│   ├── player.py            # Player state: location, sanity, inventory
│   ├── parser.py              # Command input parsing
│   ├── sanity.py               # Sanity tiers & narration distortion
│   ├── entities.py              # The stalking presence (dread system)
│   ├── world.py                  # Resolves a scenario's templates into one playthrough
│   └── rng.py                     # Seeded RNG for reproducible randomness
├── data/                  # Adventure content lives here, not in code
│   └── manor/               # The first scenario ("The Manor")
│       ├── manifest.yaml     # Title, intro text, starting room
│       ├── rooms.yaml         # Rooms: description variants, exits
│       ├── items.yaml          # Items: placement pools, sanity effects
│       └── events.yaml          # Random one-time events
├── tests/
│   └── test_engine.py      # Parser, sanity, loader/validator, world-gen, win/lose
├── requirements.txt        # PyYAML
└── README.md
```

Adding a new adventure means adding a new folder under `data/` with those
same four files — the engine itself doesn't need to change. Run one with
`python main.py --scenario <folder-name>`.

Not yet started: `save_load.py`.

## Getting Started

### Requirements
- Python 3.10 or later

### Installation
```bash
git clone <repo-url>
cd eldritch
pip install -r requirements.txt   # installs PyYAML
```

### Running the Game
```bash
python main.py                                  # a fresh, randomized run of "manor"
python main.py --scenario manor                 # same thing, explicit
python main.py --seed 42 --show-seed            # a reproducible run, for testing
```

If a scenario's data files have a mistake in them (a typo'd room name, a
locked door with no key, etc.), the game will refuse to start and print
exactly what's wrong, rather than crashing mid-playthrough.

### Running the Tests
```bash
python tests/test_engine.py
```

## How to Play

| Command              | Effect                                    |
|-----------------------|--------------------------------------------|
| `look` / `l`            | Describe current surroundings             |
| `go <direction>` / `n`,`s`,`e`,`w`,`u`,`d` | Move (also `in`/`out`) |
| `take <item>`             | Pick up an item                           |
| `drop <item>`               | Drop an item                              |
| `use <item>`                  | Use an item (e.g. a key on a locked door) |
| `inventory` / `i`               | List carried items                        |
| `status` / `stats`                | Location, sanity, inventory, clue & room progress |
| `hide` / `wait`                     | Evade the presence when it manifests      |
| `save` / `load`                       | Not wired up yet                        |
| `quit`                                  | Exit the game                         |

**Winning:** find all four clues hidden around the manor, then go `out`
through the front door.
**Losing:** your sanity reaches 0, or the presence catches you when it
manifests and your next move isn't fleeing or hiding.

## Roadmap

- [x] Core game loop & command parser
- [x] World map & room system (randomized per playthrough)
- [x] Sanity mechanic (narration distortion + gameplay consequence via the presence)
- [x] Inventory & a first puzzle (locked door)
- [x] First playable chapter — win and lose both work end to end
- [x] Content split into data files — adventures are now YAML, not Python;
      engine validates them at startup
- [ ] Save/load system
- [ ] More rooms, more clues, more puzzles — the manor is still small
- [ ] A second scenario, to prove the engine really is adventure-agnostic
- [ ] Additional/varied endings beyond win/caught/broken
- [ ] Polish — styling, pacing

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
- **The threat:** an unseen presence, not a monster you see coming. Dread
  builds quietly (faster at low sanity) and manifests as a sudden "you are
  not alone" moment — your very next action has to be fleeing or hiding.
- **The goal:** piece together the manor's story via scattered clues, then
  leave through a front door that was locked until you understood enough.

Still open:
- Story premise / inciting incident
- Number & structure of chapters or acts
- How many distinct endings, and what determines them
- Tone calibration (slow-burn dread vs. more frequent scares)

## License

TBD — MIT suggested for a personal/open project.
