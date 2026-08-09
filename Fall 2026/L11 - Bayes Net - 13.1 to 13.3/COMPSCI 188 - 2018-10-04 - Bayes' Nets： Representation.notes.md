# CS188 — Bayes' Nets I: Representation (AIMA 13.1–13.3)

*Cleaned-up lecture transcript, organized by topic. Timestamps and
housekeeping ("let's take a two-minute break," etc.) removed — that's
not lecture content.*

> **A note on this cleanup:** this file was generated from auto-captions
> (`COMPSCI 188 - 2018-10-04 - Bayes' Nets： Representation
> [T4l6ltMMcec].en.vtt`), a YouTube-style rolling caption track where
> each cue repeats the previous line and appends new words with
> per-word timestamps. Extraction de-duplicated the rolling repeats to
> reconstruct a plain transcript, which was then reorganized into topic
> sections and lightly cleaned for readability. This is an older (2018)
> recording paired with the current course's slide deck
> (`cs188-sp26-lec14.pdf`, same folder) — the two mostly agree closely
> enough to cross-check numbers, and the classic Burglary/Earthquake/
> Alarm example numbers below are taken from that deck since the
> instructor didn't read every digit aloud on screen. Everything else
> (the live in-class traffic-network build, the two-square Ghostbusters
> example, the independence worked examples) uses figures spoken
> directly in the recording. The original `.vtt` is untouched — check it
> against the source video if exact wording ever matters.

---

## 1. Why This Matters: From Actions to Beliefs

The first part of the course was about **selecting actions** — chaining
reasoning across a sequence of actions. This unit shifts to **beliefs**:
describing how some portion of the world — a set of variables you care
about — behaves, including how those variables interact *noisily* with
each other. That's **modeling**.

**Modeling is always simplification.** You pick some random variables;
others get left out entirely, either because modeling them isn't worth
the effort or because you don't know how. Even among the variables you
keep, some interactions may be too minor or too expensive to capture.
Every model involves judgment calls: which variables to include, which
interactions to represent, where the probabilities come from and how
they're learned. Then, separately, there's what you *do* with the
model — the queries and algorithms you run against it (e.g. "what's
P(X | Y)?").

> **George Box:** *"All models are wrong, but some models are useful."*
> The goal isn't a model that's exactly right — only rare domains allow
> that — it's a model that's useful. The price of an inexact model is
> **uncertainty**: every variable and interaction you leave out shows up
> as noise on the variables you kept.

This all sits inside the broader **rational-AI** framework: agents
maximize expected utility, and part of doing that is inferring what will
happen, or inferring underlying causes from evidence — reasoning from
things you know (**evidence**) toward things you're curious about
(**query variables**), via a model connecting them. Three concrete uses
previewed for this unit:

- **Explanation / diagnostic reasoning** — observe symptoms, infer the
  underlying cause.
- **Prediction / causal reasoning** — run the model forward from a
  change; effectively a noisy simulation.
- **Value-of-information queries** (a few weeks out) — e.g. in
  Ghostbusters, trading off *probing for more evidence* against *just
  acting now*. Quantifying how much a piece of evidence is worth, in
  utility or dollar terms, connects probabilistic inference directly to
  rational decision-making.

---

## 2. Independence

Two variables in a joint distribution are **independent** if there's no
interaction between them — formally, if the joint factors into the
product of the marginals:

```
∀x,y:   P(x, y) = P(x) · P(y)
```

In general this does **not** hold — the product rule always gives you
`P(x,y) = P(x) · P(y|x)`, and only in the special case where `P(y|x) =
P(y)` (learning x tells you nothing about y) does the joint collapse
into a product of two simpler, one-dimensional tables. Equivalently:

```
∀x,y:   P(x | y) = P(x)
```

Notation: `X ⊥ Y` ("X is independent of Y") — the symbol is meant to
evoke perpendicularity, i.e. the two variables are "doing their own
thing."

**Independence is a modeling assumption**, not something handed to you.
You can look at two random variables (coin flip 1, coin flip 2) and
*choose* to model them as having no interaction term — which, if valid,
means their joint probability is just the product of their individual
probabilities. Reasons independence might *not* exactly hold in
practice: subtle/weak interactions you've chosen not to model, and
sampling noise (real coin flips are only independent in the limit).

### Worked example: splitting a 4-variable domain

Domain: `Weather` (variable weather conditions), `Traffic` (light/heavy),
`Cavity` (do I have one), `Toothache` (do I have one). A full joint
would be one 4-dimensional table. But:

- **Weather and Traffic** are plausibly correlated (bad weather → bad
  traffic) — not independent.
- **Cavity and Toothache** are plausibly correlated (go ask your
  dentist) — not independent.
- **{Weather, Traffic} and {Cavity, Toothache}**, as two *groups*,
  plausibly have no interaction with each other.

So the model can be split: `P(Weather, Traffic, Cavity, Toothache) =
P(Weather, Traffic) · P(Cavity, Toothache)` — two independent
sub-tables instead of one large one.

### Worked example: checking independence numerically

Two joint distributions over the same variables `T` (hot/cold) and `W`
(sun/rain) from the previous lecture, with different underlying numbers:

- **P1**: `P(hot, sun) = 0.4`. Checking against the marginals:
  `P(hot) = 0.5`, `P(sun) = 0.6` → `P(hot)·P(sun) = 0.3 ≠ 0.4`. **Not
  independent** — hot and sunny are positively correlated in this
  distribution (it's more likely to be hot given it's sunny).
- **P2**: `P(hot, sun) = 0.3`, which *does* equal `P(hot)·P(sun)`, and
  the same equality holds for every other cell too. **T and W are
  independent** in P2. Because of that, P2 is more compact — instead of
  writing out the full 2×2 table, you can just hand over the two
  marginals `P(T)` and `P(W)` and state that they're independent.

(Both are valid probability distributions with different parameters;
nothing here is about sampling error or how the numbers were learned —
that's a separate question for later in the course.)

### Extreme case: n independent coin flips

Flipping *n* coins, the full joint distribution has `2ⁿ` entries — one
per head/tail sequence. But if the flips are independent, you never need
to write that table down: just supply the *n* individual marginal
distributions (size `2n` total), and any joint query can be answered by
multiplying the relevant pieces together. If the coins are also
**identically distributed**, one distribution suffices for all of them.
Going from `2ⁿ` to `2n` (or to a single distribution) is an **exponential
speedup** — the same flavor of win as decomposing a CSP into independent
sub-CSPs that can be solved separately.

**But true (absolute) independence is rare**, for a structural reason:
when you build a model, you generally only include variables that
*interact* with what you care about. Weather/Traffic really are
independent of Cavity/Toothache — but that's exactly why nobody puts them
in the same model in the first place. Among the variables you actually
choose to model together, independence is too strong an assumption to
expect. What *is* common — and is the actual building block Bayes nets
rely on — is **conditional independence**.

---

## 3. Conditional Independence

**Motivating example — a dentist robot.** Three random variables:
`Toothache` (pain or not), `Cavity` (yes or no), `Catch` (does a dental
probe physically catch on a hole). Intuition: if you have a cavity, your
tooth *might* hurt — but whether the probe catches on the cavity
probably has little to do with whether you're *also* feeling pain.
Formally:

```
P(catch | toothache, cavity) = P(catch | cavity)
```

— knowing about the toothache adds nothing once cavity is known. The
same independence has to hold in the *no-cavity* case too: whatever the
baseline chance of a catch is when there's no cavity, that chance
shouldn't change just because you happen to also be in pain for some
unrelated reason.

**This is not the same as (absolute) independence of Catch and
Toothache.** If those were unconditionally independent, learning you had
a toothache would tell you *nothing* about the chance of a catch — but
it should: a toothache raises your belief in a cavity, which in turn
raises your belief in a catch. There's a real correlation between
Toothache and Catch — it's just entirely **mediated by Cavity**. Once
Cavity is known, that correlation is fully explained and nothing extra
remains. This is exactly what **conditional independence** captures — it
is strictly weaker than absolute independence.

This same statement can be written several equivalent ways (each
derivable from the others via the definition of conditional
probability):

```
P(catch | toothache, cavity) = P(catch | cavity)
P(toothache | catch, cavity) = P(toothache | cavity)
P(toothache, catch | cavity) = P(toothache | cavity) · P(catch | cavity)
```

The third form is a nice way to think about it: *once you fix the value
of Cavity*, the remaining little 2-variable distribution over Toothache
and Catch is itself an independent (factored) distribution.

**Conditional independence doesn't imply, and isn't implied by, absolute
independence.** Example: coin flips 2 and 4 are absolutely independent
*and* conditionally independent given coin flip 3 — both can be true at
once. In general, prefer the strongest assumption you can justify, but
having one doesn't rule out the other holding too.

**Formal definition**, for random variables X, Y, Z:

```
∀x,y,z:   P(x, y | z) = P(x | z) · P(y | z)
```

equivalently:

```
∀x,y,z:   P(x | z, y) = P(x | z)
```

("Once you know Z, learning Y besides doesn't change your belief about
X.") To verify this from a full joint distribution you would, in
principle, need to check every `(x,y,z)` combination — in practice, this
is almost always adopted as a **modeling assumption**, not verified
exhaustively.

---

## 4. Practice: Spotting Conditional Independence

**Traffic (T), Umbrella (U), Rain (R).** Umbrella and Traffic aren't
plausibly independent on their own — seeing an umbrella raises your
belief it's raining, which raises your belief in traffic. But once you
already know whether it's raining, the umbrella tells you nothing
*further* about traffic — there's no extra correlation on top of what
rain already explains (it's not that the sight of an umbrella itself
causes more traffic). So: **U ⊥ T | R** is a reasonable modeling
assumption. (There could always be some smaller residual interaction
that a more careful model would capture, but for now that's declared too
minor to bother with.)

**Fire (F), Smoke (S), Alarm (A).** Fire and Alarm clearly aren't
independent — that's the entire point of a fire alarm. But if the causal
mechanism is entirely "fire → smoke → smoke sensor → alarm," then once
smoke is known, learning about the fire directly adds nothing more about
whether the alarm goes off: **F ⊥ A | S**. (This assumption would break
if, e.g., the alarm also had a *temperature* sensor that responded
directly to fire — then fire would influence the alarm through a second
channel besides smoke, and the model would need to reflect that.)

---

## 5. From Conditional Independence to Compact Factorizations

The **chain rule** is always true, with no assumptions, for any ordering
of variables:

```
P(R, T, U) = P(R) · P(T | R) · P(U | T, R)
```

That's just algebra — it holds for *any* joint distribution over these
three variables. The **conditional-independence assumption** is what
does the real work: if `U ⊥ T | R`, then `P(U | T, R) = P(U | R)`, and
the factorization simplifies to:

```
P(R, T, U) = P(R) · P(T | R) · P(U | R)
```

This is the entire payoff: a potentially exponentially large joint
distribution, rewritten as a product of small, bounded-size pieces that
**don't keep growing** as more variables are added — as opposed to the
raw chain rule, where the last conditional term is exactly as large as
the whole joint distribution. **Bayes nets (a.k.a. graphical models)**
are exactly a tool for expressing which conditional-independence
assumptions you're making, in a way that's both visual and directly
tied to these factorizations.

---

## 6. A First Concrete Example: 2-Square Ghostbusters

Smallest possible Ghostbusters board: two squares, so the ghost is in
either the top or the bottom. Variables: `G` (ghost location, uniform
prior — 50/50 top vs. bottom), `T` (top-square sensor reads red or not,
noisy), `B` (bottom-square sensor reads red or not, noisy).

**Givens:**
```
P(G = top) = 0.5
P(T = red | G = top)    = 0.8
P(T = red | G = bottom) = 0.4     (symmetric numbers given for B)
```

These givens alone do **not** specify the full joint over `G, T, B` — the
chain rule would require `P(B | G, T)`, which isn't among them. But
assuming the sensors are **conditionally independent given the ghost's
true location** (`T ⊥ B | G` — plausible, since both are just noisy
readings of the same underlying fact), then `P(B | G, T) = P(B | G)`,
which *is* given. With that one conditional-independence assumption, the
handful of given numbers is enough to reconstruct the **entire** joint
distribution over all three variables — and from there, answer the same
kind of queries as before (e.g. "given both sensors read red, how likely
is the ghost at the top?").

**On knowing when CI assumptions hold:** as the modeler, you take
whatever information the problem gives you — usually in words, or from a
fairly clear causal story — and translate it into conditional-
independence statements. The right givens *plus* the right CI
assumptions together "unlock" a full joint distribution from small
pieces, without ever having to build or store the whole thing directly.
(Teaser: the algorithm that formalizes "assemble small pieces into
what's needed, without materializing the whole joint" is **variable
elimination**, covered soon.)

---

## 7. Why Joint-Distribution Tables Are a Bad Model

Even though a full joint distribution can answer any query, using it
directly as *the* model has real costs:

1. **Space** — too big to write down or store (exponential in the
   number of variables).
2. **Time** — even if stored, computing over an exponentially large
   table is slow.
3. **Statistical cost** (often under-appreciated in plain CS, central in
   AI): every entry is effectively a parameter that has to be *learned*
   from data. A model with exponentially many parameters needs
   exponentially more data to learn reliably. A model built instead from
   a handful of small, chained-together local interactions only requires
   learning those small pieces — far more **sample-efficient**. (Same
   idea shows up in RL: naive Q-learning must learn a value for every
   state, while function approximation only needs to learn the
   generalizable *aspects* of states.)

---

## 8. Bayes Nets: Graphical Notation

Bayes nets (graphical models) look a lot like CSPs:

- **Nodes** = variables, each with a domain. A node can be **unassigned
  (unobserved)** or **assigned (observed)** — same vocabulary as CSPs.
- **Arcs** = interactions between variables — informally, "direct
  influence." **Formally, an arc's true meaning is about conditional
  independence**: the *absence* of an arc between two variables encodes
  a conditional-independence assumption between them (details next
  lecture). It's often intuitive — and frequently accurate — to think of
  arrows as pointing from cause to effect, but that's not guaranteed;
  arrows do not have to encode causality.

Just as CSP local constraints imply global consequences without every
variable needing a direct constraint to every other, Bayes nets describe
many small **local interactions** that, together, imply consequences
over the entire joint distribution.

**Real-world scale examples shown in lecture:**

- **Car insurance network** (~30 variables, e.g. driver age, mileage,
  driving skill, anti-theft device, socioeconomic class, accident cost).
  A full joint over 30 variables with ~10 values each would need `10³⁰`
  entries — and, worse, would require on the order of `10³⁰` case
  studies to even estimate. The network instead encodes only the *direct*
  local dependencies (e.g. `Accident` depends directly on `DrivingQuality`
  and car-safety features, not directly on `Age` or `ZipCode` — those
  influence `Accident` only indirectly, through `DrivingQuality`). This
  network can be used **forward**, for simulation/prediction (given
  initial conditions, what's likely downstream), or the same network
  structure can support diagnostic queries.
- **"Car won't start" network** — evidence sits at the bottom (dashboard
  lights, gas gauge reading, whether the car starts) and underlying
  causes (dead battery, broken alternator) sit above; observing the
  bottom-level evidence lets you infer likely causes. A network like this
  can encapsulate more domain knowledge about cars than the person using
  it has memorized directly.
- **Cavity → Toothache, Cavity → Catch**: direct arcs from Cavity to
  each symptom, but **no** direct arc between Toothache and Catch — their
  correlation is fully mediated by the path through Cavity, matching the
  conditional-independence assumption from Section 3.

---

## 9. Building a Graphical Model by Hand: Extended Traffic Domain

Live-built in lecture, one variable and one decision at a time — a good
illustration of how much of Bayes-net construction is *making explicit
modeling choices*, not applying a formula:

- **Traffic** — start here.
- **Rain** — does rain cause traffic, or vice versa? To the best of the
  instructor's knowledge, rain causes traffic, so the arrow goes
  `Rain → Traffic`.
- **Low pressure (L)** — correlated with rain, so `L → Rain`. (A reading
  on a barometer doesn't itself *cause* rain — strictly it's "actual low
  pressure," with the barometer's *reading* of it as a further, separate
  node if you wanted to be more careful. The model here just treats `L`
  as the actual pressure.)
- **Roof drips (D)** — caused by rain (`Rain → D`); *not* directly caused
  by low pressure or by traffic — those effects, if any, are mediated
  entirely through rain.
- **Ball game (B)** — causes traffic (`B → Traffic`); doesn't affect roof
  drips. **Optional arrow**: does rain affect whether the ball game
  happens (`Rain → B`)? Plausible, and it *could* be included — but
  doing so is a genuine trade-off: a more expressive model, at the cost
  of one more conditional relationship that has to be specified/learned.
  Omitting it yields a simpler but lower-resolution model.
- **Cavity** — belongs to a completely separate, disconnected part of
  the graph (its own unrelated "dental process"). Different graphs over
  the same variable set correspond to different sets of conditional-
  independence assumptions, which in turn change exactly which
  probabilities you're on the hook for specifying.

### The Alarm network

Built the same incremental way:

- **Burglary → Alarm** (a burglary can set off the alarm).
- **Mary calls** — does burglary connect directly to Mary, bypassing the
  alarm? Depends on the story: if Mary is far away and only reacts to
  the alarm, then `Alarm → Mary` alone suffices. If instead Mary might
  see the burglary directly through her window (even with no alarm),
  you'd need an extra arc `Burglary → Mary`.
- **John calls** — normally `Alarm → John`. But if John only calls
  *because* Mary calls him first (rather than hearing the alarm
  himself), the correct arc would instead be `Mary → John`.
- **Earthquake** — could be modeled as `Earthquake → Alarm` only
  (earthquakes cause calls *only* via setting off the alarm), or, if an
  earthquake might make John and Mary call directly regardless of the
  alarm, additional direct arcs `Earthquake → John` and `Earthquake →
  Mary` would be needed.

The point of walking through all of this: in this course, either you'll
be given a model (or clearly stated assumptions) and asked to compute
with it, or you'll be asked to *produce* a model — and producing one
means making, and being able to justify, exactly these kinds of
modeling calls.

---

## 10. Formal Bayes Net Semantics

**A Bayes net is:**

1. A set of nodes, **one per variable** `Xᵢ`.
2. A **directed, acyclic graph (DAG)** over those nodes. Acyclicity
   matches causal intuition (rain causing traffic causing a ball game
   causing rain back again would be nonsensical) — and mathematically,
   "no directed cycles" is exactly the condition that guarantees the
   graph's node order corresponds to *some* valid ordering for the chain
   rule.
3. A **conditional probability table (CPT)** stored at each node: a
   distribution over that node's values, **for every combination of its
   parents' values**. Think of this as a description of a *noisy causal
   process*: e.g. not "if it rains, there's traffic" as a hard rule, but
   "if it rains, there's a 90% chance of traffic; if not, 30%."

A node with `k` parents needs one full distribution **per parent-value
combination** — so an individual CPT's size grows exponentially in that
node's own number of parents, not in the total number of variables in
the network. That local, bounded exponential blow-up (rather than a
global one) is exactly what keeps well-structured Bayes nets tractable.

### Global semantics: reconstituting the joint

Multiply together every node's CPT entry (evaluated at the relevant
parent values) to get any entry of the full joint distribution:

```
P(x1, ..., xn) = ∏i  P(xi | Parents(xi))
```

This looks like the chain rule, but it **isn't** the general chain rule —
it's the chain rule *with the missing variables representing exactly the
conditional-independence assumptions being made*. The guarantee that
this product is a valid joint distribution rests on assuming:

```
P(Xi | X1, ..., Xi-1) = P(Xi | Parents(Xi))
```

for a topological ordering of the graph (parents always precede
children) — i.e., once you condition on a node's parents, none of the
*other* earlier variables add anything further. This is exactly a
conditional-independence claim, one per node.

**Not every graph can represent every joint distribution.** A graph with
two disconnected nodes A and B can only represent joint distributions in
which A and B are (unconditionally) independent — if you want to
represent a distribution where they interact, you need to add an arc.

**What arrows do and don't tell you:** an arc from `Rain` to `Traffic`
means the CPT at `Traffic` is *allowed* to differ across values of
`Rain` — it does **not** by itself say whether rain makes traffic more
or less likely, or say anything about the qualitative sign of the
interaction. That information lives entirely in the numbers inside the
CPT, not in the topology. (In fact, a CPT could happen to assign the
*same* distribution to `Traffic` regardless of `Rain`'s value — encoding
true independence numerically — even though the arc is drawn; you
couldn't tell that from the graph alone.) CPTs are also fully general:
they can encode arbitrary relationships (not just boolean influence),
including deterministic or near-deterministic ones like a noisy XOR —
and it's good practice to avoid writing hard `0`s or `1`s into a CPT
unless an outcome truly is impossible or certain (mirrors the same
warning about exact 0/1 probabilities from the previous lecture).

**On arrow direction when there's no clear causal story:** if two
variables are correlated but there's no obvious causal direction (or the
"true" direction seems cyclic), an arc drawn *either* direction is
mathematically capable of representing any joint distribution over just
those two variables — direction only starts to matter once that arc
interacts with other arcs elsewhere in a larger graph. This is itself
good evidence that Bayes-net arrows fundamentally encode conditional
independence, not causality — causal graphs are just usually *simpler*,
easier to reason about, and (per a Q&A aside) much easier to elicit from
domain experts: it's far easier to ask a doctor "what fraction of strep
patients have a fever?" than to ask "what fraction of feverish patients
have strep?" — even though both quantities describe the same underlying
joint distribution.

---

## 11. Worked Numeric Examples

### Independent coin flips

Bayes net: `n` disconnected nodes, each with its own marginal
distribution (no arcs at all — same graph shape as any set of
unconditionally independent variables, echoing the CSP-independent-
subproblems analogy from Section 2). To get a joint entry, multiply the
relevant marginal entries directly, e.g. for a sequence
heads-heads-tails-heads with each coin fair: `P = (1/2)⁴`. Changing the
per-coin bias numbers changes the joint, but **no** setting of purely
per-node marginals (no arcs) can ever represent a joint where the
variables are correlated — only whether they're identically distributed.

### Traffic ⇄ Rain: two graphs, the same joint

**Graph A: `Rain → Traffic` (the causal direction).** `Rain` has no
parents, so it stores a plain marginal; `Traffic` stores one
distribution per value of `Rain`:

```
P(+r) = 1/4        P(-r) = 3/4
P(+t | +r) = 3/4    P(-t | +r) = 1/4
P(+t | -r) = 1/2    P(-t | -r) = 1/2
```

Reconstituting any joint entry just multiplies the pieces, e.g.:

```
P(+r, +t) = P(+r) · P(+t | +r) = 1/4 · 3/4 = 3/16
P(+r, -t) = P(+r) · P(-t | +r) = 1/4 · 1/4 = 1/16
```

(and `P(-r,+t) = 3/4·1/2 = 6/16`, `P(-r,-t) = 3/4·1/2 = 6/16` — the four
entries sum to 1, as required.)

**Graph B: `Traffic → Rain` (the arrow flipped).** Mathematically valid
too — a Bayes net doesn't care whether the arrow matches the "true"
causal story, only that you supply the CPTs the new topology demands.
Now `Traffic` needs a plain marginal and `Rain` needs one distribution
per value of `Traffic`. Deriving the CPTs that are *forced* by wanting
the identical joint table above (via Bayes' rule, `P(t)=Σr P(r,t)` and
`P(r|t)=P(r,t)/P(t)`):

```
P(+t) = 9/16        P(-t) = 7/16
P(+r | +t) = 1/3     P(-r | +t) = 2/3
P(+r | -t) = 1/7     P(-r | -t) = 6/7
```

Multiplying *these* pieces together reproduces exactly the same joint
distribution as Graph A. **The takeaway:** for two variables, either
arrow direction can represent any joint distribution — the differences
only start to matter once a graph has three or more variables, where
some topologies genuinely can't represent some joints without added
arcs (Section 10). Networks that do follow the true causal structure
tend to be simpler, and their CPTs tend to be much easier to elicit from
people, which is why causal-looking graphs are preferred in practice
even though they're not mathematically required.

### The Alarm network (Burglary, Earthquake, Alarm, John calls, Mary calls)

*(Figures below are from the accompanying slide deck — the instructor
gave the `P(B)`, `P(E)`, and the burglary-and-earthquake alarm-response
row aloud, matching these exactly, but didn't read out every remaining
cell on screen.)*

```
P(B=true) = 0.001                    P(E=true) = 0.002
```

| B | E | P(A=true \| B,E) | P(A=false \| B,E) |
|---|---|---|---|
| true | true | 0.95 | 0.05 |
| true | false | 0.94 | 0.06 |
| false | true | 0.29 | 0.71 |
| false | false | 0.001 | 0.999 |

| A | P(J=true \| A) | P(J=false \| A) |
|---|---|---|
| true | 0.90 | 0.10 |
| false | 0.05 | 0.95 |

| A | P(M=true \| A) | P(M=false \| A) |
|---|---|---|
| true | 0.70 | 0.30 |
| false | 0.01 | 0.99 |

With the network (topology + these CPTs), *any* joint query is just a
product of the matching rows — e.g. "burglary and earthquake, but no
alarm, yet John and Mary both call anyway" is the product of the five
matching conditional-probability entries. These numbers would ordinarily
either be learned from data or, as here, simply supplied as givens.

### Live demo: interactively building and querying a network

The instructor built a small network live (Low Pressure → Rain → both
Traffic and Roof-Drip), entering illustrative CPTs on the fly and
explicitly noting "I'm just making stuff up" for these particular
numbers:

```
P(low pressure) ≈ 0.1
P(rain | low pressure) ≈ 0.9        P(rain | ¬low pressure) ≈ 0.1
P(drip | rain) ≈ 0.8                P(drip | ¬rain) ≈ 0    (but never exactly 0 —
                                                              "that's a no-no in building Bayes nets")
P(traffic | rain) = 0.8             P(traffic | ¬rain) = 0.3
```

Queries run live against this network, in sequence:

1. **P(traffic)**, no evidence at all → **39%**.
2. **P(traffic | roof is dripping)** → **higher** than 39% (a wet roof
   raises belief in rain, which raises belief in traffic).
3. **P(traffic | roof dripping, and directly observing rain)** →
   slightly **higher still**, roughly **80%** — once rain is *directly*
   observed, its value is what actually drives traffic; the roof-drip
   evidence becomes almost redundant (traffic only has rain as a parent).
4. **P(traffic | roof dripping, rain, AND low pressure)** →
   **unchanged**. Once `Rain` is directly known with certainty, learning
   about `LowPressure` adds nothing further, because in this graph
   `LowPressure` only ever influences `Traffic` *through* `Rain` — this
   is conditional independence showing up concretely (`Traffic ⊥
   LowPressure | Rain`), previewed as the topic for the next lecture.

---

**Closing line from lecture:** *"...and that must have something to do
with conditional independence — we'll find out what, next week."* Next
lecture: the formal conditional-independence semantics of Bayes nets,
and exact inference.
