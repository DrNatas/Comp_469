# COMP 469 — Chapter 2 Challenge Questions

Supplement to the existing engagement Q&A. These target discrimination, application, and the
specific misconceptions the chapter tends to produce, rather than recall. Slide numbers refer to
physical slide position in the 51-slide deck.

---

## 2.1 — Agents, percepts, agent function vs. agent program

**C1. (Slide 6) Two agent programs run on the same architecture and produce identical behavior on
every percept sequence that can actually occur in the two-square vacuum world, but differ on
sequences that can never occur. Do they implement the same agent function?**

Formally no — the agent function is defined over the entire domain of percept sequences, so two
functions that differ anywhere are different functions. But the difference is unobservable in this
environment and cannot affect the performance measure. This is exactly why the chapter shifts
attention from the function to the program: the function is an external description, and what we
are graded on is behavior on reachable inputs.

*Targets:* students who treat the agent function as if it were the implementation.

---

**C2. (Slide 6) A student claims an agent with no sensors has no agent function. Rebut it.**

The percept sequence is the empty sequence at every step, so the agent function is still
well-defined: it maps the empty history to an action. The resulting behavior is a fixed,
open-loop action sequence. The environment is unobservable, not undefined — and goals can
sometimes still be achieved, which is the sensorless planning case the chapter forward-references
to Chapter 4.

---

**C3. (Slide 7) You add NoOp to the vacuum agent's action set, taking it from three actions to
four. Does the lookup table get larger?**

No. Table size is the number of *rows*, which is the number of percept sequences — |P| + |P|² + …
+ |P|ᵀ. Actions determine what can appear in the right-hand column, not how many rows there are.
Adding actions widens the choice per row; adding percepts or lifetime is what explodes the table.

*Targets:* the very common conflation of action-space size with state/table size. Ask this before
slide 27 and the big-number slide lands much harder.

---

## 2.2 — Rationality, performance measures, autonomy

**C4. (Slide 12/13) "The agent that stepped into the street was irrational, because it got
crushed." Refute this using the chapter's definition — then state what *would* have made the
same action irrational, with the same outcome.**

Rationality maximizes *expected* performance given the percept sequence and prior knowledge. The
cargo door was not inferable from available evidence, so the choice was rational and the outcome
was bad. Perfection maximizes actual performance and is not achievable. What would have made it
irrational: failing to gather cheap, available information first. Looking both ways is required by
rationality, because information gathering that improves the expected outcome is itself a rational
action. Same outcome, different verdict.

---

**C5. (Slide 13) The dung beetle and the sphex wasp both fail. Which is the better analogy for a
model deployed on a distribution it was not trained for, and why?**

The wasp. The beetle simply lacks a sensor for the condition it needs. The wasp *does* re-check,
repeatedly, but its check cannot detect that its own plan is failing — the feedback loop exists
and is blind to the relevant failure. That is the deployed-model case: monitoring is running, the
metrics look fine, and nothing in the loop is capable of reporting that the operating assumption
has been violated. Both are failures of autonomy: behavior fixed by designer or evolutionary
assumption rather than by percepts.

---

**C6. (Slide 10) A phishing-triage agent is rewarded for the number of emails it correctly labels.
Name the reward-hacking failure mode, then write a better measure.**

The agent maximizes label volume on the easy majority class. Bulk marketing and newsletters are
plentiful and trivially classifiable, so accuracy climbs while recall on actual phish goes to near
zero. This is the vacuum agent dumping dirt so it can clean it again: the measure rewards visible
effort rather than the environment outcome. A better measure scores the environment: number of
successful phishing messages reaching a user inbox, penalized by analyst-hours consumed handling
false positives. Note that the second term is necessary — optimize the first alone and the agent
quarantines everything.

---

**C7. (Slide 11) Give a performance measure under which the steady Agent A and the bursty Agent B
score identically, then change one term so A wins, and one so B wins.**

Mean tickets resolved per hour scores them equally by construction. Add a penalty on maximum queue
wait and A wins, because B's long absences produce a single terrible worst case. Reward throughput
in the single best hour and B wins. The point is that the average did not fail to answer the
question — it concealed that a question was being asked. Every performance measure encodes a value
judgment about distribution, and picking the mean is a choice, not a neutral default.

---

**C8. (Slide 9) The vacuum's performance measure is unchanged, but clean squares can now become
dirty again at random. Is the original agent still rational, and what does that tell you about
where rationality lives?**

No longer rational. Once dirt can reappear, sitting still guarantees losing points on squares that
may have become dirty, so periodic re-checking becomes the expected-performance-maximizing
behavior. Nothing about the agent's code changed and nothing about the performance measure
changed — only an assumption about environment dynamics. Rationality is a property of the
agent-environment-measure triple, never of the agent alone.

---

## 2.3 — PEAS and environment properties

**C9. (Slide 16) Two students classify chess differently: one says static, one says semidynamic.
Who is right?**

Both, for different task environments. Chess without a clock is static. Chess with a clock is
semidynamic: the board does not change while the agent deliberates, but the agent's score does,
because time is being consumed. The disagreement is not about chess — it is about which task
environment they specified. This is the cleanest demonstration in the chapter that the properties
classify a *specification*, not a world.

---

**C10. (Slide 16/17) Taxi driving is partly unpredictable because other drivers are
unpredictable. Why does the chapter refuse to call that stochastic?**

Because uncertainty arising from the actions of other agents is handled by the multiagent
dimension, and is deliberately excluded from the deterministic/stochastic judgment. If we folded
it in, every multiagent environment would be stochastic by definition and the dimension would
carry no information. Determinism is judged with respect to the environment's own transition
behavior given all agents' actions.

*Targets:* the single most common environment-classification error on exams.

---

**C11. (Slide 17) A self-driving car cannot perceive the road surface behind it. Partially
observable, or effectively fully observable?**

It depends entirely on the performance measure, and the question is not answerable without one.
If nothing behind the vehicle is relevant to the choice of action, the environment is effectively
fully observable. Add a term penalizing being rear-ended and the same physical world becomes
partially observable, because now something relevant is unperceived. Relevance is defined by the
performance measure, so changing the measure can reclassify the environment without touching a
single sensor.

---

**C12. (Slide 18) Fill all four cells of the known/unknown × fully/partially observable matrix
with tasks that are not on the slide.**

Known + fully observable: tic-tac-toe, or a Rubik's cube in hand. Known + partially observable:
Minesweeper, or Battleship. Unknown + fully observable: a new board game where all pieces are
visible but you have not read the rules. Unknown + partially observable: operating an unfamiliar
industrial control system, or a new detection tool running against traffic you have not
characterized. If a student produces a cell they cannot fill, that is usually the cell they have
collapsed into the other axis.

---

**C13. (Slide 16) Name one physical world that yields two different task environment
classifications, and say what changed.**

The same Pac-Man maze. Rendered full-screen it is fully observable. Rendered first-person with
visibility limited to adjacent tiles it is partially observable. Identical world, identical rules,
identical performance measure — only the sensor specification moved, and the correct agent
architecture moves with it.

---

**C14. (Slide 14/46) "Be helpful to students" is proposed as the performance measure for a campus
chatbot. Give two distinct ways this fails, one about the measure and one about the environment.**

The measure is unmeasurable and unfalsifiable: no state of the world clearly satisfies or violates
it, so the critic in any learning version has nothing to report and the designer cannot compare
two candidate agents. The environment problem is subtler and is the one the chapter flags — when
the performance measure is unknown to the designer, the user effectively becomes a second agent
whose preferences must be inferred, which quietly converts a single-agent task into a multiagent
one. That is a design decision being made by accident.

---

## 2.4 — Agent structure

**C15. (Slide 31) A randomized rule lets the sensorless vacuum escape its infinite loop. Has it
become a model-based agent?**

No. It has no internal state, no transition model, and no sensor model. Randomization changes the
policy from deterministic to stochastic without adding a single bit of memory. It is worth noting
that a randomized simple reflex agent can genuinely outperform a deterministic one under partial
observability — so this is a real improvement, just not an architectural one. A model-based agent
will usually beat both.

---

**C16. (Slide 30) Give one history-dependent behavior a simple reflex agent *can* reproduce, and
one it cannot. What distinguishes them?**

It can reproduce any behavior whose relevant history is encoded in the current percept — a brake
light that stays lit carries the fact "this car began braking" into the present frame. It cannot
distinguish two situations that produce identical percepts but require different actions, which is
exactly the sensorless vacuum seeing [Clean] in square A and square B. The distinguishing question
is never "does the task involve history" but "is the history-derived information present in the
current percept."

---

**C17. (Slide 32/33) The vacuum's location sensor breaks and reports the last known location
forever. Which model is now wrong, what happens in UPDATE-STATE, and which slide-13 animal is
this?**

The sensor model is wrong: world states no longer generate the percepts the model predicts. The
transition model may be perfectly fine. UPDATE-STATE keeps folding a stale percept into the belief
using a correct transition model, so the internal state drifts steadily from reality while the
agent's confidence in it is unchanged. The agent then acts decisively on a belief that is wrong.
This is the dung beetle implemented in software — a built-in assumption that no percept can
contradict.

---

**C18. (Slide 34/36) I can encode "arrive fast and safely" as a goal: define the goal set to
contain only states reached in under 20 minutes with zero collisions. So why does the chapter need
utility at all?**

Two failures. First, if under-20-minutes is unattainable, every action leads to a non-goal state,
so all actions are scored identically and the agent has no basis for choosing — goals give no
ranking among failures. Second, the encoding cannot express a trade-off: it cannot say that 21
minutes safely beats 19 minutes recklessly. Utility supplies a scalar, which gives a ranking among
both successes and failures, and it composes with probability to give expected utility under
uncertainty. Goals are the degenerate case where the utility function is binary.

---

**C19. (Slide 44) A chess program runs minimax with a hand-written evaluation function. Is it
goal-based or utility-based?**

Both, and this is the point of the slide's "design patterns, not rigid boxes" line. The goal test
is checkmate. The evaluation function is a utility function over non-terminal states, because it
ranks positions rather than accepting or rejecting them. Real systems mix the patterns freely; the
taxonomy is a design vocabulary, not a partition.

---

**C20. (Slide 38/40) Why must the performance standard sit outside the agent, where the agent
cannot modify it?**

Because the learning element optimizes whatever the critic reports. An agent that can edit its own
standard has a much cheaper path to a high reported score than improving its behavior: change the
standard. It would then be simultaneously succeeding by its own measure and failing at the task,
with no internal signal that anything is wrong. This is the same failure as the badly designed
performance measure on slide 10 and the wrong utility function on slide 37, arriving from a third
direction — which is worth saying out loud, because students tend to file those three as separate
warnings.

---

**C21. (Slide 38/39) Give a concrete problem-generator action for a learning Pac-Man, and explain
why the performance element would never choose it.**

Deliberately approach a ghost while a power pellet is active, in order to learn how long the
frightened timer actually lasts. The performance element maximizes expected score under current
knowledge and rates this as clearly suboptimal — it risks a life for no immediate points. The
problem generator accepts a known short-term loss to acquire information that improves the model,
which improves every future decision. Galileo dropping rocks was not trying to break rocks.

---

**C22. (Slide 39) Which learning-agent components does supervised fine-tuning of a model modify?
Which does an A/B test correspond to?**

Fine-tuning modifies the performance element, and if the model predicts consequences, the
transition model along with it. An A/B test is a problem generator paired with a critic: it
deliberately deploys a variant believed to be suboptimal, in order to generate informative
experience, and scores the result against a standard held fixed for the duration of the test.
Note the second half — an A/B test where the success metric is redefined mid-experiment is the
editable-critic failure from C20.

---

## 2.4.7 — Representation

**C23. (Slide 41) The model-based Pac-Man tracks position, walls, remaining food, ghost positions,
and timers. Place that on the atomic/factored/structured axis, then say what one step to the right
buys you and what it costs.**

That is factored: a set of variables with values. Moving to structured lets you express objects
and relations — "the ghost that is between me and the nearest pellet," rules that quantify over
all ghosts regardless of how many exist, and reuse of the same rule when the game adds a fifth
ghost. The cost is that reasoning and learning both get harder, and for a fixed small maze the
factored version may already capture everything the performance measure depends on.

---

**C24. (Slide 42) If structured representations write the rules of chess in one or two pages and
atomic ones need roughly 10³⁸, why is the answer not simply "always use the most expressive
representation"?**

Because concision of description and efficiency of inference are different quantities, and they
move in opposite directions. A more expressive language captures everything a less expressive one
can, at least as concisely, and more besides — but reasoning and learning over it get harder. The
rule of thumb is the least expressive representation that still captures what the task requires,
and the chapter's closing observation is that real-world systems often need to operate at several
points on the axis simultaneously.

---

**C25. (Slide 43) Why is localist-vs-distributed independent of atomic/factored/structured, rather
than being a fourth point on the same axis?**

The first axis asks how much structure the representation can express. The second asks where the
information physically lives. They vary independently: you can hold a factored state in a
distributed encoding, or an atomic one in a localist table. The practical consequence is the noise
behavior — garble a few bits in a localist encoding and Truck becomes the unrelated concept Truce;
garble a few bits in a distributed one and you land on a nearby point in the space, which carries
a similar meaning.

---

## Synthesis and derivation

**C26. (Slide 27) Derive the taxi lookup-table figure. Show why the exponent has eleven zeros,
not eight.**

70 MB/s × 3600 s ≈ 2.5 × 10¹¹ bytes for one hour from one camera, which is about 2 × 10¹² bits.
The number of distinct inputs is 2^(2×10¹²). Take log base 10: 2 × 10¹² × 0.301 ≈ 6 × 10¹¹. So
the table needs about 10^600,000,000,000 entries — six hundred billion zeros in the exponent, not
six hundred million. Worth running on the board, both because it corrects the slide and because it
converts an unimaginable number into three lines of arithmetic a student can reproduce.

---

**C27. (Slide 45) I hand you a task that is fully observable, deterministic, static, discrete, and
known — but sequential, with a long horizon. Which architecture, and what does that tell you about
the first row of this slide?**

Goal-based, with search. Full observability removes any need for internal state, so the
model-based row is unnecessary — but the current percept still cannot tell you which action leads
toward the goal fifty moves out, so reflex is not enough either. The first row of the slide reads
"fully observable + simple," and the entire load is carried by the word "simple." Observability
alone never licenses a reflex agent; horizon length does. Worth saying explicitly, because the
row invites students to read observability as the deciding property.

---

**C28. (Slide 45) Now reverse it: partially observable, but episodic, with no long-term
objective. Which architecture?**

Partial observability normally points at model-based reflex, but episodic means each decision is
independent of the last, so there is no history worth carrying across episodes. A simple reflex
agent with well-chosen features may be adequate, or a model-based agent whose state resets each
episode. The general lesson is that the slide-45 rows are not independent triggers — you read all
seven properties together, and episodic structure can cancel the state requirement that partial
observability would otherwise impose.

---

**C29. (Slides 16, 38, 45) At what point does a phishing-triage agent's environment become
multiagent, and name three consequences for the design.**

It becomes multiagent as soon as the attacker's payoff depends on the agent's behavior, which in
practice is immediately — adversaries adapt to filters. Three consequences. First, the environment
stops being static in the design-relevant sense, because the transition dynamics change over time
in response to the agent. Second, a fixed rule set has a shelf life, so a learning agent is not an
enhancement but a requirement. Third, randomized behavior can become rational: in a competitive
environment, predictability is exploitable, so a deterministic policy hands the adversary a test
oracle.

---

**C30. (Slides 22, 23) A student says the demo Pac-Man failed because BFS could not find the
pellets. What is wrong with that sentence, and what is the actual root cause?**

BFS was never called — the demo runs a simple reflex program: current percept, ordered rule,
action. Attributing the failure to a search algorithm the program does not contain is a category
error. The root cause is architectural: no memory, no model of the maze, no explicit target, and
therefore no route. BFS would help, but only after the agent has a state representation, a
successor function, a goal-selection policy, and a mechanism for turning a returned path into
actions — and even then it optimizes number of moves, not risk or score, and needs replanning
whenever the ghosts move.

---

**C31. (Whole chapter) Write PEAS for an agent whose performance measure is genuinely unknown at
design time, then say what that does to your environment classification and your architecture
choice.**

Any assistive agent works — a scheduling assistant, a research assistant. The performance measure
must be written as something like "satisfies the user's actual preferences, which are not
available to the designer." That single line propagates: the environment becomes multiagent,
because the user is now an agent whose preferences must be inferred from behavior rather than
read from a specification; it becomes partially observable with respect to the thing that matters
most, since preferences are never directly perceived; and the architecture must be a learning
agent, because the utility function has to be estimated from feedback rather than written down.
This is a good closing exercise — it forces students to use all four parts of the chapter at once
and lands directly on the value-alignment thread from Chapter 1.

---

## Six misconceptions worth pre-empting

1. Agent function is the code. (C1)
2. More actions means a bigger lookup table. (C3)
3. Unpredictable other agents make an environment stochastic. (C10)
4. Observability alone decides reflex vs. model-based. (C27)
5. Randomization adds internal state. (C15)
6. Known/unknown is a statement about sensors. (C12)

Items 3 and 6 account for most lost points on environment-classification questions; item 4 for most
lost points on architecture-selection questions.
