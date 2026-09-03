# Instructor notes (not part of the student package)

This directory is the fully solved reference implementation of the six
agents described in `ASSIGNMENT.md`, used to build and calibrate the
project. All 68 tests across `tests/` pass against it
(`python -m unittest discover -s tests`).

## What's here that students don't get

- All six `*_agent.py` files with the TODOs filled in and tuned.
- `results/trials.csv` / `summary.csv` -- 30-seed `normal` run.
- `results/trials_hard.csv` / `summary_hard.csv` -- 20-seed `hard` run.
- `results/learned_weights.json` -- one sample training run of Part 6.

## Calibration notes

- `UtilityWeights()`'s defaults in `utility_based_agent.py` were tuned by
  a short random-restart hill-climb (the same style of search Part 6
  itself does) over seeds 1-20, then rounded to clean numbers and
  validated on three disjoint held-out seed ranges. Untuned "reasonable"
  starting weights land around 55-60% win rate on `normal`; the tuned
  defaults land around 90-98%. If you rebalance the maze, ghost speed, or
  scoring in `pacman/rules.py`, re-tune these -- they are specific to the
  current `LEVEL` and `DIFFICULTIES` in `pacman/maze.py` / `pacman/rules.py`.
- The 60% win-rate threshold in `RUBRIC.md` / `test_trials_performance.py`
  is set well below the reference solution's ~90-98%, to leave headroom
  for weaker-but-correct student weight choices.
- **`hard` difficulty is not uniformly harder for every agent type.** In
  the sample `summary_hard.csv`, `goal_based` (90% win) and `greedy` (85%)
  hold up much better than `utility_based` (10%) and `learning` (0%,
  before its own training run) once ghosts move faster than Pac-Man. The
  crisp goal-test agent and the ghost-blind baseline both turn out to be
  less sensitive to the exact weight tuning than the utility-based agent
  is. This is real behavior, not a bug -- and it's a strong, authentic
  example for write-up Section 5 (rational vs. successful) and Section 6
  (trial interpretation) that you may want to point students toward if
  their own write-ups reach for something weaker.
- `NAIVE_WEIGHTS` in `learning_agent.py` is deliberately worse than
  `UtilityWeights()`'s tuned defaults (no continuation/revisit/backtrack
  preference at all, and a much weaker food pull) specifically so
  training against it shows a visible improvement. A training run of
  ~80 generations x 4 seeds typically improves mean performance on 20
  held-out seeds by several hundred to over a thousand points, though
  the exact number is noisy given how few seeds each generation is
  judged on -- that noise is itself worth a mention if a student's
  write-up doesn't already bring it up.
- The off-by-one in "two turns ago" tracking (`position_history[-2]`,
  not `[-3]`) in `model_based_agent.py` / `utility_based_agent.py` was
  caught by `test_part3_model_based.test_avoids_backtracking_...`, which
  actually plays out a short multi-turn sequence rather than only
  manipulating internal state directly. Worth keeping that style of test
  if this project gets revised further.

## Regenerating everything

```
python -m unittest discover -s tests -v
python tools/run_trials.py --count 30
python tools/run_trials.py --count 20 --difficulty hard --output results/trials_hard.csv --summary results/summary_hard.csv
python tools/train_learning_agent.py --generations 80 --train-seeds 4
```
