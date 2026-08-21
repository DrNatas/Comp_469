# COMP 469 - Chapter 2: Intelligent Agents

## Pac-Man as an autonomous agent

You are given a working game and a broken agent. Your job is to rebuild the
agent using the ideas from AIMA 4th edition, Chapter 2.

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
tests and the trial runner, works without it.

## Check that it runs

```
python tools/play.py
```

You should see a maze, a yellow agent that starts eating pellets, and a
status bar at the bottom printing the agent's reasoning one line at a time.
You should also see it get eaten within a few seconds. That is expected:
the starter agent cannot see ghosts.

Press `SPACE` to pause, `R` to restart, `ESC` to quit.

Compare it against the two provided agents:

```
python tools/play.py --agent simple_reflex
python tools/play.py --agent random
```

## Run the tests

```
python -m unittest discover -s tests -v
```

Most of them fail right now. That is the point. Each test name begins with
the task it checks, so `test_ch2_4_...` failing means go work on the block
marked `TODO(CH2-4)` in `agent.py`.

## Run the trials

```
python tools/run_trials.py
```

This plays full episodes with no window and prints a comparison table. Every
agent sees the same seeds, so differences in the results come from the
agents rather than from luck.

---

## What is in here

| Path | What it is |
|---|---|
| `agent.py` | **The only file you edit.** |
| `ASSIGNMENT.md` | The instructions, task by task. |
| `RUBRIC.md` | How this is graded. |
| `writeup/WRITEUP_TEMPLATE.md` | The written half of the assignment. |
| `tests/` | The contract. Read these; they are the spec. |
| `tools/play.py` | Watch an agent in a window. |
| `tools/run_trials.py` | Headless comparison across seeds. |
| `pacman/` | The task environment. Provided. Do not edit. |
| `results/` | Where your CSV output lands. |

Everything under `pacman/` is marked as provided infrastructure. If you find
yourself editing it to make a test pass, stop, because you are solving the
wrong problem.

## Rules

1. Edit `agent.py` and nothing else in the code.
2. Your agent gets exactly two sources of information: the percept it is
   handed each turn, and the static `MazeModel` it is constructed with. It
   has no other access to the game.
3. Do not implement DFS, BFS, uniform-cost, greedy, or A\*. Maze distances
   are provided by `self.maze.distance`. Search algorithms are Chapter 3,
   and this assignment is graded on agent structure.
4. Do not add third-party dependencies.

## If something breaks

**`ModuleNotFoundError: No module named 'pacman'`**
Run commands from the project root, not from inside `tools/` or `tests/`.

**`pygame` will not install**
Skip it. `tools/run_trials.py` and the tests do not need it. You will lose
the window, which is a real loss for debugging, but not for grading.

**`ValueError: Percept declares field(s) [...] that this environment cannot sense`**
You used a field name the environment does not have. The error message
lists every valid name.

**The window opens but nothing moves**
Your `choose_action` is probably returning `(0, 0)`, or raising. Check the
terminal for a traceback.
