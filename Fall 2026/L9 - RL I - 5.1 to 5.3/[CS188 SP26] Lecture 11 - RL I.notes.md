# CS188 Lecture 11 — Reinforcement Learning I: Model-Based Learning, TD Learning, and Q-Learning

*Cleaned-up lecture transcript, organized by topic. Timestamps,
announcements, and housekeeping removed — that's not lecture content.*

> **A note on this cleanup, and on what's actually in this file:** this
> was generated from auto-captions (`[CS188 SP26] Lecture 11 - RL I
> [H70q_bRnm6Q].en.vtt`), a YouTube-style rolling caption track where
> each cue repeats the previous line and appends new words with
> per-word timestamps. Extraction de-duplicated the rolling repeats to
> reconstruct a plain transcript, then reorganized it by topic and
> lightly cleaned it for readability. The numeric worked examples below
> were cross-checked by hand against the underlying arithmetic (e.g.
> the B→C→D episode reproduces the stated per-state returns 8/9/10
> exactly from a −1 living reward and a +10 exit; the C-state
> direct-evaluation average of 9, 9, 9, and a pit episode reproduces
> the stated **+4** once the fourth episode is read as living reward
> −1 plus a −10 pit, i.e. −11 — auto-captions garbled that specific
> number to "1"; the TD-learning example with α = 0.5 reproduces −1 and
> +3 exactly). Anywhere the source audio-to-text seems to have mangled
> a specific number beyond confident reconstruction, that's flagged
> in place rather than presented as fact. **The source `.vtt` file
> itself cuts off mid-sentence at 1:24:00** ("...I'm going to learn
> that even though going—"), so this recording (and these notes) end
> exactly where the lecture was still mid-explanation of the Q-learning
> grid-world demo; the original `.vtt` is untouched if exact wording
> ever matters.

---

## 1. Why Reinforcement Learning Is a Different Problem Than Planning

Reinforcement learning (RL) reuses the *exact same formalism* as an
MDP — states, actions, transitions, rewards, a policy — but flips a
core assumption. In an MDP you're handed the model and your job is to
**plan**: think ahead, run value iteration or expectimax, and only
*then* act. In RL, **you don't know what your actions do until you try
them, and you don't know which states are good until you visit them.**
This is the same tension introduced last lecture with the "which slot
machine pays off?" problem — you can't tell a machine's payout without
putting money in and pulling the lever.

**Opening demo:** a simulated one-legged hopping robot, reward = net
forward motion. Even this simple case shows the core RL idea visually:
the robot has to move slightly *backward* on every step (a
consequence of the trigonometry of a single hinged leg) in order to
net forward motion overall — reward is about the **sum** of outcomes,
not the immediate one, and the robot has no idea any of this works
until it's tried a huge number of variations.

**The cat-fetch video (offered half as a joke, half as a real
lesson):** someone tries to teach a cat to fetch a thrown ball the way
a dog would. By the third throw, the cats have completely disengaged.
The point: this *is* reinforcement learning — there was no actual
reward wired up for the cats, and they successfully learned to ignore
the ball. **You get what you actually reward, not what you intended to
teach** — a preview of the reward-shaping problems RL runs into
constantly.

### The agent–environment loop

The setup: an agent takes an action in some state `S`. Unlike planning
in simulation, this action is taken **for real** in the environment,
which replies by placing the agent in a resulting state `S'` and
handing back an **instantaneous reward** `R`. The agent's job is to
learn to act so as to maximize the sum (generally discounted) of these
rewards — but all it has to learn from is these observed `(s, a, s',
r)` samples as they happen.

This lecture assumes **full observability** — you always know exactly
what state you're in. The case where you *can't* fully observe your
state (e.g. partial vision) corresponds to a **Partially Observable
MDP (POMDP)**, saved for much later in the course.

Because you don't know `T` or `R` up front:
- You have to **visit** a state to learn anything about what it leads
  to.
- You have to try an action **multiple times** if the environment is
  non-deterministic, since one trial doesn't tell you the full
  distribution of outcomes.
- Statistical/sampling concerns (how many trials before you trust an
  estimate?) are front and center, exactly as with the slot machine.

### More motivating examples

- **Robot soccer (AIBO robots).** Optimal soccer gait for a
  four-legged robot isn't the "obvious" straight-legged dog-mimicking
  posture — it turns out you want more support, so the learned gait
  bends down onto the elbows. You don't know exactly how much the legs
  will slip, or how the robot's weight will shift, until you try it —
  and even a *previously trained* gait needs re-tuning on a new field
  (different turf, different slip characteristics). You can sometimes
  turn an RL problem into a pure physics/modeling problem instead — but
  only "as good as your model," which is why hybrid approaches are
  common: train in a best-guess simulation first, then "polish" with
  real-world RL. The lecture shows footage of a walking gait that
  starts out slipping and inefficient, and after training becomes
  smooth and reliably forward-moving — "super efficient."
- **A side-winding snake robot.** Contrasted with the quadruped case:
  a human could probably *manually* script a walking gait for a
  four-legged robot ("move this leg, then that leg"). Scripting the
  coordinated joint-angle sequence for a many-jointed snake so that all
  the resulting forces produce net motion (instead of just thrashing)
  is far harder to hand-write — a natural case for letting RL discover
  the pattern instead.
- **The Project 3 crawler robot.** Two controllable joint angles: the
  "shoulder" (where the yellow arm meets the body) and the "elbow"
  (where the red arm bends against the yellow arm), each of which can
  be actuated up/down or increased/decreased. There's some pattern of
  increasing and decreasing these two angles that produces a net
  forward "scooping" motion — the robot has no built-in notion of
  walking and has to discover that pattern from scratch. (This crawler
  applet runs continuously in the background through the lecture as a
  running example — see §7 for what it's actually running.)

---

## 2. The RL Version of the MDP: Same Formalism, Unknown `T` and `R`

To build the crawler bot (or any RL agent) you still have a full MDP
underneath: a set of states, a set of actions, a transition model
`T(s, a, s')`, a reward function `R(s, a, s')`, and you're still
looking for a **policy** `π(s)` telling you what to do in each state
(e.g., for the crawler, "when both angles are at 90°, actuate the
elbow in the positive direction").

**The twist:** you don't know `T` or `R`. Formally, there *is* an MDP —
it's just an **unknown** one. Until you're in a state and take an
action, you don't know what states result (`T`) or whether there's a
big reward waiting there (`R`). In the familiar grid-world example, you
don't know whether the reward waiting in the exit corner is +10 or −10
until you actually go there and "pull the exit lever." So all those
transitions are effectively unknown until you learn them by trying
things.

### Offline planning vs. online (real) execution — a core distinction

- **Offline (the MDP setting from last lecture):** you already know
  the model. You sit, think, run value iteration / expectimax, build a
  full policy — all **in simulation**, entirely inside your head/model
  — and only *afterward* do you go execute the resulting policy in the
  real world. You never actually fall in a pit while planning; you just
  imagine it and rule it out.
- **Online (the RL setting, starting today):** there is no
  crystal ball. This is exactly like the slot machine — you can't know
  the payout without actually putting money in. You are **really**
  taking these actions, and **you cannot take them back.** In search,
  an unexplored frontier node is still there if your current plan
  fails; you can backtrack. In RL, once you jump in the fire, you
  can't un-jump. This has real consequences: e.g., learning to fly a
  helicopter by RL means you will probably crash several helicopters
  along the way, so how you balance trying new things (**exploration**)
  against doing what already seems to pay off (**exploitation**)
  matters a great deal (full treatment starts next lecture).
- **Episodes.** Because you can't rewind, most RL experience is broken
  into **episodes**: a continuous run of transitions from a start
  state until some terminal condition (falling in a pit, hitting a
  time limit, crashing the helicopter), after which the agent — or a
  fresh copy of it — is reset and a new episode begins.

---

## 3. Two Broad Approaches: Model-Based vs. Model-Free

RL splits into two broad families. **Neither is inherently better than
the other** — they have different strengths and weaknesses — but in
practice, **model-free learning is the more widely used of the two.**
The lecture builds model-based learning first because it directly
reuses everything already known about solving MDPs, then uses it as a
stepping stone toward the model-free algorithms (TD learning,
Q-learning) that are the real payoff.

### Model-based learning

The idea: if you knew the MDP, you already know how to solve it
(value iteration, from last lecture). So — go find out what MDP you're
actually living in, first.

1. **Learn an empirical model.** For every state `s` and action `a`
   you've actually tried, keep counts of which `s'` you ended up in,
   and turn those counts into an estimated (empirical) transition
   model `T̂(s, a, s')`. Rewards, once observed, are typically
   deterministic and just get recorded directly as `R̂(s, a, s')`.
2. **Solve the resulting (approximate) MDP** with the ordinary
   techniques — value iteration, expectimax, whatever's appropriate.

**Worked example (grid world, states labeled A–E).** Given a fixed
policy to follow (not learning the policy — just watching an agent
execute it and taking notes) and four observed episodes:

- We want `T̂(C, east, D)`. Every time the agent took the `east`
  action from `C`, count where it landed: three times it landed in
  `D`, once it landed in `A`. So `T̂(D | C, east) = 3/4`,
  `T̂(A | C, east) = 1/4`.
- We want `T̂(C, east's reward)`. Every time `C --east--> D` was
  observed, the reward received was **−1**.
- The agent was observed taking `exit` from `D` once, landing in the
  terminal state and receiving **+10** — so that reward entry is now
  known too.
- Once enough `(s, a, s')` triples have been tallied this way, you
  have a full (if imperfect) empirical MDP, which you then hand to
  ordinary value iteration exactly as if it had been given to you
  directly.

**Problems with model-based learning** (raised as an open discussion
in lecture, then answered piece by piece):

1. **Statistical noise from small samples.** With few visits to a
   `(state, action)` pair, the empirical transition/reward estimates
   can be badly off — and this gets worse the more states there are to
   cover.
2. **No guarantee of coverage.** States the given policy never visits
   are simply unknown — nothing here ensures the experience stream
   covers everything you'd need to know.
3. **Real consequences of real experience.** Because you're not in
   simulation, badly-estimated actions can cause you to *actually*
   receive a large negative reward — fine for playing a lot of card
   games, much worse if you're teaching a real drone to fly and it
   crashes.
4. **No built-in way to go get more data where you need it.** If you
   decide "I really need better statistics on what happens at `C`,"
   this approach doesn't tell you how to *get back to* `C` — it only
   describes how to learn from experience once it arrives, not how to
   seek out the experience you want.

### An analogy that motivates model-free learning: expected age of CS188 students

**Model-based way** to compute the class's average age: first estimate
the *distribution* over ages `P(age)` by sampling ("how old are you?"
repeated across the room), using relative frequency as the estimator;
*then* compute the expectation `Σ_age P(age) · age` from that learned
distribution — a weighted average, computed after learning a model.

**Model-free way:** skip estimating `P(age)` entirely. Just ask "how
old are you?" repeatedly and keep an unweighted **running average of
the raw answers**. This converges to exactly the same expected value,
because ages that are more common in reality will simply show up more
often in the stream of answers — their higher probability shows up as
higher *frequency*, so an unweighted average of the samples
automatically reproduces the weighted average you'd get from the true
distribution. **You never need to explicitly build the model at all.**
This — "you don't need the model to compute an average; you can just
average the samples as they arrive" — is the single idea underlying
every model-free RL algorithm that follows.

---

## 4. Passive Reinforcement Learning and Direct (Monte Carlo) Evaluation

**Passive reinforcement learning** simplifies the general RL problem
in two ways at once, specifically so the core learning mechanics can
be introduced cleanly:

1. **No action selection.** The learner is just watching some agent
   (or executing some given policy) and taking notes — not deciding
   what to do. (Choosing *which* actions to try, and the
   explore/exploit trade-off that goes with it, is deferred to next
   lecture.)
2. **Fixed policy — this is policy evaluation, not control.** We're
   learning `V^π(s)`, the value of being in `s` **under a specific,
   already-fixed policy π** — not the optimal value `V*(s)`. (Learning
   optimal values is the harder problem tackled starting in §6.)

### Direct evaluation

The simplest possible idea: every time you visit a state, write down
the total (discounted) reward received from that point until the
episode ends. Average those totals across every visit to that state.
That's it — "direct evaluation." It's simple, and it **is** correct in
the limit of infinite data — but, as the lecture stresses, "no one ever
actually does this," for reasons explored below.

**Worked example.** Discount = 1, living reward = −1 per step, exit
reward = +10. First observed episode: `B --east--> C --east--> D
--exit-->` terminal, receiving rewards −1, −1, +10 respectively. The
value of `B` under this single sample is the **sum of all rewards
from that point on**, not just the next reward or the final one: `−1 +
−1 + 10 = 8`. Similarly this one episode gives a sample of `9` for `C`
(`−1 + 10`) and `10` for `D` (just the `+10`).

Across four episodes total:
- `A` was visited once, sample return `−10` (fell straight into a
  pit) → estimate `V(A) ≈ −10`.
- `B` was visited twice, both times returning `8` → estimate
  `V(B) ≈ 8`.
- `C` was visited **four** times: three of those returned `9` (the
  good path through `D`), but the fourth time the episode instead fell
  into the −10 pit (a −1 living-reward step plus the −10 terminal
  penalty, i.e. a return of −11 for that one episode). Averaging:
  `(9 + 9 + 9 + (−11)) / 4 = 16 / 4 = +4`. So `C`'s learned value comes
  out noticeably **lower** than `B`'s, purely because one of its four
  observed episodes happened to wander into the pit.

**What's good about this:** it's dead simple, it never needed to know
`T` or `R` (they're implicit in the observed rewards), and it does
converge to the right answer eventually — exactly the "ages" analogy
above, since it's just averaging samples.

**What's bad about this — the important part.** The C-vs-B comparison
above is exactly the demonstration: in this MDP, `B` and `E` are
*structurally identical* under this policy — both always transition to
`C`. So they *must* have the same true value. But direct evaluation
has no way to know that, and will happily report different learned
values for them purely from sampling noise downstream (e.g., if the
handful of episodes through `B` happened to avoid the pit while the
ones through `E` didn't). More generally:

- It **wastes all information about how states are connected.** Once
  you know `B` always leads to `C`, everything you separately learn
  about `C`'s value should *automatically* inform `B`'s value — you
  shouldn't need entirely fresh, independent data for `B` to learn
  that. Direct evaluation ignores this and re-learns each state's
  entire future essentially from scratch.
- Consequently it needs **far more data** than necessary — each state
  is absorbing all the downstream variance of the rest of the episode,
  which is irrelevant noise once you already know what the immediate
  next state's value is.
- It's a genuine small-sample-variance problem too: with too few
  visits, luck alone (whether a particular run happened to end well or
  badly) dominates the estimate.

---

## 5. From Sample-Based Bellman Updates to Temporal Difference (TD) Learning

### Recall: policy evaluation with a *known* model (last lecture)

The known-model Bellman update for evaluating a fixed policy computes,
recursively:

```
V_{k+1}(s) = Σ_{s'} T(s, π(s), s') · [ R(s, π(s), s') + γ · V_k(s') ]
```

with `V_0(s) = 0` everywhere. The key structural property this
exploits: the new estimate at `s` is built from the **old estimate one
step away**, at `s'` — you never have to unroll the *entire* rest of
the game, just plug in what you already believe about the very next
state. This is exactly the "connectivity" information direct
evaluation was throwing away.

**The central question of RL:** can we do this same one-step-lookahead
Bellman update **without knowing `T` or `R`**? We've already got the
one tool needed: **replace an average that requires a model with a
running average of samples that doesn't.** This single substitution —
turn the `Σ_{s'} T(s,a,s')[...]` expectation into a running average
over the `(s, a, s', r)` tuples you actually experience — is the idea
behind *every* algorithm for the rest of the lecture.

### The catch: you can't get 50 samples from `s` on demand

The proposed fix — collect several samples of the transition out of
`s` under `π`, average them together — runs into a real obstacle: once
you take the action `π(s)` from `s`, you land in some `s'` and you're
"off to the races." **You can't rewind time** to get a second sample
from the exact same `s`; you have to wait, possibly a long time,
before you happen to return to `s` again — and while you wait, you're
not incorporating anything you just learned. Samples don't arrive in
neat batches from a single state — they trickle in one at a time,
scattered across whatever states the agent happens to visit, in an
order you don't control.

### Temporal Difference (TD) learning

The fix: **learn from every single experience immediately, one sample
at a time**, rather than collecting a batch and averaging later. Given
a transition `(s, a, s', r)`:

```
sample  =  R  +  γ · V(s')                      (old estimate of s')
V(s)  ←  (1 − α) · V(s)  +  α · sample
```

equivalently, in "gradient step" form:

```
V(s)  ←  V(s)  +  α · ( sample − V(s) )
```

where **α is the learning rate** (e.g. 0.1 = slow, mostly trust the
old estimate; 0.5 = fast, weight the new sample heavily). This is a
**running / exponentially-weighted average**: unrolling the recursion
shows that older samples get discounted by successive factors of
`(1 − α)`, so more recent samples are weighted more heavily. That
sounds like a downside, but it's actually the right behavior: older
samples were computed against *older, less-informed* value estimates
of the downstream states, so it makes sense to trust them a little
less as newer information arrives. Under appropriate conditions
(e.g. `α` decreasing appropriately over time), this **provably
converges to the correct `V^π`.**

**Crucial and easy-to-miss point: you only ever update the value of
the state you *left*, never the state you land in.** Arriving at `s'`
by itself tells you nothing about `s'` — you haven't done anything
there yet. The reward `r` and the transition just observed tell you
something about **`s`**, the state you departed from — "you leave
learning in your wake."

**Worked example.** Discount = 1, α = 0.5. Initially all state values
are believed to be 0, except the known exit state `D`, believed to be
8.

- Observed transition: `B --east--> C`, reward **−2**. We're learning
  about `B` (the state we left), not `C`. Old estimate `V(B) = 0`.
  Sample = `−2 + 1·V(C) = −2 + 0 = −2`. New estimate:
  `V(B) = 0.5·(0) + 0.5·(−2) = −1`. This is the right direction: `B`
  used to look worth 0, and this experience — landing in a
  still-unpromising state after a costly step — should push it down.
- Observed transition: `C --east--> D`, reward **−2**. Now we learn
  about `C`. Old estimate `V(C) = 0`. Sample =
  `−2 + 1·V(D) = −2 + 8 = 6`. New estimate:
  `V(C) = 0.5·(0) + 0.5·(6) = 3`. Again the right direction: `C`
  looked neutral, but this one transition revealed it actually leads
  toward the good exit, so its value should rise.

The key advantage over direct evaluation: this update needed **no
knowledge of what happens beyond one step** — it borrowed the
already-existing estimate at the landing state instead of having to
watch the rest of the episode play out. That's exactly the
connectivity-exploitation that direct evaluation was missing.

### The wall TD (value) learning runs into

Mechanically, TD learning is just: take the known-model Bellman
*policy-evaluation* update, cross out the expectation, and replace it
with a running average. **But it only ever computes `V^π` for a fixed
π — it doesn't tell you how to extract a *policy* from what you've
learned.**

Recall how you'd normally extract a policy from state values: take an
**argmax over actions**, which means computing, for each action, the
value of the resulting **Q-state** `Q(s,a)` — and those were never
estimated here, only the plain state values `V(s)`. So even with a
perfect `V^π` in hand, action selection is stuck: you'd need the model
(`T`, `R`) to compute those Q-values from `V`, and the entire premise
of RL is that you don't have it.

**This is presented as a genuine historical dead end:** this is
essentially where reinforcement learning stalled for **decades** —
researchers knew how to evaluate a given policy from experience, but
had no way to use that to actually choose good actions or learn
*optimal* behavior; they only knew how to learn about the value of
whatever policy was already being executed. The fix — learn **Q**
values instead of state values — turns out to solve *both* problems at
once, which is the subject of the rest of the lecture.

---

## 6. Why Value Iteration Can't Just Be "TD-ified": The Max Is the Problem

We already know how to defeat not knowing `T`: replace the
`T`-weighted average with a running average of samples, exactly as TD
learning did. So why not just do the same trick to *value iteration*
(which computes `V*`, the *optimal* value) instead of policy
evaluation (which computes `V^π`)?

Recall value iteration's update:

```
V_{k+1}(s) = max_a  Σ_{s'} T(s, a, s') · [ R(s, a, s') + γ · V_k(s') ]
```

The `Σ_{s'} T(...)` averaging part is no problem — same fix as before.
**The problem is the `max_a` out front.** Under a fixed policy `π`,
there was no such max to worry about, because you were only ever
following `π`'s single prescribed action. To make value iteration
produce *optimal* answers instead of "whatever policy you happened to
follow" answers, you fundamentally need to **compare what different
actions would do** — but on any given visit to `s`, you only get to
execute **one** action and see its one outcome. You can't rewind and
try a different action from the same visit to compare them. **This
max was described in lecture as "a brick wall for reinforcement
learning for a long time"** — everyone knew they wanted this update,
knew they wanted it as a running average instead of an expectation,
and had no idea what to do about the max standing in the way.

### The breakthrough: do it on Q-values instead

Write out the analogous dynamic-programming update for **Q-values**
directly (forget sampling for a moment — assume the model is known,
just to see the structure):

```
Q_{k+1}(s, a) = Σ_{s'} T(s, a, s') · [ R(s, a, s') + γ · max_{a'} Q_k(s', a') ]
```

The crucial difference: **there is no max blocking the outer average
here.** The averaging over `s'` (weighted by `T`) is exactly the same
kind of average as before, so it can be replaced by a running sample
average exactly as with TD learning. The `max_{a'} Q_k(s', a')` piece
is now safely *inside* the update, applied to Q-values that are
already being tracked for every action out of the landing state `s'` —
computing that max costs nothing extra, since you already maintain all
of those numbers. **The choice of which action's Q-value to bootstrap
from is now a free decision made from already-known numbers, rather
than something that requires trying multiple actions in the same
visit.**

---

## 7. Q-Learning

Combining the running-average trick with the Q-value formulation above
gives **Q-learning**, applied one sample `(s, a, s', r)` at a time:

```
sample = R + γ · max_{a'} Q(s', a')
Q(s, a)  ←  (1 − α) · Q(s, a)  +  α · sample
```

As with TD learning, you learn about the `(s, a)` pair you just left —
landing in `s'` and receiving `r` tells you nothing new about `s'`
itself, only about how good the choice `a` was **from** `s`. There is
one Q-value tracked for **every state-action pair** — e.g. a typical
grid-world cell with four available moves has four separate Q-values
being learned simultaneously, even though only one of them corresponds
to the actual optimal action; the rest still get learned and still
help along the way. With Q-values available, action selection becomes
completely model-free and trivial: **just look at the Q-values leaving
your current state and pick the best one — no `T` or `R` needed at
decision time.**

### The genuinely surprising property: off-policy learning

Because the bootstrap term uses `max_{a'} Q(s', a')` — the *best*
currently-known action from the landing state — rather than the value
of whichever action you *actually* happen to take next, **Q-learning
converges to the optimal Q-values regardless of how bad the policy
generating the experience is**, as long as every state and action pair
gets tried infinitely often. You can act almost completely randomly,
repeatedly walk into pits, behave however sloppily you like — and
Q-learning will still learn the *optimal* Q-values from that
experience. This is explicitly called out in lecture as the
"mind-blowing," "not obviously possible" result that unlocked modern
reinforcement learning: **learning optimal behavior while following a
suboptimal (even essentially arbitrary) policy — "off-policy"
learning.**

### Grid-world walkthrough of Q-learning in the applet

Setup: every state has one Q-value per available action (most cells:
north/south/east/west; exit-only cells: a single "exit" Q-value, which
coincides with that state's value since it's the only action). All
Q-values start at 0, learning rate α = 0.5.

- **Episode 1:** `north` from the start state, landing in a
  zero-reward, all-zero-Q-value state → old estimate 0, sample
  `0 + max(0,0,0,0) = 0` → no change. Same for a subsequent `east`
  move (zero to zero, still no change). Then `exit`: instantaneous
  reward is **nonzero (+1)**, landing in the terminal state
  (value 0). Old estimate was 0; sample = `1 + 0 = 1`; new estimate
  `= 0.5·0 + 0.5·1 = 0.5`. Episode ends with total reward 1.
- **Episode 2:** eventually an `east` action lands in that
  now-`0.5`-valued state. Old estimate for this action was 0; sample
  `= 0 + 0.5 = 0.5`; new estimate `= 0.5·0 + 0.5·0.5 = 0.25` — "and
  there it is." Later in the same episode, the `exit` Q-value (already
  at 0.5) gets sampled again: sample `= 1 + 0 = 1`; new estimate
  `= 0.5·0.5 + 0.5·1 = 0.75`.
- **Episode 3 onward:** the pattern keeps propagating **backward**
  through the grid one bootstrapped step at a time — an action leading
  into the 0.25-valued state gets updated toward `0.5·0 + 0.5·0.25 =
  0.125`, and as the neighboring cell's own value keeps climbing (from
  0.25 toward 0.75), later visits to that same predecessor action climb
  correspondingly higher. The lecture narrates this explicitly as
  "using the connectivity" — good value discovered near the exit
  gradually bootstraps backward through however many states lead to
  it, each one learning *only* about the specific action it actually
  took.

**Demonstrating off-policy robustness live:** the instructor
deliberately and repeatedly walks the agent **south into a −10 pit**
from a state whose other, better action was already estimated around
`0.94`. Two things are shown *not* to happen:
1. **The good action's Q-value (≈0.94) does not degrade** from the
   repeated bad experience, and this good value **does not fail to
   propagate backward** to the predecessor cell — it keeps
   strengthening a neighboring cell's estimate normally.
2. **The bad "walk into the pit" action doesn't even get flagged as
   clearly bad yet**, because landing in the pit-adjacent square is
   itself a state with other, zero-valued escape routes — repeatedly
   experiencing a large negative outcome there doesn't change the
   Q-value of the state *before* it, because that update bootstraps
   off `max_{a'} Q(s', a')`, i.e. the *best* action available from the
   landing state, not whatever the agent actually did next.

**Explicit contrast drawn in lecture:** if this were plain TD *value*
learning under a fixed policy (no max), a repeated bad experience
**would** propagate backward and drag down the predecessor's estimate,
because there'd be no max shielding it — you'd just be using the one
policy's actual outcome, good or bad. The max over Q-values is
precisely what insulates a state's *good* known option from being
corrupted by badly-chosen exploratory actions elsewhere out of the
same landing state.

---

## 8. Where This Leaves Off — Exploration vs. Exploitation (Preview)

Even though Q-learning can tolerate a bad or random policy and *still*
converge to optimal values, it still needs **some** policy to generate
experience from — and that policy still has to decide, on each step,
whether to do what currently looks best (**exploitation**) or try
something it doesn't have good data on yet (**exploration**). The
lecture flags this explicitly as *the* fundamental trade-off, to be
covered starting next lecture, and previews one (imperfect but
eventually-correct) strategy: **ε-greedy** — take the best known
action, but with probability ε, do something else at random instead.
In the crawler applet, ε is shown live: with a high ε (~40% random
moves) the crawler visibly explores messily; turning ε off and forcing
it to always take its current best-known action shows it committing
fully to what it's learned so far ("behold — it lives").

*(The recording — and this transcript — cut off mid-sentence here,
partway through a live grid-world demo point about how a state's value
does or doesn't propagate. Whatever came next is not present in the
source captions.)*
