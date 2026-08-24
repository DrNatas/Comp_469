# CS188 Lecture 3 — Informed Search: Heuristics, Greedy Search, A* (AIMA 3.5–3.6)

*Cleaned-up lecture transcript, organized by topic. Timestamps and course
announcements (homework/project deadlines, discussion sections, etc.)
removed — those are administrative, not lecture content.*

> **A note on this cleanup:** this file was generated from auto-captions
> (`COMPSCI 188 - 2018-08-30 - A＊ Search and Heuristics [Mlwrx7hbKPs].en.srt`),
> which are speech-recognition output, not a human transcript. The captions
> are reorganized into topic sections and lightly cleaned for readability;
> the underlying explanations, examples, and proofs are all preserved. The
> original `.srt` is untouched — check it against the source video if exact
> wording ever matters.

---

## 1. Recap: What Is a Search Problem?

A **search problem** is defined by:

- A set of **states** — an abstraction of the world relevant to the
  agent's decision, not necessarily every real-world detail.
- **Actions**, each typically with an associated **cost**.
- A **successor function** — for a state and an action, returns the
  resulting state and its cost.
- A **start state**.
- A **goal test** — checks whether a given state satisfies the goal
  condition.

The **search tree** is built (usually only partially) from this problem:
nodes correspond to *paths* to states, and a path's cost is the sum of the
costs of the actions along it. A **search algorithm** systematically
builds out the search tree (ideally only a small fraction of it), choosing
an order in which to expand nodes from the **fringe** (the set of nodes
ready to be expanded). An **optimal** search algorithm finds least-cost
plans.

### 1.1 A non-pathing example: pancake flipping

Not all search problems are about physically moving through space. Setup:
4 pancakes of different sizes; goal is to stack them with the biggest on
the bottom and smallest on top.

- **Actions:** insert a spatula between two pancakes (or under the bottom
  one) and flip everything above the spatula. For a stack of 4, there are
  3 useful spatula positions (between pancakes 2–3, 3–4, or below pancake
  4 — inserting between 1–2 does nothing useful).
- **Cost:** number of pancakes flipped by that action.
- **State space size:** 4 choices for the bottom pancake × 3 for the next
  × 2 × 1 = **24 states** total.
- **Goal:** the fully sorted stack.

(Fun aside from the lecture: this abstraction — "pancake flipping" as a
sorting problem — was the subject of an actual paper co-authored by Bill
Gates and Christos Papadimitriou.)

### 1.2 Generic tree search (recap)

```
fringe = [start state]
loop:
    if fringe is empty: return failure
    node = choose from fringe (per strategy)
    if node passes goal test: return corresponding plan (success)
    else: expand node (call successor function), add children to fringe
```

This same loop underlies **every** strategy covered so far (DFS, BFS,
uniform cost) and the new ones in this lecture (**greedy search**,
**A\***). The only thing that changes is the **strategy** for picking
which fringe node to expand. Implementation-wise, the fringe is a
**priority queue**, and the strategy just determines the priority
function (DFS can also use a stack, BFS a plain queue, for efficiency —
but a unified priority-queue implementation works for all of them, which
is recommended for Project 1).

---

## 2. Uniform Cost Search: Recap and Limitation

**Uniform cost search (UCS)** expands the lowest cumulative-path-cost node
on the fringe first. It is **complete and optimal** — if a solution
exists, it finds the cheapest one.

**The problem:** UCS searches **equally hard in every direction**. It only
ever asks a boolean question of a state ("does this satisfy the goal?") —
it has **no notion of which direction the goal actually is**, so it
"radiates outward" uniformly. In maze demos, UCS ends up expanding nearly
every reachable state up to the goal's distance from the start (all
states closer than the goal, plus the goal itself) — hugely wasteful when
the goal has an obvious direction.

The fix: give the search algorithm information about **where the goal
is** — this is what a **heuristic** provides.

---

## 3. Heuristics

A **heuristic** is a function that **estimates how close a state is to
the goal** (or how much more cost remains). It's designed specifically
for a given search problem — going from "uninformed" to "informed" search
means, in addition to defining the search problem itself, you must now
also design a heuristic function for it.

### 3.1 Example heuristics

| Problem | Candidate heuristic | Why it's reasonable |
|---|---|---|
| Pac-Man, single target | **Manhattan distance** | Pac-Man only moves N/E/S/W, so Manhattan distance matches the grid's movement pattern. It's cheap to compute but ignores walls, so it's just an estimate. |
| Pac-Man, single target | Euclidean distance | Computable, but a worse fit than Manhattan distance since Pac-Man can't move diagonally. |
| Romania road-trip (Arad → Bucharest) | **Straight-line distance** to Bucharest | Cheap to compute from GPS coordinates; can be precomputed into a lookup table, one number per state (how far that state is estimated to be from the goal). |
| Pancake flipping | Number of pancakes **out of place** | Every misplaced pancake must be flipped at least once, and cost = pancakes flipped per action, so this under-counts (or matches) the true remaining cost. |
| Pancake flipping | ID number of the **largest pancake still out of place** | If the largest out-of-place pancake is, say, #3, then pancakes 1–3 in the stack must all still be disturbed to fix it — this measures how deep into the stack you'll need to operate. |

Two different heuristics for the same problem can give **different
numbers**, and one can be more *precise* (closer to the true remaining
cost) than another — e.g., in one example the "largest misplaced pancake"
heuristic correctly reflected a 3-cost solution, while "count of misplaced
pancakes" gave a less precise estimate. Designing a good heuristic is
described in the lecture as **"an art form."**

**Convention:** heuristics should be scaled to match cost units, and
should read **0 at the goal state** (e.g., use `4 − (longest correctly
ordered run)` rather than the raw count, so it measures *distance from*
the goal rather than *closeness to* it).

---

## 4. Greedy Search

**Strategy:** expand the fringe node that looks **closest to the goal
right now** — i.e., pick by lowest heuristic value alone.

### 4.1 Worked example (Romania)

Starting from Arad, greedy always expands whichever fringe node has the
smallest straight-line distance to Bucharest. In the traced example, it
reaches Sibiu, then Fagaras (heuristic 176), then a node with heuristic 0
(the goal) — and declares success. **But this found path is not the
optimal one** — a cheaper route through Rimnicu Vilcea existed. Greedy
took a costly-but-heuristically-promising action (to Fagaras) instead of
a cheaper one, because **greedy search completely ignores cost already
incurred** — it only looks at the estimated remaining distance.

### 4.2 Properties

- **Not optimal** — it can go down a "rabbit hole" that looks locally
  promising and follow it to a worse overall solution, ignoring cheaper
  alternatives.
- Behaves like a "best-first" search that can go straight for the (wrong
  or right) goal; worst case it behaves like a badly-guided DFS if the
  heuristic consistently points the wrong way.
- **Fast and computationally cheap** when the heuristic is decent — in
  the Romania demo, it finds a solution (and happens to be optimal there)
  with very little search. In a Pac-Man maze demo, greedy expands far
  fewer nodes than UCS but returns a **suboptimal path**, because it
  never explores directions the heuristic ranks as "farther," even if
  they're actually cheaper.

---

## 5. A* Search

**Motivating analogy (Tortoise and the Hare):** UCS is the tortoise —
slow and steady, tries everything that could possibly be cheaper before
declaring success, guaranteed optimal. Greedy is the hare — fast, heads
straight for what looks like the goal, but can take costly wrong turns.
**A\* aims to combine both: steady (optimal) *and* fast.**

**Strategy:** expand the fringe node with the lowest **`f(n) = g(n) +
h(n)`**, where:
- `g(n)` = **backward cost** — the cumulative cost of the path so far to
  reach `n`.
- `h(n)` = **forward cost** — the heuristic's estimate of the remaining
  cost from `n` to the goal.

### 5.1 Worked example (small graph)

Tracing a small graph: A* expands `S`, then its only child, then compares
`g+h` across the fringe, picking the lowest total each time — it may
expand *fewer* nodes than UCS (since `h` steers it toward the goal) while
still finding the optimal path, unlike greedy.

### 5.2 Critical rule: stop on **dequeue**, not enqueue

Just like tree search generally (§1.2), **A\* must not declare success the
moment a goal node is *enqueued*** onto the fringe — only when it is
**popped for expansion**. The lecture calls this out as **one of the most
common Project 1 bugs**.

**Counter-example proving why:** in a small worked graph, a goal node is
enqueued with cost 5 while a cheaper path (cost 4) is still sitting
unexpanded on the fringe via another node. Declaring success at
enqueue-time would return the length-5 path; only continuing until the
cheaper node is popped correctly returns the length-4 optimal path. The
general technique for proving "we can't stop early" is exactly this: find
one concrete counter-example where stopping early gives the wrong answer.

---

## 6. Is A* Always Optimal? — Admissibility

**Not automatically.** A* is optimal **only if the heuristic is
admissible**.

**Counter-example:** a small graph where the heuristic badly
*overestimates* the true remaining cost for the actual optimal path (says
"6 away" when really "3 away"). Because the heuristic makes that
optimal-path node look expensive, it sits on the fringe too long, and a
worse path gets popped and accepted first. **The problem: the heuristic
was too pessimistic** — the actual cost turned out smaller than the
estimate, which is backwards from what's required.

### 6.1 Definition: admissibility

Let `h*(n)` = the true optimal cost from node `n` to the nearest goal
(usually unknown in practice, but well-defined mathematically). A
heuristic `h` is **admissible** if, for every node `n`:

```
h(n) ≤ h*(n)      (h never overestimates the true remaining cost — "optimistic")
```

- Manhattan/straight-line distance heuristics: admissible, since the true
  cost (with walls, indirect roads, etc.) can only be equal to or greater
  than the direct-line estimate.
- Pancake "largest misplaced pancake ID" heuristic: admissible, because
  you must at minimum disturb the stack down to that depth.

**If `h` is admissible, A\* tree search is optimal.** If `h` is
*inadmissible* (too pessimistic somewhere), that guarantee breaks,
because promising partial plans can get stuck on the fringe too long
while a worse plan is accepted.

### 6.2 Formal proof sketch (tree search, admissible heuristic)

Setup: let `A` be an optimal goal node (encodes the shortest path to any
goal), `B` a suboptimal goal node, and assume `h` is admissible. **Claim:
`A` will always be popped from the fringe before `B`.**

1. Suppose `B` is ever on the fringe. Then some ancestor `n` of `A` (or
   `A` itself) must also be on the fringe — because if all of `A`'s
   ancestors were gone, `A` itself would already have been expanded.
2. `f(n) = g(n) + h(n) ≤ g(A)` — this step uses **admissibility directly**:
   `h(n)` never overestimates the true remaining cost from `n`, and the
   true remaining cost from `n` (along the path toward `A`) is exactly
   `g(A) − g(n)`, so `g(n) + h(n) ≤ g(A)`.
3. `g(A) = f(A)`, since `A` is a goal node and admissible heuristics must
   read `h = 0` at goal states (a heuristic can't be admissible while
   overestimating a true cost of 0 — so `h(A) = 0`, `h(B) = 0`).
4. `f(A) < f(B)`, since `A` is optimal and `B` is suboptimal, i.e.
   `g(A) < g(B)`, and both have `h = 0`.
5. Chaining: `f(n) ≤ f(A) < f(B)`, so `n` (the ancestor) is expanded
   before `B`. Repeating this argument for each successive ancestor of
   `A` shows that eventually `A` itself is expanded before `B`.

**Why this alone doesn't fully finish the proof (raised in Q&A):** showing
`f(n) < f(B)` for one ancestor isn't automatically enough — you need the
full chain, expanding in strict order of `f`-cost, to guarantee it
propagates down to `A` itself actually popping before `B`. The full
formal write-up is in the lecture slides; the intuition above is the
core of it.

**Special case:** if `h(n) = 0` everywhere, admissibility trivially holds,
and A* **reduces to uniform cost search** — so this proof also shows UCS
is optimal, as a degenerate case of A*. (It's just less efficient than
A* with a genuinely informative admissible heuristic.)

---

## 7. A* in Practice: Demos and Efficiency

- **Open maze:** UCS radiates equally in all directions; A* (using
  half the straight-line distance as `h`) still expands somewhat in all
  directions but **favors the goal's direction** and expands far fewer
  nodes.
- **Pac-Man maze comparison:**
  - Greedy: expands very few nodes, fast, but **suboptimal** path.
  - UCS: expands almost every state closer than the goal — thorough but
    slow.
  - A*: expands *more* than greedy but *far less* than UCS, and still
    finds the **optimal** path — "best of both worlds."
- **Large maze, node-expansion counts (UCS vs. A\* with the misplaced-tile
  heuristic on the 8-puzzle, see §8):** UCS explored **over 9,000 nodes**;
  A* found the optimal solution in only **175 nodes**.
- **Water maze (shallow/cheap vs. deep/expensive terrain):** BFS ignores
  cost entirely (steps only); greedy chases the heuristic and does little
  work but finds a poor path; UCS favors cheap terrain but still expands
  in every direction, ignoring the goal's location; **A\* uses both cost
  so far and estimated distance to goal**, doing a modest amount of work
  while still finding the optimal path.

A* is described as **the go-to planning algorithm** in practice — used in
video games, routing, speech-recognition decoding, machine translation,
and more.

---

## 8. Designing Heuristics: The 8-Puzzle

**Problem setup:** the 8-puzzle (sliding tiles on a 3×3 board with one
blank).

- **State space size:** `9!` (9 positions for the first tile, 8 for the
  next, etc.).
- **Actions:** slide a tile into the empty space (equivalently, move the
  blank around) — up to 4 successors from a given state.
- **Cost:** 1 per tile move (a design choice).

### 8.1 Heuristic 1 — number of misplaced tiles

Admissible: every misplaced tile requires at least one action to fix, so
this never overestimates. Node-expansion results (UCS vs. A* with this
heuristic), by solution depth:

| Solution depth | UCS nodes expanded | A* (misplaced-tiles) nodes expanded |
|---|---|---|
| 4 steps | 112 | fewer |
| 8 steps | 6,300+ | fewer |
| 12 steps | ~3.6 million | 227 |

### 8.2 Heuristic 2 — total Manhattan distance (sum over all tiles)

Sums each tile's Manhattan distance from its current position to its goal
position. **More informative** (closer to true cost) than "misplaced
tiles" — brings the 12-step case down from 227 nodes to **73 nodes**
(vs. UCS's ~3.6 million).

### 8.3 The "relaxed problem" trick for building admissible heuristics

A general recipe: take the original problem and **add new actions** that
make it easier (a "relaxed" version). Since the relaxed problem has
*more* options available, its optimal solution cost can only be **less
than or equal to** the true problem's optimal cost — which is exactly the
admissibility condition. So: **the optimal cost of a relaxed problem is
an admissible heuristic for the original problem.**

- *Misplaced tiles* = relaxed problem where you can teleport any tile
  directly to its destination (ignore the sliding/blocking constraint).
- *Total Manhattan distance* = relaxed problem where tiles can slide
  through each other without blocking.
- (Pac-Man analogy, mentioned for contrast: ignoring walls.)

### 8.4 Trade-offs and heuristic dominance

- Using `h = h*` (the true optimal remaining cost) would be admissible
  and minimize node expansions — but it's not useful, because **if you
  already know the true cost, you've already solved the problem.**
- General trade-off: heuristics closer to the true cost expand fewer
  nodes but usually cost more to *compute*; cheaper heuristics are faster
  per-node but less informative (more nodes expanded overall).
- **Dominance:** heuristic `h_a` **dominates** `h_c` if `h_a(n) ≥ h_c(n)`
  for *every* node `n` (not all heuristics are comparable this way — some
  are higher on some nodes and lower on others). Dominance forms a
  partial order ("semi-lattice"), with the trivial `h = 0` heuristic at
  the bottom and the exact `h*` at the top; higher in the order generally
  means more informative but potentially more expensive to compute.
- **Useful trick:** if you have two (or more) admissible heuristics, their
  **max** is also admissible, and dominates (is at least as informative
  as) either individual one.

---

## 9. Graph Search: An Upgrade to Tree Search

**Motivation:** in a search *tree*, the same state can be reached via many
different paths and thus appear as many different nodes — this causes
**exponential blow-up** relative to the (much smaller) state space graph,
much of it redundant.

**Idea:** maintain a **closed set** (set of already-expanded states).
Before calling the successor function on a state, check whether it's
already in the closed set — if so, skip it; if not, expand it and add it
to the closed set. **A state is never expanded twice.**

- Use a **set**, not a list, for the closed set — list membership checks
  are far slower and would bottleneck the algorithm. (Some textbooks use
  the term "closed list," but a set is the correct data structure.)
- **Completeness is preserved:** anything excluded by the closed-set check
  is something you've already found another way to reach, so no
  reachable goal becomes unreachable.

### 9.1 Graph search can break A*'s optimality — need for consistency

**Counter-example:** a search tree where A* first reaches some state `C`
via an expensive path, expands from there, and only *later* discovers a
cheaper path to the same `C`. Since `C` is already in the closed set, the
cheaper route is skipped — **A\* + graph search + only admissibility can
return a suboptimal solution**, because the *first* time a state is
expanded isn't guaranteed to be via the optimal path to it.

**Fix: require a stronger property — consistency (a.k.a. monotonicity).**

### 9.2 Definition: consistency

A heuristic `h` is **consistent** if, for every edge from node `n` to
successor `n'` with step cost `cost(n, n')`:

```
h(n) ≤ cost(n, n') + h(n')
```

(Admissibility only constrains `h` relative to the *true total remaining
cost*; consistency is a **local**, edge-by-edge condition tying `h` to
actual step costs.) In the lecture's counter-example, `h(n)=4` with an
edge of cost 1 to a node with `h=1` is **inconsistent** (`4 > 1 + 1`);
raising that second heuristic value to 2 restores consistency and fixes
the optimality problem in that example.

### 9.3 Why consistency fixes graph search: F never decreases

From consistency, `h(n) ≤ cost(n,n') + h(n')`; adding the accumulated
backward cost `g(n)` to both sides and using `g(n') = g(n) + cost(n,n')`
gives:

```
f(n) ≤ f(n')
```

i.e., **`f`-values never decrease along any path as you expand deeper.**
Consequence: once you expand the goal state, everything remaining on the
fringe must have an `f`-cost **at least as high**, so nothing left could
possibly produce a cheaper path — the first time you pop a goal state
with graph search + a consistent heuristic, it's guaranteed optimal. (A
fuller formal proof is left in the lecture slides.)

### 9.4 Summary of optimality conditions

| Search variant | Optimality condition |
|---|---|
| A* **tree search** | Admissible heuristic |
| A* **graph search** | **Consistent** heuristic (stronger than admissible) |

---

## 10. Lecture Summary

- A* uses both **backward cost** (`g`, cost so far) and **forward cost**
  (`h`, heuristic estimate) — `f(n) = g(n) + h(n)`.
- Optimal for **tree search** with an **admissible** heuristic
  (`h(n) ≤ h*(n)` everywhere); optimal for **graph search** with a
  **consistent** heuristic (`h(n) ≤ cost(n,n') + h(n')` for every edge).
- **Heuristic design is the key skill** for making A* actually effective
  in practice (this is a major focus of Project 1) — the **relaxed
  problem** technique (add actions to make the problem easier, then use
  its optimal cost as `h`) is the standard way to construct admissible
  heuristics.
- A* must stop only when a goal node is **dequeued/popped for
  expansion**, never merely when it's enqueued — this is one of the most
  common implementation bugs.
- **Graph search** (tracking a closed set of expanded states) avoids the
  exponential blow-up of re-exploring the same state via many paths, but
  requires a **consistent** (not just admissible) heuristic to stay
  optimal.
