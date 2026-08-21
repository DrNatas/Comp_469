# Chapter 2 Write-Up

Name:
Date:

Keep this to two or three pages. Answer from the code in front of you, not
from the textbook in general. A correct answer that could have been written
without ever opening this project will not get full marks.

---

## 1. PEAS description (5 points)

Describe this task environment using AIMA Section 2.3.1.

**Performance measure.**
> What is the agent actually judged on? Name the function and the file. List
> every term in it, including the ones that cost points.

**Environment.**
> The maze, the ghosts, the pellets, the clock. Mention anything that
> changes while the agent is deciding.

**Actuators.**
> What can the agent actually do? Be precise about how many actions it takes
> per turn and what happens if it picks an illegal one.

**Sensors.**
> What does the agent perceive? Name the mechanism that decides this, not
> just the list of fields.

---

## 2. Environment properties (7 points)

One row per dimension from AIMA Figure 2.6. Justify each from something
specific in the code, and name it.

| Property | This environment is... | Why (cite the code) |
|---|---|---|
| Fully or partially observable | | |
| Single-agent or multi-agent | | |
| Deterministic or nondeterministic | | |
| Episodic or sequential | | |
| Static or dynamic | | |
| Discrete or continuous | | |
| Known or unknown | | |

**Follow-up.** Two of these have an argument on both sides in this
particular implementation. Pick one, and make the case for the answer you
did *not* put in the table.

---

## 3. Your agent's type (5 points)

**Which figure in AIMA Section 2.4 does your agent match?**
> Name the figure and map each box in it to something concrete in
> `agent.py`.

**Which fields did you put in `Percept`, and why those?**
> In particular: you had a choice between `ghosts` and `released_ghosts`.
> Say which you took and what the other one would have cost you.

**What would it take to move your agent one type further up?**
> Sketch it. You do not have to build it.

---

## 4. Performance measure vs utility function (6 points)

These are two different things and this codebase keeps them in two different
files on purpose.

**Where does each one live?**
> File and function for both.

**Name one place they disagree.**
> Find something your utility function rewards that the performance measure
> does not, or the reverse. Explain why that gap exists and whether it is a
> flaw.

**Why does AIMA insist on the distinction?**
> Answer in your own words, in three or four sentences.

---

## 5. Rational is not the same as successful (4 points)

Run some `hard` trials and find a seed where your agent lost.

**Seed:**

**What happened.**
> Replay it with `python tools/play.py --difficulty hard --seed N` and
> describe the sequence.

**Why the losing decision was still rational.**
> AIMA Section 2.2.2 separates rationality from omniscience. Use it. What
> did the agent not know, and could it have known it given the percept it
> was handed?

**What would have to change for that decision to be irrational?**

---

## 6. Trial results (3 points)

Paste the summary table from `results/summary.csv`.

| agent | difficulty | trials | win_rate | caught_rate | mean_score | mean_decisions | mean_performance |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

**Interpretation, three to five sentences.**
> Do not restate the numbers. Explain what the gap between your agent and
> `simple_reflex` is caused by, in terms of the agent structures involved.
> The `mean_decisions` and `mean_backtracks` columns are the interesting
> ones; say what they show about memory.

---

## Optional

Anything you tried that did not work, or a weight you tuned and then
reverted. Not graded, but useful to me.
