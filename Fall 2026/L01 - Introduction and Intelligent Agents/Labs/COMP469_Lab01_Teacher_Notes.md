# COMP 469 — Lab 01: Vacuum World Agents
## Teacher Notes & Instructor Guide

> **Audience:** These notes are for you, the instructor. They cover conceptual grounding, step-by-step lab walkthrough, gotchas, grading guidance, and answers to the most common student questions.

---

## 0. Big Picture: What This Lab Is Really About

The lab has students build a small AI simulation from scratch. The *real* learning goals are conceptual:

- What makes an agent an **agent** (vs. a function or a script)?
- How does design change when you give the agent more information (percepts → memory → goals)?
- What does "rational" mean when you can only measure performance after the fact?

The coding is the vehicle, not the destination. If students can make each agent run and then *explain* why it behaves the way it does using AIMA vocabulary, they have met the lab's intent.

---

## 1. What Is a Reflex Agent, Model-Based Agent, and Goal-Based Agent?

This is the conceptual core. Spend 10–15 minutes on this before students touch code.

### 1.1 Simple Reflex Agent

**The idea:** React only to what you see *right now.* No memory. No plan.

Think of a thermostat. It does not know the history of the temperature; it only checks: *Is it too cold right now?* If yes, turn on the heat.

In this lab, the reflex agent looks at the percept (`location`, `status`) and decides. It is forbidden — by design — from storing anything between calls. A correct reflex agent has **no `self.` state** (other than possibly a pre-baked lookup table or rule set).

**Key classroom framing:**
> "If you blindfolded the agent, erased its memory between every step, and it still behaved the same way — that's a reflex agent."

**Limitation students must discover:** Without memory, the agent can revisit cells it already cleaned, waste moves bumping into walls, or get stuck in corners. This is the point of Checkpoint 2 — let them articulate this themselves.

**Serpentine sweep (the suggested rule):** On even rows, move Right; at the end of a row, move Down; on odd rows, move Left; at the end, move Down again. This is deterministic and does not require memory — the agent can reconstruct its position in the sweep from `(x, y)` alone. That is what makes it a valid reflex agent even though it *looks* smart.

**Gotcha:** Students sometimes put a `self.visited` set inside `ReflexVacuumAgent`. That disqualifies it as a reflex agent — it is now model-based. Push back on this in grading or during lab walkthroughs.

---

### 1.2 Model-Based Agent

**The idea:** Keep an internal model of the world built up from past percepts. Use that model to make smarter decisions.

The agent does not get the full grid handed to it — it only ever sees its current location and the status of the current square. But it *remembers* where it has been. This lets it avoid re-exploring squares.

In this lab, the model-based agent stores:
- `self.visited` — a set of positions it has already been to
- `self.known_status` — what the status of each visited square was when last seen
- (Stronger version) `self.path_stack` — a stack enabling backtracking

**Key classroom framing:**
> "The model-based agent is like someone navigating a dark house with a flashlight. They can only see one spot at a time, but they're building a mental map as they go."

**The backtracking version (completed code):** When no unvisited neighbor exists, the agent pops from its path stack and moves back toward a previous location. This is a depth-first search through the grid — the agent systematically explores without re-covering ground.

**Gotcha — the fallback matters a lot:** Without backtracking, the basic model-based agent can get isolated in a sub-region of the grid if all its neighbors are visited. Students who implement the basic fallback (random legal neighbor) will see the agent sometimes get "trapped" and thrash. This is fine — it becomes great material for Checkpoint 3. The backtracking version essentially guarantees full coverage on a connected grid.

**Gotcha — `known_status` is not ground truth:** Students may think the model-based agent knows everything about the world. It does not. Squares can be dirty again (in extension Option B), and the agent's model lags behind. Worth pointing this out as a preview of the "partially observable" environment classification.

---

### 1.3 Goal-Based Agent

**The idea:** Explicitly represent a desired future state (the goal), and choose actions that move toward it.

In this lab, the goal is "reach the nearest dirty square." The agent uses BFS to compute the shortest path and executes the first step of that path each turn.

**This agent is given a cheat.** It is allowed to inspect `environment.status` directly — it sees the full world state, not just a percept. The lab acknowledges this and calls it a "bridge" to Chapter 3 (search). Make sure students understand: in a fully realistic setting, a goal-based agent would use only what it has perceived. The shortcut here is pedagogical.

**Key classroom framing:**
> "The goal-based agent is like a GPS. It knows where it is, it knows where it wants to go, and it computes the best route. Every time a new dirty square appears, it re-plans."

**Why BFS?** The grid is unweighted (every move costs the same 1 point), unordered, and the agent wants the *nearest* dirty square. BFS guarantees the shortest path in an unweighted graph. A* would also work and is worth mentioning as a preview of later labs.

**Gotcha — re-planning every step:** The goal-based agent in this lab recalculates its full BFS path at every single step. This is inefficient but always correct. Students sometimes try to cache the path and only re-plan when done. That can work but introduces bugs when a dirty square gets cleaned mid-path. The simpler re-plan-every-step design is safer for this lab.

**Gotcha — the BFS must handle obstacles:** `get_neighbors()` already filters out obstacles, so if students use it in their BFS (as the completed code does), obstacles are automatically handled. If students try to re-implement neighbor expansion themselves, they often forget obstacle filtering.

---

## 2. Lab Walkthrough: Step by Step

### Section 0 — Python `.env` Setup

This is the most common place students get stuck before the lab even starts.

**What students need:**
- Python 3.9+ (3.11 recommended)
- `pip install ipykernel notebook jupyter matplotlib` inside the venv
- The kernel registered: `python -m ipykernel install --user --name comp469`
- In Jupyter, **select the "COMP 469 (.env)" kernel** before running anything

**Windows gotcha:** PowerShell's execution policy will block the activation script. Students must run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` in the same terminal before activating. This is a one-time fix per terminal session.

**Common symptom:** "I ran the cell and got `ModuleNotFoundError: No module named 'matplotlib'`." This almost always means they ran the notebook using the default system Python kernel, not the venv kernel. Have them go to **Kernel → Change Kernel → COMP 469 (.env)**.

**Do Jupyter notebooks need to be error-free when running?**

**Yes — the lab explicitly requires it.** The submission checklist states: *"Your notebook restarts and runs from top to bottom without errors."* A notebook that crashes mid-run is not a complete submission.

However, in practice:
- Students whose BFS `TODO 9` is incomplete will get no output from the goal-based agent cells, but no crash either (the stub returns `[]`, causing `NoOp`, which is handled gracefully).
- Incomplete TODO 1/2/3/4 (environment) will cause crashes downstream because other cells depend on a working environment.
- The safest grading stance: **the environment cells must work; agent cells with incomplete TODOs are acceptable if they degrade gracefully** (agent returns `NoOp` or random) and the student explains what is missing in the checkpoint.

---

### Section 1 — Setup Cell

Nothing for students to do. Imports `random`, `deque`, `dataclass`, `matplotlib`. Seeds `random` to 469 for reproducibility.

**Instructor note:** The seed means every student who has not changed anything will see the same world layouts. This is intentional for grading consistency. If students complain about "boring" results, remind them they can change seeds — but their experiments in Section 10 use their own seeds (1000 + trial), so the default seed only affects the early examples.

---

### Section 2 — PEAS Analysis

This is all written work, no code. It should take 15–20 minutes.

**Expected answers (for your reference):**

| PEAS | Answer |
|------|--------|
| Performance measure | Dirt cleaned (+10/square), actions taken (−1/step), bumps (−2 extra), maybe a bonus for finishing |
| Environment | N×N grid of squares, possibly with obstacles |
| Actuators | Suck, Up, Down, Left, Right, NoOp |
| Sensors | Current location, current square status (Clean/Dirty) |

| Property | Answer | Justification |
|----------|--------|---------------|
| Observable | Partially | Agent sees only current location/status, not the whole grid |
| Single/multi-agent | Single | One vacuum, no other agents |
| Deterministic | Deterministic | Same action → same result every time (no randomness in transitions) |
| Episodic/Sequential | Sequential | Each action affects future states |
| Static/Dynamic | Static | Environment does not change while agent is deliberating |
| Discrete/Continuous | Discrete | Finite grid, finite actions |
| Known/Unknown | Known | Rules of the world are given to the designer |

**Checkpoint 1 gotcha:** Students often confuse "known" (the *designer* knows the laws) with "observable" (the *agent* can see the world). Make sure they understand these are different axes.

---

### Section 3 — Build the Vacuum World Environment

**This is the most critical coding section.** Everything downstream depends on it.

**TODO 1 — Obstacles:**
```python
# Completed version
if location != start and random.random() < obstacle_probability:
    self.obstacles.add(location)
```
The guard `location != start` prevents the agent from spawning inside an obstacle. Students often forget this.

**TODO 2 — Dirt:**
```python
# Completed version
self.status[location] = "Dirty" if random.random() < dirt_probability else "Clean"
```
Note that after this loop, the code explicitly sets `self.status[start] = "Clean"`. This means the agent always starts on a clean square, which is a simplifying assumption worth discussing.

**TODO 3 — Suck action:**
```python
if action == "Suck":
    if self.status[self.agent_location] == "Dirty":
        self.status[self.agent_location] = "Clean"
        self.score += 10
        self.cleaned_count += 1
    return
```
Students sometimes forget `return` after Suck, which causes the movement code to also run on the same step. That is a bug: you can't move and suck in one action.

**TODO 4 — Movement:**
```python
moves = {"Up": (x, y-1), "Down": (x, y+1), "Left": (x-1, y), "Right": (x+1, y)}
next_location = moves[action]
if self.is_accessible(next_location):
    self.agent_location = next_location
else:
    self.score -= 2
```
**Coordinate system gotcha:** `Up` decreases `y` (row index), `Down` increases `y`. This is the standard screen/matrix convention (row 0 is at the top). Students from a math background sometimes try `Up = (x, y+1)` and end up with an agent that moves in the wrong direction. The visual output from `display_text` (which prints row 0 first) will reveal this immediately.

**Smoke test expected output:**
```
Start: (0, 0)
Percept: Percept(location=(0, 0), status='Clean')
Dirty squares: ~5–8 (varies by seed)
Obstacles: ~2–3 (varies by seed)
```
If "Dirty squares: 0" — their TODO 2 is still using `"Clean"` as the default.
If "Obstacles: 0" — their TODO 1 condition is still `False`.

---

### Section 4 — Visualize the World

No TODOs for students. The visualization code is pre-written. They just run it.

- `A` = agent position (blue dot in the plot)
- `D` / dark gray = dirty square
- `.` / light gray = clean square
- `#` / black = obstacle

**Gotcha:** The `plot_environment` function uses `imshow` with `cmap="Greys"`. The agent is overlaid as a scatter point. If students modify the visualization and the blue dot disappears, they likely accidentally reset the axis after `imshow`.

---

### Section 5 — Agent Interface and Random Baseline

No TODOs. Students run this to understand the `Agent` base class and see how `RandomVacuumAgent` works.

**Teaching point:** The `RandomVacuumAgent` is NOT a pure reflex agent — it does always suck when dirty (a condition-action rule), and otherwise moves randomly. It is often better than expected because of the suck rule. Use this to motivate why a smarter movement rule (Section 7) might help.

---

### Section 6 — Simulation Runner

**TODO 5** is already nearly complete in the student file — the loop body is there. Students just need to make sure they understand what each line does.

The runner:
1. Gets percept from environment
2. Asks agent for action
3. Breaks if `NoOp`
4. Executes action
5. Records score, dirty count, action
6. Breaks if environment is clean

**Gotcha:** Students sometimes try to add a `reset()` call inside the runner to allow re-running the same agent on the same world. They should use `load_world()` instead (demonstrated in Section 10). The runner itself should not reset the environment.

---

### Section 7 — Reflex Agent

**TODO 6:** Replace the random fallback with a deterministic movement rule.

**The completed serpentine rule:**
```python
if y % 2 == 0:
    preferred = "Right" if x < environment.width - 1 else "Down"
else:
    preferred = "Left" if x > 0 else "Down"

legal_actions = environment.get_neighbors(percept.location)
if preferred in legal_actions:
    return preferred

for action in ["Right", "Down", "Left", "Up"]:
    if action in legal_actions:
        return action

return "NoOp"
```

**Why this is valid as a reflex agent:** The preferred action is computed purely from `(x, y)` in the percept. No stored state. The fallback list is a fixed priority order — also no stored state.

**What students might turn in instead:** Many students will implement something like "always try Right, then Down, then Left, then Up" — a simple priority fallback. This is also a valid reflex rule, just less efficient. Accept it as long as they can explain it in Checkpoint 2.

**Common student mistake:** Adding `if x == environment.width - 1 and y % 2 == 0: return "Down"` as a special case but then returning `random.choice(...)` as the fallback. This is a *partial* reflex rule — partially deterministic and partially random. The lab says "deterministic movement rule," so push them to eliminate the `random.choice`.

---

### Section 8 — Model-Based Agent

**TODO 7:** Prefer an unvisited neighbor.
```python
if unvisited_actions:
    return random.choice(unvisited_actions)
```

**TODO 8:** Improve the fallback (basic → backtracking).

**Basic fallback (minimum viable):**
```python
if neighbors:
    return random.choice(list(neighbors.keys()))
```

**Stronger backtracking fallback (completed code version):**
The completed code uses `self.path_stack` to record the path taken and backtracks when stuck:
```python
while self.path_stack:
    previous_location = self.path_stack.pop()
    if previous_location in neighbors.values():
        return self.action_toward(location, previous_location)
```
`action_toward` converts a target coordinate into a direction string.

**Teaching the difference:** With basic fallback, the agent can end up oscillating between two visited squares forever. With backtracking, it systematically retreats along its path until it finds a branch to explore. This is depth-first search behavior.

**Grading gotcha:** The lab says the stronger version is "optional." A student who submits the basic fallback and explains its weakness in Checkpoint 3 has met the minimum. Award extension credit or bonus consideration for backtracking.

---

### Section 9 — Goal-Based Agent with BFS

**TODO 9:** Implement BFS.

**Completed BFS:**
```python
while frontier:
    location, path_so_far = frontier.popleft()

    if location in dirty_set:
        return path_so_far

    for action, next_location in environment.get_neighbors(location).items():
        if next_location not in visited:
            visited.add(next_location)
            frontier.append((next_location, path_so_far + [action]))

return []
```

**Why `deque` and `popleft()`?** Using a `deque` with `popleft()` gives O(1) dequeue from the front — that's what makes it BFS (not DFS). Using `list.pop(0)` would also work correcty but is O(n) — acceptable for a 5x5 grid, suboptimal for larger ones.

**Why store `path_so_far` in the frontier?** Because we need to reconstruct *how* we got to a node, not just *that* we reached it. The alternative is a `came_from` dict and then backtracking from the goal — both are valid. The path-in-frontier approach is simpler to understand for students new to BFS.

**Common BFS bug:** Students forget to add the start node to `visited` before the loop, which causes the start to be re-added to the frontier infinitely. The completed code initializes `visited = {start}` before the loop starts — make sure students match this.

**Another common bug:** Checking `if location in dirty_set` before expanding neighbors. If you check AFTER popping (as the completed code does), you correctly return when you reach a dirty square. If you check BEFORE adding to frontier, you may skip the dirty square itself. This is a subtle off-by-one in BFS — worth demonstrating on the whiteboard.

---

### Section 10 — Controlled Experiments

No TODOs. The `evaluate_agents` function is pre-written.

**Key design to explain:** Why does the function call `env.load_world(status, obstacles)` instead of just creating a new `VacuumEnvironment` per agent? Because even with the same seed, creating a new environment with obstacles calls `random()` internally, which advances the RNG and means subsequent agents see different worlds. `copy_world()` / `load_world()` bypasses this by copying the exact state.

**Teaching point on fairness:** This is controlled experimentation. Each agent faces the *identical* starting state. Without this, a lucky random agent might outscore the goal-based agent on some trials just because it got an easier world.

---

### Section 11 — Plot Results

No TODOs. Two bar charts: average score and average dirty squares left.

**Expected result pattern (with completed code):**
- Goal-based agent: highest avg score, lowest avg dirty left
- Model-based agent (with backtracking): second best on both metrics
- Reflex agent (serpentine): third — good on open grids, hurt by obstacles
- Random agent: lowest — lots of wasted moves

The exact numbers will vary by student implementation. What matters for grading is that the pattern makes *conceptual* sense and the student can explain it in Checkpoint 5.

---

### Section 12 — Extension Challenge

Optional. Suggested for students who finish early (unlikely in a 3-hour lab, but possible for fast coders).

- **Option A** (backtracking) — essentially what the completed model-based agent already does. Assign to students who only did the basic fallback.
- **Option B** (random new dirt) — requires modifying `execute_action` or adding a post-step event hook. Interesting but tricky.
- **Option C** (new performance measure) — a great conceptual exercise. Changing bump cost to -10 will dramatically hurt the reflex agent on obstacle-heavy worlds.
- **Option D** (10x10 grid) — just change the `evaluate_agents` call parameters.

---

### Section 13 — Final Reflection

The prompt asks: *Is the highest-scoring agent always the most rational agent?*

**What a good answer looks like:**
- Defines rationality in AIMA terms: maximizing expected performance measure, given what the agent perceives and knows
- Notes that the goal-based agent has an unfair advantage (sees full grid), so comparing scores isn't apples-to-apples
- Argues that rationality is relative to the performance measure AND the information available
- Uses actual experiment numbers: "The goal-based agent averaged X score vs. Y for the model-based agent, but the model-based agent was working with less information"

---

## 3. Is the Completed Code a Good Reference for Student Submissions?

**Yes, with caveats.** The completed code is your *instructor answer key*, not a sample student submission. Here is what differs:

| Aspect | Completed Code | Acceptable Student Submission |
|--------|----------------|-------------------------------|
| Model-based agent | Backtracking with `path_stack` | Basic fallback (random neighbor) is acceptable |
| Reflex agent | Full serpentine with obstacle fallback | Any deterministic rule that works reasonably well |
| BFS | Correct, complete | Must be correct — this is a required TODO |
| Environment TODOs 1–4 | All correct | All required — if these fail, downstream cells break |
| Written checkpoints | Not included (your job) | All 5 checkpoints required, 3–7 sentences each |
| PEAS tables | Not included | Required |
| Plots | Rendered | Must be visible in the submitted notebook |
| Final reflection | Not included | Required |

**The completed code does NOT include the written portions** — those are entirely the students' work. The code is only the implementation answer key.

**Gotcha on TODO completeness:** The student lab file marks TODO 5 (simulation runner) as something to complete, but the runner loop body is already written in the student file — students just need to make sure they understand it and don't accidentally delete it. This is the one "TODO" that is basically already done. Consider clarifying this verbally at the start of lab.

---

## 4. Common Student Gotchas (Quick Reference)

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `ModuleNotFoundError: matplotlib` | Wrong kernel selected | Switch to COMP 469 (.env) kernel |
| Dirty squares always 0 | TODO 2 still returns `"Clean"` by default | Add `random.random() < dirt_probability` check |
| Obstacles always 0 | TODO 1 condition is `if False:` | Replace with obstacle probability check |
| Agent moves in wrong direction | Coordinate system inverted (`Up = y+1`) | `Up` decrements y (row index) |
| Score never increases | Forgot `self.score += 10` in Suck | Check TODO 3 |
| BFS returns wrong path | Forgot to add start to `visited` before loop | `visited = {start}` before `while frontier:` |
| Model agent oscillates | Basic fallback with no backtracking | Acceptable — document in Checkpoint 3 |
| `ReflexVacuumAgent` has `self.visited` | Student made it model-based by mistake | Conceptual correction needed |
| Notebook crashes on goal-based cell | BFS is empty (returns `[]` → NoOp → no crash, just no cleaning) | Actually should not crash; check environment cells if it does |
| `evaluate_agents` gives identical results per agent | Students created a new env per agent instead of using `load_world` | Explain the copy/load mechanism |

---

## 5. Grading Rubric Suggestions

| Component | Points |
|-----------|--------|
| Environment (TODOs 1–4 working, smoke test passes) | 20 |
| Reflex agent — deterministic rule, no memory | 15 |
| Model-based agent — uses `self.visited`, reasonable fallback | 15 |
| Goal-based agent — correct BFS | 20 |
| Controlled experiments run, summary visible | 10 |
| Two plots visible and labeled | 5 |
| Checkpoints 1–5 answered with AIMA vocabulary | 10 |
| Final reflection paragraph | 5 |
| **Total** | **100** |

**Optional bonus (5 pts):** Extension option completed and explained.

**Zero tolerance:** Submitting the completed instructor code. PEAS tables left as "TODO".

---

## 6. Timing Guide (3-Hour Lab)

| Time | Activity |
|------|----------|
| 0:00–0:15 | Environment setup / kernel verification |
| 0:15–0:30 | Lecture: agent types, PEAS, environment properties |
| 0:30–0:50 | Section 2: PEAS table (individual or pairs) |
| 0:50–1:30 | Section 3: Environment TODOs 1–4 + smoke test |
| 1:30–1:45 | Sections 4–6: Visualization, agent interface, runner (mostly reading) |
| 1:45–2:05 | Section 7: Reflex agent (TODO 6) + Checkpoint 2 |
| 2:05–2:25 | Section 8: Model-based agent (TODOs 7–8) + Checkpoint 3 |
| 2:25–2:45 | Section 9: BFS (TODO 9) + Checkpoint 4 |
| 2:45–2:55 | Sections 10–11: Experiments + plots + Checkpoint 5 |
| 2:55–3:00 | Final reflection |

**Buffer note:** Most students will not reach the extensions in 3 hours. The BFS section (Section 9) is where they often slow down — plan to spend extra facilitation time there.
