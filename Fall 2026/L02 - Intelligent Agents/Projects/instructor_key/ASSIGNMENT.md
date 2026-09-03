# Assignment: Six Agents, One Chapter

**Reading:** AIMA 4th edition, Chapter 2, all sections.
**Files you edit:** the six `*_agent.py` files at the project root, and
`writeup/WRITEUP_TEMPLATE.md`. Nothing else.
**Points:** 100. See `RUBRIC.md`.

---

## The situation

AIMA Chapter 2 does not describe one kind of intelligent agent. It walks
through a sequence of them -- table-driven, simple reflex, model-based
reflex, goal-based, utility-based, and learning -- each one fixing a
specific failure of the one before it. This project asks you to build all
six, as six small Pac-Man agents sharing the same maze, the same percept
mechanism, and the same rules against implementing your own search.

The six files are meant to be done **in order**. Each one either fixes a
concrete failure you can watch the previous one make, or is imported
directly by a later part:

| # | File | AIMA figure | Fixes / adds |
|---|---|---|---|
| 1 | `table_driven_agent.py` | 2.4 intro, TABLE-DRIVEN-AGENT | Nothing -- this is the strawman AIMA uses to motivate everything else. |
| 2 | `simple_reflex_agent.py` | 2.10 | Replaces an impossible table with condition-action rules. |
| 3 | `model_based_agent.py` | 2.11 / 2.12 | Adds internal state, fixing the "paces forever" failure of Part 2. |
| 4 | `goal_based_agent.py` | 2.13 | Adds an explicit, changeable goal instead of fixed rules. |
| 5 | `utility_based_agent.py` | 2.14 | Replaces the goal test with a graded utility function. Builds on Part 3's state. |
| 6 | `learning_agent.py` | 2.15 | Adds a critic and a learning element that improve Part 5's weights from experience. Imports Part 5 directly. |

Run `python tools/play.py --agent table_driven` (and swap in each other
name) as you go. Compare against `python tools/play.py --agent greedy`,
a ghost-blind external baseline that is not a model answer for anything
here -- see the comments at the top of each file for what NOT to copy
from it.

Every environment fact you're allowed to use is listed in each file's own
docstring, repeated from `pacman/rules.py: Simulation.SENSOR_FIELDS`:
`player`, `current_direction`, `pellets`, `power_pellets`, `ghosts`,
`released_ghosts`, `legal_actions`, `frightened_time_remaining`. A
`Percept` dataclass field with any other name raises an error naming the
offender. `self.maze` is prior knowledge of the maze layout (walls,
`self.maze.step`, `self.maze.distance`) -- never live game state.

**Rules that apply to all six files**, same as the environment they wrap:

1. Edit the six `*_agent.py` files and nothing else in the code.
2. Each agent gets exactly two sources of information: the percept it is
   handed each turn, and the static `MazeModel` it is constructed with.
3. Do not implement DFS, BFS, uniform-cost, greedy, or A\*.
   `self.maze.distance` is provided so you never have to. Search
   algorithms are Chapter 3; this project is graded on agent structure.
4. Do not add third-party dependencies.

---

## Part 1 - Table-driven agent (6 points)

`table_driven_agent.py`. AIMA presents the table-driven agent, shows the
pseudocode, and immediately explains why nobody builds one: the table has
to have an entry for every possible percept SEQUENCE, and that blows up
combinatorially for anything but a toy percept. This part makes that
concrete instead of taking AIMA's word for it.

Your percept here is deliberately tiny: `current_direction` and
`legal_actions`. Build a real lookup table in `__init__` covering every
combination those two fields can take, and have `choose_action` do
nothing but look the key up (with a graceful fallback for a key you
somehow didn't enumerate).

TODO(CH2-1a), TODO(CH2-1b), TODO(CH2-1c) mark what to do in the file.

*Done when:* `test_part1_table_driven` passes.

## Part 2 - Simple reflex agent (8 points)

`simple_reflex_agent.py`. AIMA Figure 2.10: a short, ordered list of
condition-action rules over the CURRENT percept, and nothing else -- no
state, no lookahead. Run it and watch it clear the pellets near it, then
pace back and forth once that corridor empties: an empty corridor it just
cleared and an empty corridor it has never seen produce the exact same
percept, so it cannot tell them apart. That is not a bug to fix in this
part -- it is the reason Part 3 exists.

TODO(CH2-2a), TODO(CH2-2b) mark what to do.

*Done when:* `test_part2_simple_reflex` passes.

## Part 3 - Model-based reflex agent (10 points)

`model_based_agent.py`. AIMA Figures 2.11 / 2.12: keep Part 2's rules,
add internal state built from the percept sequence, and let one new rule
consult that state. This is still a reflex agent -- rules fire in order,
nothing is scored -- but now "have I been here before" is a condition it
can check.

TODO(CH2-3a), TODO(CH2-3b), TODO(CH2-3c) mark what to do.

*Done when:* `test_part3_model_based` passes.

## Part 4 - Goal-based agent (10 points)

`goal_based_agent.py`. AIMA Figure 2.13: an explicit GOAL and a GOAL
TEST, evaluated against what the model says each action would lead to.
No numeric weighing of competing preferences -- that is next. This
agent's goal changes with circumstances: chase food normally, but switch
to fleeing when a dangerous ghost gets close. That flexibility (new goals
without rewriting any rules) is the selling point AIMA gives goal-based
agents over reflex agents.

TODO(CH2-4a), TODO(CH2-4b), TODO(CH2-4c) mark what to do.

*Done when:* `test_part4_goal_based` passes.

## Part 5 - Utility-based agent (18 points)

`utility_based_agent.py`. AIMA Figure 2.14: keep Part 3's internal state
(given to you, unchanged), and replace rules/goal-tests with a single
UTILITY FUNCTION that scores every legal action on one numeric scale --
closer food is good, closer danger is bad, repeating yourself is mildly
bad -- and blends all of it into one number per action. This is the part
where "how good is this, all things considered" replaces "does this
satisfy the goal."

TODO(CH2-5a) (name your weights), TODO(CH2-5b) (`evaluate_action`), and
TODO(CH2-5c) (`choose_action`, replacing the starter policy already in
the file) mark what to do.

*Done when:* `test_part5_utility_based` passes, and
`test_trials_performance` shows your utility-based agent clearing the
maze in most episodes.

## Part 6 - Learning agent (8 points)

`learning_agent.py`. AIMA Figure 2.15 has four boxes: a PERFORMANCE
ELEMENT that acts (your Part 5 agent, imported directly and given to
you), a CRITIC that judges an episode (the environment's performance
measure, handed to you), a LEARNING ELEMENT that uses that judgement to
improve the performance element, and a PROBLEM GENERATOR that proposes
something to try. You build the last two: `propose_new_weights` (nudge a
couple of Part 5's weights) and `learn` (keep the nudge if it scored
better than your best so far, else revert).

This is hill-climbing over your own utility weights, not reinforcement
learning -- that's Chapter 21, out of scope here.

TODO(CH2-6a), TODO(CH2-6b) mark what to do. Once both are implemented,
train it:

```
python tools/train_learning_agent.py --generations 80
```

This drives the loop described above, prints a before/after comparison,
and saves `results/learned_weights.json`. After that, `python
tools/play.py --agent learning` and `tools/run_trials.py` will load and
use what training found automatically.

*Done when:* `test_part6_learning` passes, and a training run shows
`results/learned_weights.json` beating the naive starting point.

---

## Trials (10 points)

With every test passing, run:

```
python tools/run_trials.py --count 30
python tools/run_trials.py --count 30 --difficulty hard
python tools/train_learning_agent.py --generations 80
```

The first writes `results/trials.csv` and `results/summary.csv` covering
all six of your agents plus the `greedy` and `random` baselines. The
second is the same comparison on `hard`, where ghosts move faster than
you. The third produces `results/learned_weights.json`. Submit all three.

On `normal`, your Part 5 agent should clear the maze in most episodes; if
its win rate is under 60%, something is off in your ghost weights or your
food-distance term. On `hard`, expect to lose most episodes even with a
correct agent -- that is not a bug, and the write-up asks you about it.

---

## Write-up (30 points)

Fill in `writeup/WRITEUP_TEMPLATE.md`. It asks for:

1. A PEAS description of this task environment.
2. The seven environment properties from AIMA Figure 2.6, each justified
   from the code.
3. For EACH of the six parts: which figure in Section 2.4 it matches, and
   the one concrete thing that part added over the one before it.
4. The difference between the performance measure and a utility
   function, with the specific place each one lives in this codebase.
5. Evidence that a rational agent is not the same as a successful one:
   a seed where a sensible agent still lost, and why that does not make
   it irrational.
6. Your trial table (all six agents plus baselines, both difficulties),
   and a few sentences interpreting the progression across parts.

Keep it tight. Three to four pages is plenty -- one page more than the
single-agent version of this project, since you now have six agents to
account for instead of one. This is graded on whether you can connect the
code to the chapter, not on length.

---

## Submitting

Submit a single zip named `lastname_firstname_ch2.zip` containing:

```
table_driven_agent.py
simple_reflex_agent.py
model_based_agent.py
goal_based_agent.py
utility_based_agent.py
learning_agent.py
results/trials.csv
results/summary.csv
results/learned_weights.json
writeup/WRITEUP_TEMPLATE.md      (filled in, keep the filename)
```

Do not include the `pacman/` package or your virtual environment.

---

## Two ways to lose points for no reason

**Editing the environment.** If `pacman/` differs from what you were
given, the grader runs your six files against the original anyway, and
anything that depended on your edits fails.

**Implementing search.** `self.maze.distance` already exists in every
part that needs it. Writing your own BFS or A\* is not extra credit; it
is the wrong chapter, and the scope tests check for it.
