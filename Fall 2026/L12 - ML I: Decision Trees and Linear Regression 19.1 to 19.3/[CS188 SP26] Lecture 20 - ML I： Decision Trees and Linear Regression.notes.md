# CS188 Lecture 20 — Decision Networks, Value of Information, and the Landscape of Machine Learning

*Cleaned-up lecture transcript, organized by topic. Timestamps and
housekeeping removed — that's not lecture content.*

> **A note on this cleanup, and on what's actually in this file:** this
> was generated from auto-captions (`[CS188 SP26] Lecture 20 - ML I：
> Decision Trees and Linear Regression [pJlRSx9INkI].en.vtt`), a
> YouTube-style rolling caption track where each cue repeats the
> previous line and appends new words with per-word timestamps.
> Extraction de-duplicated the rolling repeats to reconstruct a plain
> transcript, then reorganized it by topic and lightly cleaned it for
> readability. All worked numeric examples below were cross-checked by
> hand against each other (e.g. the umbrella decision-network numbers
> all independently reproduce the stated results: `0.7×0.17+0.3×0.77 =
> 0.35`, `0.65×89+0.35×53 = 76.4`, etc.) and are internally consistent
> throughout, so they're presented as spoken. **Important:** despite the
> video's title, this particular lecture session is almost entirely a
> continuation of the *previous* lecture (decision networks, value of
> information) plus a conceptual, no-algorithms introduction to machine
> learning — the instructor explicitly says at the start *"my guess is
> we'll have to probably push linear regression to next time"* and closes
> with *"next time we'll do the decision tree learning algorithm and the
> linear regression."* **Neither topic in the title is actually taught
> in this recording.** Section 8 flags this explicitly rather than
> inventing content that wasn't delivered. The original `.vtt` is
> untouched — check it against the source video if exact wording ever
> matters.

---

## 1. Decision Networks: Bayes Nets + Actions + Utility

A **decision network** extends a Bayes net with two new kinds of nodes
so that, instead of just answering probability queries, the network can
be asked to **make a rational decision** directly:

- **Action nodes** (drawn as rectangles) — a variable representing a
  choice the decision-maker controls (e.g. take the umbrella, or not).
  Action nodes typically have **no parents**, since they aren't caused by
  anything in the model — they're chosen.
- **Utility nodes** — describe the value to the decision-maker as a
  function of the values of their parent variables (which can include
  action nodes and/or ordinary chance/state variables).

**Running example — the umbrella decision.** Should you take an umbrella
to work? There's a cost either way: carrying it is a minor hassle (and
you tend to lose it if it doesn't rain), but leaving it home is far worse
if it does rain. The right decision depends on the weather, which you
don't know — but you might have a **weather forecast** to go on.

**Modeling detail worth dwelling on — get the arrow direction right.**
The network has an arc `Weather → Forecast`, *not* the other way around.
A forecast is produced by measuring the actual weather (e.g. satellites
tracking storm systems coming in off the Pacific) — the weather causes
the forecast, not vice versa. Crucially, **utility depends on the actual
weather and the action taken, not on the forecast** — there's no direct
arc from `Forecast` to the utility node, since once you know the true
weather, the forecast adds nothing further to how good an outcome is.
(A more careful model would use a Markov model of evolving weather over
time; this example is deliberately simplified.)

### The decision-network algorithm

```
1. Fix whatever evidence has already been observed.
2. For each possible action a:
     a. Set the action node to a.
     b. Use standard Bayes-net inference to compute P(W | evidence, a),
        where W = the parent variables of the utility node.
     c. Compute expected utility:  EU(a) = Σ_w  P(w | evidence, a) · U(w, a)
3. Choose the action with the highest expected utility.
```

Nearly all the work is done by ordinary Bayes-net inference (computing
that posterior `P(W | evidence, a)`) — the decision layer on top is just
a sum and an argmax. This scales to arbitrarily complex networks (the
example given: "should I shut down the nuclear reactor?" could depend on
an enormous underlying Bayes net — the machinery doesn't care).

### Worked example: umbrella, with numbers

```
P(sunny) = 0.7        P(rainy) = 0.3
P(forecast=bad | sunny) = 0.17     P(forecast=bad | rainy) = 0.77

Utility(leave umbrella, sunny) = 100     Utility(leave umbrella, rain) = 0
Utility(take umbrella,  sunny) =  20     Utility(take umbrella,  rain) = 70
```

**No evidence at all:**
```
EU(leave) = 0.7·100 + 0.3·0  = 70
EU(take)  = 0.7·20  + 0.3·70 = 35        → best action: leave it home
```

**Forecast is bad.** Bayes-net inference (inverting the causal arrow via
the network) gives `P(sunny | bad) = 0.34`, `P(rainy | bad) = 0.66`:
```
EU(leave | bad) = 0.34·100 + 0.66·0  = 34
EU(take  | bad) = 0.34·20  + 0.66·70 = 53   → best action: take it
```

**Forecast is good** (`P(sunny | good) ≈ 0.894`, `P(rainy | good) ≈
0.106`):
```
EU(leave | good) ≈ 89
EU(take  | good) ≈ 25                     → best action: leave it home
```

Exactly the sensible policy: take the umbrella only when the forecast is
bad.

**A subtlety — when a forecast is worthless.** It's possible for a
network to conclude "take the umbrella" *regardless* of what the
forecast says — this happens when the forecast is unreliable enough that
the downside risk (getting soaked) always dominates either way. In that
case, the forecast has genuinely zero decision-making value, however
interesting it might be to read. This connects to a real engineering
problem: **a detector is only useful if it's about as reliable as the
event it detects.** A nuclear reactor might be built to fail only once
every 10 million years — but if its failure-warning light itself burns
out once every 10,000 hours (an *extremely* good light bulb, most last
about 1,000 hours), then whenever it lights up, it's overwhelmingly more
likely the *light* failed than the *reactor*. As the monitored event
gets rarer, the detector has to get correspondingly more reliable just
to remain worth paying attention to.

---

## 2. Utility of States vs. Q-Functions

There are two related but distinct kinds of "value" quantities, often
conflated in the literature:

- A function of a **state alone** → this is **utility** (`U`, same thing
  as `V` in the MDP/RL vocabulary — "V" is just what operations research
  historically called it).
- A function of a **state and an action** → this is a **Q-function** /
  **Q-value**, exactly as in MDPs and reinforcement learning.

In the umbrella network above, the utility node has the *action* node
(`take`/`leave`) as a direct parent — that makes it, strictly, a
**Q-value node**, not a pure utility function. But conceptually, an
action by itself shouldn't matter to how happy you are — **what you
actually care about is the resulting state of the world.** You're not
upset because you chose "take the umbrella"; you're upset if that choice
leads to an outcome you don't like (looking silly on a sunny day) or
avoids one you do (getting soaked).

**Refined version:** replace the direct `Action → Utility` link with
explicit state variables that the action influences — e.g. `GotWet?`
and `FeltSilly?` — and make the utility node depend only on *those*.
Same numbers overall, but reorganized around outcomes rather than the
raw action label. This is **generally more concise**, because it
separates two things that don't need to be entangled: a compact utility
function over outcomes, and a separate transition model describing what
actions actually do.

**Why this separation matters — the chess illustration:**
- **Transition model** for chess (legal moves): roughly half a page.
- **Utility function** for chess: about two lines — did I checkmate my
  opponent, or is it a draw/stalemate?
- **Q-function** for chess, if you tried to write it as one big
  table mapping (state, action) → win/lose-with-optimal-play: roughly
  **10³⁸ pages** — because there are on the order of 10⁴⁰ reachable
  chess states, each with ~30–40 legal actions, and the Q-function has
  to specify an outcome for every one of them.

This is offered as a deep reason intelligent agents *know things*
(physics, chemistry, how the world generally works) rather than only
ever memorizing a policy or Q-function outright: if a concise Q-function
existed for everything, agents would just learn *that* directly and
never need any separate model of how the world works at all.

---

## 3. Value of Information (VPI)

**Value of information** — another concept originating with **von
Neumann** (his 1944 book) — answers: *how much is it worth to find out
some currently-unknown variable before deciding?*

**Concrete question:** should you bother checking the weather forecast
at all (imagine it costs you effort or money) before deciding about the
umbrella?

**The idea in words:** figure out what you'd do (and how good that
outcome would be) *if* the forecast turned out good, and separately *if*
it turned out bad. Weight those two hypothetical outcomes by how likely
each forecast value actually is (computed from the Bayes net), and
compare the resulting expected value against what you'd get by deciding
right now with no extra information.

### Worked example, continuing the umbrella network

```
No information:               best = leave,  EU = 70
If forecast turns out good (P = 0.65):   best = leave,  EU = 89
If forecast turns out bad  (P = 0.35):   best = take,   EU = 53

Expected value WITH the forecast = 0.65·89 + 0.35·53 = 76.4
Value of information = 76.4 − 70 = 6.4
```

So finding out the forecast is worth **6.4 units of utility** (dollars,
or whatever the utility scale represents) in this scenario — decision
networks aren't just for picking the best action given what you know;
they can also tell you **whether it's worth finding out more**, and
exactly how much any particular piece of information is worth.

**General formula**, for evidence variable `Eᵢ` not yet observed, given
evidence already in hand `e`:

```
VPI(Eᵢ | e) = [ Σ_ei  P(ei | e) · MaxEU(e, ei) ]  −  MaxEU(e)
```

### Where this generalizes

- **Doctors** facing thousands of possible tests/questions can, in
  principle, compute the VPI of each before ordering it — and stop
  gathering information once every remaining option has VPI ≈ 0 (nothing
  left to learn would change the recommended treatment).
- **Oil companies** use exactly this reasoning before committing hundreds
  of millions of dollars to drilling: cheaper information-gathering
  options first (seismic surveys, low-cost test drilling, satellite
  imagery, consultants), each evaluated for its VPI relative to its cost.
- **Real doctors are often measurably suboptimal** relative to a VPI
  calculation — researchers have found that matching an algorithm's
  behavior to actual doctor behavior requires adding a large
  **disutility for the doctor personally missing a diagnosis** (i.e.
  their own embarrassment) on top of patient outcomes, suggesting doctors
  partly optimize for a different objective than pure patient welfare.
- **Everyday perception** (eye movements, selective auditory attention)
  is framed as continuous, cheap, ongoing value-of-information seeking —
  your senses actively gather the evidence most useful for your
  wellbeing, rather than passively receiving a fixed stream.
- **Ghostbusters demo**: the live demo showed the algorithm choosing
  probe locations by VPI, repeating probes only as long as another probe
  is worth more than acting immediately — in one run it busted at only
  8% confidence because a further probe wasn't worth the cost of the
  extra turn; in another run, after a "green" (far-away) reading pushed
  probability mass toward one corner of the board, the algorithm probed
  the *opposite* corner next as the most informative next square, before
  eventually converging and busting near 98% confidence.

### Three properties of VPI

1. **Non-negative.** `VPI(Eᵢ | e) ≥ 0`, always — informally, "there's no
   way that knowing more should hurt you"; more formally, you always
   retain the *option* to simply ignore the new information and do
   exactly what you would have done anyway, so you'd only ever act
   differently if doing so helps. **Caveat:** this can fail in
   **game-theoretic** (multi-agent) settings — in some games, one agent
   knowing more can make it *harder* for agents to reach a cooperative
   outcome, so the theorem is specific to single-agent decision problems.
2. **Not additive.** It's tempting to think VPI adds up like buying
   separate goods (worth 10 to learn X, 17 to learn Y, so 27 to learn
   both) — but that's false for information. Trivial counterexample:
   checking whether a coin came up heads twice in a row — the second
   check is nearly worthless once you've already looked once.
   Non-additivity also runs the other way: two variables can *each*
   individually have zero VPI (neither alone would change your decision)
   while having positive VPI **together** (learning both at once might
   change your decision, even though neither could alone). Consequence:
   a greedy algorithm that always acquires whichever single variable has
   the highest VPI is **not guaranteed to behave optimally** overall.
3. **Order-independent.** The value of acquiring a *set* of evidence
   variables doesn't depend on what order you acquire them in — so it's
   natural to think of "evidence to gather" as an unordered set rather
   than a sequence.

---

## 4. What Is "Learning"? Framing and Scope

**Definition used in this course:** learning is any process that
improves an agent's performance as a result of experience.

> *"The baby, assailed by eyes, ears, nose, skin, and entrails at once,
> feels it all as one great blooming, buzzing confusion..."*
> — William James, 1890. Learning becomes essential precisely when the
> agent's designer can't be omniscient about the environment in advance.

> *"Instead of trying to produce a programme to simulate the adult mind,
> why not rather try to produce one which simulates the child's? If this
> were then subjected to an appropriate course of education one would
> obtain the adult brain."*
> — Alan Turing, 1950. Learning is also just a good **system-construction
> method**: expose a system to reality instead of hand-writing all its
> behavior — and it lets a system do things its designers couldn't
> explain how to do even if asked.

**Four questions to ask when designing any learning agent:**
1. What's the overall agent design that should produce the desired
   performance?
2. Which *piece* of that agent are you trying to improve, and how is
   that piece represented?
3. What data is actually available for that piece — in particular, do
   you know the *correct* answers, or only some weaker signal?
4. What prior knowledge is already available to bootstrap the process?

| Agent design | Component being learned | Representation | Feedback | Prior knowledge |
|---|---|---|---|---|
| MCTS search (e.g. AlphaGo-style) | Evaluation function | Linear function of board features | Win / loss | Rules of the game |
| MDP agent | Transition model | Transition matrix | Observed action outcomes | Available actions, possible states |
| Utility-based patient monitor | Physiology/sensor model | Dynamic Bayes net | Observation sequences | Human physiology, sensor design |
| Chatbot | Context-based word predictor | Transformer (deep net) | Known next word | Tokenization, vector space |

**Three broad categories:**
- **Supervised learning** — the correct answer is given for every
  training instance.
- **Reinforcement learning** — only a reward signal is available, no
  correct-answer labels.
- **Unsupervised learning** — "just make sense of the data," the least
  precisely defined of the three. Historical example: biologists
  observing that life on Earth clusters into species, genera, families,
  orders, phyla — nobody labeled the data with the right taxonomy in
  advance; the categories themselves were *discovered*.

**A note on scope, and a pointed aside about current systems:** what's
popularly called "machine learning" today (large language models) is a
narrow corner of supervised learning, itself one narrow corner of ML as
a whole. One entire category of learning that's ubiquitous in humans —
**compiling / caching a generalized solution** once you've worked
something out the hard way, so you never have to re-derive it from
scratch again — isn't covered in this course, and, pointedly, isn't
something current commercial "AI" systems do either: a language model
asked the same question repeatedly, anywhere in the world, redoes the
full expensive computation from scratch **every single time**, at real
electricity cost, rather than learning to skip the work it already did.

---

## 5. Why Does Learning Exist At All? A Biological Aside

- **Flies adapt almost instantly, without learning.** In an experiment
  using a laser to clip the tip off a fly's wing mid-flight, the fly
  corrects its wingbeat pattern within **a single wingbeat** — far too
  fast to be "learning" in any meaningful sense; the correction is
  essentially pre-programmed.
- **Precocial animals** (e.g. wildebeest calves) can stand and run
  within minutes of birth — they don't learn to walk, they're born able
  to.
- **Humans are the opposite (altricial).** Newborns know very little.
  Historical experiments literally tried isolating infants from all
  speech to see if they'd spontaneously start speaking Latin (the
  "perfect language," per medieval European ideas circa 1100 AD) — they
  didn't. What newborns *do* have hard-wired: basic eye-tracking
  (following a moving finger) and rudimentary face recognition (newborns
  attend to face-like shapes more than other shapes of similar
  complexity). Interestingly, babies born preterm (around 7 months) show
  a stepping reflex — held upright, their legs move as if walking — that
  fades and has to be *re-learned* later if the same child is carried to
  full term.
- **The evolutionary trade-off:** species that need to operate across a
  huge range of environments (like humans) benefit from a long,
  expensive learning period (10–15 years) that produces highly flexible
  adults — as long as parents can sustain the child that long. Other
  species instead hard-wire behavior and skip the learning investment
  entirely.
- **Turing's justification restated:** rather than hand-coding all adult
  behavior, build a "child machine," start it near-blank, and let a
  learning process plus exposure to the world do the rest.
- **Learning as an engineering choice, not a philosophical necessity:**
  for some tasks, learning turns out to be the *best practical*
  engineering method — not because hand-coding is impossible in
  principle, but because it's the more effective route in practice.
  Reinforcement learning was the practical path to superhuman Go; by
  contrast, **world-championship chess was reached mainly through
  hand-engineered search plus a hand-coded evaluation function**
  (structurally similar to what AlphaGo later used, but without RL to
  train the evaluation function) — reinforcement learning didn't work
  well for chess until much more recently. Other tasks (distinguishing
  the spoken words "cat" and "cut" — something virtually every human can
  do instantly but can't explain as an algorithm) essentially have **no
  practical alternative to learning**, because nobody can write down the
  rule directly.

---

## 6. A Little History of Learning Machines

- **Behaviorism (B. F. Skinner)** modeled all learning as
  stimulus–response conditioning. During WWII, in the absence of
  workable electronic guidance systems, Skinner's group trained
  **pigeons** to guide missiles: a pigeon pecked at a touch-sensitive
  screen showing the target, steering the missile via conditioned
  pecking behavior. Skinner also famously raised his own daughter,
  Deborah, partly using a similar conditioning-box apparatus — a detail
  that generated lasting controversy, though Deborah herself later said
  in interviews that she felt the experience had been fine and that she
  learned a great deal from it.
- **Frank Rosenblatt's Perceptron** — one of the earliest actual learning
  *machines* (physical hardware implementing a learning algorithm, not
  just a mathematical idea). A single perceptron is an extremely simple
  neural-network unit; wiring up a grid of them (e.g. 64 arranged in a
  square) allowed training on simple tasks like character recognition.
  Despite how primitive this looks today, contemporary newspapers
  reported it as "the beginning of superintelligent machines" — a
  considerable overstatement of what these early, one-bit learning
  systems could actually do.

---

## 7. Designing a Learning Agent: Worked Examples

Turing's "blank slate" ideal is rarely how learning agents are actually
built in practice — usually some agent-design template is fixed in
advance, and only specific pieces of it are learned.

**A cautionary tale: evolving FORTRAN programs (1950s).** One genuinely
from-scratch attempt: represent candidate agents as FORTRAN programs,
score them by a fitness function (e.g. video-game performance), and
"breed" the next generation by mixing code from the fittest parents.
Because FORTRAN is Turing-complete, in principle *any* algorithm —
including a superintelligent one — lies somewhere in the search space,
so the approach couldn't be ruled out on theoretical grounds. In
practice it failed. The contemporary explanation was that FORTRAN
programs are extremely **fragile** to small mutations (change one
variable name to an uninitialized one and the whole program typically
just breaks), unlike DNA, which tends to degrade gracefully under small
mutations rather than catastrophically. A caveat: the computers
available at the time were roughly **100 trillion times** less powerful
than today's — so whether the approach was fundamentally unworkable, or
simply started too early, remains genuinely open.

**Example A — MCTS/AlphaGo-style evaluation function.** Represent it as
a **linear function** over hand-designed board features; the weights are
what gets learned. The available feedback is sparse — during play, there
is no "this weight should be 6" signal, only an eventual win/loss result
— which is exactly what pushes this problem into **reinforcement
learning** rather than direct supervised fitting. Prior knowledge
available: the rules of the game, meaning the transition model itself
doesn't need to be learned at all (true for both AlphaGo and Deep Blue).

**Example B — transition model for an MDP.** Represented plainly as a
transition matrix (state × action → next-state probabilities). Unlike
the evaluation-function case, you directly **observe** the resulting
state after taking an action — so in an important sense you already have
the "correct answer" for each training instance, making this
comparatively closer to ordinary supervised learning, and easier than
the sparse-reward evaluation-function case above.

**Example C — learning to play a brand-new video game (informal).**
Humans bring an enormous amount of unstated prior knowledge to a game
they've genuinely never played before — "video-game physics": pressing
"left" moves you left, not up; a 2D space stays continuous and doesn't
spontaneously grow or shrink or develop holes; collectible gold coins
are almost certainly good, not harmful. None of this is learned *from*
the specific new game — it's carried over from a lifetime of prior
exposure to games in general, and it's exactly the kind of prior
knowledge an agent with no such background would be missing.

---

## 8. Supervised Learning: The Formal Setup

*(This is as far into "machine learning proper" as this lecture actually
gets — see the closing note in Section 9.)*

**Setup:** an unknown target function `f`. A **training set** of labeled
examples `(xⱼ, yⱼ)` where `yⱼ = f(xⱼ)` — `yⱼ` is the *label*, the correct
answer for input `xⱼ`. Examples: `xⱼ` = an image, `f(xⱼ)` = "giraffe" or
not; `xⱼ` = a seismic signal, `f(xⱼ)` = "explosion" or "earthquake" (a
problem the instructor has worked on directly). In general `x` can be
essentially anything — an image, a movie, a book, a lecture — and `f`
maps it to whatever label is of interest.

The learning algorithm's job is to output a **hypothesis** `h` that's
**close to `f`** — ideally identical, but realistically just accurate on
new, unseen inputs (the "test set"), not merely on the training examples
it was shown. Making "close to `f`" mathematically precise, and asking
whether that closeness can be *guaranteed*, is the subject of
**probably approximately correct (PAC) learning theory** — pointed to,
not covered, in this lecture (roughly AIMA §19.5-ish).

### Hypothesis spaces

Historically, classical statistics offered very few choices (essentially
"linear regression, or a mixture of Gaussians — pick one"). The modern
menu is much larger:

- **Linear models** — the oldest, going back 200+ years.
- **Logistic regression** — despite the name, actually a *classifier*:
  a linear function of the inputs, thresholded to produce a yes/no
  output (or a probability).
- **Neural networks** — described informally as "giant tunable
  circuits."
- **Decision trees** — nested if-then branches ("if this, then if that,
  then... the answer is X").
- **Nearest-neighbor** — for a new query, find the closest training
  example and return *its* label; described as working surprisingly well
  across many problems despite its simplicity.
- **Grammars** — accept/reject whether an input (e.g. a sentence) is
  well-formed.
- **Arbitrary programs** — an entire ML subfield is devoted to learning
  programs directly from input/output examples.

**Classification** = learning a function with a **discrete** output
value (e.g. giraffe vs. llama — including a brief aside about giraffes'
famously long tongues, illustrated with a personal childhood story about
a giraffe stealing an ice-cream cone at the zoo). **Regression** =
learning a function with a **real-valued** output (conventionally also
assuming a real-valued vector input, though that's not strictly
required).

**Why it's called "regression":** by historical accident — the first
paper to do curve-fitting of this kind happened to have the word
"regression" on its figure for an unrelated reason, everyone assumed
that was the name for the technique, and it stuck permanently despite
having nothing really to do with "regressing" toward anything.

### Curve-fitting and the central open question

Given five data points, several curves could all be called "hypotheses"
that fit the data to varying degrees:

- A straight line (linear regression) — simple, but might miss a point.
- A parabola — fits better, still misses one point.
- A high-order polynomial passing near all points — but such curves tend
  to swing wildly ("go completely bonkers") outside the range of the
  data, and are extremely **unstable**: a small change in one data point
  can produce a huge change in the fitted curve.
- A curve that threads through **every single point exactly** — a
  technically valid hypothesis (it's still the output of *some*
  nonlinear function), but intuitively a bad choice that "no one in
  their right mind" would pick.

The open question the lecture poses, without yet answering: **what's the
actual principled reason** the last option is a bad idea, if it fits the
data perfectly?

---

## 9. The Basic Questions of Supervised Learning

Posed as the organizing questions for everything still to come (decision
trees, linear regression, and beyond):

1. **Which hypothesis space `H`?** — Needs to be expressive enough to
   plausibly contain something close to the true `f`.
2. **How do you measure degree of fit?** — E.g., is it acceptable for a
   hypothesis to miss one point entirely (treating it as an outlier)?
3. **How do you trade off fit against complexity?** — This is
   **Occam's razor**: a hypothesis shouldn't be any more complicated than
   the data actually justifies; you're not entitled to add extra
   curves and wiggles without evidence for them. (Historical aside: named
   for William of Ockham, a medieval philosopher; the now-standard
   spelling "Occam" comes from French translations of his Latin work,
   which lacked a natural "k" — his name was originally closer to
   "Ockham.")
4. **How do you actually find the best-scoring hypothesis?** — A genuinely
   **computational** question, separate from the statistical ones above:
   for many hypothesis classes, finding the truly best-fitting function
   is itself computationally intractable — giving a second, independent
   reason (beyond statistical suitability) to prefer one hypothesis space
   over another.
5. **How confident should you be that a good-looking fit will generalize?**
   — Given a hypothesis that fits the training data well, what
   justifies believing it'll also do well on data it's never seen? How
   much would you be willing to bet on that? This is the domain of
   **learning theory**, mentioned but not developed here.

---

## 10. What Wasn't Covered — And Comes Next

As flagged at the top of this file: **this lecture, despite its title,
did not reach either decision trees or linear regression.** Time ran out
partway through laying the *conceptual groundwork* for supervised
learning (Sections 8–9 above). The instructor's closing line: *"I guess
that's what we have time for today. So, next time we'll do the decision
tree learning algorithm and the linear regression."* Both topics — the
actual decision-tree induction algorithm (attribute selection via
information gain/entropy) and the least-squares derivation for linear
regression — belong to the **following** lecture's recording, not this
one.
