# Chapter 3 Search Labs: Jupyter Notebooks

These five labs are based only on Chapter 3, "Solving Problems by Searching," from the uploaded course document.

## Contents

1. `Lab_01_Problem_Solving_Agents.ipynb`
   - Problem-solving agent cycle
   - Search problem formulation
   - Romania map route planning GUI

2. `Lab_02_Search_Trees_Frontiers_Redundant_Paths.ipynb`
   - State-space graph vs. search tree
   - Node, parent pointers, frontier, reached table
   - Redundant paths and cycle effects

3. `Lab_03_Uninformed_Search_Strategies.ipynb`
   - Breadth-first search
   - Uniform-cost search
   - Depth-first search
   - Depth-limited search
   - Iterative deepening search
   - Bidirectional BFS

4. `Lab_04_Informed_Heuristic_Search.ipynb`
   - Heuristic function h(n)
   - Greedy best-first search
   - A* search
   - Weighted A*
   - hSLD consistency checks on the Romania map

5. `Lab_05_Heuristic_Functions_8_Puzzle.ipynb`
   - 8-puzzle formulation
   - Misplaced tiles heuristic h1
   - Manhattan distance heuristic h2
   - Relaxed-problem intuition
   - A* comparison and GUI puzzle animation

## Setup for student PCs

Use Python 3.10 or newer if possible.

From a terminal or command prompt:

```bash
python3 -m venv .env                                          
source .env/bin/activate
python3 -m pip install --upgrade pip
python -m pip install jupyterlab notebook matplotlib ipywidgets
jupyter lab
```

Open the notebooks and run cells from top to bottom.

## Notes

- Each notebook is self-contained.
- The Romania map data and 8-puzzle examples are hardcoded, so no internet is needed during class.
- GUI controls use `ipywidgets`. If widgets do not appear, install or upgrade `ipywidgets` and restart Jupyter.
