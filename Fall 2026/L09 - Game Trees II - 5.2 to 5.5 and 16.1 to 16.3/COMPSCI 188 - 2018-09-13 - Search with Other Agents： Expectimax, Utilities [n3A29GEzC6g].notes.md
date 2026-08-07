# Search with Other Agents: Expectimax, Utilities

## Lecture overview

This lecture extends adversarial search to situations where outcomes are uncertain rather than controlled by a purely adversarial opponent, and then asks a more basic question: what are the "utilities" that agents have been maximizing all along, and why is it rational to maximize their expectation?

The main topics are:

- Chance nodes and the **expectimax** algorithm
- Modeling assumptions: adversarial vs. random vs. mixed opponents
- Why pruning and simple depth limits behave differently with chance nodes
- A refresher on random variables, probability distributions, and expected value
- Multi-agent game trees where each player has an independent utility
- Where utilities come from and why minimax breaks down as a general decision rule
- The rationality axioms and the von Neumann–Morgenstern theorem
- Assessing utility values in practice, and risk attitudes toward money
- The Allais paradox

## 1. From minimax to expectimax

Recall the two-branch game tree from the previous lecture: MAX chooses between a branch leading to (10, 10) and a branch leading to (9, 100), each controlled below by a MIN node. Minimax says go left, guaranteeing 10, because a rational MIN will always steer toward the 9 on the right-hand branch.

But minimax assumes the opponent is a perfect adversary. What if the "opponent" is not actually optimizing against you — maybe it is an agent that doesn't always play optimally, or the branch is decided by something like a coin flip? If the right branch is resolved by a fair coin flip between 9 and 100, the average value of that branch is:

\[
\frac{9 + 100}{2} = 54.5
\]

which is now better than the guaranteed 10 on the left. This gives a formal reason to prefer the right branch when the outcome is governed by chance rather than by an adversary.

To represent this, game trees gain a third node type:

- **Triangles pointing up**: MAX nodes
- **Triangles pointing down**: MIN nodes
- **Circles**: chance nodes

Searching a tree containing chance nodes is called **expectimax search**.

### Why would a chance node appear in a model of the world?

- The game is designed to be stochastic (e.g., dice rolls).
- The opponent's behavior is unpredictable, and it may be more useful to model it with a probability distribution than to model it as a perfect adversary.
- Actions do not execute deterministically — e.g., a robot's wheels may slip, so the intended action does not always produce the intended result.

### Expectimax value

In a stochastic setting the right quantity to compute is the **average** result under optimal play, not the worst case:

\[
V(s) =
\begin{cases}
U(s) & \text{if } Terminal(s)\\
\max\limits_{a \in A(s)} V(Result(s,a)) & \text{if MAX moves}\\
\sum\limits_{a \in A(s)} P(a) \, V(Result(s,a)) & \text{if a chance node}
\end{cases}
\]

Max nodes work exactly as in minimax. Chance nodes replace the MIN operator with a probability-weighted average (an **expectation**).

Note that the expectimax value of a node (e.g., 54.5 above) need not be an outcome that ever actually occurs in a single play of the game — it is the long-run average if the game were played many times.

### Expectimax pseudocode

```text
VALUE(state):
    if TERMINAL(state):
        return UTILITY(state)
    if state is a MAX node:
        return MAX-VALUE(state)
    if state is a chance node:
        return EXP-VALUE(state)

MAX-VALUE(state):
    value = -infinity
    for action in ACTIONS(state):
        value = max(value, VALUE(RESULT(state, action)))
    return value

EXP-VALUE(state):
    value = 0
    for action in ACTIONS(state):
        p = PROBABILITY(action)
        value += p * VALUE(RESULT(state, action))
    return value
```

### Worked examples

For a chance node with children valued 8, 24, −12 and probabilities 1/2, 1/3, 1/6:

\[
\tfrac{1}{2}(8) + \tfrac{1}{3}(24) + \tfrac{1}{6}(-12) = 4 + 8 - 2 = 10
\]

When probabilities are not stated explicitly, the default assumption is a **uniform distribution** over the children. For children valued 3, 12, 9 under a MAX node with an equal-probability chance node beneath it: (3+12+9)/3 = 8, so the MAX node's value is 8.

## 2. Pac-Man example: modeling assumptions matter

Consider Pac-Man flanked by two ghosts, losing a point per time step, with food nearby.

- **Modeled as minimax** (ghosts as perfect adversaries): since Pac-Man is going to lose regardless, minimax concludes the least-bad option is to rush the nearest ghost and get eaten quickly, minimizing time-step losses.
- **Modeled as expectimax** (e.g., the blue ghost's direction is a coin flip): running toward the side with the ghosts now has two possible outcomes — get chased and lose, or have the ghost wander away and be able to eat food for a high reward. If the average of those two outcomes beats the certain loss from charging a ghost, expectimax chooses to go that way instead. This does not guarantee a good outcome on any single run — sometimes it will be lucky, sometimes not — but it does better on average.

The important caveat: these are **modeling assumptions**, and they can be wrong.

- Running expectimax against a truly adversarial ghost is naive — it will be exploited.
- Running minimax against a truly random ghost is overly cautious — it forgoes opportunities that a rational agent would take.

Understanding how the world actually behaves is necessary to choose the right model.

## 3. Pruning and depth limits with chance nodes

**Alpha–beta pruning does not generally work with chance nodes.** With minimax, once MIN's best option is known to be no better than an alternative MAX already has, that whole subtree can be skipped, because MIN chooses the single worst leaf. With a chance node, however, the *value* depends on the average of *all* children — one very large or very small value anywhere in the subtree can swing the average, so no child can be safely ignored unless there are known bounds on the possible values.

**Depth-limited search with an evaluation function still applies.** As with minimax, if the tree is too large to search to termination, the agent can stop after a fixed depth and substitute an evaluation function's estimate for the true value, then back that estimate up through the chance and max nodes.

## 4. Probability review

- A **random variable** represents an event whose outcome is unknown.
- A **probability distribution** assigns weights to each possible outcome.
- Probabilities are always non-negative and sum to 1 over all outcomes.
- Modeling choices matter: deciding how many discrete outcomes to use (e.g., "empty / mild / heavy" traffic) and what probability to assign each is a design decision, and it directly affects what an expectimax agent will do.
- Probabilities can be updated as new evidence arrives (e.g., traffic is more likely heavy specifically at 8 a.m.) — this is the subject of later material on probabilistic reasoning.

### Expected value

The expected value of a function of a random variable is the probability-weighted average over outcomes. Example: if travel time to the airport is 20, 30, or 60 minutes depending on traffic, weighted by the traffic distribution, the expected travel time might come out to 35 minutes.

Two lotteries can have the same expected value but different variance (e.g., outcomes tightly clustered vs. spread between 0 and a much larger number); people may have preferences between them beyond the raw expectation — see risk attitudes below.

In an expectimax tree, the probabilities at a chance node might come from something simple (a known die) or from something computationally expensive (e.g., a physical simulation of weather to decide indoor vs. outdoor event planning). Either way, for the purposes of the search algorithm, the probabilities are simply given.

A key caveat: the probabilities in the tree are the agent's **model** of the opponent/environment. If the model is wrong, the resulting strategy is only as good as the assumption.

## 5. Modeling a mixed-strategy opponent

Suppose the opponent is known to play depth-2 minimax 80% of the time and a uniformly random move the other 20% of the time. To capture this in a game tree without hand-coding the "occasionally take a risk against the random 20%" behavior, the opponent's node is modeled as a **chance node with two branches**:

- 80% branch: the single action produced by a depth-2 minimax search of the opponent's position.
- 20% branch: another chance node, uniformly random over the remaining actions.

Running expectimax over this constructed tree causes the desired risk-taking behavior to emerge automatically from the search, rather than being hard-coded.

**Cost implication:** every time such a chance node is encountered, a full sub-search (here, depth-2 minimax) must be run just to determine the probabilities to use at that node. If the opponent were modeled as depth-10 minimax 80% of the time, every chance node in the tree would require a depth-10 minimax search — a large constant-factor cost increase over plain minimax, where each player's assumption about the other is consistent and no extra side-computation is needed. This mismatch between what each player assumes about the other is what forces the extra computation; in ordinary minimax, both players consistently assume the other is a perfect adversary, so the tree structure alone is sufficient.

## 6. The dangers of optimism and pessimism

- **Optimism** (assuming chance when the world is actually adversarial): leads to being exploited, since real threats are not accounted for.
- **Pessimism** (assuming the worst case when the world is actually benign or random): leads to overly conservative behavior and missed opportunities.

Pac-Man demo results, averaged over multiple runs, comparing the two search types against two ghost behaviors:

| Pac-Man strategy | Ghost behavior | Outcome |
|---|---|---|
| Expectimax | Random | Best average score (~503) — matched to an easy environment and exploits it |
| Expectimax | Adversarial | Lower score, but not disastrous — mismatched but still reasonably cautious |
| Minimax | Random | Overly cautious; wastes time being "scared" before committing, but eventually recovers since danger never was hard-coded away entirely |
| Minimax | Adversarial | Correctly cautious and matched to the environment |

The worst combination in practice is an agent that is too optimistic against a genuinely adversarial opponent, since it gets exploited most consistently.

## 7. Other game tree structures

### Backgammon: alternating max/min/chance

Backgammon adds a third dispatch case: MAX moves, a die roll (chance) determines options, then MIN moves, repeating. This only requires switching from a 3-way dispatch (max/min/terminal) to a 4-way dispatch (max/min/chance/terminal) — the algorithmic change is small.

Backgammon has a large state space (roughly 20 legal moves per position) and heavy stochasticity from the dice, so even a small search depth yields a very large tree, and the probability of reaching any particular deep node shrinks quickly. Because chance limits how much any single branch can dominate the outcome (unlike minimax, where an adversary can deterministically force a path), **no single branch matters as much as it would in a pure minimax game**. Historically, this is why the first AI to reach world-champion level at any game (backgammon) could get away with just a depth-2 search paired with a strong, reinforcement-learning-trained evaluation function — deep search matters less when averaging smooths out the impact of any one unlucky branch.

### Multi-agent games with independent utilities

In a game with more than two players (e.g., red, blue, green), each terminal node carries a **separate utility value for each player**, rather than one shared zero-sum value. Minimax is a special case of this where the two players' values happen to be exact negatives of each other.

Because utilities are now independent per player, interesting dynamics can emerge:

- Two players can end up effectively **cooperating** if their preferences over a shared branch happen to align, even though neither was told to cooperate — it falls out purely from the payoff structure.
- A player's preferences can be ignored by another player whose choice doesn't depend on them, producing outcomes a naive read of "everyone wants the best deal" would not predict.

**Algorithm:** at each node, each player passes up the full vector of values (one per player) associated with whichever child the node's owner would choose (their own coordinate is maximized). The mechanics resemble minimax/expectimax, but a vector of values is propagated instead of a single number.

## 8. Utilities: where do they come from?

The course's running principle since the first lecture has been: a rational agent maximizes **expected utility**. This section asks why that principle is justified, and where the utility numbers themselves come from.

### Utilities must be specified for the agent

An agent cannot be allowed to choose its own utility function — e.g., a house-cleaning robot that could pick its own utility might decide "high utility, no matter what I do" and do nothing. Utilities have to be supplied externally by the designer, based on what outcomes are actually desired.

### Why minimax fails as a general decision rule

If you use a strict worst-case (minimax) approach to every real-world decision — e.g., deciding to leave the house — you must account for arbitrarily bad low-probability events (being hit by a car, an earthquake, etc.). Under minimax reasoning, the worst case always dominates, so a comprehensive minimax agent that accounts for rare catastrophic outcomes would essentially never act. Minimax is only usable if you have already excluded rare extreme events from consideration ahead of time. This motivates using **expected** utility instead: the **maximum expected utility (MEU) principle** says a rational agent should choose the action that maximizes its expected utility given its knowledge of how the world works.

### The numeric values matter, not just the ranking

Squaring all the terminal values in a minimax tree does not change minimax's decision, because minimax only depends on the relative *ordering* of leaf values, which squaring preserves (for non-negative values). But squaring the same terminal values **does** change the decision under expectimax, because averaging is sensitive to the actual magnitudes, not just their order. This shows that for expectimax-style reasoning, the specific numbers assigned to outcomes are meaningful, not just their relative preference order.

### Formal definition

A **utility function** is a mapping from outcomes (states of the world) to real numbers describing an agent's preferences. In a simple game, utilities are just given by the rules (e.g., +1 win, −1 loss, 0 draw). The claim — proven by a theorem below — is that for any agent with *rational* preferences, such a utility function must exist, even outside of simple games.

A **lottery** is the standard term for a situation with uncertain outcomes ("prizes"): an event that resolves to prize A or prize B according to some probability distribution. Preference notation: A ≻ B means A is strictly preferred to B; A ~ B means the agent is indifferent between them.

## 9. Rationality axioms and the von Neumann–Morgenstern theorem

For a preference relation over outcomes/lotteries to be considered rational, it should satisfy:

- **Orderability**: for any two prizes, the agent either prefers one over the other or is indifferent — there is always a comparison.
- **Transitivity**: if A ≻ B and B ≻ C, then A ≻ C.
- **Continuity**: if A ≻ B ≻ C, there exists some probability mix of A and C that is exactly equivalent to B.
- **Substitutability**: if A ~ B, then a lottery containing A can be swapped for the same lottery with B substituted in, without changing preference.
- **Monotonicity**: if A ≻ B, then a lottery giving a higher probability to A (and correspondingly lower to B) is preferred to one giving a lower probability to A.

### Why transitivity matters: the money-pump argument

If an agent's preferences are not transitive (e.g., prefers B ≻ A, A ≻ C, but also C ≻ B), it can be exploited: starting from C, the agent will pay a small amount to trade up to B, then pay again to trade up to A, then pay again to trade back down to C — ending up with the same prize it started with but strictly less money. A non-transitive agent can be money-pumped indefinitely.

### The theorem

The **von Neumann–Morgenstern theorem** (also attributed to Ramsey, 1931) states: given any preference relation satisfying the axioms above, there exists a real-valued utility function \(U\) such that:

\[
A \succeq B \iff U(A) \geq U(B)
\]

and the utility of a lottery equals the probability-weighted sum of the utilities of its prizes:

\[
U(\text{Lottery}) = \sum_i p_i \, U(\text{prize}_i)
\]

This is exactly the averaging operation performed at expectimax chance nodes — the theorem is what justifies treating that averaging step as the "correct" thing to do, provided the underlying preferences are rational.

## 10. Assessing utility values in practice

- Utilities can be **normalized**: assign the best possible outcome a utility of 1 and the worst possible outcome a utility of 0 (e.g., "worst" might be death). Extreme-outcome units such as **micromorts** (a one-in-a-million chance of death) or **quality-adjusted life years** are used in some domains to quantify these extremes.
- Utility functions are only defined **up to positive affine transformation**: adding a constant or multiplying by a positive scalar does not change the behavior implied by the utility function, since it doesn't change the relative comparisons used by averaging.
- Simple preference rankings (without lotteries) only reveal ordering, not the actual utility numbers. To recover numeric utility values, a **standard gamble** is used: offer a choice between a guaranteed prize and a lottery between the best possible outcome and the worst possible outcome (e.g., "instant death"), and find the probability at which the person is indifferent between the guaranteed prize and the gamble. That probability directly gives the normalized utility of the guaranteed prize.

## 11. Money vs. utility, and risk attitudes

Money is **not** the same as utility. For a lottery with probability \(p\) of winning \(X\) and \(1-p\) of winning \(Y\):

- Expected monetary value: \(pX + (1-p)Y\)
- Utility of the lottery: \(p\,U(X) + (1-p)\,U(Y)\)

These are generally different, because \(U\) need not be linear in money.

- If the utility curve for money **rises but flattens out** as money increases (concave), the utility of the lottery is *less* than the utility of the expected monetary value — this describes a **risk-averse** agent. Most people are risk-averse: the first million dollars is worth much more (in utility) than an additional million once you already have a billion.
- The reverse curve (convex) describes **risk-prone** behavior.

### Certainty equivalent and insurance

For a lottery between $1,000 and $0 (expected value $500), most people would accept a guaranteed amount noticeably *less* than $500 — often around $400 — in exchange for giving up the lottery. This guaranteed amount is the **certainty equivalent**, and it lies below the expected monetary value for a risk-averse agent.

This gap is exactly where insurance is profitable: an insurance company can offer to buy the lottery ticket for $400 (a fair trade from the individual's risk-averse perspective), while holding a large pool of similar independent lotteries where, by the law of large numbers, the average payout converges to the true expected value of $500. The $100 spread between $400 and $500 is the room for a mutually beneficial deal — anywhere in that range, both the individual and the insurer come out ahead relative to their own certainty equivalents.

### The Allais paradox

Consider two choices:

- **Choice 1**: Lottery A (80% chance of $4,000, 20% chance of $0) vs. Lottery B (guaranteed $3,000).
- **Choice 2**: Lottery C (20% chance of $4,000, 80% chance of $0) vs. Lottery D (25% chance of $3,000, 75% chance of $0).

Empirically, most people prefer **B over A**, and **C over D**.

Assuming \(U(\$0) = 0\) (utility functions can always be shifted so the worst case is 0):

- B ≻ A implies: \(U(3000) > 0.8\,U(4000)\)
- C ≻ D implies: \(0.2\,U(4000) > 0.25\,U(3000)\), i.e. \(0.8\,U(4000) > U(3000)\)

These two inequalities directly contradict each other — no utility function can satisfy both preferences simultaneously, meaning this common pattern of choices is, strictly, **irrational** under the standard VNM framework.

One proposed resolution is that the model of "outcome" is incomplete: choosing A and ending up with $0 carries an additional cost beyond the money — the regret ("stupidity") of having passed up a guaranteed $3,000 for nothing. If that regret term is included in the utility of the $0 outcome under choice A specifically, the apparent contradiction can be resolved without declaring the person irrational — it instead reflects an underspecified outcome/utility model.

## Key takeaways

- Expectimax replaces MIN's worst-case choice with a probability-weighted average at chance nodes, and is appropriate when outcomes are governed by randomness or an unpredictable agent rather than a perfect adversary.
- Modeling assumptions matter: expectimax against a truly adversarial opponent is exploitable; minimax against a truly random opponent is needlessly conservative.
- Alpha–beta-style pruning generally does not apply to chance nodes, since any single child can swing an average; depth limits with evaluation functions still work.
- Modeling a probabilistic mix of opponent strategies (e.g., 80% minimax / 20% random) lets the desired risk-taking strategy emerge from search, at the cost of running a full sub-search at every chance node.
- Multi-agent (non-zero-sum) game trees carry a vector of utilities per node; minimax is the special case where two players' utilities are exact negatives.
- The Maximum Expected Utility principle — not minimax — is the general rational decision rule, because minimax breaks down once rare extreme events are considered.
- Rational preferences (orderability, transitivity, continuity, substitutability, monotonicity) guarantee, via the von Neumann–Morgenstern theorem, that a utility function exists and that expected-utility averaging is the correct decision procedure.
- Utility functions are unique up to positive affine transformation, and can be elicited in practice via standard gambles.
- Money and utility are not the same: most people are risk-averse, which is why certainty equivalents lie below expected monetary value and why insurance markets can be mutually beneficial.
- The Allais paradox shows that common human choices can violate the rationality axioms under a naive money-only utility model, though richer models (incorporating regret) can restore consistency.
