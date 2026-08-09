# CS188 Lecture 13 — Probability (AIMA 12.1–12.5)

*Cleaned-up lecture transcript, organized by topic. Timestamps and the
opening current-events aside (Anthropic/DoD contract news) removed —
that's not lecture content.*

> **A note on this cleanup:** this file was generated from auto-captions
> (`[CS188 SP26] Lecture 13 - Probability.vtt`), a YouTube-style rolling
> caption track where each cue repeats the previous line and appends new
> words with per-word timestamps. Extraction de-duplicated the rolling
> repeats to reconstruct a plain transcript, which was then reorganized
> into topic sections and lightly cleaned for readability. Two caveats:
> **(1)** auto-captions garble spoken digits badly, and this lecture leans
> on a worked numeric example (the Season/Temperature/Weather table) —
> where the transcript's spoken numbers didn't reconcile with the source
> slide deck (`cs188-sp26-lec13.pdf`, same folder), the slide's printed
> values are used instead, since they're unambiguous and this is the
> exact deck taught in the video. **(2)** the recording itself — not just
> the caption file — ends mid-sentence around the 81-minute mark, right
> as the instructor begins formally defining conditional independence,
> having explicitly skipped a full walkthrough of the Ghostbusters
> example moments earlier. The last section below flags what's on the
> slides but was never actually spoken in this recording. The original
> `.vtt` is untouched — check it against the source video if exact
> wording ever matters.

---

## 1. Why Representation Matters

A **representation** is a formal language — syntax plus semantics — for
expressing information. Once you have one, you can build algorithms that
manipulate the syntax (operate on the representation), and those
algorithms produce *semantic consequences*: conclusions that actually
follow from the information represented. That's the basis for reasoning,
decision-making, and pretty much everything else an agent does.

AI has studied representation since the late 1950s; philosophers have
studied it for roughly 2,500 years, almost entirely under the heading of
**logic**. Logic deals with *definite* information; **probability theory**
deals with *uncertain* information. In that sense this course is picking
up the story halfway through — logic itself is covered in the earlier
chapters of the textbook (roughly ch. 7–11) but isn't part of this unit.

**Why representation, concretely:** you could build a representation of
any complex system in C++ — it's Turing-equivalent, so it's universal —
but it would be inelegant and error-prone. Mathematicians instead
represent complex dynamical systems as **partial differential
equations**, then implement a simulator for the PDE in C++ afterward. The
PDE is the formal representation of the *dynamics*; C++ is just the
implementation substrate. The same split applies to Markov decision
processes: you could hand-write a giant MDP in code, but **Bayes nets**
(starting next lecture) let you represent large, complex probability
models — including the probabilistic structure underlying an MDP —
elegantly, rather than as a giant lookup table.

---

## 2. Uncertainty Is the Rule, Not the Exception

Games like chess and tic-tac-toe, where the outcome of every action is
known in advance, are the *exception*. **Determinism is just the special
case of uncertainty squeezed down to nothing.** The real world is rife
with uncertainty.

**Running example:** if you leave for SFO 90 minutes before your flight,
will you make it? (The lecture used to use 60 minutes, but that got too
stressful to even think about.) Sources of uncertainty raised in
discussion: traffic (which itself varies with time of day, holidays, ball
games...), and more generally:

- **Partial observability** — the state of the road, other drivers'
  plans, etc.
- **Noisy sensors** — a radio traffic report or Google Maps entry can be
  out of date or simply wrong (e.g. reporting a stalled vehicle on the
  Bay Bridge that isn't there anymore by the time you arrive).
- **Immense complexity** of modeling and predicting traffic, security
  lines, etc. Even with a perfect physical model of the universe, fully
  simulating something like tire wear at the molecular level for a
  100-mile drive would require more compute than exists on Earth.
- **Lack of knowledge of world dynamics** — will a tire burst? Will you
  need a COVID test?

These reduce to **two distinct sources of uncertainty**:

1. **Ignorance** — you genuinely cannot observe something (what every
   driver intends to do) or your sensors are noisy/wrong.
2. **"Laziness"** — in quotes, because it isn't really laziness: it is
   *computationally infeasible* to model everything at the level of
   detail that would make the outcome deterministic.

They have different fixes. Ignorance can only be fixed by **changing your
access to the world** — more sensors, more experiments (e.g. how fast
does rubber actually decompose?). Laziness can be fixed by **not being
lazy** — more compute, more explicit, detailed knowledge written down.

**Probabilities** are how you summarize the residual uncertainty after
admitting both limits. As with MDPs, probabilities then combine with
**utilities** to drive decisions:

```
a* = argmax_a  Σ_s  P(s | a) · U(s)
```

`U(s)` is a number describing how good a state is. In an MDP, utility
happened to be a *sum of rewards* — but that's a special case, not the
general definition (there's good reason to think humans don't actually
decompose utility additively over time either). Utility theory gets its
own treatment later in the course; for now, focus is on the probability
side of this equation.

---

## 3. Possible Worlds and the Basic Laws of Probability

The first move in probability theory is to enumerate everything that
could happen — the **possible worlds**, written **Ω** (capital omega).

- Rolling one die → Ω = {1, 2, 3, 4, 5, 6} (ignore the die landing and
  balancing on a corner — assume that doesn't happen).
- A **probability model** attaches a number P(ω) to every possible world.
  For a fair die, P(ω) = 1/6 for each.

Real probability models routinely have millions, billions, or
quintillions of possible worlds — sometimes infinitely many — so most of
this unit (and next lecture) is about representing a model *without*
writing a number next to every single world.

**The two basic laws of probability** (for discrete/countable Ω — real-
valued/continuous variables need extra machinery, covered in a stats
course, not here):

```
0 ≤ P(ω) ≤ 1              for every possible world ω
Σ_{ω ∈ Ω} P(ω) = 1        (they sum to one across all possible worlds)
```

An **event** is any subset of Ω. E.g. for one die roll: "roll < 4" is the
set {1, 2, 3}; "roll is odd" is {1, 3, 5}. The **probability of an
event** is the sum of the probabilities of the worlds it contains:

```
P(A) = Σ_{ω ∈ A} P(ω)
P(roll < 4) = P(1) + P(2) + P(3) = 1/2
```

That's the entirety of the basic laws.

---

## 4. Why These Laws? De Finetti's Dutch-Book Argument

There have been many historical proposals for how to reason with
uncertain information, not all of them consistent with these laws.
**De Finetti (1931)** showed that if you make bets according to degrees
of belief that *violate* the laws of probability, an opponent can
construct a set of bets that guarantees you lose money **no matter which
outcome occurs**. This is one of the most fundamental justifications for
probability theory being *the* right framework for uncertain reasoning.

It's an instance of a more general idea: **rationality constraints**.
The same style of argument (constructing a "money pump" — an agent that
can be guaranteed to hand over money because its decisions violate
rationality) is why, ~250 years of debate later, rational decision-making
is generally taken to mean **maximizing expected utility** — a theme that
returns when utility theory is covered directly.

---

## 5. Random Variables

As the late Joe Halpern (a prominent AI probabilist) used to say:
**"random variables are neither random nor variables"** — they're
**deterministic functions of a possible world ω**.

Concretely: given a possible world (say, a die roll of 4), you can ask
various *questions* about it — is it even? is it bigger than two? — and
each such question, evaluated across all possible worlds, is a random
variable.

- `Odd(ω)`: is the roll odd? Range = {true, false}. `Odd(1) = true`,
  `Odd(6) = false`.
- `Temperature`: range = {hot, cold}.
- `Duration` (time to the airport): range = [0, ∞) — a continuous range.
- `LGhost` (ghost location): range = a discrete set of grid coordinates.

The **range** of a random variable is the set of values it can take
across all possible worlds. Random variables are always written with a
capital letter; specific values use lowercase.

The **probability distribution** of random variable X gives, for every x
in its range, the probability of the event "X = x":

```
P(X = x) = Σ_{ω : X(ω) = x} P(ω)         ("P(x)" for short, when unambiguous)
```

`P(X)` (no specific value) refers to the whole distribution — think of it
as a vector/table of probabilities, one per value in the range.

**Note on zero:** saying an event has probability exactly zero is
equivalent to asserting it is *logically impossible* — you'd be willing
to bet your life, at any odds, that it won't happen. Reserve exact 0s and
1s for genuine logical certainty/impossibility (e.g. "x = 2 and x = 3
simultaneously"); anything merely unlikely should get a small nonzero
probability instead.

---

## 6. Joint Distributions

The **joint distribution** gives the probability for every *combination*
of values across several variables. Running example for the rest of the
lecture: `Temperature ∈ {hot, cold}`, `Weather ∈ {sun, rain, fog, meteor}`.

| P(T, W)   | hot  | cold |
|-----------|------|------|
| **sun**   | 0.45 | 0.15 |
| **rain**  | 0.02 | 0.08 |
| **fog**   | 0.03 | 0.27 |
| **meteor**| 0.00 | 0.00 |

All 8 entries sum to 1 — the outcomes are pairwise disjoint and
collectively exhaustive.

---

## 7. Building Possible Worlds from Random Variables

In practice nobody hands you a ready-made Ω. You start from the **random
variables and their ranges** you care about, then build Ω as the
**Cartesian product of those ranges**.

**Two dice, Roll1 and Roll2:** how many possible worlds? 6 × 6 = **36**.

If a game (Monopoly, Craps, ...) doesn't care about *order* — rolling a
6-then-4 is the same outcome as 4-then-6 — you can define a derived
random variable that sorts the pair into a canonical (high, low) form.
The probability of the canonical outcome "6, 4" is then the *sum* of the
two raw worlds that map to it: {Roll1=6, Roll2=4} and {Roll1=4,
Roll2=6}. The canonical/sorted representation has a genuinely different
distribution than the raw pair.

Assuming the two rolls are **independent**, each of the 36 raw worlds has
probability `1/6 × 1/6 = 1/36`. (If you're worried the dice might be
biased — or made by the same manufacturer, correlating their biases —
you can add explicit bias variables and model that too; this is exactly
the kind of thing Bayes nets make easy.)

**Critical sizing fact:** for *n* variables each with range size *d*, the
number of possible worlds is:

```
d^n        NOT   n × d
```

Think of it as an *n*-digit number in base *d* (each variable is a
"digit slot"). This trips up roughly 8% of students on the midterm even
after being told directly — don't be one of them.

If *d* is infinite (continuous variables), it's worse still — how do you
even represent a distribution over infinitely many worlds? (Probability
theorists have answers; out of scope here, everything in this unit
assumes finite ranges.) Even staying finite, exponentially-sized joint
distributions are the central problem this unit is building toward
solving — **Bayes nets are the best general tool we have** for beating
that exponential blow-up down to something close to linear in the number
of variables.

---

## 8. Answering Queries from a Joint Distribution

Given a joint distribution, `P(A) = Σ_{ω∈A} P(ω)` lets you answer **any**
logical query, like a SQL query against a probability model:

- **P(hot ∧ sunny)?** Read directly off the table: **0.45**.
- **P(hot)?** Sum every cell where T = hot: 0.45 + 0.02 + 0.03 + 0.00
  = **0.5**.
- **P(hot ∨ ¬foggy)?** Easier via the complement — the only way this is
  *false* is "cold and foggy" (0.27), so the answer is
  **1 − 0.27 = 0.73**.

---

## 9. Marginal Distributions

A **marginal distribution** is a lower-dimensional distribution derived
from a higher-dimensional one, by **summing out** (eliminating) the
variables you don't want:

```
P(X = x) = Σ_y P(X = x, Y = y)
```

("Marginal" is a historical term from actuarial/insurance tables, where
row and column sums were literally written in the *margins* of the page.)

Summing the joint table down each column gives the temperature marginal;
summing across each row gives the weather marginal:

|            | hot  | cold | **P(W)** |
|------------|------|------|----------|
| **sun**    | 0.45 | 0.15 | **0.60** |
| **rain**   | 0.02 | 0.08 | **0.10** |
| **fog**    | 0.03 | 0.27 | **0.30** |
| **meteor** | 0.00 | 0.00 | **0.00** |
| **P(T)**   | **0.5** | **0.5** |      |

Treat marginalization the same way you'd treat any algebraic operation —
like subtracting 2 from both sides of `u = v + 2` to isolate `v`. It's
one of a small set of standard moves for manipulating probability
expressions; a few more follow below.

---

## 10. Conditional Probability

**Definition** (this *is* the definition, not a derived fact):

```
P(a | b) = P(a, b) / P(b)          (the conditioning variable goes on the bottom)
```

**Intuition:** picture Ω as a big space, with A and B as two overlapping
regions. "Conditioning on B" means restricting your entire universe to
just the B region — throw away everything where B is false. Within that
restricted universe, `P(A | B)` asks: what fraction of the remaining
probability mass also lies in A (i.e., in A ∩ B)?

**Worked example:** P(W = sun | T = cold)? Restrict to the "cold" column
(sun=0.15, rain=0.08, fog=0.27, meteor=0.00 — these sum to P(T=cold) =
0.50). Within that column, the "sun" slice is 0.15:

```
P(W=sun | T=cold) = P(W=sun, T=cold) / P(T=cold) = 0.15 / 0.50 = 0.3
```

**Conditional distributions** extend this from a single event to a full
distribution — the probability of every value of one variable, given an
observation about another:

| P(W \| T=hot) | P(W \| T=cold) |
|---|---|
| sun: 0.90 | sun: 0.30 |
| rain: 0.04 | rain: 0.16 |
| fog: 0.06 | fog: 0.54 |
| meteor: 0.00 | meteor: 0.00 |

Putting both columns together gives `P(W | T)`. **This is not the same
object as a joint distribution.** A joint distribution (like `P(T,W)`
above) is a matrix where every axis is interchangeable — there's no
priority between rows and columns. A conditional distribution like
`P(W|T)` should instead be thought of as **a vector of vectors**: for
each value of T, a separate distribution over W. The left side and right
side of the conditioning bar are not symmetric.

---

## 11. Normalizing a Distribution

**Normalizing** restores the "sums to one" property to a set of numbers
that don't currently satisfy it: multiply every entry by
`α = 1 / (sum of all the entries)`.

**Worked example:** the *unnormalized* slice `P(W, T=cold)` = [0.15,
0.08, 0.27, 0.00] sums to 0.5, not 1. So `α = 1/0.5 = 2`; multiplying
every entry by 2 gives [0.30, 0.16, 0.54, 0.00] — exactly the
`P(W | T=cold)` conditional distribution computed above. In general:

```
P(W | T=cold) = P(W, T=cold) / P(T=cold) = α · P(W, T=cold)
```

Like marginalization, treat this as a standard, near-automatic algebraic
move once you recognize the pattern.

---

## 12. The Product Rule

Rearranging the definition of conditional probability gives the
**product rule**:

```
P(a | b) · P(b) = P(a, b)
```

**Rule of thumb:** probability expressions tend to come in *pairs* — an
expression with B on the right of the conditioning bar, paired with
another where B is on the left (`P(B)` can be thought of as `P(B |
nothing)` — your prior belief before any evidence). If partway through a
homework derivation you find B on the *same* side (e.g. left) in two
expressions you're trying to combine, that's a sign you may have flipped
something incorrectly via Bayes' rule or the product rule — not a hard
rule, but a useful sanity check.

**Worked example:** `P(W|T) · P(T) = P(W,T)` exactly reproduces the full
joint table from Section 6, starting from the conditional distributions
in Section 10 and the temperature marginal `P(T) = [0.5, 0.5]`.

---

## 13. The Chain Rule

Repeatedly applying the product rule lets you factor **any** joint
distribution into a product of one-variable-at-a-time conditionals.
Treating `(X1, X2)` as a single combined variable and applying the
product rule twice:

```
P(x1, x2, x3) = P(x3 | x1, x2) · P(x1, x2)
              = P(x3 | x1, x2) · P(x2 | x1) · P(x1)
```

In general, for any number of variables:

```
P(x1, x2, ..., xn) = ∏_i  P(xi | x1, ..., x_{i-1})
```

— the product, over all variables, of each variable conditioned on every
variable that precedes it in the chosen ordering. This is **central to
how Bayes nets work** (next lecture).

---

## 14. Probabilistic Inference by Enumeration

The general question: given a full joint distribution over `X1, ..., Xn`,
partition the variables into:

- **Query variable(s) Q** — what you want to know.
- **Evidence variable(s) E = e** — what you've actually observed.
- **Hidden variable(s) H** — everything else.

You want `P(Q | e)`. **Important:** this is genuinely different beliefs
for genuinely different evidence — it's not that an earlier belief was
"wrong." E.g., from the SFO example:

```
P(on time | no accidents)                    = 0.90
P(on time | no accidents, 5 a.m.)             = 0.95   (traffic hasn't started yet)
P(on time | no accidents, 5 a.m., raining)    = 0.80   (rain drags it back down)
```

These are all consistent — they're statements about different epistemic
circumstances (different amounts of evidence), not contradictions.

**The three-step recipe:**

```
Step 1 — Restrict: keep only the joint-distribution rows consistent with the evidence e
Step 2 — Sum out H:  P(Q, e) = Σ_h P(Q, h, e)
Step 3 — Normalize:  P(Q | e) = α · P(Q, e)
```

The order in which you sum out the hidden variables doesn't matter
mathematically — addition is commutative and associative, so any order
gives the same answer. (It *will* matter for efficiency once actual
Bayes-net inference algorithms are covered — noted here as a preview.)

### Worked example: Season, Temperature, and Weather

Add a third variable, `Season ∈ {summer, winter}`, which shifts the
temperature/weather distribution:

| Season | Temp | Weather | P    |
|--------|------|---------|------|
| summer | hot  | sun     | 0.35 |
| summer | hot  | rain    | 0.01 |
| summer | hot  | fog     | 0.01 |
| summer | hot  | meteor  | 0.00 |
| summer | cold | sun     | 0.10 |
| summer | cold | rain    | 0.05 |
| summer | cold | fog     | 0.09 |
| summer | cold | meteor  | 0.00 |
| winter | hot  | sun     | 0.10 |
| winter | hot  | rain    | 0.01 |
| winter | hot  | fog     | 0.02 |
| winter | hot  | meteor  | 0.00 |
| winter | cold | sun     | 0.15 |
| winter | cold | rain    | 0.20 |
| winter | cold | fog     | 0.18 |
| winter | cold | meteor  | 0.00 |

**Q: P(W)?** No evidence, so skip straight to summing out the two hidden
variables (Season, Temperature) — for each weather value, add up all 4
rows that produce it (one per season/temperature combination):

```
P(sun)    = 0.35 + 0.10 + 0.10 + 0.15 = 0.70
P(rain)   = 0.01 + 0.05 + 0.01 + 0.20 = 0.27
P(fog)    = 0.01 + 0.09 + 0.02 + 0.18 = 0.30
P(meteor) = 0.00 + 0.00 + 0.00 + 0.00 = 0.00
```

That's exactly what "summing over the hidden variables" means:
enumerate every combination of their values, and add up the joint entry
for each.

**Q: P(W | winter)?** Now there *is* evidence — first restrict to the 8
rows where Season = winter (discard the 8 summer rows entirely). The only
remaining hidden variable is Temperature, so sum over hot/cold:

```
P(sun, winter)    = 0.10 + 0.15 = 0.25
P(rain, winter)   = 0.01 + 0.20 = 0.21
P(fog, winter)    = 0.02 + 0.18 = 0.20
P(meteor, winter) = 0.00 + 0.00 = 0.00
                                   ----
                     normalizer:  0.66
```

Normalize by `α = 1/0.66`:

```
P(sun  | winter) ≈ 0.38
P(rain | winter) ≈ 0.32
P(fog  | winter) ≈ 0.30
P(meteor | winter) = 0.00
```

### Why this doesn't scale

Query variables are usually one or a handful; evidence might be a dozen
or two. But a realistic model can easily have **hundreds or thousands**
of variables, and inference-by-enumeration has three separate, equally
fatal problems:

1. **Time**: summing out H is `O(d^n)` — exponential in the number of
   hidden variables.
2. **Space**: just *storing* the joint distribution is `O(d^n)`.
3. **Data**: *estimating* `O(d^n)` table entries from data requires on
   the order of `O(d^n)` (realistically more, maybe ~100×) data points.

Concretely: 1,000 boolean variables → `2^1000 ≈ 10^300` entries. The
observable universe has roughly `10^80` atoms — so even if you could
store one probability per atom in the entire universe, you'd be short by
a factor of about `10^220`. This isn't a matter of needing a faster
computer; the representation itself is unbuildable.

**But dice don't behave this way.** Rolling 10 dice instead of 2 doesn't
require billions of times more experiments to characterize, because the
dice are **independent** — you estimate one 6-entry table once, and the
joint probability of any combination is just the product of individual
entries. This is precisely the kind of structure — independence and,
more generally, **conditional independence** — that Bayes nets are built
to exploit, decomposing an exponential joint distribution into small
pieces that can each be estimated separately.

---

## 15. Bayes' Rule

Write the product rule **both directions** and set them equal:

```
P(a, b) = P(a | b) · P(b) = P(b | a) · P(a)
```

Divide through by `P(b)`:

```
P(a | b) = P(b | a) · P(a) / P(b)
```

That's it — Bayes' rule is a one-line rearrangement of the product rule.
(Aside: the portrait everyone associates with "Thomas Bayes" almost
certainly isn't him — it's an unidentified 17th-century clergyman that
got misattributed at some point. His actual grave in London is reported
to still be covered in flowers, 300-plus years on, from visiting
Bayesians.)

**Why it's useful, despite being trivial to derive:**

1. It lets you **build one conditional from its reverse** when only one
   direction is easy to state or measure directly.
2. It describes a formal **update step**: prior belief `P(a)` →
   posterior belief `P(a | b)` after observing evidence b. This is, in a
   real sense, a formal theory of learning from experience — whether the
   "experience" is a scientific instrument's reading, a baby's sensory
   input, or a doctor's observed symptoms.

**The causal-direction motivation:** your model of how the world works
is usually naturally stated as `P(effect | cause)` — "if it rains, the
grass gets wet"; "if a patient has disease X, they'll have a fever and a
rash with such-and-such probability." But the reasoning you actually need
to do usually runs the *other* way: you observe the effect (wet grass; a
feverish, rashy patient) and need to infer the hidden cause (did it
rain, or did a sprinkler/dog cause it? which of several diseases does the
patient have?). Bayes' rule is exactly the tool for flipping a
conditional from the natural/causal direction into the diagnostic
direction you actually need.

---

## 16. Independence

Two variables X and Y are **(absolutely) independent** if their joint
distribution factors into the product of their marginals, for every
value pair:

```
P(x, y) = P(x) · P(y)     for all x, y
```

equivalently, `P(x | y) = P(x)` — observing y tells you nothing new about
x.

**Dice example:** `P(Roll1=5, Roll2=3) = P(Roll1=5)·P(Roll2=3) = 1/6 ×
1/6 = 1/36`. Observing Roll1 = 5 doesn't change your belief about Roll2
at all — it's still uniform over {1,...,6}. (Contrast: if instead you're
told both dice are "loaded to always favor one number," but not told
*which* number — now seeing a 5 on die 1 *does* raise your belief that
die 2 will also show 5, because the dice are no longer independent; they
share an unknown bias.)

**Why it matters:** for *n* independent binary variables (e.g. *n* coin
flips), the full joint distribution has `2^n` entries — but because of
independence, it's fully determined by just `n` numbers (one bias per
coin), each estimable separately. That's an **exponential-to-linear**
reduction in what you need to represent and measure.

**The catch:** true, unconditional independence is **rare** in the real
world — dice and coins are *specially engineered* to be independent and
symmetric. Pick almost any two real-world random variables and there's
usually some plausible causal story linking them. What **is** almost
ubiquitous, instead, is **conditional independence** — independence that
holds *once you condition on* some other variable. Conditional
independence gets the same exponential-to-linear win as full
independence, but shows up constantly in real domains — which is exactly
what Bayes nets are designed to represent and exploit.

---

## 17. Where the Recording Ends — Conditional Independence (from slides only)

The instructor explicitly skipped a full walkthrough of the next
example — *"I think I'll skip over Ghostbusters because it takes a
little bit long to describe... I'll just go to some other common sense
examples"* — and the recording/transcript then **cuts off mid-sentence**
moments later, while stating the formal definition of conditional
independence. Everything below this point is drawn from the
**slide deck only** (`cs188-sp26-lec13.pdf`) and was **not** actually
narrated in this recording — treat it as a pointer to what comes next,
not as cleaned-up lecture content:

- **Formal definition:** X is conditionally independent of Y given Z iff,
  for all x, y, z: `P(x | y, z) = P(x | z)` — equivalently
  `P(x, y | z) = P(x | z) · P(y | z)`.
- **Ghostbusters / Naïve Bayes example on the slides:** a ghost hides in
  a 3×3 grid (`G`, 9 possible locations); each of the 9 squares has a
  color sensor reading (`C_{x,y} ∈ {red, orange, yellow, green}`) whose
  distribution depends only on distance to the ghost. The full joint
  `P(G, C₁,₁, ..., C₃,₃)` would have `9 × 4⁹ = 2,359,296` entries — but
  because each `C_{x,y}` is conditionally independent of every other
  sensor reading *given* G, the chain rule collapses this to:
  `P(G) · ∏_{x,y} P(C_{x,y} | G)` — exponential in the number of squares
  down to roughly linear. This structure (one query variable, all
  evidence variables conditionally independent given it) is called a
  **Naïve Bayes model**.
- Two informal domains were posed for the class to reason about
  (presumably picked up next lecture): **{Traffic, Umbrella, Raining}**
  and **{Fire, Smoke, Alarm}** — in both cases, asking which pairs are
  independent, and which become conditionally independent once you
  condition on the right third variable.
- **Next time (per the closing slide):** Bayes nets, and elementary
  inference in Bayes nets.
