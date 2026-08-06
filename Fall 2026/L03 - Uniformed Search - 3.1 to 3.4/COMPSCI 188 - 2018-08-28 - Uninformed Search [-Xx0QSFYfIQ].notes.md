# CS188 Lecture 2 — Uninformed Search (AIMA 3.1–3.4)

*Cleaned-up lecture transcript, organized by topic. Timestamps and course
announcements (project deadlines, office hours, research recruiting, etc.)
removed — those are administrative, not lecture content.*

> **A note on this cleanup:** this file was generated from auto-captions
> (`COMPSCI 188 - 2018-08-28 - Uninformed Search [-Xx0QSFYfIQ].en.srt`),
> which are speech-recognition output, not a human transcript. The captions
> are reorganized into topic sections and lightly cleaned for readability;
> the underlying explanations, examples, and demos are all preserved. The
> original `.srt` is untouched — check it against the source video if exact
> wording ever matters.

---

## 1. Reflex Agents vs. Planning Agents

Before formalizing search, the lecture contrasts two ways an agent can
choose actions.

### 1.1 Reflex agents

A **reflex agent** picks an action based on the current percept (and maybe
some memory), **without considering the consequences of the action**.

- Example: a fly buzzes near your face and you flinch/close your eyes —
  you don't reason through "what happens if I keep my eyes open vs.
  closed," you just react.
- Example: touching a hot stove — you pull your hand back immediately
  rather than reasoning about how burned it might get.
- Reflex agents **can be rational**: rationality is about *optimal
  behavior*, not about *how* the agent arrived at that behavior. Pulling
  your hand off a flame instantly is more optimal than pausing to reason
  through consequences.

**Pac-Man demo (reflex agent):** the agent always moves toward the
*nearest* dot.
- In an open maze, this works fine — moving toward the closest dot
  succeeds because there's nothing better to do anyway.
- In a maze with a wall between Pac-Man and the nearest dot, the reflex
  agent just keeps bumping into the wall forever, since "nearest dot" keeps
  pointing in the same (blocked) direction. It never finds a way around.
  Since Pac-Man loses a point for every time step that passes, this is
  clearly **not optimal** behavior.

### 1.2 Planning agents

A **planning agent** asks *"what if I take this sequence of actions —
what would happen?"* This requires:

1. A **model** of how the world works (so consequences can be predicted).
2. A **goal** — either a specific goal state, or a goal *test/condition*
   that can be satisfied in multiple ways.

Planning agents hypothesize sequences of actions and evaluate them against
the goal. Two properties we'll want to evaluate any planning algorithm on:

- **Optimal** — achieves the goal at minimum cost.
- **Complete** — if a solution exists, the algorithm is guaranteed to find
  it.

**Pac-Man demo (planning vs. replanning):**
- *Full planning:* the agent pre-computes (via many expansions) the entire
  optimal sequence of actions to clear the whole board before acting.
  This can take a while, because it must consider a huge number of
  candidate action sequences before it can be sure it found the optimal
  one.
- *Replanning:* instead of planning the whole game up front, the agent
  only plans a path to the *nearest* dot, executes that plan, then
  re-plans to the next-nearest dot, and repeats. This starts acting almost
  immediately and continuously re-plans during execution — a practical
  compromise when full planning is too slow (this is the strategy used in
  Project 1).

---

## 2. Search Problems: Formal Definition

To let a single algorithm solve many different real-world problems, we
**formalize** the problem as a **search problem** with these components:

| Component | Meaning |
|---|---|
| **State space** | The set of all possible configurations the world could be in. |
| **Successor function** | For a given state, returns the available actions and the resulting states (and the cost of each action). |
| **Start state** | Where the agent begins. |
| **Goal test** | A condition (or specific state) that determines whether a state satisfies the goal. |
| **Solution / plan** | A sequence of actions that transforms the start state into a state satisfying the goal test. |

The key payoff: once a real-world problem is cast into this interface, any
algorithm built to work with the interface can solve it — search problems
are the unifying abstraction for this unit.

Note that a search problem is a **model** — it's always a simplification
of the real world, and a lot of the art of applying search is deciding
*what to include* in the state space (see §7 for what goes wrong when the
model is wrong).

### 2.1 Example: Romania road map

Goal: find a route from Arad (start) to Bucharest (has the airport).

- **State space:** cities (chosen because we only care about the path
  between cities — a different problem might need a finer-grained state
  space, e.g. sub-segments of road).
- **Successor function:** neighboring cities on the map graph, with cost
  = distance along that edge (could instead be modeled as travel time,
  traffic, potholes, etc. — a different choice of cost).
- **Start state:** Arad.
- **Goal test:** `state == Bucharest`.
- **Solution:** one of the possible paths through the graph from Arad to
  Bucharest (there are several — an *optimal* solution is the shortest
  one).

Note: if you change the state space, the successor function generally has
to change too — they must stay compatible with each other.

### 2.2 Example: Pac-Man, "just get to a location" (pathing)

- **State space:** Pac-Man's `(x, y)` location.
- **Successor function:** N/E/S/W moves; blocked by walls (moving into a
  wall doesn't change the state).
- **Goal test:** Pac-Man is at the target location.

### 2.3 Example: Pac-Man, "eat all the dots"

Now the goal changes, so the state space must change too:

- **State space:** `(Pac-Man location, food-present bitmask)`. Since the
  map is fixed, food state can be represented as one boolean per possible
  food location — e.g. 30 food locations → a 30-bit vector.
- **Successor function:** same N/E/S/W actions, but now the *result*
  state also updates the food bitmask (eating a dot flips its bit).
- **Goal test:** all bits in the food bitmask are `false`. (Pac-Man's own
  location doesn't matter for the goal test here — only whether all food
  is gone.)

**Takeaway:** the same physical environment gives rise to *different*
search problems (different state spaces and successor functions)
depending on what the actual goal is.

---

## 3. Counting the Size of a State Space

Given a maze with:
- 120 possible Pac-Man positions
- 30 possible food locations (each present or absent)
- 12 possible positions per ghost, 2 ghosts
- Pac-Man facing one of 4 directions (N/E/S/W)

**Full world state** size (everything that could vary):

```
120 (Pac-Man position) × 2^30 (food on/off per location)
    × 12 (ghost 1) × 12 (ghost 2) × 4 (facing direction)
```

The `2^30` term dominates and makes this astronomically large — this is
why counting state spaces matters: the exponent is what should worry you.

**Search-problem state space** size depends on *what the problem actually
needs to track*:
- *Pathing* (§2.2): only needs Pac-Man's position → **120** states. Small
  and fast to search.
- *Eat-all-dots* (§2.3): needs position **and** food bitmask, but not
  ghost position or facing (irrelevant to this goal) → `120 × 2^30`
  states. This is why full planning (§1.2 demo) took a while to compute —
  the state space it has to reason over is enormous, even though the maze
  itself is small.

(Aside from lecture Q&A: this count is technically a slight
over-estimate, since e.g. "Pac-Man standing on a food square with the
food still present" can't actually occur — food is eaten instantly on
arrival. In practice you treat this as a ballpark estimate, not an exact
count.)

### 3.1 Harder example: eat all dots while keeping ghosts scared

Class exercise: Pac-Man must eat all dots while ghosts stay scared the
entire time (eating a power pellet scares ghosts for a while; if a scared
ghost's timer runs out, the game effectively ends because it's no longer
achievable to "always keep ghosts scared").

What needs to be in the state space? By working backward from what the
**goal test** and **successor function** each require:

- **Food pellet locations** — needed for the goal test (all food eaten).
- **Power pellet locations remaining** — needed by the successor function,
  to know when Pac-Man eats one and resets the scared timer.
- **Scared-ghost timer** — needed by the successor function, to know when
  the "game over" transition happens (ghosts stop being scared).
- **Ghost locations** — needed *only if* your model assumes ghosts can
  respawn un-scared after being eaten while scared (then you must track
  them to detect that event). If you model the world as "ghosts never
  respawn un-scared, just trust the timer," you can drop ghost locations
  from the state.

This illustrates the general method: for each candidate state variable,
ask (1) do I need it for the **goal test**, and (2) do I need it for the
**successor function** to correctly simulate what happens next? Also
consider: don't over-simplify past what the goal test/successor function
actually need (e.g., tracking the exact set of remaining food locations
rather than just a count, because the goal test needs to know *when* food
is gone, and the successor function needs to know *which* dot Pac-Man is
currently on).

---

## 4. State Space Graphs vs. Search Trees

- A **state space graph** is a mathematical representation of a search
  problem: nodes = (abstracted) states, edges = the successor function,
  and some nodes satisfy the goal test. **Each state appears exactly
  once** in this graph.
- In practice, state space graphs are usually far too large to build
  explicitly (recall `2^30`-scale examples above) — they're a conceptual
  tool, not something you construct on a computer.
- A **search tree** is what a search *algorithm* actually builds, starting
  from the start state and repeatedly calling the successor function. A
  node in the search tree represents an entire **path** (sequence of
  states/actions) from the start, not just a single state — so the same
  state can appear in the tree multiple times, once per distinct path that
  reaches it.
- Because of this, the search tree can be **much larger** than the state
  space graph — and can even be **infinite** for a tiny, finite state space
  graph. Example: a 4-node graph (`S, A, B, G`) where cycles exist between
  nodes produces an infinite search tree, because paths can loop
  (`S→A→B→A→B→...`) forever.
- In practice, search algorithms build the search tree **incrementally, on
  demand** — just enough of it to find a solution, not the whole thing.

---

## 5. Generic Tree Search Algorithm

This is the shared skeleton behind DFS, BFS, and Uniform Cost Search — the
**only thing that differs between them is the strategy for picking which
node to expand next.**

```
initialize the search tree with just the start state
loop:
    if the fringe (set of leaf nodes) is empty: return failure  (no solution)
    choose a leaf node from the fringe according to the search strategy
    if that node's state passes the goal test: return the corresponding plan (success)
    else: expand it — call the successor function on its state,
          add the resulting children to the fringe
```

Key vocabulary:
- **Fringe** (a.k.a. frontier) — the set of leaf nodes of the search tree
  that are candidates for expansion.
- **Expansion** — removing a node from the fringe, calling the successor
  function on it, and adding its children back to the fringe.
- **Strategy** — the rule for choosing *which* fringe node to expand next;
  this is the one thing that varies between DFS/BFS/UCS.

**Important subtlety:** you only declare success when you **expand** a
node and its state passes the goal test — not merely when a goal state
first *appears on the fringe*. (The lecture calls out that stopping as
soon as a goal node appears on the fringe, rather than waiting until it's
actually selected for expansion, is one of the most common bugs students
make in Project 1. It matters once cost-based strategies like UCS are in
play — see §8.)

### 5.1 Worked trace (small graph)

Using a small hand-drawn graph (`S → D/E/P`, etc., ending at goal `G`),
the lecture traces the fringe step by step: `S` is expanded first (only
option); then a node is picked from the fringe per the chosen strategy,
checked against the goal test, and if not a goal, expanded — repeating
until a node reaching `G` is popped **and** checked, at which point the
plan `S → E → R → F → G` is returned. The full search tree for this tiny
problem is far larger than what actually needed to be explored to find
the solution — illustrating why the *strategy* (which leaf to expand)
matters so much.

---

## 6. Evaluating Search Strategies

Four properties used to compare strategies, defined using:
- **b** = branching factor (successors per node, assumed uniform for
  analysis)
- **m** = maximum depth of the search tree (could be infinite)
- **s** = depth of the shallowest solution

| Property | Meaning |
|---|---|
| **Complete** | Guaranteed to find a solution if one exists. |
| **Optimal** | Guaranteed to find the *least-cost* solution. |
| **Time complexity** | How much work (roughly, nodes expanded) to find a solution. |
| **Space complexity** | How much memory (roughly, max fringe size) is needed. |

A full tree of depth `m` with branching factor `b` has `b^m` nodes in its
last layer alone — and since growth is exponential, the last layer
dominates the total node count, so the whole tree is `O(b^m)`.

---

## 7. Depth-First Search (DFS)

**Strategy:** always expand the **deepest** node on the fringe first
(ties broken arbitrarily, e.g. alphabetically).

Traced on the example tree: DFS drives straight down one branch until it
hits a dead end (no successors), backtracks to the next-deepest option,
and continues — sweeping left to right through the tree until it happens
to expand the goal.

| Property | DFS |
|---|---|
| Time | `O(b^m)` — worst case, must explore the whole tree if the solution is at the far end. |
| Space | `O(b·m)` — only needs to remember the current path plus each path's unexplored siblings. **Much better than the tree's total size.** |
| Complete | Yes, **if** the tree is finite (bounded `m`). Not complete on infinite trees — DFS can go down an infinite branch and never come back. |
| Optimal | **No** — it returns whatever solution it finds going left-to-right, which may be far from cheapest. |

---

## 8. Breadth-First Search (BFS)

**Strategy:** always expand the **shallowest** node on the fringe first —
i.e., explore the tree layer by layer.

| Property | BFS |
|---|---|
| Time | `O(b^s)` — depends on the depth of the shallowest solution, not the whole tree. |
| Space | `O(b^s)` — the fringe holds an entire near-complete layer at the deepest point reached, which is exponential in `s`. **Much worse than DFS's memory usage.** |
| Complete | Yes — it will eventually reach any existing solution's depth. |
| Optimal | **Only if all action costs are equal** (e.g., cost 1 per step) — then shallowest = cheapest. If action costs differ, BFS is **not** guaranteed optimal (it only minimizes number of actions, not total cost). |

### 8.1 DFS vs. BFS trade-offs (from demos)

- If the goal lies deep in a mostly-fruitless part of the tree while a
  shallow solution exists on the *other* side, **BFS drastically
  outperforms DFS**, since DFS could sweep the entire unhelpful branch
  first.
- Conversely, if there are many goal states and they're all deep, DFS may
  find one quickly while BFS is still busy clearing shallow layers.
- If you have **memory constraints**, DFS's much lower space complexity
  may force your hand even if you'd prefer BFS's shortest-path guarantee.

Grid-maze visual demos in the lecture confirm this directly: BFS expands
outward from the start roughly by distance (bending around walls); DFS
finds *a* solution but takes an erratic, often much longer path.

---

## 9. Iterative Deepening

**Motivation:** BFS finds shallow/short solutions without wasting time on
huge deep subtrees, but costs a lot of memory. DFS is memory-cheap but can
go down unbounded/unhelpful branches. **Iterative deepening** combines
DFS's space efficiency with BFS's behavior of finding shallow solutions
first.

**Idea:** run depth-limited DFS repeatedly, increasing the depth limit
each round:
1. Run DFS with depth cap 1. If no solution found, stop and go to the next
   round (the successor function is modified to report "no successors
   beyond depth 1").
2. Increase the cap to 2 and re-run DFS from scratch.
3. Keep increasing the cap by 1 and re-running until a solution is found.

This never uses more memory than plain DFS (since each round is just a
depth-limited DFS), while still finding the shallowest solution first, like
BFS.

**On the redundancy concern:** re-running DFS from scratch at each
increasing depth cap seems wasteful (you redo all the earlier, shallower
work every round) — but it's not as bad as it sounds. Because trees grow
exponentially with depth, the **last layer explored is roughly as large as
all previous layers combined**, so the marginal cost of one extra round of
iterative deepening is comparable to the cost of a single BFS layer
expansion. This is why the technique is worth using despite looking
redundant on paper.

---

## 10. Uniform Cost Search (UCS)

**Motivation:** what if actions have **different costs**, not just a flat
cost of 1 per step?

**Strategy:** like BFS, but instead of "expand shallowest first," **expand
the fringe node with the lowest cumulative path cost first.**

**Worked trace:** starting from `S`, the fringe holds nodes with
cumulative costs (e.g. 1, 9, 3); UCS always pops the lowest — expand cost
3, then compare remaining costs, etc., accumulating path cost as it goes
(e.g. a step of cost 3 then a step of cost 2 gives a cumulative cost of 5
for that node). Even when a goal state first appears on the fringe (say,
with cost 9), **UCS does not stop** — it keeps expanding lower-cost nodes
first, because a cheaper path to the goal might still be discovered
through one of them. Only once the **goal node itself is popped for
expansion** (i.e., it has the lowest cumulative cost on the fringe) does
UCS declare success — at that point, by construction, every other path
that could still be found costs at least as much, so the returned
solution is guaranteed optimal.

### 10.1 Properties

Let `C*` = optimal solution cost, and `ε` (epsilon) = the minimum cost of
any single action (all costs assumed positive). Define **effective depth**
= `C*/ε` — the deepest a path could go while still costing less than
`C*`.

| Property | UCS |
|---|---|
| Time | `O(b^(C*/ε))` |
| Space | `O(b^(C*/ε))` |
| Complete | Yes (assuming positive costs, no negative-cost cycles). |
| Optimal | **Yes** — whenever the goal is expanded, nothing remaining on the fringe can possibly be cheaper. |

### 10.2 Limitation

UCS explores outward in **every direction** based purely on cost so far —
it has no notion of *where the goal is*, so it can waste a lot of work
exploring cost-cheap regions that lead away from the goal. (Demo: in a
maze with cheap "shallow water" and expensive "deep water" terrain, UCS
correctly prefers shallow water, expanding it faster than deep water — but
it's still blind to the goal's direction, unlike BFS/DFS which ignore
terrain cost entirely.) This blindness to the goal's location is exactly
what the **next lecture (A\* search / heuristics)** addresses.

---

## 11. Unifying DFS, BFS, and UCS

All three algorithms are the **same generic tree search** (§5) — they only
differ in the **priority** used to pick the next fringe node. This means a
single implementation (a priority queue) can support all three by simply
changing the priority function:

| Strategy | Priority (lower value popped first) |
|---|---|
| DFS | Prefer **deeper** nodes (e.g., priority = negative depth, or implemented as a stack/LIFO). |
| BFS | Prefer **shallower** nodes (implemented as a queue/FIFO). |
| UCS | Prefer **lowest cumulative path cost**. |

This is the recommended way to structure Project 1's search code — one
generic search function parameterized by a fringe data structure /
priority function, rather than separate implementations per strategy.

---

## 12. Where Search Goes Wrong in Practice

Two real-world examples of search "failing" that are actually **modeling**
failures, not algorithm failures:

1. **MapQuest turn-by-turn routing:** a route directs a driver to make a
   turn that's not actually usable by a car. This isn't a bug in A*/UCS/
   BFS — it means the **map data (state space) didn't match reality**
   (e.g. a turn that's graph-legal but physically restricted).
2. **Boat-trip routing bug:** a route sends a car across water on a "boat
   trip," repeatedly. Likely not an algorithm bug — more likely the map is
   **missing an edge/path** near the destination, so the state space
   graph simply doesn't contain the real route; the successor function
   just keeps returning whatever's actually in the (incomplete) graph.

**Takeaway:** when search produces a bad-looking result on a real-world
problem, the first thing to question is whether the **search problem
formulation** (state space / successor function / costs) actually
captures the real world correctly — not whether the search algorithm
itself is broken.

---

## 13. Summary Table

| Strategy | Fringe order | Time | Space | Complete? | Optimal? |
|---|---|---|---|---|---|
| DFS | Deepest first | `O(b^m)` | `O(b·m)` | Yes, if tree finite | No |
| BFS | Shallowest first | `O(b^s)` | `O(b^s)` | Yes | Only if uniform step cost |
| Iterative Deepening | Depth-limited DFS, increasing limit | ~`O(b^s)` | `O(b·s)` | Yes | Only if uniform step cost |
| Uniform Cost Search | Lowest cumulative cost first | `O(b^(C*/ε))` | `O(b^(C*/ε))` | Yes | Yes |

Next lecture: **A\* search**, which adds a heuristic to UCS so the search
is informed about *where the goal is*, rather than expanding blindly in
every cost-cheap direction.
