# CS188 — Markov Decision Processes (MDPs), Part 1/2: Formalism, Discounting, and Value Iteration

*Cleaned-up lecture transcript, organized by topic. Timestamps,
announcements, and housekeeping removed — that's not lecture content.*

> **A note on this cleanup, and on what's actually in this file:** this
> was generated from auto-captions (`COMPSCI 188 - 2018-09-18 - Markov
> Decision Processes (MDPs) Part 1/2 .en.vtt`), a YouTube-style rolling
> caption track where each cue repeats the previous line and appends
> new words with per-word timestamps. Extraction de-duplicated the
> rolling repeats to reconstruct a plain transcript, then reorganized
> it by topic and lightly cleaned it for readability. The worked
> racecar-MDP numbers below were cross-checked by hand (v1(cool) = 2,
> v1(warm) = 1, v1(overheated) = 0, v2(cool) = 3.5, v2(warm) = 2.5 all
> reproduce correctly from the stated rewards and transition
> probabilities). **One number does not check out and is flagged in
> place:** in the discounting quiz (§10), the instructor's stated value
> for a three-step-away exit under γ = 0.1 ("point zero zero one") is
> arithmetically inconsistent with the rest of the example — the
> correct value is 0.01, not 0.001 — most likely a captioning slip on a
> spoken decimal. The states in that same quiz (labeled by the
> instructor as points on a line, heard here as "B," "D," etc.) are
> under-specified in the audio itself, not just the captions, so that
> section is presented as a worked illustration of the *concept*
> (discounting trades off "how much" against "how soon") rather than a
> verbatim reproduction of exact grid coordinates. The original `.vtt`
> is untouched if exact wording ever matters.

---

## 1. Why MDPs: Search With Uncertain Outcomes

Markov Decision Processes generalize search problems to the case where
**you're not entirely sure what your actions are going to do until you
try them.** Ordinary search problems have states, actions, and costs,
and you build a plan you like — move a robot around a grid, move
Pac-Man around a board. MDPs add non-determinism: in the real world you
often know what actions are *available* and roughly what they *might*
do, but not which outcome will actually occur. If a robot tries to
shimmy along a ledge to grab a gem, it might succeed, or it might fall
into a pit. You know the *possible* outcomes but not which one will
happen on a given attempt, so you have to plan — or more precisely,
compute a **policy** — that accounts for every outcome that might
occur.

---

## 2. Grid World: The Running Example

Just as search had running examples (mazes, CSPs, games), MDPs get a
running example: **grid world.** A robot moves on a grid with north,
south, east, and west actions, walls block its path, and — the new
ingredient — actions are noisy. Grid world is just *one* MDP among a
huge space of possible MDPs, and the lecture explicitly warns against
over-fitting intuitions to this particular example (a preview of the
"don't overfit" theme that recurs in the machine learning unit).

**The noise model used throughout the lecture:** 80% of the time, an
action succeeds and you move in the direction you attempted (or bounce
off and stay put, if there's a wall there). The other 20% of the time
you drift 90° off course — 10% you veer one way, 10% the other (e.g.
attempting north might actually yield north, west, or east, but *never
south* — moving directly opposite your intended direction is defined
to never happen in this particular model).

**Rewards in grid world** come in two forms:
- **Exit rewards.** Reaching a labeled exit square and taking the
  `exit` action ends the episode and pays out that square's value —
  e.g. +1 for the "gem" exit, −1 for the "pit" exit.
- **Living reward.** A reward received on *every* step that doesn't
  exit the game — it can be positive, negative, or zero, and is a
  parameter of the specific grid world being solved.

The general MDP idea underneath both: **taking a transition from one
state to another always produces a reward of some kind.** The goal,
loosely, is to maximize the sum of these rewards (formalized precisely
in §9 once discounting is introduced).

A deterministic version of this problem could just be solved with
ordinary search — for each state, look at the available moves, and
take whichever one is known to lead somewhere better. In an MDP, taking
an action from a state can lead to **multiple** possible next states,
each with a known probability — you know the full distribution over
outcomes, you just don't know in advance which particular outcome will
occur on any single attempt.

---

## 3. The MDP Formalism

Formally, an MDP is defined by a set of quantities, much like a search
problem was:

- **A set of states** `S` — configurations of the problem, exactly as
  in search.
- **A set of actions** `A` — as in search, though in search these were
  sometimes left implicit (a successor function); in an MDP they're
  explicit, labeled choices.
- **A transition function** `T(s, a, s')` — the key departure from
  search. In search, being in state `s` and taking action `a` leads to
  exactly one successor state (plus a cost). In an MDP, it can lead to
  **multiple** possible successor states `s'`. `T(s, a, s')` is the
  conditional probability of landing in `s'`, given that you were in
  state `s` and chose action `a`.
- **A reward function** `R(s, a, s')` — a positive, negative, or zero
  reward received on that transition. It may in principle depend only
  on `s`, only on `s'`, or (in general) on the full triple — where you
  started, what you did, and where you landed. (E.g. crossing a cliff
  successfully vs. falling into a fire pit are different `s'` outcomes
  from the same `(s, a)`, with very different rewards.)
- **A start state**, and possibly **terminal states** — but unlike
  search's clean "goal test," MDPs in full generality just keep
  playing; sometimes a state stops the game, sometimes the game could
  go on forever, and algorithms need to handle that explicitly (see
  §11).

Because this is a fundamentally different (non-deterministic) class of
problem, **A\* search will not solve it** — it needs its own class of
algorithms, which is the subject of the rest of this lecture and the
next. One algorithm for it already exists in a form students have
seen: **expectimax search**, originally introduced as a variant of
minimax where "the opponent" was actually chance (rolling dice). It
turns out to be closely — almost exactly — related to the algorithms
used to solve MDPs (formalized in §8).

---

## 4. The Markov Property

"Markov," in AI, means that **given the present state, the future is
independent of the past.** In an MDP, this means the transition
probabilities — what happens if you take this action in this state —
can depend on the current state and the chosen action, but **not** on
how you got there. A robot deciding whether to cross a narrow bridge
cares about where it is and what it's doing, not the specific route it
took to get there.

This is the same discipline search required: a state has to contain
*everything* the successor function needs, or the formulation breaks.
(Recall Pac-Man's state needing to encode which dots have been eaten,
not just position.) MDPs require the same care in formulation, so that
knowing the state and the action is enough to fully determine the
distribution over what happens next.

---

## 5. Policies, Not Plans

In search, an agent does offline computation — thinks, thinks, thinks
— and produces a **plan**: a fixed sequence of actions, executed step
by step, landing exactly where planned. MDPs are for a noisier world;
a fixed sequence of actions can't be trusted to play out as expected,
because any given action might not produce its most likely outcome.

**Live grid-world demo:** the instructor repeatedly takes actions
(north, north, east, east, ...) and shows that even a "good" action
sometimes fails to produce its most likely result — an attempted east
move once resulted in *staying in the same square* rather than moving
(a low-probability slip outcome that still happened). The lesson: if
you had blindly pre-committed to a fixed action sequence, an
unexpected outcome partway through would leave you off-plan with no
way to recover.

The MDP analog of a plan is a **policy**: not a sequence of actions,
but a **function from states to actions** — "if you're in this state,
do this." Written `π(s)`. Solving an MDP generally means finding the
**optimal policy** `π*` — the policy (or one of possibly several tied
optimal policies) that maximizes expected utility if followed.

- An **explicit policy** is a literal table: for every state, the
  recommended action. Following it is then a pure reflex lookup — no
  computation required at decision time; all the computation happened
  up front, while building the table. This is realistic when the state
  space is small enough to enumerate (grid world) and unrealistic when
  it isn't (e.g. Pac-Man with many dots — the state space is far too
  large to write down explicitly).
- An **implicit policy** computes the action on demand instead — this
  is what expectimax search actually is: it doesn't pre-compute a full
  table, it runs a fresh computation (turning the crank on a game tree)
  every time an action is needed.

---

## 6. Qualitative Behavior: How the Living Reward Shapes the Optimal Policy

A sequence of grid-world demos, all solving the *same* MDP formalism
with different **living reward** values, is used to show how radically
different qualitative behavior "emerges through the computation" just
by tuning one number:

- **Small negative living reward (a light "toll," e.g. −0.1 per
  step):** near the start, the optimal policy takes the safe long way
  around the pit — the toll for extra steps is too minor to justify the
  risk of the pit.
- **A genuine oddity — walking into a wall.** With a *very* small
  living reward, the agent has effectively unlimited patience. In one
  square, the optimal policy directs the agent to walk **into a wall**
  repeatedly. Reasoning: moving toward the pit risks falling in;
  walking into the wall guarantees no progress *most* of the time, but
  carries **zero** risk of falling in on any given attempt — and
  occasionally, purely from the 20% noise, the agent will slip
  sideways and escape the dangerous square without ever having risked
  the pit directly. The lecture calls this a spontaneous discovery of
  an *optimal-but-unintuitive exploit* of the rules as specified —
  comparable to an anecdote about AIBO robots learning an unintended
  "physically legal but not intended" way to shoot a soccer ball.
- **Larger negative living reward (e.g. −0.4):** roughly comparable in
  size to the terminal rewards themselves. The agent now prefers the
  safe route in general, but from the square nearest the pit, it will
  simply risk the pit rather than pay for ten extra turns to shimmy
  around safely.
- **Very large negative living reward (e.g. −2):** every step now
  costs more than falling into the pit does. The optimal policy heads
  for the **closest exit available**, pit or no — "get me out of this
  game."

The point: identical algorithm, identical rules-of-the-game structure
— only the reward parameters change — and yet the resulting optimal
behavior spans "cautious," "exploits a technicality," "moderately
reckless," and "actively suicidal to end the game faster."

---

## 7. A Second Running Example: The Racecar MDP

To show that MDPs don't need any spatial/grid structure, the lecture
introduces a tiny second running example used for the rest of this
lecture and the next: a **racecar** with three states — **cool**,
**warm**, and **overheated** — and two actions, **slow** and **fast**.
`overheated` is a terminal (game-over) state. Rewards are attached to
the *transitions* (an action from a state), not to which state you
land in, and — unlike grid world — in this MDP they depend only on the
starting state and action, not on the landing state:

- **Cool, slow** → reward **+1**, stays cool with probability 1.
- **Cool, fast** → reward **+2**, stays cool with probability 0.5, or
  transitions to warm with probability 0.5.
- **Warm, slow** → reward **+1**, stays warm with probability 0.5, or
  cools back down to cool with probability 0.5.
- **Warm, fast** → reward **−10**, transitions to overheated (game
  over) with probability 1.

Intuitively: going fast is always worth twice as much as going slow,
*regardless* of where you land — but going fast while already warm
risks ending the game entirely. The obviously-good behaviors — "go
fast while cool, go slow while warm, and reflect on your life choices
if you ever end up overheated, since by construction optimal play never
lands you there" — are used as a sanity check before formalizing how
an algorithm would actually derive this.

---

## 8. MDPs as Expectimax Trees: Q-States and Transitions

To compute the right action from, say, the `cool` state, you can build
out a tree of possible futures exactly as in expectimax: alternating
levels of **choice nodes** (the agent picks an action) and **chance
nodes** (the environment resolves that action to some actual outcome,
according to the known probability distribution) — never worse than
that known distribution, unlike a true adversarial worst case.

**One thing immediately jumps out that didn't happen in ordinary
expectimax:** the same handful of states (here, just three) recur over
and over throughout the tree. Doing an exponential amount of duplicate
work over only three underlying states is clearly wasteful — a
motivation returned to directly in §12.

This tree makes a new concept visible: **Q-states.** Given a state `s`
and a chosen action `a`, before the environment has resolved that
action to any particular outcome, the agent is in a **Q-state** —
committed to an action, but with the actual result not yet known. The
value of a Q-state is the expected utility of having taken action `a`
from state `s` and acting optimally from then on. The arc from a
Q-state down to a particular resulting state `s'` — labeled with its
transition probability and reward — is called a **transition**.

So the full recursive structure of an MDP, laid out as a tree: **state
→ (max over actions) → Q-state → (average over probabilistic outcomes)
→ state → ...**, exactly mirroring expectimax's alternation of max
nodes and chance nodes.

---

## 9. Utilities Over Sequences of Rewards, and Why We Discount

Since rewards trickle in step by step across an episode, an agent
needs preferences not just over single outcomes but over **sequences**
of rewards.

**First preference, uncontroversial:** more total reward is better
than less. If that were the whole story, the right utility would just
be the plain sum of rewards.

**Second preference, the new and important one:** given a choice
between the *same total* reward sooner vs. later — e.g. `(0, 0, 1)` vs.
`(1, 0, 0)` — most people prefer it **sooner**, though being indifferent
is also a defensible position depending on the setting. A plain sum of
rewards can't distinguish these two sequences at all, since they add
up to the same total — yet real preferences often do distinguish them
(the classic framing: would you take $100 now, or $100 in 20 years? Or
even $100 now vs. $110 in 20 years — many people still take the $100
now).

**The standard fix: exponential discounting.** A reward received `k`
time steps in the future is worth `γᵏ` times what it would be worth
right now, where `γ` (gamma) is a parameter with `0 < γ ≤ 1`. Mechanically,
this is implemented by hitting each level of the expectimax-style
recursion with one additional factor of `γ` as you go deeper — so
rewards far enough in the future eventually stop mattering much at all,
since they've been discounted so many times.

**Worked comparison.** With `γ = 0.5`, the sequence `(1, 2, 3)` has
discounted utility `1·1 + 2·0.5 + 3·0.25 = 1 + 1 + 0.75 = 2.75` — noticeably
less than the plain sum of 6, and in particular **less** than the
reversed sequence `(3, 2, 1)`, whose discounted utility is
`3·1 + 2·0.5 + 1·0.25 = 3 + 1 + 0.25 = 4.25`. Same three numbers, same
total — different order, different utility, because sooner rewards
count for more. Setting `γ = 1` recovers plain undiscounted summation
as a special case.

**Why discount, specifically** (stated as three separate reasons):
1. Sooner rewards plausibly really do carry higher utility than later
   ones — sometimes literally, e.g. money that could otherwise be
   invested and compound.
2. It **helps algorithms converge** (guarantees a bounded sum even over
   an infinite or very long horizon — elaborated in §11).
3. It follows from a deeper theoretical justification: **stationary
   preferences** (next section).

---

## 10. Stationary Preferences, and the Discounting Quiz

**Stationary preferences**, informally: if you prefer reward sequence
`A = (a₁, a₂, a₃, ...)` over `B = (b₁, b₂, b₃, ...)`, then — assuming both
sequences are prefixed with the *same* reward `r` at the first time
step — you should still prefer `A` over `B` once both are shifted one
step later. This is presented as a reasonable-sounding axiom, directly
analogous to the rational-preference axioms used earlier in the course
to derive expected-utility theory from raw preferences.

**The theorem:** if preferences over reward sequences are stationary,
there are only two functional forms of utility consistent with that —
the plain (undiscounted) sum, or the exponentially discounted sum. (Stationarity
can break down in settings with a genuinely finite horizon, where being
close to the end changes what's achievable — e.g. a life, or a game
with a fixed number of moves left, where a reward "pushed out too far"
might fall off the edge of the horizon entirely.)

A student's question distinguished two independent knobs that are easy
to conflate: a grid world's **living reward** (a flat per-step penalty
or bonus, entirely separate from discounting — the grid-world examples
in §6 all ran with `γ = 1`, i.e. *undiscounted*, and used the living
reward alone to shape behavior) versus **discounting** (the exponential
`γᵏ` factor applied when converting a *sequence* of rewards into a
single utility number). Both can be present in the same MDP
simultaneously and do different jobs — flat additive penalties can
happen with or without discounting; discounting itself is specifically
about converting a sequence into one number and only makes sense in the
exponential form if you want to preserve the stationary-preference
property.

### Quiz: how γ changes the optimal policy

A small deterministic linear grid world (a row of states, exit points
at each end with different payoffs — a larger payoff at one end, a
smaller one at the other) was used to quiz how the optimal policy
changes with `γ`:

- **With γ = 1 (undiscounted):** it is always correct to head toward
  the larger exit reward, no matter how many extra steps that costs,
  because waiting costs nothing under this policy's reward structure —
  a sequence like `(0, 0, 0, 10)` is worth exactly 10, identically to
  getting the 10 immediately.
- **With a small γ (e.g. 0.1):** being several steps away from the
  large reward now costs you multiple compounding factors of `γ`,
  while a smaller reward that's only one step away is barely
  discounted at all. Past some threshold of distance, it becomes
  optimal to take the **smaller, closer** reward instead of the
  larger, farther one — heavy discounting effectively shrinks the
  agent's planning horizon and makes it locally greedy. (The specific
  numeric comparison offered in lecture for the three-steps-away case
  doesn't reproduce correctly by hand — see the note at the top of this
  file — but the qualitative conclusion, that discounting flips the
  optimal choice from "farther but bigger" to "closer but smaller," is
  the intended takeaway.)

`γ`, in other words, softly encodes something like the agent's
effective **planning horizon**: technically an MDP always plans
infinitely far ahead, but the faster `γ` decays, the more that distant
planning tails off toward irrelevance, making the agent behave more
greedily.

---

## 11. Handling Episodes That Could Go On Forever

The racecar MDP can in principle run forever (alternate fast/slow
cleverly and never overheat), which means the plain sum of rewards
over such an episode is literally **infinite** — a problem, since
algorithms need to compare different actions by their value, and
"infinity vs. infinity" carries no information. Three standard fixes:

1. **Finite horizon.** Simply declare that episodes terminate after a
   fixed number of steps `T` (e.g. "you've got a hundred moves, go").
   A subtlety: this can produce **non-stationary policies** — the
   optimal action in a given state can depend on how much time is
   left, not just on the state itself. This is intuitive by analogy to
   sports: end-of-game strategy often looks nothing like strategy
   earlier on, because the value of future consequences (like an
   overheated racecar, or a foul) changes as the clock runs out.
2. **Discounting.** Even though the raw sum of an infinite reward
   sequence can diverge, the **discounted** sum of a bounded reward
   sequence stays finite whenever `0 < γ < 1` (a standard convergent-series
   argument) — this is a second, independent reason (beyond §9's
   stationary-preferences argument) that discounting is such a
   convenient modeling choice.
3. **Absorbing states.** Some MDPs have a state that, while not
   literally guaranteed to be reached on any fixed step, is reached
   with probability 1 in the limit — the probability of the episode
   running on forever without ever hitting it tails off to zero. That
   guarantee alone is often sufficient for algorithms to behave well,
   without needing an explicit horizon cutoff.

---

## 12. Recap: The Quantities That Define and Solve an MDP

**Defining an MDP** requires: a set of states (including a start
state), a set of actions, a transition function `T(s, a, s')`
(possibly landing in *multiple* successor states per action, unlike
search), a reward function `R(s, a, s')` per transition, and a
discount `γ` specifying how a sequence of rewards becomes a single
utility (sum, or discounted sum).

**Solving an MDP** takes that full specification as *input* — this is
the crucial contrast the lecture flags for what's coming in
reinforcement learning, where the model itself is *not* given — and
produces, as *output*, a **policy**: a mapping from every state to its
optimal action.

To compute that mapping, several intermediate quantities are needed,
directly paralleling expectimax:

- **V(s)** — the **value of a state**: the expected utility of being
  in state `s` and acting optimally from then on. `V*(s)` denotes the
  *optimal* value. This corresponds to a max node in the expectimax
  tree.
- **Q(s, a)** — the **value of a Q-state**: the expected utility of
  being in state `s`, having committed to action `a` (regardless of
  whether `a` was actually a good choice), and acting optimally
  thereafter. This corresponds to a chance node.
- **π\*(s)** — the **optimal policy**: the action recommended by
  optimal play from state `s`.

**Grid-world illustration of values:** the exit squares themselves
have `V = +1` / `V = −1` (only one possible future: take `exit`).
Every other square's value is some average over all the ways optimal
play from there could go, folding in both the probability of reaching
a good exit and the (discounted, living-reward-adjusted) cost of
getting there — so, for instance, a start square far from the good
exit has a markedly lower value (illustrated in lecture as roughly
0.5) than a square right next to it, purely because more of the
20%-noise "bad luck" mass has a chance to intervene along a longer
path. **Q-values illustration:** each state has one Q-value per
available action (visualized as four pie-slices per grid cell — one
per compass direction); an example Q-value of roughly 0.85 was shown
for taking `east` from a state a couple of squares from the good exit,
with the *other* three actions from that same square all valued lower,
since they lead toward less favorable continuations.

The **fundamental operation** needed to solve any MDP: compute each
state's value — its expectimax value — under optimal play. Expectimax
search already computes this, in principle; the point of the rest of
the lecture is to find a **more efficient** algorithm than literally
running expectimax on a tree that both duplicates identical subtrees
exponentially often and, per §11, may not even be finite.

---

## 13. The Bellman Equations

Writing the relationship between `V*` and `Q*` recursively, exactly
mirroring the max/chance alternation of an expectimax tree:

```
V*(s)     =  max_a  Q*(s, a)
Q*(s, a)  =  Σ_{s'} T(s, a, s') · [ R(s, a, s') + γ · V*(s') ]
```

The first line just says: the optimal value of a state is the best of
its available Q-values (a max node's value is the best of its
children). The second line unpacks a Q-state's value: from `(s, a)`,
you don't yet know which `s'` you'll land in, so you take the
`T`-weighted **average** over all possible outcomes; for each possible
`s'`, you collect the immediate reward `R(s, a, s')` plus the
**discounted** value of continuing optimally from there, `γ · V*(s')`.

These two equations together are the **Bellman equations** — the core
recursive definitions relating the optimal values of states to the
optimal values of *other* states one step away ("one-step lookahead").
The lecture stresses these are worth memorizing cold, since variants of
them recur constantly for the rest of the course.

**The catch:** this is a *system of equations* defining `V*` in terms
of itself (via other states' `V*`), not yet an algorithm for actually
computing it — and because of the `max_a`, it's not even a **linear**
system, so it can't just be solved by matrix inversion the way a
plain linear system could. An actual algorithm for solving it is
introduced next.

---

## 14. From Duplicated Expectimax Trees to Time-Limited Values

Returning to the racecar's expectimax tree (§8): running raw expectimax
on it is unattractive for two compounding reasons — (1) the same small
set of states recurs constantly, so there's **exponentially duplicated
work**, and (2) since the racecar MDP has no forced termination, the
tree is **literally infinite**, and running expectimax on an infinite
tree doesn't even terminate.

Both problems have an obvious-in-hindsight fix: **cache** values once
computed (rather than recomputing identical subtrees over and over),
and **depth-limit / truncate** the tree at some finite depth, relying
on discounting to make sufficiently deep contributions negligible.
Combining those two ideas essentially reinvents the algorithm covered
next — **value iteration** — except value iteration builds the answer
from the *bottom up* (start shallow, incrementally go deeper, caching
as you go) rather than recursing from the top down.

**The key intermediate concept: time-limited values.** Instead of the
intractable `V*(s)` (optimal value over a possibly-infinite future),
define `V_k(s)`: the expected value of starting in state `s` and
acting optimally, **if the game is guaranteed to end in exactly `k`
more time steps.** This is exactly what a depth-`k` expectimax search
rooted at `s` would compute — and critically, it's perfectly
well-defined and finite for any `k`, even in an MDP whose true horizon
is infinite.

**Grid-world walkthrough of `V_k` for increasing `k`:**
- `V_0(s) = 0` for every state — with zero more time steps, there's no
  time left to collect any reward at all.
- `V_1`: exit squares become nonzero immediately (`+1` at the good
  exit, `−1` at the pit — since `exit` is the only available action
  and it resolves in one step); every other square stays at 0 (with a
  zero living reward in this particular demo) since one step isn't
  enough to reach any exit.
- `V_2`: a square two steps from the good exit rises to roughly 0.72 —
  a blend of the (higher-probability) case of successfully reaching
  and taking the exit within two steps, and the (lower-probability)
  case of slipping and failing to reach it in time (contributing 0 to
  the average). Notably, the square **directly adjacent to the pit**
  stays at exactly 0, even though jumping into the pit in two steps
  is a literally reachable outcome — because doing so is never part of
  *optimal* play, so `V_2` (which assumes optimal play throughout)
  simply routes around it.
- Continuing to `V_4`, `V_5`, `V_6`, ...: increasingly distant squares
  (like the far corner) start to show positive value as the horizon
  becomes long enough for even a roundabout, possibly-slip-prone path
  to reach a good exit within `k` steps.
- **An observed pattern, called out explicitly:** watching the
  **arrows** (the greedy action implied by the current `V_k` at each
  square) rather than the raw numbers, the arrows typically stop
  changing well **before** the underlying values finish "fine-tuning" —
  the implied policy often converges faster than the value function
  does.

---

## 15. The Value Iteration Algorithm

Value iteration is essentially "building a layer cake": figure out
what's achievable in 0 more steps, then use that to figure out what's
achievable in 1 more step, then 2, and so on, stopping once the
values stop changing appreciably (convergence is deferred to next
lecture; only the algorithm itself is covered here).

**Update rule**, applied to every state at each iteration:

```
V_0(s)      = 0                                        for all s
V_{k+1}(s)  = max_a  Σ_{s'} T(s, a, s') · [ R(s, a, s') + γ · V_k(s') ]
```

This is **exactly** the Bellman equation from §13, with one crucial
difference: it relates the *known* vector `V_k` to a *new* vector
`V_{k+1}`, so — unlike the Bellman equations themselves — it's an
actual, directly computable procedure, not a system that has to be
solved all at once. Practically, it amounts to a **single-ply
(one-step) expectimax lookahead** from every state, using the
previous iteration's `V_k` values as ready-made estimates of "what
happens after this."

**Cost per iteration:** for each of `|S|` states, considering each of
`|A|` actions, and for each action summing over up to `|S|` possible
successor states in the worst case — `O(|S|²·|A|)` in the worst case,
though in practice each action typically has only a small, bounded
number of possible successors, so the real cost is usually far lower.
This only works when the state space is small enough to enumerate
directly — the opposite regime from search, where the state space was
often assumed too large to enumerate. (Bridging that gap is explicitly
deferred to the function-approximation material roughly a week later
in the course.)

The lecture notes this will be *proven* to converge to the true `V*`
next lecture — this session only establishes the algorithm and works
an example.

---

## 16. Worked Example: Value Iteration on the Racecar MDP

Using the racecar MDP from §7 (rewards +1/+2/+1/−10 for
slow-cool/fast-cool/slow-warm/fast-warm respectively; fast-warm
transitions to the terminal overheated state):

- **`V_0`:** 0 for cool, warm, and overheated — zero time steps left
  means zero achievable reward from anywhere.
- **`V_1`:**
  - `V_1(overheated) = 0` — the game is already over; no actions are
    available.
  - `V_1(cool) = 2` — with only one time step left, going fast is
    strictly better than going slow (+2 vs. +1), and there's no future
    to worry about jeopardizing, so the "risk" of ending up warm
    doesn't matter within a one-step horizon.
  - `V_1(warm) = 1` — here going fast is actively bad (a guaranteed
    −10, since one time step doesn't allow for recovering from
    overheating), so the optimal action is slow, guaranteeing +1.
- **`V_2`:**
  - `V_2(cool)`: comparing the two actions using cached `V_1` values.
    Slow: `1 + γ·V_1(cool) = 1 + 2 = 3`. Fast: `2 + 0.5·V_1(cool) +
    0.5·V_1(warm) = 2 + 0.5·2 + 0.5·1 = 2 + 1 + 0.5 = 3.5`. Fast wins,
    so `V_2(cool) = 3.5`.
  - `V_2(warm)`: Slow: `1 + 0.5·V_1(warm) + 0.5·V_1(cool) = 1 + 0.5·1 +
    0.5·2 = 1 + 0.5 + 1 = 2.5`. Fast: `−10 + V_1(overheated) = −10 + 0
    = −10`. Slow wins by a wide margin, so `V_2(warm) = 2.5`.

Each state's `V_{k+1}` is computed purely by looking up the *already
computed* `V_k` values for its possible successors — no re-derivation
of the whole future is needed, which is exactly the efficiency gain
over raw expectimax that motivated this algorithm in §14.

**Where this leaves off:** continuing this process indefinitely on the
racecar MDP does **not** converge to a finite answer under `γ = 1`
(undiscounted) — a case flagged as one of the "defective" cases from
§11 where the reward can genuinely diverge to infinity. The lecture
closes by deferring the explanation of *why* value iteration converges
(under an appropriate `γ < 1`) — along with a follow-up class of
algorithms — to the next lecture.
