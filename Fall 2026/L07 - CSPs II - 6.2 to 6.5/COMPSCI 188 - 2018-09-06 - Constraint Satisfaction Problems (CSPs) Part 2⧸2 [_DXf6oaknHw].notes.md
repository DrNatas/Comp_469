# CS188 Lecture 6 — CSPs Part 2: K-Consistency, Structure, and Local Search (AIMA 6.2–6.5)

*Cleaned-up lecture transcript, organized by topic. Timestamps and class
housekeeping (a two-minute break, a quiz aside, "let's use two letters"
banter) removed — those are administrative, not lecture content.*

> **A note on this cleanup:** this file was generated from auto-captions
> (`COMPSCI 188 - 2018-09-06 - Constraint Satisfaction Problems (CSPs)
> Part 2⧸2 [_DXf6oaknHw].en.vtt`), which are speech-recognition output,
> not a human transcript. This caption track uses **rolling duplicate
> lines** (each cue re-shows the previous line plus one new line), so the
> raw `.vtt` was first deduplicated into continuous text, then reorganized
> into topic sections and cleaned for readability — punctuation,
> capitalization, and a handful of clear ASR misrecognitions fixed (e.g.
> "art/our consistency" → "arc consistency," "Wang consistency" → "node
> consistency," "editor of algorithm" → "iterative algorithm," "main
> conflicts" → "min-conflicts"). The underlying explanations, examples,
> and Q&A exchanges are preserved. The original `.vtt` is untouched — check
> it against the source video if exact wording ever matters. This lecture
> is a direct continuation of the Part 1 notes (`L06 - CSPs - 6.1/COMPSCI
> 188 - 2018-09-04 - Constraint Satisfaction Problems (CSPs) Part 1⧸2
> [81z2ANjQcH4].notes.md`) and assumes that material.

---

## 1. Recap: CSP Ingredients and Backtracking Search

A CSP has **variables**, each with a **domain** of possible values, and
**constraints** over them:

- **Implicit constraints** — a snippet of code you run against a proposed
  assignment to check legality. General, but you can't statically analyze
  or precompute anything from it, and it can be slower (you have to call
  out to it every time).
- **Explicit constraints** — a literal enumeration of the legal tuples,
  e.g. for countries `A` and `B`: `{(red,green), (green,blue), ...}`.
- The **constraint graph** only shows *where* a constraint exists (an edge
  between two variables), never *what* it is — you have to look inside the
  implicit/explicit representation to find that out. (Same idea recurs
  later with Bayes nets: the graph structure tells you which variables
  depend on which, but not the actual conditional probabilities.)
- **Arity:** unary (a restricted domain — not the same thing as a *binary
  domain*, which just means a variable has two possible values), binary
  (a constraint over exactly two variables), and higher-order (three or
  more). Not all algorithms handle higher-order constraints.

**The goal, in this class:** find *any one* solution — an assignment that
satisfies every constraint. (You could imagine other goals — find *all*
solutions, which may be exponentially many; find the *best* solution under
some weighting; answer existence questions like "is there a solution where
this node is green" — but today's algorithms are all "find one and stop.")

**Backtracking search** (from last lecture): map the CSP onto a search
tree where a state is a *partial assignment* — the root is the empty
assignment, the successor function assigns a value to one more variable,
and the leaves are complete assignments. Implemented recursively, but
behaviorally identical to depth-first search. Pseudocode shape: if the
assignment is complete, return it; otherwise pick the next unassigned
variable, loop over its domain values in some order, and for each
consistent value, recurse — backtracking on failure.

**Important framing, repeated for a reason:** solving CSPs in general is
**NP-hard**. Nothing covered today changes that fact — there will always
be CSP instances that are, as far as we know, genuinely hard. What these
techniques buy you is speed on the (very common, in practice) instances
that have exploitable structure.

---

## 2. Recap: The Three Classes of Speedup (and Why They're Different from A\*)

Unlike an A\* heuristic — which is hand-crafted for one specific problem —
these are **general-purpose** techniques: they help on many CSPs, though
not all, and there's no way to know in advance exactly how much a given
one will help on a given problem.

1. **Filtering** — after each assignment, look ahead for consequences
   ("is this subtree already doomed?") and backtrack immediately if so.
   - **Forward checking:** only propagates from the newly *assigned*
     variable to its unassigned neighbors. Cheap, but weak — it's "the
     minimum amount of filtering" needed to even call something a
     filtering algorithm.
   - **Arc consistency (AC-3):** propagates across the *whole* graph, not
     just around the latest assignment, so it detects failures earlier
     and further away. Still doesn't solve the NP-hardness, and costs
     more compute per step.
2. **Ordering** — *which* variable to assign next, and *which* value to
   try first for it.
   - **Variable ordering (MRV / fail-fast):** since every variable must
     eventually be assigned, tackle the ones with the fewest remaining
     legal values first, so failures surface early and backtracking stays
     local instead of burying you deep in the tree.
   - **Value ordering (least-constraining value):** unlike variables, you
     don't have to try every value — if the first one works, you're done.
     So be *optimistic* here: tentatively assign a candidate value, run a
     filtering pass, and prefer whichever value leaves the most domain
     values intact elsewhere (i.e. disturbs the rest of the graph least).
3. **Structure** — look at the constraint graph's shape and either exploit
   a special-purpose algorithm for that shape, or reshape the graph into
   something more tractable. **This is today's new material.**

---

## 3. Arc Consistency, Revisited

A quick re-grounding before extending the idea: an **arc** is a *directed*
edge between two variables — tail and head. Arc `X → Y` is consistent if,
for every value remaining in `X`'s domain, some value in `Y`'s domain
satisfies the constraint. To fix an inconsistent arc, delete offending
values from the **tail**.

**Worked example (mid-backtracking-search state):** `WA = red`, `Q =
green` already assigned; `NT`, `NSW`, `V`, `SA` are unassigned but have
had 0–2 domain values pruned by earlier filtering.

- `V → NSW`: check every value in `V`'s domain (the tail) — `red` is fine
  (NSW can be blue), `green` is fine, `blue` is fine (NSW can be red). Arc
  is already consistent.
- `SA → NSW`: `SA`'s only remaining value is `blue`; is there a legal
  extension at `NSW`? Yes, `red`. Consistent in this direction.
- `NSW → SA` (the *reverse* direction of the same edge — direction
  matters!): `NSW = red` can extend to `SA = blue`, fine — but `NSW =
  blue` cannot (both would be `blue`). This arc is **not** consistent;
  fix it by deleting `blue` from `NSW`'s domain.
- **Cascade:** that deletion invalidates the *earlier* `V → NSW` check —
  it had relied on `blue` still being available at `NSW`. Recheck: `V =
  red` used to be fine because `NSW` could be `blue`; now that's gone, so
  `red` must be deleted from `V`'s domain too. Once that's done, `V →
  NSW` is consistent again.
- **The interesting case:** `SA → NT` (neither assigned yet). Existing
  filtering has already pinned both down to only `blue` remaining — but
  they're adjacent, so they can't both be `blue`. The only fix is to
  delete `blue` from the tail — which leaves an **empty domain**. An
  empty domain is a definitive signal: the CSP has no solution from here,
  and it's time to backtrack. (Filtering only ever removes values that
  are *definitely* illegal given the current assignment — so if a domain
  is nonempty, that's *not* a guarantee of legality, just "not yet
  disproven." But empty *is* a guarantee of failure — "there's no secret
  fourth color.")

Running AC-3 to exhaustion (repeatedly popping arcs off a queue, deleting
from tails, and re-queuing any arc pointing at a variable that just lost a
value) is what makes an entire graph arc consistent. It terminates because
an arc only gets re-queued after a domain shrinks, and a domain can only
shrink a bounded number of times. **Important:** this filtering pass runs
again after *every single assignment* in the backtracking search — it's
not a one-time preprocessing step (unless you're using it that way
deliberately).

**Q&A — why does arc consistency detect failure earlier than forward
checking?** Failure means some node has no legal assignment left, given
what's already been assigned. The more arcs you check, the more likely
you are to notice that — and arc consistency chains information across
the *whole* graph, so it can detect failures far from the most recent
assignment. Forward checking only ever looks at what's immediately
adjacent to the newest assignment (arguably you'd discover the same thing
one step later anyway, under favorable orderings).

---

## 4. K-Consistency

Arc consistency is really a two-variable statement: for *any pair* of
variables, if you assign one, you can extend to the other. What about
three variables? All bets are off — that's the gap this section fills.

**The consistency hierarchy, restated so it generalizes:**

| Order | Name | Statement |
|---|---|---|
| 1 | **Node consistency** ("one-consistency") | Every variable's domain has at least one value satisfying its own unary constraints. Trivial — just enforce unary constraints once, up front, and you're done with this level forever. |
| 2 | **Arc consistency** ("two-consistency") | For any *pair* of nodes, any legal assignment to one can be extended to a legal assignment of the other. |
| K | **K-consistency** | For any *K* nodes, if you've legally assigned any `K−1` of them, there's guaranteed to be a legal extension to the `K`-th. |

Higher `K` is strictly more powerful but gets **exponentially more
expensive** very fast (you're now reasoning about triples, quadruples,
etc. of domains instead of pairs). In this class, `K = 2` (arc
consistency) is the one you need to know cold, but the general idea of
higher orders matters conceptually. (3-consistency specifically has a
name — **path consistency**, for three nodes forming a line.)

### 4.1 Strong K-consistency

Plain K-consistency assumes you already *got to* `K−1` legally assigned —
but nothing guarantees that's possible. **Strong K-consistency** is a
package deal: being strongly `K`-consistent also implies being 1-, 2-,
3-, ..., and `(K−1)`-consistent.

**Claim:** if a graph with `N` nodes is strongly `N`-consistent, you can
solve it with **zero backtracking**. Sketch: node 1 is 1-consistent, so
just legally assign it (satisfies its unary constraints). Node 2: the arc
from node 1 is 2-consistent, so *whatever* you picked for node 1, there's
a legal value for node 2 — assign it. Node 3: 3-consistent, so any legal
assignment to the first two extends to it — assign it. By induction,
every node can be assigned in sequence with no backtracking ever needed.

**Why this isn't as exciting as it sounds:** if you could quickly
*establish* strong `N`-consistency, you'd be solving an NP-hard problem
without backtracking — a contradiction, since these problems are
provably hard in general. Establishing strong `N`-consistency in general
is itself just as hard as solving the CSP. It's not useless, though — this
"go forward without worrying about the past" idea is exactly the engine
behind the tree-structured-CSP algorithm below, which *does* work, just
not on arbitrary graphs.

---

## 5. Exploiting Problem Structure

### 5.1 Independent subproblems

If the constraint graph splits into **disconnected components** (findable
by a simple graph search — "CS 70 style" reachability), each component is
an entirely separate CSP: solve them independently and combine the
results, with zero interaction cost. (Tasmania, in the Australia example,
is exactly this — an island with no constraints connecting it to the
mainland.)

**Why this matters, concretely:** a single CSP of `N` variables with
domain size `D` costs up to `D^N` in the worst case. Split into `N/C`
independent pieces of size `C`, the cost becomes `(N/C) · D^C` — for `N =
80`, `D = 2`, `C = 20`, this is the difference between **billions of
years** and **under a second**, under reasonable assumptions about
assignments-per-second.

**Caveat:** this is "zero out of ten" useful in practice as a *technique*
— you'll essentially never encounter a CSP with genuinely independent
subproblems, because the whole point of posing a CSP as one problem is
that the variables interact. (If they didn't, you'd have already split
it up during formulation.) Still a useful mental model — and, occasionally
in something like map coloring, genuinely disconnected regions really do
show up.

### 5.2 Tree-structured CSPs

**Theorem:** if the constraint graph has no loops (it's a tree), the CSP
can be solved in time **linear in the number of variables** (and
quadratic in domain size) — no exponential blowup at all. This is
dramatically better than the general `D^N` case, and it's not an unusual
case to run into — many real problems are tree-shaped or close to it.
(The same underlying property reappears later for tree-structured Bayes
nets.)

**The algorithm, in two passes:**

1. **Order:** pick an arbitrary node as the root, and let that induce a
   topological ordering / linearization over the rest of the (originally
   undirected) tree. Any root works equally well.
2. **Backward pass (right to left, leaves toward root):** for each node,
   in reverse topological order, enforce the consistency of the single
   arc pointing *into* it from its parent — deleting inconsistent values
   from the parent's (tail) domain as needed. Because it's a tree, each
   node has **exactly one** incoming arc to worry about (this is the
   first place the tree property gets used).
3. **Forward pass (root to leaves):** assign the root any remaining
   value. Then assign each subsequent node in topological order — because
   the backward pass already guaranteed the parent→child arc is
   consistent, *whatever* was assigned to the parent is guaranteed to have
   a legal extension at the child. **No backtracking is ever needed** in
   this pass.

**Runtime:** `O(n · d²)` — linear in the number of variables/arcs
processed (each visited a constant number of times across both passes),
and `d²` for checking a single arc's tail values against its head values.

**Why the proof needs the tree property (not just "arc consistent"):**
after the backward pass, every parent→child arc is consistent *and stays
that way*, because later steps in the backward pass only ever delete
values from a *tail* further from the root — never touch a domain that's
already been finalized as a "head." The forward-pass induction then goes:
assign the parent, and because the parent→child arc is consistent,
*something* at the child is guaranteed to work. **This specifically
requires each node to have only one parent.** If a node had *two* parents
(no longer a tree), consistency of each individual parent-arc only
guarantees a legal extension *for that parent alone* — there's no
guarantee both parents' legal extensions coincide on the same value at
the shared child. Getting that joint guarantee would require
3-consistency between the two parents and the child, which plain arc
consistency doesn't give you. This is exactly why the technique is
tree-specific.

### 5.3 Cutset conditioning: making a near-tree into a tree

Most real graphs aren't trees, but many are *close* — "tree-ish." One fix:
delete nodes until what's left **is** a tree (or independent), then
exploit that.

**Conditioning** = instantiating a variable to a specific value and
propagating the consequences to its neighbors' domains. The trick: pick a
small set of nodes (the **cutset**) whose removal leaves a tree (or
disconnected pieces), then solve the residual graph **once for every
possible instantiation** of the cutset. Each cutset assignment, combined
with a solution to the resulting residual (tree) CSP, is a solution to
the original problem.

- If the cutset has size `C`, you're solving up to `D^C` residual CSPs
  (though in practice you can often stop as soon as one instantiation
  yields a solution — you don't have to try them all).
- Each residual CSP, if it's a tree, solves in linear time via the
  algorithm above — so the total cost is roughly `D^C · (tree-solve
  cost)`, which is a huge win whenever `C` is small relative to `N`.
- **Finding the smallest cutset that turns a graph into a tree is itself
  NP-hard** in general — but when a small cutset happens to be easy to
  spot (as in many real graphs), the technique is a big practical win.
  (In-class quiz on a small example graph: after some back-and-forth
  about which node(s) to cut, it turned out the graph was already
  effectively tree-shaped — the smallest cutset needed was the **empty
  set**. Moral: check whether you even need to delete anything before
  assuming you do.)

### 5.4 Tree decomposition ("mega-variables")

A different, more advanced way to turn a near-tree into a tree (mentioned
at a lighter level of detail, not examined in depth): instead of
*deleting* nodes, **group** clusters of the original variables into
"mega-variables" that form a tree over larger units.

- Each mega-variable represents a small clique/fragment of the original
  CSP (e.g. the `{WA, NT, SA}` corner of the Australia graph). Its
  "domain" is the enumerated set of *locally consistent sub-solutions* to
  that fragment (not raw color values — whole legal triples of colors).
- **You can't just solve each fragment independently**, though: a
  solution to fragment A might color `NT` red while a solution to
  fragment B colors it green, and those don't agree — so the fragments
  need constraints *between* the mega-variables requiring agreement on any
  variable they share.
- If the resulting mega-graph is a tree, and the clustering satisfies a
  property called the **running intersection property** (a variable that
  appears in two mega-variables must appear in every mega-variable along
  the tree path between them — it can't "disappear and reappear"), the
  whole thing solves efficiently with the tree-CSP algorithm from §5.2 —
  just over much bigger, compound variables. **"No free lunch, but you
  can push your lunch around the plate."**

---

## 6. Local Search / Iterative Improvement: Min-Conflicts

A completely different way to solve CSPs — not a smarter search over
partial assignments, but a **randomized, iterative** approach over
*complete* assignments.

**The key inversion, compared to everything above:** backtracking search
maintains assignments that are always *legal but possibly incomplete*.
Local search instead maintains an assignment that is always **complete
but possibly illegal** — e.g. start with a two-node map-coloring graph
where *both* nodes are colored red (a complete, but constraint-violating,
assignment) and improve it from there.

**Algorithm (min-conflicts):**

```
while the CSP isn't solved:
    pick a variable that participates in a violated constraint
    reassign it to the value that violates the fewest constraints
    (i.e. hill-climb on "total number of violated constraints")
```

- **No fringe, no backup plan.** There's exactly one current state at any
  time; you tweak it until it works or you give up. This is dramatically
  more memory-efficient than tree/graph search, which can carry an
  exponentially large set of untried alternatives.
- **Demo (N-Queens):** start with all queens randomly placed (mostly
  conflicted). Repeatedly pick a conflicted queen at random and move it to
  the column/row position with the fewest remaining attacks. Even though
  intermediate steps can occasionally make things briefly worse, the
  process reliably converges to a solution in a small, roughly constant
  number of steps — **regardless of `N`**. Where earlier techniques could
  handle N-Queens for `N` in the tens or low hundreds, min-conflicts can
  solve instances of essentially any size almost instantly from a random
  start.
- **No guarantees whatsoever:** it can in principle run forever, it can
  introduce new conflicts while fixing others, and it gives no optimality
  guarantee if constraints are weighted. It's simply very fast, very
  often, in practice.

### 6.1 The constraint-to-variable ratio ("critical ratio")

An important empirical pattern, based on the ratio of (number of
constraints) to (number of variables):

- **Very few constraints relative to variables** → easy. Lots of freedom
  to satisfy everything; min-conflicts (or almost anything) finds a
  solution instantly.
- **Very many constraints relative to variables** → *also* easy,
  somewhat counterintuitively — with constraints everywhere, there's
  little "wiggle room," so a solution (if one exists) tends to be found
  by chasing consequences down quickly.
- **The middle "critical ratio"** — just enough constraints to make the
  problem genuinely hard to solve *and* hard to tell whether you're even
  on the right track — is where these iterative methods spike badly in
  runtime.

**The bad news:** many real-world problems people actually want to solve
tend to sit in that hard middle zone, not in the easy extremes. N-Queens
happens to be relatively under-constrained, which is part of why it looks
deceptively easy for min-conflicts — don't over-generalize from it.

---

## 7. Summary: CSP-Solving Techniques

- CSPs are a special kind of search problem where states are **partial
  assignments** and the goal test decomposes into **constraints**.
- Because the goal test decomposes, it can be "smeared" incrementally
  through the search — that's **backtracking search**, a faster DFS
  variant.
- Sped up further by **ordering** (MRV / least-constraining-value),
  **filtering** (forward checking / arc consistency / K-consistency), and
  **structure** (independent components, tree-structured CSPs, cutset
  conditioning, tree decomposition).
- **Min-conflicts** is a fast, practically effective but *unguaranteed*
  alternative based on iterative improvement over complete assignments —
  which leads directly into local search in general.

---

## 8. Local Search, in General

Local search generalizes the min-conflicts idea beyond CSPs to any
optimization problem: you're a robot standing in a mountain range trying
to find the highest peak, but you can only see a short distance around
your current position.

**Contrast with tree/graph search:** tree search (BFS, UCS, A\*, ...)
keeps an explicit, possibly exponentially large set of **unexplored
alternatives** (the fringe) to fall back on — that's exactly what makes it
**complete** (if the current path fails, it tries something else,
eventually exhausting every option in the worst case) but also
potentially slow. **Local search keeps no fringe at all** — a single
current state, locally modified via a new kind of "successor function"
that makes local tweaks rather than extending a partial plan. This is
fast and memory-efficient, but comes with **no completeness and no
optimality guarantee**.

### 8.1 Hill climbing

Move to the best neighboring state; stop when no neighbor is better than
where you are. In a schematic 1D landscape, you climb until you hit a
**local maximum** — a point where every direction you can move is
downhill.

- **No way to tell local vs. global maximum from where you're standing** —
  they look identical from the inside; only outside knowledge or
  comparing multiple runs can reveal it (imagine climbing Everest and
  hitting a false summit).
- **Quiz illustration:** starting from different points (`X`, `Y`, `Z`) on
  the same landscape lands you at *different* local maxima (`B`, `D`,
  `E`) — the algorithm is entirely path-dependent, with no notion of
  momentum to carry it past a local dip (that idea exists in fancier
  variants, not plain hill climbing).
- **Practical fix:** run many **random restarts** in parallel from
  different starting points, and keep the best result found across all of
  them.

### 8.2 Simulated annealing

Designed specifically for landscapes where hill climbing gets stuck too
early: instead of only ever moving uphill, it's "hill climbing with a lot
of caffeine" — it deliberately bounces around, sometimes accepting worse
moves, to escape local optima.

**Algorithm:** maintain a **temperature** that decreases over a schedule
(a physics analogy to metal cooling, with math behind it). At each step,
pick a **random** successor (not necessarily the best one) and compute the
change in value. If it's better, take it. If it's worse, take it anyway
with some probability — higher when the move is only slightly worse, and
higher overall when the temperature is high. As temperature → 0, behavior
converges to plain hill climbing.

- **Theoretical guarantee:** if temperature is decreased *sufficiently
  slowly*, simulated annealing is guaranteed to converge to the **global**
  optimum. Intuition: over infinite time, the fraction of time spent
  "bouncing" in any given region is proportional to how good that region
  is — better hills get visited (and stayed in) more, in the limit.
- **Practical caveat:** this guarantee doesn't hold on any finite time
  budget. Escaping a local optimum requires taking several downhill steps
  in a row, and the more of those are needed, the exponentially less
  likely you are to take them all consecutively — so in practice you can
  still get stuck unless only one or two downhill steps are needed to
  escape. This motivates designing smarter, larger structural jumps
  ("ridge operators") rather than relying purely on small random jitter.

### 8.3 Genetic algorithms

A different kind of "ridge operator," using a natural-selection metaphor
(not pushed too literally — like simulated annealing's physics analogy,
it's a name, not a proof):

- Maintain a population of candidate states, each with a **fitness**
  score.
- **Selection:** fitter candidates are more likely to be duplicated;
  weaker ones are dropped — essentially several restarts running in
  parallel with survival pressure.
- **Crossover:** the genuinely new idea — take **partial hypotheses**
  from two surviving candidates and recombine them into a new candidate.
  Example for N-Queens: take two decent (but not perfect) boards, slice
  each down the middle, and splice the left half of one with the right
  half of the other. If the problem happens to decompose that way (a good
  left half plus a good right half genuinely can combine into something
  better), this works; it can also combine the *worst* of both halves and
  produce something worse. Still requires multiple restarts and rounds in
  practice.
- **Why it's worth mentioning:** it's an example of moving through the
  search space via large, structural jumps rather than small local
  nudges — a fundamentally different move-generation strategy than hill
  climbing or simulated annealing's single-step jitter.

---

## 9. Closing

That's the full toolkit for CSPs: backtracking search as the baseline,
sped up by ordering, filtering, and structural exploitation — plus
min-conflicts / local search as a fast but unguaranteed alternative
family of methods.

**Next lecture:** adversarial search — planning when it's not just you
acting, but other agents actively working against you.
