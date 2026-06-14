# Chapter 12: Quantifying Uncertainty teaching demos

This package supports the lecture deck with small, runnable Python examples.

## Files

- `chapter12_uncertainty_demos.py`: main script with all demos.
- `chapter12_uncertainty_demos.ipynb`: notebook wrapper that imports the script and runs each demo.

## Run all demos

```bash
python chapter12_uncertainty_demos.py
```

## Run one demo

```bash
python chapter12_uncertainty_demos.py expected_utility
python chapter12_uncertainty_demos.py full_joint
python chapter12_uncertainty_demos.py bayes
python chapter12_uncertainty_demos.py naive_bayes
python chapter12_uncertainty_demos.py wumpus
```

## Classroom use

1. Run `expected_utility` before probability notation to show why probabilities need utilities.
2. Run `full_joint` after the Toothache-Cavity-Catch table.
3. Run `bayes` while discussing the stiff-neck and meningitis example.
4. Run `naive_bayes` during text classification.
5. Run `wumpus` at the end of the chapter to show exact enumeration and risk ranking.
