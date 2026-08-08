# CS188 Lecture 4 — Graph Search Wrap-Up & Local Search (AIMA 4.1–4.2)

*Cleaned-up lecture transcript, organized by topic. Timestamps and course
announcements (project/homework deadlines, enrollment, Ed/office hours,
etc.) removed — those are administrative, not lecture content.*

> **A note on this cleanup:** this file was generated from auto-captions
> (`[CS188 SP26] Lecture 4 - Local Search [oDdDycxGdAk].en-en.vtt`), which
> are speech-recognition output, not a human transcript. Unlike the
> earlier `.srt` lectures, this caption track does **not** use rolling
> duplicate lines, so extraction was a straightforward concatenation; the
> content below is reorganized into topic sections and lightly cleaned
> for readability, with the underlying explanations, examples, and Q&A
> exchanges preserved. The original `.vtt` is untouched — check it
> against the source video if exact wording ever matters.

---

## 1. Recap: A* Search So Far

Every search algorithm covered up to this point shares the same skeleton:
start at a state, call the successor function to get new states from
available actions, and repeat — building out a (possibly infinite) search
tree. What differs is only the **order** in which nodes are pulled from
the fringe:

- **DFS** — goes straight down one side.
- **BFS** — strips off layer by layer.
- **UCS** — like BFS but ordered by cumulative cost `G`.
- **Greedy** — orders by heuristic `H` alone; fast, but can head straight
  for a suboptimal goal.
- **A\*** — orders by `F = G + H`: `G` is the backward cost accumulated
  so far, `H` is an admissible (optimistic) estimate of the remaining
  cost. This is the same search as UCS, but it "charges more" for states
  that look farther from the goal.

The hard part in practice isn't the algorithm — it's **designing the
heuristic**.

---

## 2. Admissible Heuristics: The "Search Ball" Intuition

- A heuristic takes a **state** (not a path) and returns a number
  estimating the cost to the nearest goal. It doesn't matter how you got
  to that state.
- **`H = 0` everywhere** (the *trivial heuristic*) is always admissible —
  running A* with it is identical to running plain uniform cost search.
  It's the simplest possible admissible heuristic, but it buys you
  nothing.
- Since `H = 0` is always safe, the real work in optimal search is
  **creating better (still admissible) heuristics** — most of the effort
  in solving a hard search problem optimally goes here.

**Why heuristic tightness matters, concretely:** on a uniform-cost grid
(e.g. every square costs 5), the *ideal* search would only expand nodes
directly on the path to the goal — essentially greedy behavior, and in
this special case greedy happens to be correct. But A* with an imperfect
heuristic will "radiate out" partially in every direction. The **size of
that wasted radius is governed by the gap between the heuristic's
estimate and the true cost** — e.g. if a square really costs 30 to reach
but the heuristic thinks it's 20, that gap of 10 is exactly how far
"sideways" the search will unnecessarily explore. **The work done is, in
general, exponential in that gap** — so tightening heuristics is the key
lever for making A* fast.

### 2.1 Inadmissible heuristics

Nothing stops you from writing code that hands A* an inadmissible
heuristic (something that sometimes overestimates) — the code will run
fine, but **you immediately lose the optimality guarantee**. Sometimes
that trade-off (faster, but possibly suboptimal) is acceptable in
practice; sometimes it isn't.

---

## 3. Building Admissible Heuristics via Relaxation

**Recipe:** take your problem and imagine **extra actions** are legally
available (a "relaxed" version of the problem). Solving the relaxed
problem optimally gives you a heuristic that's guaranteed to be a lower
bound on the real cost — because anything achievable without the extra
actions is still achievable with them, so the relaxed-optimal cost can
only be ≤ the true optimal cost.

- **Pac-Man maze:** relax by allowing "move through a wall" — the optimal
  cost in that relaxed world is exactly Manhattan distance, which is
  therefore a valid lower bound (admissible heuristic) for the real maze.
- **Romania road trip:** relax by imagining a direct road exists between
  *every* pair of cities (i.e., straight-line/"crow flies" distance) — real
  road paths can only be longer, so straight-line distance is admissible.
- **Eat-all-the-dots:** relaxations could include only worrying about one
  dot, ignoring walls, or ignoring ghosts — any of these gives a cheaper
  (or equal), solvable stand-in problem.

### 3.1 Worked example: the 8-puzzle

Recall the setup: sliding-tile puzzle, states = permutations of tiles
(`9!` states — 9 choices for the first tile, 8 for the next, etc.), 4
possible actions (move a tile adjacent to the blank into the blank),
cost 1 per move.

Two admissible heuristics, both derived as relaxed-problem solutions:

| Heuristic | Relaxation | Value at example start state |
|---|---|---|
| **Number of misplaced tiles** (excluding the blank) | Add an action: "teleport any tile directly to its destination" | 8 |
| **Total Manhattan distance** (sum over all tiles) | Add the assumption that tiles can slide through each other without blocking | 18 |

Node-expansion comparison (illustrating why a *tighter* heuristic
matters, not just *any* admissible heuristic): as solution depth grows
(4, 8, 12 steps away), **uniform cost search's node count blows up very
quickly**, while A* with the (weak) misplaced-tiles heuristic grows much
more slowly, and A* with the (tighter) total-Manhattan-distance heuristic
grows slower still. **A bigger heuristic value at the start state is a
good sign** — it means the heuristic is capturing real cost, as long as
it's still an underestimate.

### 3.2 The "use the true cost" thought experiment

What if you used the *actual* optimal cost `H*` as your heuristic?
- Admissible? Yes (trivially, `H* ≤ H*`).
- Would A* only expand nodes on an optimal path? **Yes** — from the proof
  that A* expands nodes in increasing `F`-order, everything off the
  optimal path would have strictly higher `F` than everything on it.
- **Why don't we do this?** Because computing the true cost `H*(n)` for
  every state generally *requires solving the search problem itself* —
  you'd need a search just to build your heuristic. The heuristic must
  come from a **significantly simpler (usually relaxed) problem** that's
  fast to solve, or the trade-off isn't worth it.

**The core trade-off:** the trivial heuristic (`H = 0`) costs nothing to
compute but does no work for you; the true-cost heuristic (`H*`) is
perfect but as expensive as solving the whole problem. **The right
heuristic lives in between** — tight enough to meaningfully shrink the
search, cheap enough that computing it doesn't dominate the runtime.
There's no formula for finding this sweet spot — it's described as "art
and creativity."

### 3.3 Heuristic dominance

- If `H_a(n) ≥ H_c(n)` for **every** node `n`, then `H_a` **dominates**
  `H_c` — it's at least as informative everywhere, and (if both are
  admissible) using `H_a` can only expand fewer or equal nodes.
- Given two admissible heuristics, their **point-wise maximum** is also
  admissible and dominates both individually — a simple, reliable way to
  combine heuristics.
- This dominance relationship forms a **semi-lattice**: the trivial `H=0`
  heuristic sits at the bottom, the true cost `H*` sits at the top, and
  everything else falls somewhere in between. (A lot of published A*
  research is exactly this: finding a heuristic that's cheap to compute
  but sits close to `H*` in this lattice.)

---

## 4. Upgrading Tree Search to Graph Search

**Motivation:** in a search tree, the *same state* can be reached via many
different action sequences, so it can appear repeatedly — causing
exponential blow-up relative to the actual (much smaller) state space.
Revisiting a state is wasted work; ideally, the first time you find a
state is remembered so later rediscoveries can be skipped.

### 4.1 Mechanism: the closed set

- Maintain a **closed set** of states that have already been expanded
  (their successor function has already been called).
- When popping a node off the fringe: if its state is already in the
  closed set, **skip it** (don't re-expand); otherwise expand it and add
  the state to the closed set.
- **Must be a true set (constant-time membership check)** — using a list
  and scanning it turns every check into linear time, which silently
  wrecks performance (called out as a common Project 1 mistake).
- **Timing matters:** a state is only added to the closed set **after**
  it's expanded — not merely when a plan reaching it is placed on the
  fringe. (Same principle as the goal test: reaching the fringe isn't
  enough; only actual expansion/dequeue counts.)

### 4.2 Completeness is preserved

If a goal is deleted from the search tree by the closed-set check, that's
only because an earlier, un-deleted search-tree node already reached the
same state — so no *reachable* goal becomes unreachable. Graph search
remains complete.

### 4.3 Optimality is *not* automatically preserved

**Counter-example (small graph, `S → A/B`, both leading toward goal
`G`):** even with an **admissible** heuristic, tracing A* + graph search
step by step shows it can return a suboptimal path. What happens:

1. A* first reaches state `C` via a costlier path (through `B`) and
   expands it, adding `C` to the closed set.
2. A cheaper path to `C` (through `A`) is discovered later, but when it's
   time to expand that better route to `C`, the closed-set check says "already
   expanded — skip," so the cheaper route is discarded.
3. The final answer is built on top of the *first* (worse) route to `C`,
   producing a suboptimal overall path — despite the heuristic being
   admissible.

**Root cause:** admissibility only guarantees something about the
*heuristic relative to the whole remaining path to the goal*. It does
**not** guarantee that the *first* time a state is popped and closed, it
was reached optimally. Graph search needs a **stronger** property to be
safe.

### 4.4 Consistency (a strengthening of admissibility)

**Definition:** for every edge/action from state `n` to successor `n'`
with real cost `cost(n, n')`:

```
H(n) − H(n') ≤ cost(n, n')       (equivalently: H(n) ≤ cost(n, n') + H(n'))
```

This is a **local, edge-by-edge triangle inequality**: the heuristic is
not allowed to *drop* by more than the actual cost of a single action. In
the counter-example above, the heuristic dropped by more (e.g., a real
edge cost of 1 paired with a heuristic drop of 3) than the edge cost
allowed — that's an *admissible-but-inconsistent* heuristic, and fixing
the heuristic so its drop across that edge never exceeds the edge's real
cost restores correctness.

Two useful consequences of consistency:
1. **`F` never decreases** along any path as the search goes deeper.
2. Combined with the (already-known) fact that A* tree search expands
   nodes in non-decreasing `F` order, consistency additionally guarantees
   that **for every state, the path that reaches it optimally is
   expanded before any path that reaches it sub-optimally** — which is
   exactly the property that failed in the counter-example above. These
   two facts together are what make **graph search provably optimal**
   when the heuristic is consistent.

**Practical note:** consistency is stronger than admissibility (consistent
⟹ admissible), but relaxed-problem heuristics (§3) — the standard recipe
for building admissible heuristics — **almost always turn out to be
consistent too**, even though consistency is more annoying to verify
formally.

### 4.5 Summary: tree search vs. graph search optimality

| Search variant | Optimality requires |
|---|---|
| A* **tree search** | Admissible heuristic |
| A* **graph search** | **Consistent** heuristic |

### 4.6 Alternative fix: a "closed map" instead of a closed set

**Q&A idea:** instead of a closed *set*, keep a closed **map** from state
→ best cost found so far. If a state is rediscovered with a *strictly
better* cost, reopen and re-expand it. This patches optimality even under
an inconsistent (or sometimes even inadmissible) heuristic, but you lose
a clean bound on how much repeated work you might end up doing. Useful in
practice when a heuristic is "almost always" consistent and you just want
resilience against occasional violations.

### 4.7 Memory caveat: when *not* to use graph search

Graph search must remember **every state ever expanded**, which can
exhaust memory long before time becomes the bottleneck — writing a huge
number of states to memory is cheap and fast to do, so you can fill RAM
surprisingly quickly. **DFS**, by contrast, only needs memory linear in
current depth (its fringe can literally just be the call stack) —
exponentially less than tracking a whole closed set. So: when memory is
the binding constraint (e.g. searching for very deep or very "far"
solutions), a plain tree search like DFS can be preferable to graph
search despite graph search's usual efficiency advantage. (Techniques
like **iterative deepening** — depth-limited DFS with increasing cutoffs,
or the same idea using `F`-cost cutoffs instead of depth — exist
specifically to recover some of graph search's benefits without its
memory cost; not covered in detail here.)

**Fringe vs. closed-set data structures:** the fringe needs fast
insertion and fast "pull off the best" — typically a **priority queue**
(or a stack/plain queue for DFS/BFS specifically). The closed set needs
fast **add** and **contains** — must be a true set, or membership checks
degrade to linear time and silently slow down the whole search.

---

## 5. Local Search

### 5.1 Motivation: when the *path* doesn't matter

All search so far has cared about the **plan** (the sequence of actions)
— e.g. in Pac-Man pathing, knowing *how* you got to the goal matters. But
many problems only care about the **final configuration**, not how it was
reached:

- **N-Queens:** place N queens on an N×N board so none threaten each
  other. If someone hands you a valid board, you can verify it instantly
  — you don't care how they found it.
- **Traveling Salesman:** find a minimum-cost tour visiting every city
  once. You want the tour itself, not a record of how it was discovered.

For problems like these, instead of building up **partial** plans piece
by piece (as in tree/graph search), the state space can instead be the
set of **complete configurations** — and you search by repeatedly
**improving** one configuration.

### 5.2 Iterative improvement / hill climbing

**Idea:** keep track of a **single current state** (not a fringe of many
candidates), define operators that turn one complete configuration into
another, and repeatedly move to better neighbors.

**Example: N-Queens.**
- **States:** any placement of N queens on the board (possibly with
  conflicts) — not partial boards being built up column by column.
- **Actions:** move a queen.
- **Objective:** something like the number of pairwise conflicts (queens
  threatening each other), which you want to minimize.

**Hill-climbing algorithm:**
```
loop:
    look at all neighboring states
    if the best neighbor is better than the current state: move there
    else: stop (you're at a local optimum)
```

**Key property: constant space.** Unlike tree/graph search, there's no
fringe, no closed set, no goal test in the traditional sense — just one
state being repeatedly nudged toward "better."

### 5.3 Challenges: local optima, plateaus, and blindness to the global picture

- **Local optimum:** every neighbor looks worse, so the algorithm stops —
  even if a better ("global") optimum exists elsewhere. From any given
  state, you only know your **local** geometry (what's uphill from here);
  you never know whether a flat spot is a true local optimum or a
  shoulder, and you never know when you've found the *global* optimum.
- **Plateaus/shoulders:** regions where many neighboring states have
  equal value — hill climbing has no principled way to navigate through
  a long sequence of ties.
- Real search landscapes are often full of many small local optima along
  the way to better regions, not just one clean hill.

### 5.4 Fixes and variants (heuristic, not guaranteed)

None of these come with clean optimality proofs like A* — they're
empirical rules of thumb, and what works is very problem-dependent.

- **Random restarts:** rerun hill climbing from many different starting
  states, hoping to land in a good basin at least once. How many restarts
  are "enough" is generally unknown for non-convex problems with many
  local optima.
- **Sideways moves:** allow moving to an equally-good (not just strictly
  better) neighbor, to escape plateaus.
- **Variable step size:** take bigger or smaller steps from the current
  state — bigger steps can smooth over small local bumps but risk
  overshooting a good, narrow region; smaller steps track local structure
  more faithfully but get stuck in small optima more easily.
- **Simulated annealing:** allow "bad" (downhill) moves, with the
  probability of accepting a bad move controlled by a **temperature**
  parameter that decreases over time (named for the metallurgical
  annealing process — controlled cooling to reach a low-energy, ordered
  state). High temperature → readily accept worse moves (more
  exploration); low temperature → mostly move uphill (more exploitation).
  - **Theoretical guarantee:** if temperature is decreased *sufficiently
    slowly*, simulated annealing is guaranteed to eventually visit every
    state (given infinite time and enough random wandering) and will
    spend proportionally more time in better regions — so in the limit it
    converges to the **global optimum**.
  - **Practical caveat:** this guarantee relies on "sufficiently slow" and
    "infinite time," which aren't available in practice — so real-world
    performance varies and isn't guaranteed. Works best when the search
    landscape looks mostly uphill with small bumps to smooth over, rather
    than being generally chaotic.
- **Beam search:** maintain **K** candidate states in parallel (not just
  1). Each iteration, generate all neighbors of all K states (branching
  factor `B` → `K×B` candidates), then keep only the best K overall —
  **not** necessarily one-per-parent. This differs from simply running K
  independent random restarts in parallel: in beam search, the K
  candidates **implicitly communicate** — if one search finds a
  promising region, the shared K-slot "beam" fills up with variants from
  that region, reallocating exploration effort toward what's working
  (loosely analogous to natural selection).
- **Genetic algorithms:** an extension of beam-search-style population
  search that adds **crossover** — an operator that combines two
  different good solutions into a third, splicing together
  partially-independent "traits." Example: for N-Queens, if one board is
  good on the left half and another is good on the right half, splice
  them together. This only helps when a problem is **semi-decomposable**
  (its sub-parts interact somewhat, but aren't fully coupled) — e.g. map
  coloring of disconnected regions could be solved fully independently;
  N-Queens' left/right halves interact but aren't fully coupled, so
  crossover can plausibly help. (Not heavily used in modern practice —
  e.g. neural network training uses hill-climbing-style gradient descent
  with restarts, but no analogous "crossover" between trained models,
  since it's unclear how to safely mix two trained circuits.)

### 5.5 Continuous state spaces (preview)

Everything covered in this unit has been over **discrete** spaces — true
for roughly the first two-thirds of the course. But many real problems
(including neural network training, discussed later in the course) are
**continuous** — e.g. placing airports in Romania at arbitrary real-valued
coordinates to minimize total distance to cities gives a continuous
objective function over a vector of positions. Approaches for continuous
spaces:

1. **Discretize** the space (put it on a grid) and treat it as a discrete
   search problem.
2. **Random perturbations** — take discrete random steps through the
   continuous space.
3. **Analytic methods** — use derivatives/gradients (and possibly second
   derivatives for curvature information), e.g. Newton's method and
   related techniques. These look nothing like A*-style search and belong
   to a different family of methods (some covered later in the course,
   some not).

---

## 6. Closing Lesson: Search Is Only as Good as Its Model

**Local search summary:**
- **Configurational/optimization problems** (goal state matters, path
  doesn't) can be solved via local search instead of tree/graph search.
- **Hill climbing** — go uphill until stuck.
- **Simulated annealing** — allow downhill moves in a controlled
  (temperature-scheduled) way to escape local optima.
- **Beam search** — maintain a population of candidates with implicit
  resource-sharing toward promising ones.
- **Genetic algorithms** — extend beam-search populations with crossover
  between good solutions.
- Many machine learning algorithms are fundamentally **local search**
  (e.g. gradient-based training), as opposed to the planning-style
  tree/graph search covered earlier in the unit.

**Final reminder, tying back to the whole search unit:** search always
runs over a **model** of the world — an agent plans in simulation, then
executes the resulting plan in reality. **Your search is only as good as
your model.** Two real-world examples of "search gone wrong" that are
actually **modeling** failures, not algorithm failures (echoing the same
lesson from Lecture 2):

- **MapQuest routing to a real address:** the route was clean, complete,
  and cost-optimal by the algorithm's own logic — but it directed a
  driver to a road/turn that didn't actually exist in the real world.
  Nothing about the search algorithm, completeness, optimality, or
  heuristic consistency was at fault — **the underlying map data (the
  model) was simply wrong.**
- **A once-real routing bug from City → Norway:** a route between two
  nearby points was computed as passing through England — the opposite
  failure mode (a **missing** link/connection in the map data caused the
  model to misrepresent the real geography, rather than an **extra**,
  nonexistent one as in the MapQuest case).

**Takeaway:** always check the real world before executing a plan that
was only ever validated in simulation — the algorithm can be flawless and
still produce a bad outcome if the model itself doesn't match reality.
