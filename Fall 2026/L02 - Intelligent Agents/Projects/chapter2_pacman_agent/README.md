# COMP 469 - Chapter 2: Six Agents, One Chapter

## Pac-Man as six different kinds of autonomous agent

You are given a working game and six broken agents. Your job is to build
each one using the ideas from AIMA 4th edition, Chapter 2 -- table-driven,
simple reflex, model-based reflex, goal-based, utility-based, and
learning, in that order.

Read `ASSIGNMENT.md` for the actual instructions. This file just gets you
running.

---

## Setup

You need Python 3.10 or newer.

```
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Pygame is only needed for the game window. Everything else, including the
tests and the trial/training tools, works without it.

## Check that it runs

```
python tools/play.py --agent table_driven
python tools/play.py --agent simple_reflex
python tools/play.py --agent greedy
```

You should see a maze, a yellow agent, and a status bar printing the
agent's reasoning one line at a time. `table_driven` and `simple_reflex`
will not play well yet -- they are unfinished. `greedy` is a working
external baseline, provided so you have something correct to compare
against; it is not a model answer for any of your six parts (see the
comments at the top of `pacman/agents/greedy_baseline.py`).

Once your files are filled in:

```
python tools/play.py --agent model_based
python tools/play.py --agent goal_based
python tools/play.py --agent utility_based
python tools/play.py --agent learning
```

Press `SPACE` to pause, `R` to restart, `ESC` to quit.

## Run the tests

```
python -m unittest discover -s tests -v
```

Most of them fail right now. That is the point. Each test file matches
one part (`test_part1_table_driven.py` checks `table_driven_agent.py`,
and so on); `test_scope.py` and `test_trials_performance.py` check things
that span all six.

## Run the trials

```
python tools/run_trials.py --count 30
```

Plays full episodes with no window for all six of your agents plus the
`greedy` and `random` baselines, and prints a comparison table. Every
agent sees the same seeds, so differences in the results come from the
agents, not from luck.

## Train the learning agent

```
python tools/train_learning_agent.py --generations 80
```

Only meaningful once `learning_agent.py` (Part 6) is finished. Runs the
problem-generator / critic loop from AIMA Figure 2.15, prints a
before/after comparison, and saves `results/learned_weights.json`. After
that, `tools/play.py --agent learning` and `tools/run_trials.py` pick up
whatever training found automatically.

---

## What is in here

| Path | What it is |
|---|---|
| `table_driven_agent.py` | **Part 1. Yours to edit.** |
| `simple_reflex_agent.py` | **Part 2. Yours to edit.** |
| `model_based_agent.py` | **Part 3. Yours to edit.** |
| `goal_based_agent.py` | **Part 4. Yours to edit.** |
| `utility_based_agent.py` | **Part 5. Yours to edit.** |
| `learning_agent.py` | **Part 6. Yours to edit.** Imports Part 5 directly. |
| `ASSIGNMENT.md` | The instructions, part by part. |
| `RUBRIC.md` | How this is graded. |
| `writeup/WRITEUP_TEMPLATE.md` | The written half of the assignment. |
| `tests/` | The contract. Read these; they are the spec. |
| `tools/play.py` | Watch an agent in a window. |
| `tools/run_trials.py` | Headless comparison across seeds. |
| `tools/train_learning_agent.py` | Trains Part 6. |
| `pacman/` | The task environment. Provided. Do not edit. |
| `results/` | Where your CSV and JSON output lands. |

Everything under `pacman/` is provided infrastructure. If you find
yourself editing it to make a test pass, stop -- you are solving the
wrong problem.

## Rules

1. Edit the six `*_agent.py` files and nothing else in the code.
2. Each agent gets exactly two sources of information: the percept it is
   handed each turn, and the static `MazeModel` it is constructed with.
   None of them has any other access to the game.
3. Do not implement DFS, BFS, uniform-cost, greedy, or A\*. Maze
   distances are provided by `self.maze.distance`. Search algorithms are
   Chapter 3, and this project is graded on agent structure.
4. Do not add third-party dependencies.

## If something breaks

**`ModuleNotFoundError: No module named 'pacman'`**
Run commands from the project root, not from inside `tools/` or `tests/`.

**`pygame` will not install**
Skip it. `tools/run_trials.py`, `tools/train_learning_agent.py`, and the
tests do not need it. You will lose the window, which is a real loss for
debugging, but not for grading.

**`ValueError: Percept declares field(s) [...] that this environment cannot sense`**
You used a field name the environment does not have. The error message
lists every valid name.

**`TypeError: UtilityWeights.__init__() got an unexpected keyword argument ...` while loading `learning_agent.py`**
Part 6 imports Part 5's `UtilityWeights` directly and constructs one with
every field filled in. Finish Part 5 (`TODO(CH2-5a)`) first.

**The window opens but nothing moves**
That agent's `choose_action` is probably returning `(0, 0)`, or raising.
Check the terminal for a traceback.
