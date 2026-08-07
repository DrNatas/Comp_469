# CS188 Lecture 5 — Constraint Satisfaction Problems, Part 1 (AIMA 6.1)

*Cleaned-up lecture transcript, organized by topic. Timestamps, class
housekeeping ("giant slides check," attendance banter, break announcement)
removed — those are administrative, not lecture content.*

> **A note on this cleanup:** this file was generated from auto-captions
> (`COMPSCI 188 - 2018-09-04 - Constraint Satisfaction Problems (CSPs) Part
> 1⧸2 [81z2ANjQcH4].en.vtt`), which are speech-recognition output, not a
> human transcript. This caption track uses **rolling duplicate lines**
> (each cue re-shows the previous line plus one new line), so the raw
> `.vtt` was first deduplicated into continuous text, then reorganized into
> topic sections and cleaned for readability — punctuation, capitalization,
> and a handful of clear ASR misrecognitions fixed (e.g. "art consistency"
> → "arc consistency," "essay"/"si" → "SA" for South Australia, "for
> checking" → "forward checking"). The underlying explanations, examples,
> and Q&A exchanges are preserved. The original `.vtt` is untouched — check
> it against the source video if exact wording ever matters.

---

## 1. Recap: What Search Assumed, and Where It Breaks Down

Every search algorithm so far has secretly relied on a bundle of
assumptions about the world:

- **Single agent** — you're making the plan; no other agents whose actions
  are uncertain or adversarial.
- **Deterministic** — the plan, once executed, unfolds exactly as modeled.
  This requires the model itself to be correct.
- **Fully observed** — you know the complete current state of the world,
  so you can simulate forward and predict how it evolves.
- **Discrete state space.**

These are all simplifications, and the rest of the course is largely about
relaxing them one at a time.

Within that world, search so far has targeted **planning problems**: what
matters is the *sequence of actions* — the path to the goal — which is why
concepts like path cost and depth show up everywhere. Heuristics are the
tool for injecting problem-specific bias into an otherwise generic search
procedure ("the goal is probably this way").

There's a second class of problems: **identification problems**. Here you
don't care about the path or how long it took to find the answer — you
just want the final **assignment** itself, and in general all such
assignments are the same "length" (every variable gets a value). CSPs are
a special case of identification problems, and because they're a special,
more structured case, they admit algorithms that plain black-box search
can't use.

---

## 2. What Makes a CSP Different from Standard Search

In ordinary search, a state is a black box — some opaque data structure
you can only call `getSuccessors()` and `isGoal()` on. The goal test can
be *any* function over states; think of it as a judge who looks at each
candidate plan and says "goal" or "not goal," with no explanation.

A CSP exposes structure instead:

- A set of **variables** `X_1, ..., X_n`.
- Each variable has a **domain** `D_i` of values it can take (domains can
  differ per variable).
- A **state** is an assignment of domain values to (some or all of the)
  variables.
- The **successor function** is just "assign a value to one more
  unassigned variable."
- The **goal test** is decomposed into a set of explicit **constraints** —
  rules about which combinations of variable/value pairs are legal.

Instead of a judge who only says legal/illegal, you now have the actual
laws written down, so you can check "am I currently breaking a rule?"
*before* reaching a complete assignment — and detect errors early. Writing
down variables, domains, and constraints is a **representation language**:
it's a model of the problem that a general-purpose CSP solver can then
exploit with specialized algorithms, rather than treating the problem as
an opaque search black box.

---

## 3. Example 1: Map Coloring (Australia)

The running example for the lecture (and the book): color a map of
Australia's states/territories so that no two adjacent regions share a
color.

- **Variables:** one per region — `WA`, `NT`, `SA`, `Q`, `NSW`, `V`, and
  `T` (Tasmania, a disconnected island — color it whatever, which turns
  out to matter later).
- **Domains:** `{red, green, blue}` for each variable.
- **Constraints:** adjacent regions must differ. These can be written two
  ways:
  - **Implicit constraint** — a snippet of code you execute to check
    legality, e.g. `WA != NT`: look up both values, return true/false.
  - **Explicit constraint** — an enumerated list of legal pairs in the
    joint cross-domain, e.g. `(WA, NT) ∈ {(red,green), (red,blue),
    (blue,green), ...}` (but never `(red,red)`).
- **Solution:** any assignment where every variable has a value and no
  constraint is violated — e.g. `WA=red, NT=green, SA=blue, Q=red,
  NSW=green, ...`. In general, if a CSP has one solution it usually has
  many (often exponentially many).

---

## 4. Example 2: N-Queens — Two Formulations

Place N queens on an N×N board so that none attack each other (no shared
row, column, or diagonal).

### 4.1 Formulation A: one variable per square

- **Variables:** `X_ij` for every square — quadratically many (`N²`).
- **Domains:** `{empty, queen}` (or `{0, 1}`).
- **Constraints:** for any two squares that share a row, column, or
  diagonal, forbid both being `1` — e.g. for `X_ij` and `X_ik`, legal
  cross-domain pairs are `(0,0), (0,1), (1,0)`, never `(1,1)`.
- **Problem:** if that's *all* the constraints, the trivial all-empty
  board satisfies everything — nothing forces N queens to actually be
  placed. You need one more constraint, e.g. an implicit one: `sum of all
  X_ij == N` (this can't easily be written explicitly — it needs looping
  code).

### 4.2 Formulation B: one variable per row

- **Variables:** `Q_k`, one per row.
- **Domain:** which column the queen in that row occupies. This bakes in
  "exactly one queen per row" for free — no separate sum constraint
  needed.
- **Constraints:** for every pair of queens `(Q_i, Q_j)`, forbid
  column/diagonal collisions — e.g. `(Q_1, Q_2)` can be `(1,3)` or `(1,4)`
  but not `(1,2)` (diagonal threat).

**Lesson (same as in search):** how you formulate a problem matters. A
formulation that bakes more of the solution's structure directly into the
variables/domains (Formulation B) gives a smaller, easier-to-search space
than one that needs extra bookkeeping constraints bolted on
(Formulation A).

---

## 5. Constraint Graphs

A **constraint graph** has one node per variable and an edge for each
constraint that touches (at most) two variables. It tells you *where*
constraints are, not *what* they are — you'd still need to look inside an
edge to see it's e.g. an inequality.

- **Binary CSP:** every constraint touches at most two variables — these
  can be drawn as normal graph edges.
- **Unary constraints:** restrictions on a single variable's domain
  (really just a domain reduction, e.g. "this square must be green").
- Constraint graphs let algorithms exploit graph structure/topology —
  different shapes admit different specialized algorithms (previewed for
  a later lecture).

In the AI Space applet used for demos, each variable is drawn as a circle
showing its current domain (e.g. all of `{1,2,3,4,5}` for 5-Queens before
anything is assigned), and edges between variables (e.g. between queens
`A` and `B`) hide an underlying constraint (e.g. "not vertically or
diagonally threatening") inside the edge.

---

## 6. Example 3: Cryptarithmetic

The classic puzzle where letters stand for digits and the arithmetic must
work out (e.g. `TWO + TWO = FOUR`).

- **Variables:** one per letter (`T`, `W`, `O`, ...), **plus** extra
  variables for the **carry bits** at each column of the addition.
- **Domains:** digits for the letters; a restricted domain (`{0,1}`) for
  the carry bits.
- **Constraints:**
  - **All-diff:** every letter must map to a different digit (otherwise
    everything collapses to `0`). An all-diff constraint touching many
    variables can be decomposed into a bunch of pairwise
    not-equal constraints.
  - **Arithmetic constraints** relating a column's letters and its carry,
    e.g. `O + O = R + 10 * carry`.
- **Drawing this as a constraint graph:** an all-diff (or any constraint
  touching 3+ variables) can't be drawn as a simple edge. Convention:
  draw a **square** for the constraint with lines to every participating
  variable — an edge is really just the special case of a square in the
  middle of a 2-variable constraint.

---

## 7. Example 4: Sudoku

- **Variables:** the open squares.
- **Domain:** `1`–`9`.
- **Constraints:** all-diff across each row, each column, and each 3×3
  box. Pre-filled squares are effectively **unary constraints** ("this
  square must be `1`").
- **Aside:** some Sudoku puzzles solve themselves through pure propagation
  (pick a square, it pins down another, which pins down another...);
  others require guessing, hitting dead ends, and backtracking. That
  difficulty gap maps directly onto the algorithms covered later in this
  unit (filtering vs. plain backtracking).

---

## 8. Example 5: The Waltz Algorithm (Line-Drawing Interpretation)

An early computer-vision algorithm (not how vision is done today, but a
historically important example of CSP-as-perception) for interpreting
line drawings of 3D objects — deciding which edges/corners are convex
("outie") vs. concave ("innie"), and what's occluding what.

- **Variables:** each line intersection in the drawing.
- **Values:** the local interpretation at that intersection (e.g.
  outie/innie).
- **Constraints:** connected intersections must have compatible
  interpretations (can't have one side declared convex and the connected
  side concave).
- Solutions correspond to physically realizable 3D interpretations of the
  2D line drawing — an early example of computation giving rise to
  something like visual reasoning, quite different in flavor from
  path-search.

---

## 9. Varieties of CSPs and Constraints

This class focuses on **discrete, finite-domain** CSPs, but it's worth
knowing the landscape:

| Domain type | Notes |
|---|---|
| Discrete, finite | If every domain has `D` values, complete assignments are `O(D^N)` — already exponential. Includes **Boolean CSPs / SAT** (domain `{true, false}`, constraints = clauses) — known **NP-complete**. |
| Discrete, infinite | E.g. integers or strings as domain values. With **linear constraints** (e.g. job scheduling: "job A ends before job B starts") these are solvable, though still hard; **nonlinear constraints** can become undecidable quickly. |
| Continuous | E.g. real-valued scheduling times (telescope observation windows). With **linear constraints**, these are **linear programs** — solvable in polynomial time (seen in CS 70 / CS 170). General continuous constraints are still very hard. |

**Constraint arity:**

- **Unary** — restricts a single variable's domain.
- **Binary** — relates two variables (e.g. `SA != WA`). Note: "binary
  constraint" is about the constraint's arity, not the variables having
  binary domains.
- **Higher-order** — three or more variables at once (e.g. cryptarithmetic
  carries, all-diff).
- **Preferences / soft constraints** — not hard legality rules but costs
  ("I'd *prefer* red to green"). This turns the problem into a
  **constrained optimization problem** and foreshadows Bayes nets, which
  reason over similar graph structures but with real-valued costs — not
  covered further here.

**CSPs in the real world:** extremely common — meeting/event scheduling
("when can everyone meet"), course timetabling (fitting classes to rooms
and times with minimal conflicts), and many other real-valued,
large-scale scheduling problems.

---

## 10. Solving CSPs: The Standard Search Formulation

Map a CSP onto ordinary search:

- **State:** a partial assignment (which variables have values so far).
- **Initial state:** the empty assignment.
- **Successor function:** assign a value to one currently-unassigned
  variable.
- **Goal test:** the assignment is complete **and** satisfies all
  constraints.

### 10.1 Why naive BFS/DFS on this formulation is bad

- **Naive BFS** is the nightmare case: every solution sits at the deepest
  level of the tree (only a *complete* assignment can be a goal), and
  every shallower level has zero goals. BFS must fully expand every level
  above the solutions before reaching any of them — it explores
  everywhere the goals *aren't* before finding where they *are*.
- **Naive DFS** (assign variables one at a time, only check
  constraints/goal-test at a complete assignment) is a bit better — DFS at
  least makes a real effort toward the bottom of the tree — but it still
  wastes enormous effort: it can build up long chains of assignments that
  already violate a constraint, without noticing until the very end.

### 10.2 Backtracking Search

**Key insight:** in a CSP, once you've violated a constraint, nothing you
do deeper in the tree can un-violate it (unlike general search, where a
locally-bad-looking path can still lead somewhere good). Combined with the
fact that variable assignments are commutative (order doesn't affect the
final assignment, only search efficiency), this gives two free
improvements over naive DFS:

1. **Fix a single variable ordering** — assign one variable at a time
   rather than letting the successor function pick any variable in any
   order.
2. **Check constraints incrementally** — as soon as an assignment violates
   a constraint, stop and backtrack immediately; don't keep extending a
   doomed partial assignment.

DFS + these two improvements is called **backtracking search** — the
basic, uninformed CSP algorithm (the name is fairly generic; it isn't
describing anything fancier than "DFS that prunes on constraint
violation"). At the root, expand the first variable in the fixed ordering
into its domain values; any branch that immediately violates a constraint
against what's already assigned gets crossed off and never explored
further. Plain backtracking search can solve N-Queens for roughly `N ≈
25` — respectable, but still fundamentally exponential.

**High-level shape of the algorithm:** if the assignment is complete,
return it (no separate final constraint check needed — violations would
already have been caught along the way). Otherwise, pick an unassigned
variable (a **choice point**), pick an ordering over its domain values
(another **choice point**), and for each value, check constraints and
recurse. Backtracking search is usually implemented recursively — a bad
idea for general search (where you want fine control over the fringe/queue)
but natural here, since all you need is straightforward recurse-and-
backtrack behavior.

---

## 11. Three General-Purpose Speedup Techniques

Unlike A\*-style heuristics, which are custom to a specific search
problem, CSPs admit **general-purpose** techniques that give large speed
gains across a wide range of problems:

1. **Ordering** — which variable to work on next, and in what order to
   try its values.
2. **Filtering** — detect inevitable failure early, instead of waiting to
   hit a dead end.
3. **Structure** — exploit properties of the constraint graph itself
   (works well for some graph shapes, not others — covered in the next
   lecture).

---

## 12. Filtering, Part 1: Forward Checking

**Idea:** track a shrinking **domain** for every *unassigned* variable —
not just "assigned vs. unassigned," but a live "as far as I know, these
are still legal candidates" cloud for each unassigned variable.

**Forward checking rule:** whenever a variable is assigned, look at every
other variable connected to it by a constraint and cross off any value in
their domain that would now conflict with the new assignment. This
doesn't assign those neighbors — it just prunes their candidate lists.

- If a domain shrinks to empty at any point, there is **no** way to
  complete the assignment from here — back out immediately, without
  waiting to actually try assigning that variable.
- Even variables you haven't touched yet can visibly shrink as
  assignments accumulate elsewhere in the graph.

**Limitation:** forward checking only checks constraints between the
*newly assigned* variable and its *unassigned* neighbors. It does **not**
catch a conflict that exists purely between two variables that are both
still unassigned (e.g., `NT` and `SA` both being reduced down to only
`blue` remaining — a real problem, since they're adjacent — goes
undetected by forward checking until you actually try to assign one of
them). "Anything further is thinking too hard for forward checking."

---

## 13. Filtering, Part 2: Arc Consistency

Arc consistency formalizes what it actually means to have "checked" a
constraint, and fixes forward checking's blind spot.

### 13.1 Arcs

- The constraint graph has undirected edges, but consistency is checked
  per **directed arc**: an edge between `A` and `B` yields two arcs to
  check, `A → B` and `B → A`.
- You can even ask about an arc between two variables that *aren't*
  directly connected by a constraint (trivially consistent, since nothing
  constrains them).
- **Arc `X → Y` is consistent** if, for **every** value `x` still in `X`'s
  domain (the *tail*), there exists **some** value `y` in `Y`'s domain
  (the *head*) that doesn't violate the constraint. To *make* an arc
  consistent, delete offending values from the **tail**.

**Memory aid ("CSP police"):** think of constraints as laws and these
algorithms as police pulling an arc over and searching its trunk — if the
trunk (tail domain) has anything that's guaranteed illegal given what's
left in the head, it gets thrown out. **Always delete from the tail.**

### 13.2 Worked examples (Australia)

- `NT → WA` (given `WA = red`): checking every value left in `NT`'s
  domain against the constraint `NT != WA` — `blue` and `green` are both
  fine, but `red` is **not**, since `WA = red` leaves nothing legal for
  `NT` to pair with. Delete `red` from `NT`'s domain to restore
  consistency.
- `Q → WA`: `Q` and `WA` aren't even adjacent, so this arc is trivially
  consistent already — nothing to delete.
- **Direction matters:** checking `SA → NSW` and then `NSW → SA`
  separately can give different results, since tail and head are swapped.
  In the worked example, `SA → NSW` was consistent, but `NSW → SA` was
  not (deleting a value from `NSW`'s domain was required).
- **Cascading re-checks:** once a value is deleted from `NSW`'s domain,
  every arc that was previously declared consistent *pointing into* `NSW`
  (e.g. the earlier `SA → NSW` check) might now be invalid, because the
  deleted value may have been the very thing that was making it
  consistent. So it has to be rechecked — deletions ripple outward through
  the graph.

**Forward checking, reframed:** forward checking is exactly "enforce the
consistency of every arc that points *into* the variable you just
assigned." Full arc consistency generalizes this to **all** arcs in the
graph, including ones that don't touch the most recent assignment — which
is what lets it catch the `NT`/`SA`-both-forced-to-`blue` case that
forward checking misses.

### 13.3 The AC-3 Algorithm

Maintains a **queue of arcs** to check (a queue inside a search that
already has its own queue — "it's like Inception").

```
queue = all arcs in the graph
while queue is not empty:
    (X, Y) = queue.pop()
    if REVISE(X, Y):        # delete values from X's domain unsupported by Y
        if X's domain is now empty: FAIL
        push every arc (Z, X) back onto the queue, for all neighbors Z of X
```

`REVISE(X, Y)`: for every value in `X`'s domain, check whether *some*
value in `Y`'s domain satisfies the constraint; if not, delete it from
`X`.

- **Only defined for binary CSPs** (arcs relate exactly two variables;
  higher-order constraints aren't handled here).
- **Termination:** an arc only gets re-queued when a value is actually
  deleted from a domain, and a given domain can only lose values a finite
  number of times (`≤ D`) before it's empty — so the process is guaranteed
  to converge.
- **Runtime:** revising one arc costs `O(D²)` (check every tail value
  against every head value). With `N` variables there are `O(N²)` arcs
  (both directions), and each arc can be revisited up to `D` times — worst
  case around `O(D³N²)` (can be tightened by a factor of `D` with a
  smarter implementation, not covered here). It's polynomial — "kind of
  Gabby polynomial," but not unreasonable.
- **Why arc consistency alone can't solve CSPs:** general CSP satisfiability
  is NP-hard (SAT is a CSP), so no polynomial filtering algorithm can
  fully solve every CSP by itself — arc consistency only **prunes**;
  backtracking search is still required on top of it.

### 13.4 What arc consistency does and doesn't guarantee

After enforcing arc consistency across an entire graph, one of three
things is true:

1. **Exactly one solution remains** (sometimes achievable with zero
   further backtracking).
2. **Multiple solutions remain** — still need backtracking search to find
   one.
3. **No solutions remain, but the graph doesn't know it yet** — this can
   happen because arc consistency only reasons about **pairs** of
   variables at a time. A concrete counter-example: three mutually
   adjacent regions with only two colors' worth of "room" between them —
   every *pairwise* arc can check out consistent, while no assignment
   satisfying all three simultaneously exists. Arc consistency doesn't
   detect violations that only show up across three or more variables at
   once.

### 13.5 Forward Checking vs. Arc Consistency, head to head

Running both on the same partially-doomed map-coloring graph:

- **Forward checking** doesn't notice the graph is doomed until several
  more assignments have been made past the point where the problem was
  actually created — it wastes a chunk of computation before discovering
  the dead end (only propagates from *assigned* to *unassigned*
  variables).
- **Arc consistency** propagates the consequences of the very first
  problematic assignment much further immediately — variables far away in
  the graph already show a shrunken domain before you ever try to assign
  them. It may still require some backtracking, but that backtracking
  tends to be much more local and limited.

**Trade-off (echoes the A\* discussion):** enforcing arc consistency after
every assignment does more work per assignment (like A\*'s heuristic
computation) in exchange for needing far fewer assignments/backtracks
overall. It generally pays for itself, but — like most engineering
trade-offs — how much it pays off is problem-dependent.

---

## 14. Ordering Heuristics

Two orthogonal, general-purpose ordering ideas, layered on top of
whatever filtering algorithm is running:

### 14.1 Minimum Remaining Values (MRV) — variable ordering

Pick the unassigned variable with the **fewest legal values left** in its
(filtered) domain — i.e. work wherever the constraints are currently
"biting" hardest, rather than jumping to an unrelated, unconstrained part
of the problem.

- Also called **most-constrained-variable** or **fail-fast ordering**.
- **Why fewest, not most?** Every variable *must* be assigned eventually —
  there's no way to skip a hard one. If a branch of the search is going to
  fail, you want to discover that as early (and as cheaply) as possible,
  so you should deliberately steer toward the variable that looks most
  likely to expose a problem right now. "You should always rush into the
  scary door, because you're going to have to assign every variable
  anyway."

### 14.2 Least Constraining Value (LCV) — value ordering

For the variable currently being assigned, pick the value that **rules
out the fewest** values in neighboring variables' domains.

- This is the opposite instinct from MRV, and for a good reason:
  **variables** must all eventually be assigned, but **values** don't —
  if you pick well, you may never need to try the alternatives at all. So
  for values, chase the option most likely to succeed, not the hardest
  one.
- Computing this exactly requires simulating the filtering step for each
  candidate value to see how much it would prune — more expensive to
  compute, but can pay off by avoiding backtracking altogether.

**Summary of the asymmetry:** hardest **variable** first (fail fast, since
all variables are mandatory); easiest/most-promising **value** first
(succeed fast, since not all values need to be tried).

### 14.3 Combined demo

Running arc consistency **plus** MRV together on the same toy Australia
graph solves it quickly with little to no backtracking — the search jumps
directly to whichever variable is the current "hotspot" as propagation
narrows domains, rather than wandering to unrelated parts of the graph.
(The toy example is small enough that it doesn't really showcase where
least-constraining-value pays off — that benefit shows up more on larger,
harder problems where CSPs get genuinely difficult to solve.)

---

## 15. Closing

CSPs can be very hard to solve in general (the field's algorithms don't
change that — SAT is NP-complete, and general CSP satisfiability is
NP-hard). What today's techniques (backtracking + forward checking / arc
consistency + MRV / LCV ordering) buy you is a large practical speedup on
top of that hard ceiling — and on many real problems, that's enough to
turn an intractable brute-force search into something solvable.

**Next lecture (Thursday):** what to do when problems get big — other
solving methods beyond backtracking search, and techniques that exploit
the **structure** of a CSP's constraint graph directly.
