# Chapter 2 Intelligent Agents - Student Starter Code

This package accompanies the Chapter 2 Pac-Man assignment. The modified file
starts with the original policy and contains `TODO(CH2-...)` markers for the
graded refactor. Do not edit the baseline copy.

## Files

- `src/autonomous_pacman_agent_baseline.py` - untouched comparison policy
- `src/autonomous_pacman_agent.py` - student working file with TODO markers
- `tests/test_chapter2_contract.py` - contract checks that pass after the refactor
- `tools/run_trials.py` - paired-seed, headless evaluation support
- `results/trials.csv` - output template

## Setup and interactive run

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\Activate.ps1
python -m pip install pygame
python src/autonomous_pacman_agent_baseline.py
python src/autonomous_pacman_agent.py
```

## Contract checks

The starter is intentionally incomplete, so several tests fail until the
Chapter 2 refactor is finished.

```bash
python -m unittest discover -s tests -v
```

## Paired trials

The headless runner itself does not require Pygame:

```bash
python tools/run_trials.py \
  --baseline src/autonomous_pacman_agent_baseline.py \
  --modified src/autonomous_pacman_agent.py \
  --count 10 \
  --output results/trials.csv \
  --summary results/summary.csv
```

The supplied maze-distance helper is provided infrastructure. 
