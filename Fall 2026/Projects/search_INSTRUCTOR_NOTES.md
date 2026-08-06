# CS188 Proj 1 (Search) — Instructor Notes

Solution code is filled in directly in `search/search.py` and
`search/searchAgents.py`. Verified with `python3 autograder.py` →
**26/25** (q1–q6, q8 at max; q7 gets the bonus point for beating the
7000-node threshold at 4137 expanded nodes on trickySearch).

**Keep this file and the solved `search/` folder out of anything students
clone** — this repo looks like it doubles as the course materials repo.

---

## Q1 — DFS (`search.py`)

Standard graph-search template used identically for all four algorithms
(Q1–Q4): pop from fringe → **goal-test the popped state** → if already
visited, skip → mark visited → push unvisited successors.

**Gotchas to watch for in student code:**
- **Tree search instead of graph search.** No visited set at all → infinite
  loop or exponential blowup on any maze with a cycle (`openMaze`,
  `graph_infinite.test`). Usually surfaces as a hang, not a crash — students
  think the autograder is broken.
- **Using recursion.** Works on tiny mazes, hits Python's recursion limit on
  `mediumMaze`/`bigMaze`.
- Returning states instead of actions.

## Q2 — BFS

**The #1 stumbling block, and one I hit myself building this key.** The
natural "optimized" instinct is:
```python
if successor not in visited:
    if problem.isGoalState(successor):
        return actions + [action]   # early goal test at generation time
    visited.add(successor)          # mark visited at push time
    fringe.push(...)
```
This is a legitimate, textbook-correct BFS — it still finds the shortest
path. But it produces a **different node-expansion trace** than the
reference solution, and Berkeley's small synthetic tests
(`graph_manypaths.test`, `graph_backtrack.test`, etc.) assert the *exact*
`expanded_states` list, not just path optimality. Early-goal-test code will
pass `pacman_1.test` (checks cost/optimality) but silently fail 2–3 of the
graph unit tests with no obvious explanation.

**Fix:** goal-test at pop time and mark visited at pop time, exactly like
Q1/Q3/Q4 — see the template above. If a student's BFS finds a correct,
optimal path but fails graph tests, this mismatch is almost certainly why.
Worth flagging in section/office hours proactively.

## Q3 — UCS

- Priority pushed must be **cumulative path cost**, not the incremental
  `stepCost` of the last edge.
- Goal test must happen at pop time (`ucs_5_goalAtDequeue.test` targets this
  directly) — a node can be enqueued more than once at different costs;
  testing the goal on the *first* enqueue rather than the *cheapest* dequeue
  can return a suboptimal path.
- `util.PriorityQueue.update()` exists for in-place priority decreases;
  it's fine (and simpler to reason about) to instead just push duplicates
  and skip stale entries via a `bestCost` dict on pop, which is what the
  solution here does. Either approach is valid — don't dock students for
  picking one over the other.

## Q4 — A*

Same shape as UCS, with `priority = g(successor) + h(successor)`. Common
bug: computing `h(state)` for the *current* node instead of the *successor*
when pushing children. `astar_3_goalAtDequeue.test` exists for the same
reason as UCS's — catches early-goal-test bugs.

## Q5 — CornersProblem state space

State = `(pacmanPosition, cornersVisitedTuple)`.

- **Must use a tuple, not a list**, for `cornersVisited` — search algorithms
  put states in `set()`s / use them as dict keys, and lists aren't
  hashable. This fails loudly (`TypeError: unhashable type`), so it's
  usually self-correcting, but confusing for students seeing that error for
  the first time.
- If a student instead keeps a **mutable list on the problem instance**
  (e.g. `self.visited`) rather than folding visited-corners into the state
  itself, the state space stops being Markovian — search can't backtrack
  correctly and results are wrong in subtle, hard-to-debug ways. This is the
  most conceptually important idea in Q5: *the state must fully capture
  everything needed to know if you're done*, not just position.
- This question silently depends on a correct Q2 (BFS is used to sanity
  check it) — if a student's Q5 fails with no diagnostic beyond "make sure
  to complete Q2 first," send them back to the Q2 goal-test-at-pop issue
  above before they burn time on Q5 itself.

## Q6 — Corners heuristic

Solution: greedily chain Manhattan distance to the *nearest* remaining
corner, then the next-nearest from there, etc. Admissible and consistent
because it ignores walls (never overestimates) and is monotonic step to
step.

- **Inadmissible variant students often try:** distance to the *farthest*
  corner, or the sum of distances to all remaining corners in arbitrary
  order — both can overestimate the true cost.
- **Slow variant:** using real maze distance (BFS) between corners instead
  of Manhattan distance — technically tighter, but expensive if
  recomputed on every heuristic call without caching; can time out on
  `mediumCorners`.
- The autograder explicitly checks non-negativity, admissibility at the
  start state, and total nodes expanded (bonus-tier threshold), so a buggy
  heuristic that's merely "less wrong" than trivial will show up as a
  partial-credit case, not a hard fail — useful to know when triaging.

## Q7 — Food heuristic

This is the one question where a *weak but valid* heuristic (max Manhattan
distance to remaining food) is easy and gets partial credit, but the
efficient credit-worthy solution needs care:

- **Must take `max`, not `sum`**, of distances to remaining food dots.
  Summing overestimates (inadmissible) — Pacman doesn't have to retrace its
  steps to reach every dot independently, so summing produces suboptimal
  A* solutions. This is explicitly what the assignment page warns about:
  "if A* finds a worse solution than UCS, your heuristic is not
  consistent."
- Real maze distance (not Manhattan) to the farthest dot is what gets full
  marks on the node-expansion thresholds (15000 → 12000 → 9000 → 7000 on
  `trickySearch`); our solution hits **4137**, clearing all four tiers plus
  the bonus point.
- **Must cache.** `mazeDistance()` runs a fresh BFS every call — calling it
  uncached for every food dot on every heuristic evaluation is what causes
  student solutions to time out rather than just score lower. `problem.
  heuristicInfo` is explicitly provided for this and persists across calls
  on the same problem instance — point students at it directly, the
  docstring hints at it but easy to skim past.

## Q8 — Suboptimal search / ClosestDotSearchAgent

- `AnyFoodSearchProblem.isGoalState` is a one-liner: `return self.food[x][y]`.
  The classic bug here is `self.food[y][x]` — the `Grid` class in this
  codebase is indexed `[x][y]`, and it's an easy accidental swap, especially
  since students are used to `grid[row][col]` from other contexts. It fails
  silently (returns wrong bool, not a crash) unless they test on an
  asymmetric layout.
- Intended solution is plain BFS (`search.bfs`, all step costs are 1) — A*
  or UCS also work here but are unnecessary and slower.
- **By design this whole strategy is globally suboptimal** — repeatedly
  chasing the nearest dot doesn't produce the shortest overall tour (that's
  the traveling-salesman-flavored point of the "Suboptimal Search" title).
  Students sometimes think their code is broken because the final path
  isn't shortest; reassure them that's expected — grading here is
  pass/fail on correctness, not path optimality.

---

## Cross-cutting notes

- `PositionSearchProblem`, `FoodSearchProblem`, and the abstract
  `SearchProblem` base class are fully provided and should never be
  touched — if a student's diff touches those, that's worth a comment on
  its own.
- `self._expanded += 1  # DO NOT CHANGE` inside `CornersProblem.
  getSuccessors` is easy to accidentally delete while filling in the loop
  around it — worth calling out since it silently breaks the "nodes
  expanded" grading line without breaking correctness.
- Directions/action encoding: `Actions.directionToVector(action)` and
  `self.walls[x][y]` (also `[x][y]`, not `[y][x]`) are the two most common
  index-order slips across every question that touches the grid directly.
