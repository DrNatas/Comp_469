# COMP 469 Lab 02 — Instructor Notes
### Solving Problems by Searching (AIMA Chapter 3) — 3-hour lab

This is the classroom-management companion to `COMP469_Lab02_Search_INSTRUCTOR.ipynb`, which has the solved code and answer keys inline. Use this document for pacing, setup logistics, common student mistakes, and grading.

---

## 1. Before the Lab

- **Environment:** students need `networkx` and `ipywidgets` in addition to whatever was installed for Lab 01. If your lab image was frozen after Lab 01, push an update or have students run `pip install networkx ipywidgets` before the setup cell.
- **`aima/` package:** confirm every student machine (or shared lab image) has the `aima/` folder with `search.py` and `notebook_utils.py` sitting next to the notebook, or one directory up. The bootstrap cell searches upward for it and raises a clear `FileNotFoundError` if it's missing — tell students to read that error message rather than guessing.
- **Distribute only** `COMP469_Lab02_Search.ipynb` (the student copy) to the class. Keep the `_INSTRUCTOR` notebook and this file for yourself.
- **Optional pre-read:** AIMA Chapter 3 through Section 3.5 (Informed Search). Students who haven't read at least Section 3.3 (Search Algorithms) will struggle with the vocabulary in the checkpoints, though the guided TODOs don't strictly require it.

---

## 2. Pacing Guide (3 hours / 180 minutes)

| Time | Section | What students are doing |
|---|---|---|
| 0:00–0:20 | Setup + Problem Formulation Review (Sections 0–2) | Environment check, PEAS table, read `Problem`/`Node` source |
| 0:20–0:35 | Define & Visualize Romania Problem (Sections 3–4) | One-line TODO, run `show_map`, Checkpoint 1 |
| 0:35–1:10 | BFS + DFS (Sections 5–6) | Two guided implementations, Checkpoint 2 |
| 1:10–1:30 | Uniform-Cost Search (Section 7) | One guided implementation — expect this to take the full 20 min, it's the conceptually hardest TODO block |
| 1:30–2:05 | Heuristic + Greedy + A* (Sections 8–9) | Heuristic function, shared best-first helper, Checkpoint 3 |
| 2:05–2:25 | 8-Puzzle Heuristics (Section 10) | Two heuristic functions, Checkpoint 4 |
| 2:25–2:55 | Controlled Experiment + Plots (Sections 11–12) | Timing TODO, run experiment, read plots, Checkpoint 5 |
| 2:55–3:10 | Extension Challenge (Section 13, optional/bonus) | Pick one of three options |
| 3:10–3:15 | Final Reflection + submit | — |

**If you're running short on time:** Section 13 (Extension Challenge) is the one section explicitly designed to be optional/bonus — cut it first. If you need to cut further, Section 10 (8-puzzle) can be assigned as a take-home follow-up, since it is somewhat self-contained and doesn't feed into the Section 11 experiment (which only uses the Romania algorithms).

**If students are moving faster than expected:** point strong students at Section 13 Option B (weighted A*) early — it's the most conceptually rich of the three and rewards students who finish the core lab with 30+ minutes to spare.

---

## 3. Section-by-Section Common Mistakes

### Section 2 — Problem Formulation Review
- Students often mark the route-finding problem "partially observable" because *they personally* don't know the map yet. Clarify: the *agent* in this formulation has the full map (Figure 3.1) from the start; observability is about perceiving current state, not about how the agent acquired its world model.

### Section 3 — Define the problem
- Easy to swap start/goal (`GraphProblem("Bucharest", "Arad", ...)`). This still runs and still produces *a* valid answer, so it won't error — but `romania_problem.goal_test("Bucharest")` will print `False` in the smoke test below it, which is your tell.

### Section 5 — BFS
- **The #1 bug in this lab:** students write `frontier.pop()` instead of `frontier.popleft()`. Since `list.pop()`-style code is muscle memory, and `deque` supports both ends, this compiles and runs — it just silently turns BFS into DFS. Symptom: BFS's path/cost/nodes-expanded exactly matches DFS's, or is otherwise no longer the expected `Sibiu → Fagaras → Bucharest` / cost 450 / 6 nodes. Have students print `type(frontier)` and ask them which end of the deque `popleft()` vs `pop()` removes from.

### Section 6 — DFS
- The exact DFS path is sensitive to neighbor ordering in the underlying dict, so don't require an exact string match to the reference path — verify structurally (stack used, LIFO order, cost is a legitimate path cost) instead.

### Section 7 — Uniform-Cost Search
- If `f` is left returning a constant (forgotten TODO), the priority queue stops ordering by cost and UCS collapses to something resembling BFS (same 450 cost instead of the optimal 418). Have students print `f(node)` for two different nodes to confirm it varies.
- Some students restructure the goal-test to fire at child-generation time (copying the BFS/DFS pattern) rather than after `pop()`. This still finds *a* path but breaks UCS's optimality guarantee on graphs where a cheaper path to the goal is found later. Flag this even if their output happens to look correct on the Romania map, since the shortcut isn't safe in general.

### Section 9 — Greedy / A*
- If `astar_search`'s `f` doesn't include `n.path_cost`, it silently degenerates into greedy search, and both will report the same 450-cost path/3-node-expansion result. This is a good diagnostic: A* and greedy giving *identical* output is a red flag.

### Section 10 — 8-Puzzle
- Off-by-one in `index_goal`: some students hand-index rows/cols starting at 1. Since Python indices are 0-based throughout this lab, double-check any student whose Manhattan distances are consistently off by a small constant.
- Whether to include the blank tile in `misplaced_tiles` is a legitimate judgment call — see the Checkpoint 4 answer key in the instructor notebook. Don't mark a student wrong for including it as long as their admissibility reasoning holds up.

### Section 11 — Controlled Experiment
- Neamt↔Craiova is the long diagonal route across the map and will make DFS noticeably slower / more node-heavy than the other four pairs. This is expected, not a bug, and is good fodder for Checkpoint 5 discussion.

---

## 4. Grading Rubric (suggested weights — adjust to your syllabus)

| Component | Weight | Notes |
|---|---|---|
| TODOs 1–13 completed correctly | 40% | Use the `SOLUTION` comments in the instructor notebook as the reference; partial credit for structurally correct-but-buggy code (e.g., correct approach, wrong pop direction) |
| Checkpoints 1–5 | 35% | Look for reasoning tied to their own output, not just recited definitions — see the instructor notebook's answer keys for the specific idea each question should surface |
| Experiment summary + plots | 15% | Both required plots present and legible; summary table reflects actual run results |
| Final reflection | 10% | Should reference specific numbers from their own experiment and distinguish completeness / optimality / efficiency as separate ideas, not one vague "better/worse" axis |
| Extension challenge | Bonus (up to +5%) | Any one of the three options, reasoned through correctly |

**A signal of strong understanding:** the student's Checkpoint 3 and Checkpoint 5 answers correctly identify that greedy best-first search is *not* optimal despite expanding fewer nodes, and can articulate *why* in terms of ignoring path-cost-so-far — this is the single idea the whole lab builds toward.

**A signal the student may have copied results without understanding them:** exact-decimal agreement with another student's `time_seconds` column (timing will naturally vary machine-to-machine), or a Final Reflection that doesn't reference any specific number from their own run.

---

## 5. Anticipated Questions From Students

- **"Why does DFS sometimes find a cheaper path than BFS?"** Coincidence of which branch it explores first — DFS has no cost-awareness at all, so any relationship between its result and the optimal cost is not guaranteed in either direction. Point them to Checkpoint 5, Q3.
- **"Why do greedy and A* expand so few nodes compared to UCS?"** The heuristic gives them a sense of *direction*; UCS only knows cost paid so far, not how much is left, so it has to explore roughly equally in every direction until it's certain of the cheapest path.
- **"Is A* always better than UCS, then?"** Only when a good admissible heuristic is available. Designing that heuristic is real work (see Section 8's discussion of straight-line distance, and Section 10's misplaced-tiles vs. Manhattan-distance comparison) — A*'s advantage is not free.
- **"What happens if my heuristic isn't admissible?"** A* can return a suboptimal solution. Section 13 Option B (weighted A*, `w > 1`) is designed to let students see this directly rather than just being told about it.

---

## 6. Files in This Lab Package

| File | Audience | Purpose |
|---|---|---|
| `COMP469_Lab02_Search.ipynb` | Students | The lab itself — guided TODOs, checkpoints, experiment, extension challenge |
| `COMP469_Lab02_Search_INSTRUCTOR.ipynb` | Instructors only | Fully solved code with expected console output, plus inline answer keys and teaching notes at the point of use |
| `COMP469_Lab02_Instructor_Notes.md` | Instructors only | This file — pacing, common mistakes, grading rubric |
