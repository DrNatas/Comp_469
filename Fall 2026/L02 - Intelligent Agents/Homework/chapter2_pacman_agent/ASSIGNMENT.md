# Assignment: Build an Intelligent Agent

**Reading:** AIMA 4th edition, Chapter 2, all sections.
**Files you edit:** `agent.py` and `writeup/WRITEUP_TEMPLATE.md`. Nothing else.
**Points:** 100. See `RUBRIC.md`.

---

## The situation

`agent.py` currently holds a simple reflex agent. It looks at the current
percept, walks toward the nearest food, and does nothing else. It cannot see
ghosts, does not know which way it is facing, does not know whether a power
pellet is active, and forgets everything the instant it acts.

Run `python tools/play.py` and watch it die.

Your job is to turn it into a **model-based, utility-based agent**: AIMA
Figure 2.12 crossed with Figure 2.14. When you are done it should clear the
maze in most episodes instead of being eaten in the first ten seconds.

The seven tasks below are marked in `agent.py` as `TODO(CH2-1)` through
`TODO(CH2-7)`. Do them in order; each one builds on the last. Delete each
marker as you finish it.

---

## Part 1 - The agent program (60 points)

### CH2-1 - Give the agent working sensors

The environment builds your percept by reflection. It reads the field names
declared on your `Percept` dataclass and fills in exactly those, and nothing
else. A field you do not declare is a thing your agent cannot see.

Right now `Percept` declares four fields. Add three more:

| Field | Type | What it gives you |
|---|---|---|
| `current_direction` | `tuple[int, int]` | the action taken last turn |
| `released_ghosts` | `tuple[tuple[int, int], ...]` | positions of ghosts that are out of the house |
| `frightened_time_remaining` | `float` | seconds of power-pellet mode left, `0.0` when off |

Use those exact names. The complete list of sensable fields is in the
`agent.py` docstring; anything else raises an error that names the offender.

> **Why `released_ghosts` and not `ghosts`?** Both exist. `ghosts` includes
> ghosts still locked in the house, which cannot reach you. Picking between
> them is a modelling decision, and you should say which you chose and why
> in the write-up.

*Done when:* `test_ch2_1_*` passes.

### CH2-2 - Name every preference

The starter hides its preferences inside `choose_action` as bare numbers:
`-2.0`, `25.0`, `80.0`. A reader cannot tell what the agent wants without
tracing the arithmetic.

Move all of them into `UtilityWeights` as named fields, and add weights for
everything you introduce later. At minimum you need named weights covering:

- distance to the nearest food
- landing on a regular pellet, and on a power pellet
- catching a frightened ghost, and closing distance on one
- colliding with a dangerous ghost
- a dangerous ghost one, two, and three steps away
- keeping a comfortable distance, with a cap
- continuing in the same direction
- revisiting a tile you have already eaten
- reversing straight back into the tile you just left

Pick your own numbers. You will defend them in the write-up.

*Done when:* `test_ch2_2_*` passes. One of those tests overrides your
collision weight and checks the agent's behaviour changes, so the weights
have to be the numbers actually driving the decision, not decoration
alongside hard-coded literals.

### CH2-3 and CH2-4 - Give the agent a memory

A simple reflex agent cannot distinguish "this corridor is full of pellets"
from "I ate this corridor 40 turns ago", because both produce the same
percept. That is why it paces. AIMA's answer is internal state: a compact
summary of the percept sequence.

In `__init__`, add:

```python
self.visit_counts: dict[tuple[int, int], int] = {}
self.position_history: deque[tuple[int, int]] = deque(maxlen=4)
self.revisit_decisions = 0
self.backtrack_decisions = 0
```

Then implement `update_internal_state(percept)` so that one call records the
current position in both structures.

Keep `position_history` short. It is a rolling window for spotting an
immediate reversal, not a log of the episode.

*Done when:* `test_ch2_3_*` and `test_ch2_4_*` pass.

### CH2-5 - Write the utility function

Implement `evaluate_action(percept, action)`. It scores **one** action and
returns `(total_utility, contributions)`, where `contributions` maps each
term name to the signed number it contributed.

Required keys, and what they mean:

| Key | Weighted? | Meaning |
|---|---|---|
| `food_distance` | yes | pull toward the nearest remaining food |
| `regular_pellet` | yes | bonus for landing on a pellet |
| `power_pellet` | yes | bonus for landing on a power pellet |
| `ghost` | yes | the whole ghost term, danger or prey |
| `continuation` | yes | small bonus for not turning |
| `revisit` | yes | penalty scaled by visit count |
| `backtrack` | yes | penalty for immediate reversal |
| `food_distance_steps` | no | raw distance, for reporting |
| `ghost_distance_steps` | no | raw distance, for reporting |
| `revisit_count` | no | raw count, for reporting |

The seven weighted terms must sum to `total_utility`. The three raw values
are evidence for the status line and must not be added in.

Behaviour to get right:

- Compute the landing tile with `self.maze.step(percept.player, action)`.
- Get distances from `self.maze.distance(start, goals)`. Do not write your
  own search.
- **Frightened:** landing on a ghost is a large gain; otherwise closer
  ghosts are more attractive, which means a *negative* coefficient on
  distance.
- **Not frightened:** landing on a ghost is disastrous. One, two, and three
  steps away should be progressively less alarming. Past that, more space is
  mildly good, but cap it, or the agent will find a safe corner and sit in
  it forever.
- Penalise the landing tile in proportion to `visit_counts`.
- Penalise the landing tile if it is the one you occupied two turns ago.
- Raise `ValueError` if `action` is not in `percept.legal_actions`.

*Done when:* `test_ch2_5_*` passes.

### CH2-6 and CH2-7 - Select, and explain

Rewrite `choose_action` to:

1. Return `(0, 0)` with `"No legal"` in `last_reason` if there are no legal
   actions.
2. Call `update_internal_state` exactly once.
3. Score every legal action with `evaluate_action` and return the best.
   Iterate in `percept.legal_actions` order and compare with strict `>`, so
   ties always break the same way and your trial results are reproducible.
4. Never return an illegal action.

Then set `last_reason` to one short line containing the direction name and
the tokens `U=`, `food=`, `ghost=`, and `memory=`, where memory is the sum
of the revisit and backtrack contributions. Example:

```
LEFT | U=-31.0 | food=3 | ghost=6 | memory=-2.0
```

That line is drawn live in the game window. It is the fastest debugging tool
you have here: you can watch a percept become a number and the number become
a move.

*Done when:* `test_ch2_6_*` and `test_ch2_7_*` pass, and
`python -m unittest discover -s tests` reports OK.

---

## Part 2 - Trials (10 points)

With the tests passing, run:

```
python tools/run_trials.py --agents student,simple_reflex,random --count 30
python tools/run_trials.py --agents student,simple_reflex --count 30 --difficulty hard
```

This writes `results/trials.csv` and `results/summary.csv`. Submit both.

On `normal` a finished agent should clear the maze in most episodes. If your
win rate is under 60 percent, something is wrong with your ghost weights or
your food-distance term.

On `hard` the ghosts move faster than you are. Expect to lose most episodes
even with a correct agent. That is not a bug, and Part 3 asks you about it.

---

## Part 3 - Write-up (30 points)

Fill in `writeup/WRITEUP_TEMPLATE.md`. It asks for:

1. A PEAS description of this task environment.
2. The seven environment properties from AIMA Figure 2.6, each with a
   one-line justification drawn from the code.
3. Which agent type yours is, mapped to a figure in Section 2.4, and what it
   would take to move it one step further.
4. The difference between the performance measure and your utility function,
   with the specific place each one lives in this codebase.
5. Evidence that a rational agent is not the same as a successful one: find
   a seed where your agent played sensibly and still lost, and explain why
   that does not make it irrational.
6. Your trial table, and three to five sentences interpreting it.

Keep it tight. Two to three pages is plenty. I am grading whether you can
connect the code to the chapter, not word count.

---

## Submitting

Submit a single zip named `lastname_firstname_ch2.zip` containing:

```
agent.py
results/trials.csv
results/summary.csv
writeup/WRITEUP_TEMPLATE.md      (filled in, keep the filename)
```

Do not include the `pacman/` package or your virtual environment.

---

## Two ways to lose points for no reason

**Editing the environment.** If `pacman/` differs from what you were given,
the grader runs your `agent.py` against the original anyway, and anything
that depended on your edits fails.

**Implementing search.** `self.maze.distance` already exists. Writing your
own BFS is not extra credit; it is the wrong chapter, and the contract tests
check for it.
