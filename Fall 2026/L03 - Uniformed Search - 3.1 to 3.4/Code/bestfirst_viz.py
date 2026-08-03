"""
====================================================================
COMP 469 - Introduction to Artificial Intelligence  (CSU Channel Islands)
Best-First Search Visualizer
Faithful to Russell & Norvig, AIMA 4th ed., Figure 3.7
====================================================================

The point of this module is NOT to be a fast search library. It is to make
every line of Figure 3.7 observable:

    - which node is popped, and why (its f-value was minimum)
    - what the frontier looks like at every iteration
    - what the `reached` table remembers, and when it changes
    - exactly when a child is added, re-added (better path found), or pruned
    - the difference between the STATE GRAPH and the SEARCH TREE

Breadth-first, uniform-cost, depth-first, depth-limited and iterative
deepening all use the SAME best-first framework with a different evaluation
function f (and, for the last two, a depth cutoff). That is the central idea
of AIMA section 3.3.1 and this module is built to make students feel it
rather than just read it.

Determinism
-----------
Everything is seeded. The same command produces the same trace on your
laptop, on the classroom machine, and in the handout you print. Use
`--seed N` to change it, `--random-costs` to replace the real Romania road
distances with randomized ones.

Usage
-----
    python3 bestfirst_viz.py                       # all static demos, writes PNGs
    python3 bestfirst_viz.py --demo compare        # metrics table
    python3 bestfirst_viz.py --demo romania        # Romania contact sheets
    python3 bestfirst_viz.py --demo grid           # maze comparison
    python3 bestfirst_viz.py --demo tree           # classroom tree contact sheets

    python3 bestfirst_viz.py --demo explore-tree     # interactive window (tree)
    python3 bestfirst_viz.py --demo explore-romania  # interactive window (Romania)

    python3 bestfirst_viz.py --demo explore-tree --big   # lecture-hall font sizes

Interactive window controls
---------------------------
    Right arrow / Left arrow  step forward / back
    Home / End                first / last iteration
    Space                     play / pause
    1..5                      switch search strategy
    r                         restart current strategy
    [ and ]                   lower / raise L (Depth-limited only)

Run from Windows PowerShell:
    cd "C:\\path\\to\\Code"
    py -m pip install matplotlib
    py bestfirst_viz.py --demo explore-tree

Run from macOS Terminal:
    cd "/path/to/Code"
    python3 -m pip install matplotlib
    python3 bestfirst_viz.py --demo explore-tree

In Jupyter:
    from bestfirst_viz import *
    p = romania_problem('Arad', 'Bucharest')
    node, trace = best_first_search(p, f_uniform_cost(p))
    print_trace(trace)
    plot_search_panels(p, trace, title="Uniform-cost search on Romania")
"""

from __future__ import annotations

import argparse
import heapq
import itertools
import math
import random
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterator

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import FancyBboxPatch, Patch, PathPatch
from matplotlib.widgets import Button

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# ====================================================================
# PART 0 - Reproducibility and presentation settings
# ====================================================================

DEFAULT_SEED = 469
SEED = DEFAULT_SEED

# Global font multiplier. `--big` raises it so the figure survives a
# lecture-hall projector.
SCALE = 1.0


def set_seed(seed: int) -> None:
    """Set the seed used by every randomized problem generator."""
    global SEED
    SEED = seed


def set_scale(scale: float) -> None:
    global SCALE
    SCALE = scale


def fs(size: float) -> float:
    """Scaled font size."""
    return size * SCALE


# Palette chosen to stay distinguishable under the common forms of color
# vision deficiency (Okabe-Ito based). Shape is used as a redundant channel,
# so the figure still reads correctly in grayscale printouts.
C_UNSEEN = "#e6e6e9"
C_FRONTIER = "#0072b2"   # blue   - square marker
C_EXPANDED = "#9a9a9a"   # grey   - circle marker
C_CURRENT = "#d55e00"    # orange-red - star marker
C_PATH = "#009e73"       # green
C_START = "#56b4e9"
C_GOAL = "#cc79a7"
C_DISCARD = "#ffffff"    # generated then thrown away (dashed outline)
C_INK = "#111827"
C_RULE = "#d1d5db"

MARKER = {
    "current": "*",
    "frontier": "s",
    "expanded": "o",
    "path": "o",
    "unseen": "o",
    "discarded": "X",
}


def set_window_title(fig, title="COMP 469 - CSU Channel Islands"):
    """Set the title shown in the desktop window's title bar."""
    manager = getattr(fig.canvas, "manager", None)
    if manager is not None and hasattr(manager, "set_window_title"):
        manager.set_window_title(title)


def add_figure_curly_brace(fig, x, y0, y1, width=0.018, linewidth=2.0,
                           color="#777777"):
    """Draw a thin, resize-safe left curly brace in figure coordinates."""
    if y1 <= y0:
        raise ValueError("y1 must be greater than y0")

    height = y1 - y0
    middle = (y0 + y1) / 2.0
    x_right = x + width
    x_inner = x + width * 0.18
    x_left = x - width * 0.35
    upper_shoulder = middle + height * 0.13
    lower_shoulder = middle - height * 0.13

    vertices = [
        (x_right, y1),
        (x_inner, y1), (x_inner, middle + height * 0.30), (x_inner, upper_shoulder),
        (x_inner, middle + height * 0.06), (x_left, middle + height * 0.035), (x_left, middle),
        (x_left, middle - height * 0.035), (x_inner, middle - height * 0.06), (x_inner, lower_shoulder),
        (x_inner, middle - height * 0.30), (x_inner, y0), (x_right, y0),
    ]
    codes = [MplPath.MOVETO] + [MplPath.CURVE4] * 12

    patch = PathPatch(
        MplPath(vertices, codes), transform=fig.transFigure, fill=False,
        edgecolor=color, linewidth=linewidth, capstyle="round",
        joinstyle="round", clip_on=False, zorder=10,
    )
    fig.add_artist(patch)
    return patch


# ====================================================================
# PART 1 - The data structures named in Figure 3.7
# ====================================================================


class Node:
    """A node in the search TREE.

    Careful, students: a Node is not a state. A state is a place
    (e.g. 'Sibiu'). A Node is one particular path that arrives at that
    place, together with its cost. The same state can appear in many
    different nodes. The search-tree panel in the interactive window exists
    entirely to make that sentence visible.

    `verdict` records what BEST-FIRST-SEARCH decided about this node at the
    moment it was generated: NEW, BETTER, PRUNED, CYCLE or CUTOFF. It is
    instrumentation only - the algorithm never reads it.
    """

    __slots__ = ("state", "parent", "action", "path_cost", "verdict")

    def __init__(self, state, parent=None, action=None, path_cost=0.0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost  # this is g(n)
        self.verdict = "ROOT"

    def __repr__(self):
        return f"<{self.state} g={self.path_cost:g}>"

    def path(self) -> list["Node"]:
        """Nodes from the root down to this node."""
        node, back = self, []
        while node:
            back.append(node)
            node = node.parent
        return list(reversed(back))

    def solution(self) -> list:
        """The sequence of states from initial to here."""
        return [n.state for n in self.path()]

    def depth(self) -> int:
        d, node = 0, self.parent
        while node:
            d += 1
            node = node.parent
        return d


FAILURE = Node("failure", path_cost=math.inf)
CUTOFF = Node("cutoff", path_cost=math.inf)


class PriorityQueue:
    """`frontier <- a priority queue ordered by f`

    Implemented with a binary heap. The insertion counter keeps ordering
    deterministic among equal f-values, which matters a great deal when you
    want a whole class to reproduce the same trace.

    `tiebreak` controls what happens on ties:
        "fifo" - oldest first. This is what makes f = depth behave exactly
                 like textbook breadth-first search.
        "lifo" - newest first. This is what makes f = -depth behave like
                 textbook depth-first search, which backtracks into the most
                 recently generated branch. Without it you get a
                 "deepest-first" search whose trace does not match the DFS
                 students draw by hand.

    Note (worth five minutes of lecture): Figure 3.7 says "add child to
    frontier" without removing the older, worse entry for that state. So the
    frontier can hold stale duplicates. That is fine for correctness, because
    `reached` is the source of truth and any stale pop is discarded by the
    `reached` check on re-expansion. We keep the pseudocode's literal
    behavior and draw the stale entries with hatching so students can see
    them.
    """

    def __init__(self, f: Callable[[Node], float], tiebreak: str = "fifo"):
        if tiebreak not in ("fifo", "lifo"):
            raise ValueError("tiebreak must be 'fifo' or 'lifo'")
        self.f = f
        self.tiebreak = tiebreak
        self.heap: list[tuple[float, int, Node]] = []
        self._counter = itertools.count()
        self.max_size = 0

    def add(self, node: Node) -> None:
        order = next(self._counter)
        key = order if self.tiebreak == "fifo" else -order
        heapq.heappush(self.heap, (self.f(node), key, node))
        self.max_size = max(self.max_size, len(self.heap))

    def pop(self) -> Node:
        return heapq.heappop(self.heap)[2]

    def top(self) -> Node:
        return self.heap[0][2]

    def __len__(self) -> int:
        return len(self.heap)

    def __bool__(self) -> bool:
        return bool(self.heap)

    def sorted_items(self) -> list[tuple[float, Node]]:
        """Frontier contents in true pop order - for display only."""
        return [(pri, node) for pri, _, node in sorted(self.heap, key=lambda t: t[:2])]

    def stale_count(self, reached: dict | None) -> int:
        if not reached:
            return 0
        return sum(1 for _, _, n in self.heap if reached.get(n.state) is not n)


# ====================================================================
# PART 2 - Problem interface (AIMA section 3.1)
# ====================================================================


class Problem:
    """Subclass and override actions/result/action_cost as needed."""

    def __init__(self, initial, goal=None):
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        raise NotImplementedError

    def result(self, state, action):
        raise NotImplementedError

    def is_goal(self, state) -> bool:
        return state == self.goal

    def action_cost(self, s, action, s_prime) -> float:
        return 1.0


class GraphProblem(Problem):
    """Route finding on an undirected weighted graph."""

    def __init__(self, initial, goal, graph: dict, locations: dict):
        super().__init__(initial, goal)
        self.graph = graph
        self.locations = locations

    def actions(self, state):
        return sorted(self.graph[state])  # sorted => deterministic traces

    def result(self, state, action):
        return action  # action == "go to that city"

    def action_cost(self, s, action, s_prime) -> float:
        return self.graph[s][s_prime]


class MultiGoalGraphProblem(GraphProblem):
    """Graph problem that succeeds when it reaches any goal state."""

    def __init__(self, initial, goals, graph, locations):
        super().__init__(initial, None, graph, locations)
        self.goals = set(goals)

    def is_goal(self, state) -> bool:
        return state in self.goals


class GridProblem(Problem):
    """4-connected grid with walls for comparing search strategies.

    Action costs are randomized but SEEDED, so the same maze with the same
    seed always produces the same numbers. That is what makes the three
    strategies genuinely comparable: they must all solve the identical
    problem instance.
    """

    def __init__(self, grid: list[str], initial=None, goal=None, seed: int | None = None):
        self.grid = [list(row) for row in grid]
        rng = random.Random(SEED if seed is None else seed)
        self.edge_costs = {}
        self.rows, self.cols = len(self.grid), len(self.grid[0])
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == "S":
                    initial = initial or (r, c)
                elif self.grid[r][c] == "G":
                    goal = goal or (r, c)
        super().__init__(initial, goal)
        for r in range(self.rows):
            for c in range(self.cols):
                if self.blocked(r, c):
                    continue
                for dr, dc in ((1, 0), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if not self.blocked(nr, nc):
                        cost = rng.randint(1, 9)
                        self.edge_costs[((r, c), (nr, nc))] = cost
                        self.edge_costs[((nr, nc), (r, c))] = cost

    def blocked(self, r, c) -> bool:
        return not (0 <= r < self.rows and 0 <= c < self.cols) or self.grid[r][c] == "#"

    def actions(self, state):
        r, c = state
        moves = [("up", -1, 0), ("down", 1, 0), ("left", 0, -1), ("right", 0, 1)]
        return [name for name, dr, dc in moves if not self.blocked(r + dr, c + dc)]

    def result(self, state, action):
        r, c = state
        return {"up": (r - 1, c), "down": (r + 1, c),
                "left": (r, c - 1), "right": (r, c + 1)}[action]

    def action_cost(self, s, action, s_prime) -> float:
        return self.edge_costs[(s, s_prime)]


# ====================================================================
# PART 3 - BEST-FIRST-SEARCH  (Figure 3.7, line for line)
# ====================================================================


@dataclass
class Step:
    """One full pass through the while-loop, recorded for replay."""

    i: int
    popped: Node
    priority: float
    is_goal: bool
    children: list[tuple[Node, str]] = field(default_factory=list)
    frontier_nodes: list[tuple[float, Node]] = field(default_factory=list)
    reached_snapshot: dict = field(default_factory=dict)   # state -> g
    changed_states: list = field(default_factory=list)     # reached entries touched here
    stale_in_frontier: int = 0
    stale_ids: set = field(default_factory=set)
    depth_limit: int | None = None
    cutoff_here: bool = False
    stale_pop: bool = False
    detail: bool = True

    # Cheap counters, always recorded.
    frontier_size: int = 0
    reached_size: int = 0
    expanded_count: int = 0
    generated_count: int = 0

    # Shared references to the search's own growing lists. Storing a copy per
    # step was quadratic: on the maze it allocated gigabytes before the run
    # finished. Each step keeps a pointer plus a length instead.
    _expanded_all: list = field(default_factory=list, repr=False)
    _generated_all: list = field(default_factory=list, repr=False)

    @property
    def expanded_nodes(self) -> list[Node]:
        return self._expanded_all[: self.expanded_count]

    @property
    def generated_nodes(self) -> list[Node]:
        return self._generated_all[: self.generated_count]

    # Convenience views kept for backward compatibility with older notebooks.
    @property
    def frontier_after(self) -> list[tuple[float, Any]]:
        return [(p, n.state) for p, n in self.frontier_nodes]

    @property
    def reached_after(self) -> list:
        return list(self.reached_snapshot)

    @property
    def expanded_so_far(self) -> list:
        return [n.state for n in self.expanded_nodes]


def expand(problem: Problem, node: Node) -> Iterator[Node]:
    """function EXPAND(problem, node) yields nodes"""
    s = node.state
    for action in problem.actions(s):
        s_prime = problem.result(s, action)
        cost = node.path_cost + problem.action_cost(s, action, s_prime)
        yield Node(state=s_prime, parent=node, action=action, path_cost=cost)


def is_cycle(node: Node) -> bool:
    """AIMA IS-CYCLE: does this node's state already appear on its own path?"""
    seen, walker = set(), node.parent
    while walker:
        seen.add(walker.state)
        walker = walker.parent
    return node.state in seen


def best_first_search(problem: Problem, f: Callable[[Node], float], *,
                      tiebreak: str = "fifo", depth_limit: int | None = None,
                      tree_like: bool = False, dominance: str = "path-cost",
                      detail_steps: int = 400, max_steps: int = 20_000):
    """function BEST-FIRST-SEARCH(problem, f) returns a solution node or failure

    Returns (solution_node_or_FAILURE_or_CUTOFF, trace).

    The search logic below is unmodified pseudocode; every `trace` /
    `expanded` / `verdict` line is pure instrumentation and can be deleted
    without changing behavior.

    Three optional switches turn this into the other strategies in the
    lecture, without introducing a second algorithm:

    depth_limit
        Refuse to expand any node at or beyond this depth and report CUTOFF.
        This is depth-limited search (AIMA Figure 3.12).

    tree_like
        Drop the `reached` table entirely and use IS-CYCLE on the path
        instead. This is the tree-like search of AIMA section 3.3.3, and it
        is what depth-limited and iterative-deepening search actually use.
        It matters: with a `reached` table, a state first discovered on a
        deep, cheap path can permanently block the shallow path that a
        depth-limited search needs to find.

    dominance
        Which value the `reached` test compares.

        "path-cost" is literally what Figure 3.7 prints: keep the child if
        its g is lower. That is the right test when f = g, and it is the
        wrong test for every other f. With f = depth, a state already
        reached shallowly gets re-added and RE-EXPANDED whenever some deeper
        path turns out to be cheaper. On the maze this makes "breadth-first"
        expand ten times more nodes than the maze has cells.

        "priority" compares f instead, which is the correct dominance test
        for whatever f you actually chose, and makes f = depth behave like
        the breadth-first search students draw by hand.

        Run demo_reexpansion() to show both numbers side by side. This is
        the reason AIMA gives breadth-first its own pseudocode in Figure 3.9
        instead of leaving it as a call to BEST-FIRST-SEARCH.
    """
    if dominance not in ("path-cost", "priority"):
        raise ValueError("dominance must be 'path-cost' or 'priority'")
    key = (lambda n: n.path_cost) if dominance == "path-cost" else f
    node = Node(state=problem.initial)                      # node <- NODE(STATE=problem.INITIAL)
    frontier = PriorityQueue(f, tiebreak)                   # frontier <- a priority queue ordered by f
    frontier.add(node)                                      #   ...with node as an element
    reached = None if tree_like else {problem.initial: node}

    trace: list[Step] = []
    expanded: list[Node] = []
    generated: list[Node] = [node]
    cutoff_seen = False
    i = 0

    while frontier:                                         # while not IS-EMPTY(frontier) do
        node = frontier.pop()                               #   node <- POP(frontier)
        i += 1
        step = Step(i=i, popped=node, priority=f(node),
                    is_goal=problem.is_goal(node.state),
                    depth_limit=depth_limit)
        if reached is not None:
            step.stale_pop = reached.get(node.state) is not node

        if problem.is_goal(node.state):                     #   if problem.IS-GOAL(node.STATE)
            expanded.append(node)
            _record(step, frontier, reached, expanded, generated)
            if trace and i > detail_steps:
                _demote(trace[-1])
            trace.append(step)
            return node, trace                              #     then return node

        expanded.append(node)

        if depth_limit is not None and node.depth() >= depth_limit:
            step.cutoff_here = True
            cutoff_seen = True
            _record(step, frontier, reached, expanded, generated)
            if trace and i > detail_steps:
                _demote(trace[-1])
            trace.append(step)
            if i >= max_steps:
                break
            continue

        for child in expand(problem, node):                 #   for each child in EXPAND(problem, node)
            s = child.state                                 #     s <- child.STATE
            generated.append(child)

            if tree_like:
                if is_cycle(child):
                    child.verdict = "CYCLE (state already on this path)"
                else:
                    child.verdict = "NEW"
                    frontier.add(child)
                step.children.append((child, child.verdict))
                continue

            if s not in reached:                            #     if s is not in reached
                reached[s] = child                          #       reached[s] <- child
                frontier.add(child)                         #       add child to frontier
                child.verdict = "NEW"
                step.changed_states.append(s)
            elif key(child) < key(reached[s]):              #     or child.PATH-COST < reached[s].PATH-COST
                old = key(reached[s])
                reached[s] = child                          #       reached[s] <- child
                frontier.add(child)                         #       add child to frontier
                child.verdict = f"BETTER ({old:g} -> {key(child):g})"
                step.changed_states.append(s)
            else:
                child.verdict = f"PRUNED (have {key(reached[s]):g})"
            step.children.append((child, child.verdict))

        _record(step, frontier, reached, expanded, generated)
        if trace and i > detail_steps:
            _demote(trace[-1])
        trace.append(step)

        if i >= max_steps:
            break

    return (CUTOFF if cutoff_seen else FAILURE), trace      # return cutoff / failure


def _record(step: Step, frontier: PriorityQueue, reached, expanded, generated) -> None:
    """Snapshot everything the visualizer needs. Instrumentation only."""
    step.frontier_size = len(frontier)
    step.reached_size = len(reached) if reached is not None else 0
    step._expanded_all = expanded
    step.expanded_count = len(expanded)
    step._generated_all = generated
    step.generated_count = len(generated)
    step.stale_in_frontier = frontier.stale_count(reached)
    step.frontier_nodes = frontier.sorted_items()
    step.reached_snapshot = ({s: n.path_cost for s, n in reached.items()}
                             if reached is not None else {})
    step.stale_ids = ({id(n) for _, n in step.frontier_nodes
                       if reached.get(n.state) is not n}
                      if reached is not None else set())


def _demote(step: Step) -> None:
    """Drop the heavy per-step snapshots once we are past the detail window.

    Keeps the counters, so the metrics table stays exact. The visualizers only
    ever draw the early steps (contact sheets, the interactive window) or the
    final step (the maze comparison), and both of those keep full detail.
    """
    step.frontier_nodes = []
    step.reached_snapshot = {}
    step.stale_ids = set()
    step.detail = False


# ====================================================================
# PART 4 - The search algorithms are ONE algorithm with different f's
# ====================================================================


def f_breadth_first(problem):
    """f(n) = depth  ->  breadth-first search"""
    return lambda n: n.depth()


def f_uniform_cost(problem):
    """f(n) = g(n)  ->  uniform-cost / Dijkstra"""
    return lambda n: n.path_cost


def f_depth_first(problem):
    """f(n) = -depth  ->  depth-first search (pair with tiebreak='lifo')"""
    return lambda n: -n.depth()


@dataclass
class Strategy:
    """One row of the lecture: a name, an f, and the settings it needs."""

    name: str
    formula: str
    blurb: str
    note: str
    make_f: Callable
    tiebreak: str = "fifo"
    depth_limit: int | None = None
    tree_like: bool = False
    iterative: bool = False
    dominance: str = "path-cost"


STRATEGIES: dict[str, Strategy] = {
    "Breadth-first": Strategy(
        name="Breadth-first",
        formula="f(n) = depth(n)",
        blurb="Pop the shallowest frontier node first.",
        note=("A minimum-priority queue ordered by depth pops nodes tier by "
              "tier. Ties are broken oldest-first, which is exactly the FIFO "
              "queue in the textbook. Optimal only when every action costs "
              "the same."),
        make_f=f_breadth_first,
        tiebreak="fifo",
    ),
    "Uniform-cost": Strategy(
        name="Uniform-cost",
        formula="f(n) = g(n)",
        blurb="Pop the lowest accumulated path cost first.",
        note=("g(n) is the total action cost from the start to n. Popping the "
              "cheapest node first is Dijkstra's algorithm. This is the only "
              "strategy here that is guaranteed to return a cheapest path."),
        make_f=f_uniform_cost,
        tiebreak="fifo",
    ),
    "Depth-first": Strategy(
        name="Depth-first",
        formula="f(n) = -depth(n)",
        blurb="Pop the deepest available frontier node first.",
        note=("Depth 0 gives priority 0, depth 1 gives -1, depth 2 gives -2. "
              "Since -2 < -1, a minimum queue pops the deepest node. The "
              "negative sign is not a cost and not an error. Ties are broken "
              "newest-first, which reproduces the LIFO stack of the textbook "
              "version. Uses no extra memory beyond the current path, but is "
              "neither complete nor optimal in general."),
        make_f=f_depth_first,
        tiebreak="lifo",
    ),
    "Depth-limited": Strategy(
        name="Depth-limited",
        formula="f(n) = -depth(n), cut off at depth L",
        blurb="Depth-first, but never expand past the limit.",
        note=("Nodes at the limit are popped and goal-tested, then discarded "
              "without being expanded. If any node was cut off and no goal "
              "was found, the result is CUTOFF, which is different from "
              "FAILURE: cutoff means 'maybe deeper', failure means 'not "
              "anywhere'. Runs tree-like, with a cycle check on the current "
              "path instead of a reached table."),
        make_f=f_depth_first,
        tiebreak="lifo",
        depth_limit=2,
        tree_like=True,
    ),
    "Iterative deepening": Strategy(
        name="Iterative deepening",
        formula="depth-limited with L = 0, 1, 2, ...",
        blurb="Repeat depth-limited search with a growing limit.",
        note=("Each restart throws away everything and searches again one "
              "level deeper. That sounds wasteful, but the last level "
              "dominates the node count, so the repeated work is a constant "
              "factor. It buys breadth-first's shallowest-goal guarantee at "
              "depth-first's memory cost. Watch the step counter reset when "
              "the limit increases."),
        make_f=f_depth_first,
        tiebreak="lifo",
        tree_like=True,
        iterative=True,
    ),
}

# The three strategies that share one framework with no extra machinery.
CORE_STRATEGIES = ["Breadth-first", "Uniform-cost", "Depth-first"]

# Kept so existing notebooks that import ALGORITHMS still work.
ALGORITHMS = {
    "Breadth-First  f = depth": f_breadth_first,
    "Uniform-Cost   f = g": f_uniform_cost,
    "Depth-First    f = -depth": f_depth_first,
}


def run_strategy(strategy: Strategy, problem: Problem, max_depth: int = 14):
    """Run one strategy on one problem. Returns (result_node, trace)."""
    if not strategy.iterative:
        return best_first_search(
            problem, strategy.make_f(problem),
            tiebreak=strategy.tiebreak,
            depth_limit=strategy.depth_limit,
            tree_like=strategy.tree_like,
            dominance=strategy.dominance,
        )

    combined: list[Step] = []
    for limit in range(max_depth + 1):
        node, trace = best_first_search(
            problem, strategy.make_f(problem),
            tiebreak=strategy.tiebreak, depth_limit=limit, tree_like=True,
        )
        for step in trace:
            step.depth_limit = limit
            step.i += len(combined)
        combined.extend(trace)
        if node is not FAILURE and node is not CUTOFF:
            return node, combined
        if node is FAILURE:
            # Exhausted the whole reachable space with no cutoff: deeper
            # limits cannot help.
            return FAILURE, combined
    return CUTOFF, combined


# ====================================================================
# PART 5 - Text trace and metrics
# ====================================================================


def print_trace(trace: list[Step], max_steps: int | None = None, width: int = 78) -> None:
    print("=" * width)
    print(f"{'BEST-FIRST-SEARCH trace':^{width}}")
    print("=" * width)
    last_limit = object()
    for step in trace[: max_steps or len(trace)]:
        if step.depth_limit != last_limit:
            last_limit = step.depth_limit
            if step.depth_limit is not None:
                print(f"\n--- depth limit L = {step.depth_limit} ---")
        tag = "  <-- GOAL, return this node" if step.is_goal else ""
        if step.cutoff_here:
            tag = "  <-- at depth limit, not expanded (CUTOFF)"
        print(f"\nIteration {step.i}")
        print(f"  POP  -> {step.popped.state}   (f = {step.priority:g}, "
              f"g = {step.popped.path_cost:g}, depth = {step.popped.depth()}){tag}")
        if step.stale_pop:
            print("  (this was a stale duplicate; reached already holds a better node)")
        if step.is_goal:
            print(f"  path : {' -> '.join(str(s) for s in step.popped.solution())}")
            print(f"  cost : {step.popped.path_cost:g}")
            break
        for child, verdict in step.children:
            print(f"      child {str(child.state):<16} g={child.path_cost:<7g} {verdict}")
        front = ", ".join(f"{s}({p:g})" for p, s in step.frontier_after[:8])
        more = "" if len(step.frontier_after) <= 8 else f", ... (+{len(step.frontier_after) - 8})"
        print(f"  frontier: [{front}{more}]")
        if step.stale_in_frontier:
            print(f"  ({step.stale_in_frontier} stale duplicate(s) sitting in the frontier)")
    print("\n" + "=" * width)


def metrics(node: Node, trace: list[Step]) -> dict:
    """The four numbers AIMA compares strategies on, plus the answer."""
    solved = node is not FAILURE and node is not CUTOFF
    expansions = sum(1 for s in trace if not s.is_goal and not s.cutoff_here)
    # Iterative deepening restarts the search, so each restart has its own
    # generated-node list. Sum them, or the total under-reports the repeated
    # work that is the whole point of the strategy.
    per_run: dict[int, int] = {}
    for st in trace:
        per_run[id(st._generated_all)] = st.generated_count
    generated = sum(per_run.values())
    peak_frontier = max((s.frontier_size for s in trace), default=0)
    return {
        "found": solved,
        "result": "solution" if solved else ("cutoff" if node is CUTOFF else "failure"),
        "cost": node.path_cost if solved else math.inf,
        "depth": node.depth() if solved else -1,
        "expansions": expansions,
        "generated": generated,
        "peak_frontier": peak_frontier,
        "path": node.solution() if solved else [],
    }


def comparison_table(problem: Problem, names: list[str] | None = None) -> list[dict]:
    """Compare strategies on ONE problem instance.

    This used to build a fresh randomized problem per algorithm, which meant
    the columns were not comparable at all. Every strategy now solves the
    identical instance.
    """
    names = names or CORE_STRATEGIES
    rows = []
    print(f"\n{'Strategy':<22}{'Cost':>8}{'Depth':>7}{'Expand':>8}"
          f"{'Gener.':>8}{'Peak fr.':>10}   Path")
    print("-" * 108)
    for name in names:
        node, trace = run_strategy(STRATEGIES[name], problem)
        m = metrics(node, trace)
        m["strategy"] = name
        rows.append(m)
        path = " -> ".join(str(s) for s in m["path"]) or f"({m['result']})"
        if len(path) > 42:
            path = path[:39] + "..."
        cost = f"{m['cost']:g}" if m["found"] else "inf"
        print(f"{name:<22}{cost:>8}{m['depth']:>7}{m['expansions']:>8}"
              f"{m['generated']:>8}{m['peak_frontier']:>10}   {path}")
    print("-" * 108)
    print("Expand = nodes expanded. Gener. = nodes created. Peak fr. = largest frontier.")
    print("All strategies solved the same instance with the same action costs.\n")
    return rows


# ====================================================================
# PART 6 - Visualization
# ====================================================================


def _node_status(node: Node, step: Step, frontier_ids: set, expanded_ids: set,
                 stale_ids: set) -> str:
    if node is step.popped:
        return "current"
    if id(node) in frontier_ids:
        return "stale" if id(node) in stale_ids else "frontier"
    if id(node) in expanded_ids:
        return "expanded"
    if node.verdict.startswith(("PRUNED", "CYCLE")):
        return "discarded"
    return "superseded"


def _step_index_sets(step: Step):
    frontier_ids = {id(n) for _, n in step.frontier_nodes}
    expanded_ids = {id(n) for n in step.expanded_nodes}
    return frontier_ids, expanded_ids, set(step.stale_ids)


# --------------------------------------------------------------------
# 6a. The state graph
# --------------------------------------------------------------------


def draw_state_graph(ax, problem: GraphProblem, step: Step, show_costs=True,
                     show_f=True, title=True):
    """The map. Cities are STATES; each city appears exactly once."""
    ax.clear()
    ax.set_facecolor("#fbfcfe")

    frontier_values: dict = {}
    for priority, state in step.frontier_after:
        frontier_values.setdefault(state, priority)

    expanded_states = set(step.expanded_so_far)
    path_nodes = step.popped.path()
    path_states = {n.state for n in path_nodes}
    path_edges = {frozenset((a.state, b.state)) for a, b in zip(path_nodes, path_nodes[1:])}

    drawn = set()
    for city, neighbors in problem.graph.items():
        for neighbor, cost in neighbors.items():
            key = frozenset((city, neighbor))
            if key in drawn:
                continue
            drawn.add(key)
            (x1, y1), (x2, y2) = problem.locations[city], problem.locations[neighbor]
            on_path = key in path_edges
            ax.plot([x1, x2], [y1, y2],
                    color=C_PATH if on_path else C_RULE,
                    linewidth=3.4 if on_path else 1.2, zorder=1)
            if show_costs:
                ax.text((x1 + x2) / 2, (y1 + y2) / 2, f"{cost:g}",
                        fontsize=fs(6.8), color="#4b5563", ha="center", va="center",
                        bbox={"facecolor": "#ffffff", "edgecolor": C_RULE,
                              "linewidth": 0.4, "alpha": 0.95,
                              "boxstyle": "round,pad=0.12"},
                        zorder=2)

    groups: dict[str, list] = {}
    for city, (x, y) in problem.locations.items():
        if city == step.popped.state:
            key = "current"
        elif city in path_states:
            key = "path"
        elif city in frontier_values:
            key = "frontier"
        elif city in expanded_states:
            key = "expanded"
        elif city == problem.initial:
            key = "start"
        elif problem.goal is not None and city == problem.goal:
            key = "goal"
        else:
            key = "unseen"
        groups.setdefault(key, []).append((x, y))

    style = {
        "current": (C_CURRENT, 420, "*"),
        "path": (C_PATH, 170, "o"),
        "frontier": (C_FRONTIER, 165, "s"),
        "expanded": (C_EXPANDED, 140, "o"),
        "start": (C_START, 160, "o"),
        "goal": (C_GOAL, 160, "o"),
        "unseen": (C_UNSEEN, 95, "o"),
    }
    for key, pts in groups.items():
        color, size, marker = style[key]
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=size, c=color,
                   marker=marker, edgecolors="#374151", linewidths=1.0, zorder=4)

    for city, (x, y) in problem.locations.items():
        lines = [str(city)]
        if show_f and city in frontier_values:
            lines.append(f"f={frontier_values[city]:g}")
        if city == problem.initial:
            lines.append("START")
        if problem.goal is not None and city == problem.goal:
            lines.append("GOAL")
        bold = city in {problem.initial, problem.goal, step.popped.state}
        ax.annotate("\n".join(lines), (x, y), xytext=(0, 12),
                    textcoords="offset points", ha="center", va="bottom",
                    fontsize=fs(7.6), color=C_INK,
                    fontweight="bold" if bold else "normal", zorder=5)

    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        head = "GOAL FOUND" if step.is_goal else f"pop {step.popped.state}"
        ax.set_title(f"STATE GRAPH - step {step.i}: {head}", fontsize=fs(10.5), color=C_INK)


# Kept under the old name so existing lecture notebooks keep running.
def draw_graph_step(ax, problem: GraphProblem, step: Step, show_labels=True):
    draw_state_graph(ax, problem, step, show_costs=False, show_f=show_labels)


# --------------------------------------------------------------------
# 6b. The search tree - the panel that teaches "a node is not a state"
# --------------------------------------------------------------------


def _layout_search_tree(root: Node, nodes: list[Node]):
    """Assign (x, y) to every generated node. Leaves get consecutive x."""
    children: dict[int, list[Node]] = {}
    for n in nodes:
        if n.parent is not None:
            children.setdefault(id(n.parent), []).append(n)

    pos: dict[int, tuple[float, float]] = {}
    counter = itertools.count()

    stack = [(root, False)]
    while stack:
        node, processed = stack.pop()
        kids = children.get(id(node), [])
        if not kids:
            pos[id(node)] = (next(counter), -node.depth())
            continue
        if processed:
            xs = [pos[id(k)][0] for k in kids]
            pos[id(node)] = (sum(xs) / len(xs), -node.depth())
        else:
            stack.append((node, True))
            for kid in reversed(kids):
                stack.append((kid, False))
    return pos, children


def draw_search_tree(ax, step: Step, max_nodes: int = 260, title=True):
    """The search tree so far. Every generated NODE gets its own box.

    A city that was reached three different ways appears three times here and
    once on the map. That contrast is the whole lesson.
    """
    ax.clear()
    ax.set_facecolor("#ffffff")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor(C_RULE)

    nodes = step.generated_nodes
    if not nodes:
        return
    if len(nodes) > max_nodes:
        ax.text(0.5, 0.5, f"search tree has {len(nodes)} nodes\n(too many to draw)",
                ha="center", va="center", transform=ax.transAxes,
                fontsize=fs(9), color="#6b7280")
        return

    root = nodes[0]
    pos, children = _layout_search_tree(root, nodes)
    frontier_ids, expanded_ids, stale_ids = _step_index_sets(step)

    for node in nodes:
        if node.parent is None or id(node) not in pos or id(node.parent) not in pos:
            continue
        x1, y1 = pos[id(node.parent)]
        x2, y2 = pos[id(node)]
        discarded = node.verdict.startswith(("PRUNED", "CYCLE"))
        ax.plot([x1, x2], [y1, y2],
                color="#c9ccd1" if discarded else "#8b8f96",
                linestyle=":" if discarded else "-",
                linewidth=1.0, zorder=1)

    fill = {
        "current": C_CURRENT, "frontier": C_FRONTIER, "expanded": C_EXPANDED,
        "discarded": C_DISCARD, "superseded": "#f1f2f4", "stale": C_FRONTIER,
    }
    n_label = max(1, len(nodes))
    label_size = fs(max(4.6, min(8.0, 90.0 / math.sqrt(n_label) * 0.9)))

    for node in nodes:
        if id(node) not in pos:
            continue
        x, y = pos[id(node)]
        status = _node_status(node, step, frontier_ids, expanded_ids, stale_ids)
        face = fill[status]
        edge = "#374151" if status != "discarded" else "#b0b4ba"
        text_color = "#ffffff" if status in ("current", "frontier", "stale") else C_INK

        ax.scatter([x], [y], s=190 if status == "current" else 130,
                   c=face, marker="o", edgecolors=edge,
                   linewidths=1.6 if status == "current" else 0.9,
                   linestyle="dashed" if status == "discarded" else "solid",
                   hatch="///" if status == "stale" else None, zorder=3)
        ax.text(x, y, str(node.state)[:3], ha="center", va="center",
                fontsize=label_size, color=text_color, zorder=4,
                fontweight="bold" if status == "current" else "normal")
        ax.text(x, y - 0.30, f"{node.path_cost:g}", ha="center", va="top",
                fontsize=label_size * 0.85, color="#4b5563", zorder=4)

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs) - 1.0, max(xs) + 1.0)
    ax.set_ylim(min(ys) - 0.8, max(ys) + 0.6)

    if title:
        depth_span = int(-min(ys))
        ax.set_title(f"SEARCH TREE - {len(nodes)} nodes generated, depth {depth_span}"
                     f"   (label = state, number below = g)",
                     fontsize=fs(9.5), color=C_INK)


# --------------------------------------------------------------------
# 6c. The frontier drawn as an actual queue
# --------------------------------------------------------------------


def draw_frontier_strip(ax, step: Step, max_items: int = 14):
    """Boxes left to right in true pop order. Leftmost is popped next."""
    ax.clear()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("#ffffff")
    for spine in ax.spines.values():
        spine.set_edgecolor(C_RULE)

    items = step.frontier_nodes
    ax.set_xlim(0, max_items + 0.6)
    ax.set_ylim(0, 1)

    ax.text(0.06, 0.90, "FRONTIER (priority queue, next pop on the left)",
            transform=ax.transAxes, fontsize=fs(8.6), color=C_INK,
            va="top", fontweight="bold")

    if not items:
        ax.text(0.5, 0.42, "frontier is empty - the search is over",
                transform=ax.transAxes, ha="center", fontsize=fs(9), color="#6b7280")
        return

    shown = items[:max_items]
    for k, (priority, node) in enumerate(shown):
        stale = id(node) in step.stale_ids
        face = "#fde8dc" if k == 0 else ("#eef4fb" if not stale else "#f4f4f6")
        edge = C_CURRENT if k == 0 else (C_FRONTIER if not stale else "#a5a8ae")
        box = FancyBboxPatch((k + 0.12, 0.14), 0.76, 0.42,
                             boxstyle="round,pad=0.02,rounding_size=0.06",
                             linewidth=1.6 if k == 0 else 1.0,
                             edgecolor=edge, facecolor=face,
                             hatch="///" if stale else None, zorder=2)
        ax.add_patch(box)
        ax.text(k + 0.5, 0.44, str(node.state)[:9], ha="center", va="center",
                fontsize=fs(7.8), color=C_INK, fontweight="bold", zorder=3)
        ax.text(k + 0.5, 0.245, f"f={priority:g}", ha="center", va="center",
                fontsize=fs(7.0), color="#4b5563", zorder=3)

    ax.annotate("POP", xy=(0.5, 0.60), xytext=(0.5, 0.80),
                ha="center", fontsize=fs(7.6), color=C_CURRENT, fontweight="bold",
                arrowprops={"arrowstyle": "-|>", "color": C_CURRENT, "linewidth": 1.4})

    if len(items) > max_items:
        ax.text(max_items + 0.35, 0.36, f"+{len(items) - max_items}\nmore",
                ha="center", va="center", fontsize=fs(7.0), color="#6b7280")
    if step.stale_in_frontier:
        ax.text(0.99, 0.90, f"{step.stale_in_frontier} stale duplicate(s), hatched",
                transform=ax.transAxes, ha="right", va="top",
                fontsize=fs(7.4), color="#6b7280")


# --------------------------------------------------------------------
# 6d. Static contact sheets (unchanged role, better legends)
# --------------------------------------------------------------------


LEGEND = [
    Patch(facecolor=C_CURRENT, edgecolor="#374151", label="just popped"),
    Patch(facecolor=C_FRONTIER, edgecolor="#374151", label="on frontier (f shown)"),
    Patch(facecolor=C_EXPANDED, edgecolor="#374151", label="already expanded"),
    Patch(facecolor=C_PATH, edgecolor="#374151", label="path to popped node"),
    Patch(facecolor=C_UNSEEN, edgecolor="#374151", label="not yet reached"),
]


def plot_search_panels(problem: GraphProblem, trace: list[Step], title: str,
                       n_panels: int = 9, outfile: str | None = None,
                       show_costs: bool = True):
    """A contact sheet of the first N iterations - the workhorse lecture figure."""
    steps = trace[:n_panels]
    cols = 3
    rows = math.ceil(len(steps) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4.8 * cols, 4.2 * rows))
    axes = axes.ravel() if hasattr(axes, "ravel") else [axes]
    for ax, step in zip(axes, steps):
        draw_state_graph(ax, problem, step, show_costs=show_costs)
    for ax in axes[len(steps):]:
        ax.axis("off")
    fig.legend(handles=LEGEND, loc="lower center", ncol=5, frameon=False, fontsize=fs(9))
    fig.suptitle(title, fontsize=fs(13), y=0.995)
    fig.tight_layout(rect=[0, 0.045, 1, 0.975])
    if outfile:
        fig.savefig(outfile, dpi=140)
        plt.close(fig)
        return outfile
    return fig


def plot_tree_panels(trace: list[Step], title: str, n_panels: int = 9,
                     outfile: str | None = None):
    """Contact sheet of the SEARCH TREE growing. Pairs with plot_search_panels."""
    steps = trace[:n_panels]
    cols = 3
    rows = math.ceil(len(steps) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4.8 * cols, 3.6 * rows))
    axes = axes.ravel() if hasattr(axes, "ravel") else [axes]
    for ax, step in zip(axes, steps):
        draw_search_tree(ax, step, title=False)
        ax.set_title(f"step {step.i}: pop {step.popped.state}"
                     f"   ({len(step.generated_nodes)} nodes)", fontsize=fs(9))
    for ax in axes[len(steps):]:
        ax.axis("off")
    fig.suptitle(title, fontsize=fs(13), y=0.995)
    fig.tight_layout(rect=[0, 0.01, 1, 0.975])
    if outfile:
        fig.savefig(outfile, dpi=140)
        plt.close(fig)
        return outfile
    return fig


def plot_grid_comparison(grid: list[str], outfile: str | None = None,
                         names: list[str] | None = None):
    """Side-by-side expanded-node maps on ONE shared maze instance."""
    names = names or CORE_STRATEGIES
    problem = GridProblem(grid)
    fig, axes = plt.subplots(1, len(names), figsize=(5.2 * len(names), 5.4))
    axes = axes if hasattr(axes, "__len__") else [axes]
    for ax, name in zip(axes, names):
        node, trace = run_strategy(STRATEGIES[name], problem)
        m = metrics(node, trace)
        expanded = set(trace[-1].expanded_so_far)
        frontier = {s for _, s in trace[-1].frontier_after}
        path = set(node.solution()) if m["found"] else set()

        img = [[0] * problem.cols for _ in range(problem.rows)]
        for r in range(problem.rows):
            for c in range(problem.cols):
                if problem.grid[r][c] == "#":
                    img[r][c] = 1
                elif (r, c) in path:
                    img[r][c] = 4
                elif (r, c) in expanded:
                    img[r][c] = 2
                elif (r, c) in frontier:
                    img[r][c] = 3
        cmap = matplotlib.colors.ListedColormap(
            ["#ffffff", "#37474f", C_EXPANDED, C_FRONTIER, C_PATH])
        ax.imshow(img, cmap=cmap, vmin=0, vmax=4)
        sr, sc = problem.initial
        gr, gc = problem.goal
        ax.text(sc, sr, "S", ha="center", va="center", color=C_START, fontweight="bold")
        ax.text(gc, gr, "G", ha="center", va="center", color="#c62828", fontweight="bold")
        cost = f"{m['cost']:g}" if m["found"] else "inf"
        ax.set_title(f"{name}   {STRATEGIES[name].formula}\n"
                     f"expanded {m['expansions']} | peak frontier {m['peak_frontier']} | "
                     f"path cost {cost}", fontsize=fs(10))
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("One framework, three evaluation functions, one identical maze - "
                 "grey = nodes expanded", fontsize=fs(13))
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    if outfile:
        fig.savefig(outfile, dpi=140)
        plt.close(fig)
        return outfile
    return fig


def interactive_stepper(problem: GraphProblem, trace: list[Step]):
    """Jupyter-only slider. Requires ipywidgets; degrades gracefully."""
    try:
        from ipywidgets import IntSlider, interact
        from IPython.display import display
    except ImportError:
        print("ipywidgets not installed - run `pip install ipywidgets`, "
              "or use plot_search_panels() instead.")
        return

    def show(i=1):
        fig, axes = plt.subplots(1, 2, figsize=(13, 6))
        draw_state_graph(axes[0], problem, trace[i - 1])
        draw_search_tree(axes[1], trace[i - 1])
        display(fig)
        plt.close(fig)

    return interact(show, i=IntSlider(min=1, max=len(trace), step=1, value=1,
                                      description="iteration"))


# ====================================================================
# PART 7 - Problem instances
# ====================================================================

# Real road distances from AIMA Figure 3.1. Keep these: the class can check
# the uniform-cost answer (418 from Arad to Bucharest) against the book.
ROMANIA_GRAPH_RAW = {
    "Arad": {"Zerind": 75, "Sibiu": 140, "Timisoara": 118},
    "Bucharest": {"Urziceni": 85, "Pitesti": 101, "Giurgiu": 90, "Fagaras": 211},
    "Craiova": {"Drobeta": 120, "Rimnicu": 146, "Pitesti": 138},
    "Drobeta": {"Mehadia": 75},
    "Eforie": {"Hirsova": 86},
    "Fagaras": {"Sibiu": 99},
    "Hirsova": {"Urziceni": 98},
    "Iasi": {"Vaslui": 92, "Neamt": 87},
    "Lugoj": {"Timisoara": 111, "Mehadia": 70},
    "Oradea": {"Zerind": 71, "Sibiu": 151},
    "Pitesti": {"Rimnicu": 97},
    "Rimnicu": {"Sibiu": 80},
    "Urziceni": {"Vaslui": 142},
}

ROMANIA_LOCATIONS = {
    "Arad": (91, 492), "Bucharest": (400, 327), "Craiova": (253, 288),
    "Drobeta": (165, 299), "Eforie": (562, 293), "Fagaras": (305, 449),
    "Giurgiu": (375, 270), "Hirsova": (534, 350), "Iasi": (473, 506),
    "Lugoj": (165, 379), "Mehadia": (168, 339), "Neamt": (406, 537),
    "Oradea": (131, 571), "Pitesti": (320, 368), "Rimnicu": (233, 410),
    "Sibiu": (207, 457), "Timisoara": (94, 410), "Urziceni": (456, 350),
    "Vaslui": (509, 444), "Zerind": (108, 531),
}


def _undirected(g: dict) -> dict:
    out = {city: {} for city in ROMANIA_LOCATIONS}
    for a, nbrs in g.items():
        for b, w in nbrs.items():
            out[a][b] = w
            out[b][a] = w
    return out


ROMANIA_GRAPH = _undirected(ROMANIA_GRAPH_RAW)


def randomized_graph_costs(graph: dict, low: int = 1, high: int = 20,
                           rng: random.Random | None = None) -> dict:
    """Topology-preserving graph with fresh symmetric positive costs."""
    rng = rng or random.Random(SEED)
    out = {state: {} for state in graph}
    assigned = {}
    for state, neighbors in graph.items():
        for neighbor in neighbors:
            edge = frozenset((state, neighbor))
            if edge not in assigned:
                assigned[edge] = rng.randint(low, high)
            out[state][neighbor] = assigned[edge]
    return out


def romania_problem(initial="Arad", goal="Bucharest", randomize: bool = False,
                    seed: int | None = None) -> GraphProblem:
    """Romania with the real AIMA distances by default.

    Randomized costs are available with randomize=True, but the real numbers
    are worth keeping as the default: uniform-cost search must return
    Arad - Sibiu - Rimnicu - Pitesti - Bucharest at cost 418, which students
    can verify against the textbook.
    """
    graph = ROMANIA_GRAPH
    if randomize:
        graph = randomized_graph_costs(ROMANIA_GRAPH, 10, 250,
                                       random.Random(SEED if seed is None else seed))
    return GraphProblem(initial, goal, graph, ROMANIA_LOCATIONS)


def _build_maze() -> list[str]:
    """A long barrier (only gap at the bottom) plus a concave cup around the
    goal. Chosen so the expansion counts separate dramatically: different
    frontier-ordering rules explore the map in visibly different ways.
    """
    R, C = 19, 43
    g = [["."] * C for _ in range(R)]
    for r in range(0, 14):
        g[r][20] = "#"
    for c in range(28, 38):
        g[6][c] = "#"
        g[14][c] = "#"
    for r in range(6, 15):
        g[r][37] = "#"
    g[10][3] = "S"
    g[10][33] = "G"
    return ["".join(row) for row in g]


MAZE = _build_maze()

# Small classroom tree used to show how the fringe changes after each pop.
TREE_GRAPH = {
    "A": {"B": 1, "C": 1},
    "B": {"D": 1, "E": 1},
    "C": {"F": 1, "G": 1},
    "D": {"H": 1, "I": 1},
    "E": {"J": 1, "K": 1},
    "F": {"L": 1, "M": 1},
    "G": {"N": 1, "O": 1},
}
TREE_LOCATIONS = {
    "A": (3.5, 4), "B": (1.5, 3), "C": (5.5, 3),
    "D": (0.5, 2), "E": (2.5, 2), "F": (4.5, 2), "G": (6.5, 2),
    "H": (0, 1), "I": (1, 1), "J": (2, 1), "K": (3, 1),
    "L": (4, 1), "M": (5, 1), "N": (6, 1), "O": (7, 1),
}


def tree_problem(goal: str = "O", seed: int | None = None) -> GraphProblem:
    """The 15-node classroom tree. Costs are seeded, so the deck, the handout
    and the live demo all show identical numbers.

    The goal is worth changing live. With goal="O" (rightmost leaf) the
    LIFO tiebreak sends depth-first straight to it in three expansions and
    depth-first looks brilliant. With goal="H" (leftmost leaf) depth-first
    has to walk the entire tree and looks terrible. Same algorithm, same
    tree, opposite verdict: that is exactly the point about depth-first
    having no guarantees.
    """
    rng = random.Random(SEED if seed is None else seed)
    graph = {state: {} for state in TREE_LOCATIONS}
    for parent, children in TREE_GRAPH.items():
        for child in children:
            cost = rng.randint(1, 20)
            graph[parent][child] = cost
            graph[child][parent] = cost
    return GraphProblem("A", goal, graph, TREE_LOCATIONS)


def multi_goal_tree_problem() -> MultiGoalGraphProblem:
    """Tree with two goals: H and O. Depth-first reaches H first and stops."""
    p = tree_problem()
    return MultiGoalGraphProblem("A", {"H", "O"}, p.graph, p.locations)


# ====================================================================
# PART 8 - The interactive explorer
# ====================================================================


def explorer_window(problem: GraphProblem, strategy_names: list[str], title: str,
                    show_costs: bool = True, tree_annotations: bool = False,
                    figsize=(16.0, 9.0)):
    """One window: state graph, search tree, frontier queue and commentary.

    Every strategy button runs on the SAME problem object, so switching
    strategies compares like with like. The previous version rebuilt the
    problem with fresh random costs on every click, which silently changed
    the question being asked.

    Keys: Left/Right step, Home/End jump, Space play/pause, r restart,
    1..5 pick a strategy, [ and ] change the depth limit while
    Depth-limited is selected.
    """
    state = {"name": strategy_names[0], "index": 0, "trace": [],
             "solution": FAILURE, "playing": False}

    fig = plt.figure(figsize=figsize, facecolor="#f4f6f8")
    set_window_title(fig, "COMP 469 - Best-First Search Visualizer")

    # When the b/m annotations are on, the state graph shifts right to leave
    # room for the tier brace and the "b^k nodes" labels.
    graph_left = 0.182 if tree_annotations else 0.135
    graph_width = 0.348 if tree_annotations else 0.395
    ax_graph = fig.add_axes((graph_left, 0.375, graph_width, 0.525))
    ax_tree = fig.add_axes((0.545, 0.375, 0.285, 0.525))
    ax_info = fig.add_axes((0.845, 0.055, 0.148, 0.885), facecolor="#ffffff")
    ax_front = fig.add_axes((0.135, 0.145, 0.695, 0.135))
    ax_calc = fig.add_axes((0.135, 0.045, 0.695, 0.082), facecolor="#ffffff")

    for panel in (ax_info, ax_calc):
        panel.set_xticks([])
        panel.set_yticks([])
        for spine in panel.spines.values():
            spine.set_edgecolor(C_RULE)

    fig.text(0.48, 0.975, title, ha="center", va="top",
             fontsize=fs(15), fontweight="bold", color=C_INK)

    info_head = ax_info.text(0.06, 0.985, "", transform=ax_info.transAxes, va="top",
                             fontsize=fs(9.4), fontweight="bold", color="#0b5c3f",
                             linespacing=1.25)
    info_note = ax_info.text(0.06, 0.80, "", transform=ax_info.transAxes, va="top",
                             fontsize=fs(8.2), color=C_INK, linespacing=1.22)
    info_step = ax_info.text(0.06, 0.485, "", transform=ax_info.transAxes, va="top",
                             fontsize=fs(8.6), color=C_INK, linespacing=1.28)
    info_children = ax_info.text(0.06, 0.235, "", transform=ax_info.transAxes, va="top",
                                 fontsize=fs(7.6), family="monospace",
                                 color=C_INK, linespacing=1.18)
    calc_text = ax_calc.text(0.012, 0.90, "", transform=ax_calc.transAxes, va="top",
                             fontsize=fs(7.8), family="monospace", color=C_INK,
                             linespacing=1.25)

    brace_artists = []
    if tree_annotations:
        brace_artists.append(add_figure_curly_brace(
            fig, x=0.112, y0=0.400, y1=0.890, width=0.009, linewidth=1.6))
        brace_artists.append(fig.text(0.103, 0.645, "m tiers", va="center", ha="center",
                                      rotation=90, fontsize=fs(8.6), color="#333333"))

    fig.legend(handles=LEGEND, loc="lower center", bbox_to_anchor=(0.48, 0.288),
               ncol=5, frameon=False, fontsize=fs(8.4))

    def priority_explanation(node: Node, name: str) -> str:
        d, g = node.depth(), node.path_cost
        if name == "Uniform-cost":
            return f"g={g:g} -> f={g:g}"
        if name in ("Depth-first", "Depth-limited", "Iterative deepening"):
            return f"depth={d} -> f={-d}"
        return f"depth={d} -> f={d}"

    def run(name: str):
        state["name"] = name
        state["index"] = 0
        solution, trace = run_strategy(STRATEGIES[name], problem)
        state["solution"] = solution
        state["trace"] = trace
        for i, button in enumerate(strategy_buttons):
            active = strategy_names[i] == name
            button.color = "#cfe3f5" if active else "#e5e7eb"
            button.ax.set_facecolor(button.color)
        draw()

    def draw():
        trace = state["trace"]
        if not trace:
            return
        step = trace[min(state["index"], len(trace) - 1)]
        strategy = STRATEGIES[state["name"]]

        draw_state_graph(ax_graph, problem, step, show_costs=show_costs)
        if tree_annotations:
            # How the state space grows tier by tier: b, b^2, ..., b^m. The
            # y values are the tree's own data coordinates, so the labels stay
            # attached to A, B/C, D-G and H-O when the window is resized.
            level_transform = ax_graph.get_yaxis_transform()
            for y, text in ((4, "1 node"), (3, "b nodes"),
                            (2, "b² nodes"), (1, "bᵐ nodes")):
                ax_graph.text(-0.02, y, text, transform=level_transform,
                              va="center", ha="right", fontsize=fs(8.2),
                              color="#333333", clip_on=False)
        draw_search_tree(ax_tree, step)
        draw_frontier_strip(ax_front, step)

        limit_line = ("" if step.depth_limit is None
                      else f"\ndepth limit L = {step.depth_limit}")
        # The side panel has a fixed width, so bigger fonts must mean fewer
        # words. In presentation mode the note drops to its first sentence.
        wrap = max(18, int(40 / max(SCALE, 1.0)))
        note = strategy.note
        if SCALE > 1.15:
            note = note.split(". ")[0] + "."
        info_head.set_text(f"{strategy.name}\n{strategy.formula}\n"
                           f"{textwrap.fill(strategy.blurb, width=wrap)}{limit_line}")
        info_note.set_text(textwrap.fill(note, width=wrap))

        status = "GOAL FOUND" if step.is_goal else (
            "CUTOFF at limit" if step.cutoff_here else "searching")
        stale_note = "\nthis pop was a stale duplicate" if step.stale_pop else ""
        info_step.set_text(
            f"ITERATION {step.i} OF {len(trace)}\n"
            f"popped     {step.popped.state}\n"
            f"priority f {step.priority:g}\n"
            f"path cost g {step.popped.path_cost:g}\n"
            f"depth      {step.popped.depth()}\n"
            f"generated  {step.generated_count}\n"
            f"frontier   {step.frontier_size}\n"
            f"status     {status}{stale_note}"
        )

        if step.children:
            lines = [f"{str(c.state)[:9]:<10}g={c.path_cost:<5g}{v.split(' (')[0]}"
                     for c, v in step.children[:8]]
            if len(step.children) > 8:
                lines.append(f"... {len(step.children) - 8} more")
            body = "\n".join(lines)
        elif step.is_goal:
            body = "(goal test passed on pop;\n no expansion happens)"
        elif step.cutoff_here:
            body = "(at the depth limit;\n children are not generated)"
        else:
            body = "(none)"
        info_children.set_text("CHILDREN GENERATED\n" + body)

        solution = state["solution"]
        solved = solution is not FAILURE and solution is not CUTOFF
        final = " -> ".join(str(s) for s in solution.solution()) if solved else (
            "cutoff" if solution is CUTOFF else "no solution")
        nxt = (f"{step.frontier_nodes[0][1].state} (f={step.frontier_nodes[0][0]:g})"
               if step.frontier_nodes else "nothing left")
        budget = max(34, int(104 / max(SCALE, 1.0)))
        path_so_far = " -> ".join(str(s) for s in step.popped.solution())
        answer = final + (f"   cost {solution.path_cost:g}" if solved else "")
        calc_text.set_text(
            f"WHY THIS NODE  {step.popped.state}: "
            f"{priority_explanation(step.popped, state['name'])}"
            f"  = smallest f in the frontier\n"
            f"NEXT POP       {nxt[:budget]}\n"
            f"PATH SO FAR    {path_so_far[:budget]}\n"
            f"FINAL ANSWER   {answer[:budget]}"
        )

        ax_graph.set_title(
            f"STATE GRAPH - step {step.i} of {len(trace)}: "
            f"{'GOAL' if step.is_goal else 'pop ' + str(step.popped.state)}"
            + ("   road labels = action costs" if show_costs else ""),
            fontsize=fs(10.5), color=C_INK)
        fig.canvas.draw_idle()

    def go(delta):
        state["index"] = max(0, min(len(state["trace"]) - 1, state["index"] + delta))
        draw()

    def jump(index):
        state["index"] = max(0, min(len(state["trace"]) - 1, index))
        draw()

    # ---- controls -------------------------------------------------
    fig.text(0.012, 0.935, "STRATEGY", fontsize=fs(9.0), fontweight="bold", color="#374151")
    short = {"Iterative deepening": "Iter. deepening"}
    strategy_buttons = []
    for row, name in enumerate(strategy_names):
        b_ax = fig.add_axes((0.006, 0.865 - row * 0.062, 0.092, 0.048))
        button = Button(b_ax, f"{row + 1}. {short.get(name, name)}",
                        color="#e5e7eb", hovercolor="#d1d5db")
        button.label.set_fontsize(fs(7.8))
        button.on_clicked(lambda _e, chosen=name: run(chosen))
        strategy_buttons.append(button)

    nav = []
    for label, cb, x in (("|<", lambda _e: jump(0), 0.006),
                         ("< Prev", lambda _e: go(-1), 0.030),
                         ("Next >", lambda _e: go(1), 0.066)):
        b_ax = fig.add_axes((x, 0.145, 0.022 if label == "|<" else 0.032, 0.045))
        b = Button(b_ax, label, color="#e5e7eb", hovercolor="#d1d5db")
        b.label.set_fontsize(fs(8.0))
        b.on_clicked(cb)
        nav.append(b)

    play_ax = fig.add_axes((0.006, 0.088, 0.092, 0.045))
    play_button = Button(play_ax, "Play", color="#e5e7eb", hovercolor="#d1d5db")
    play_button.label.set_fontsize(fs(8.2))

    timer = None
    try:
        timer = fig.canvas.new_timer(interval=750)

        def tick():
            if state["playing"]:
                if state["index"] >= len(state["trace"]) - 1:
                    toggle_play(None)
                else:
                    go(1)

        timer.add_callback(tick)
    except Exception:  # backend without timer support
        timer = None

    def toggle_play(_event):
        if timer is None:
            return
        state["playing"] = not state["playing"]
        play_button.label.set_text("Pause" if state["playing"] else "Play")
        (timer.start if state["playing"] else timer.stop)()
        fig.canvas.draw_idle()

    play_button.on_clicked(toggle_play)

    reset_ax = fig.add_axes((0.006, 0.036, 0.092, 0.045))
    reset_button = Button(reset_ax, "Restart (r)", color="#e5e7eb", hovercolor="#d1d5db")
    reset_button.label.set_fontsize(fs(8.2))
    reset_button.on_clicked(lambda _e: run(state["name"]))

    def on_key(event):
        if event.key in ("right", "n"):
            go(1)
        elif event.key in ("left", "p"):
            go(-1)
        elif event.key == "home":
            jump(0)
        elif event.key == "end":
            jump(len(state["trace"]) - 1)
        elif event.key == " ":
            toggle_play(None)
        elif event.key == "r":
            run(state["name"])
        elif event.key in ("[", "]") and state["name"] == "Depth-limited":
            # Live lever: raise the limit until the goal stops being a cutoff.
            strategy = STRATEGIES["Depth-limited"]
            strategy.depth_limit = max(0, (strategy.depth_limit or 0)
                                       + (1 if event.key == "]" else -1))
            run("Depth-limited")
        elif event.key and event.key.isdigit():
            k = int(event.key) - 1
            if 0 <= k < len(strategy_names):
                run(strategy_names[k])

    fig.canvas.mpl_connect("key_press_event", on_key)

    # Keep every widget alive; matplotlib drops callbacks on garbage collection.
    fig._comp469_widgets = strategy_buttons + nav + [play_button, reset_button] + brace_artists
    fig._comp469_timer = timer

    run(strategy_names[0])
    plt.show()
    return fig


# ====================================================================
# PART 9 - Demos
# ====================================================================


def demo_romania(randomize: bool = False):
    """Contact sheets for breadth-first and uniform-cost on the real map."""
    for name, filename in (("Breadth-first", "01_breadth_first_romania.png"),
                           ("Uniform-cost", "02_uniform_cost_romania.png")):
        p = romania_problem("Arad", "Bucharest", randomize=randomize)
        print(f"\n### {name} on Romania: Arad -> Bucharest")
        node, trace = run_strategy(STRATEGIES[name], p)
        print_trace(trace)
        out = plot_search_panels(p, trace, f"{name}: Arad to Bucharest  ({STRATEGIES[name].formula})",
                                 n_panels=6, outfile=OUTPUT_DIR / filename)
        print("wrote", out)
        m = metrics(node, trace)
        print(f"cost {m['cost']:g} in {m['depth']} steps via "
              f"{' -> '.join(str(s) for s in m['path'])}")


def demo_compare(randomize: bool = False):
    print("\n### One algorithm, three evaluation functions - Romania, Arad -> Bucharest")
    comparison_table(romania_problem("Arad", "Bucharest", randomize=randomize))
    print("### The same three on the 15-node classroom tree, goal O")
    comparison_table(tree_problem())


def demo_grid():
    print("\n### Grid maze: how much of the map each f explores")
    out = plot_grid_comparison(MAZE, outfile=OUTPUT_DIR / "03_grid_comparison.png")
    print("wrote", out)
    comparison_table(GridProblem(MAZE))


def demo_reexpansion():
    """Why AIMA gives breadth-first its own pseudocode (Figure 3.9).

    Figure 3.7's reached test asks "is this child cheaper in g?". That is the
    right question only when f = g. Run f = depth through the literal
    pseudocode on a graph with varied action costs and states get re-added and
    re-expanded every time a cheaper-but-deeper path turns up.

    Depth-first is deliberately absent from this table. There is no valid
    dominance test for f = -depth: "deeper is better" would re-open every
    state forever, so the search never terminates. That is not a bug in the
    demo, it is the reason depth-first has to run tree-like, with a cycle
    check on the current path instead of a reached table.
    """
    print("\n### The reached test: compare g, or compare f?")
    for label, problem in (("Romania (real road distances)", romania_problem()),
                           ("Maze (random costs 1-9)", GridProblem(MAZE))):
        print(f"\n{label}")
        print(f"{'strategy':<16}{'reached test':<26}{'Expand':>8}{'Gener.':>9}"
              f"{'Peak fr.':>10}{'Cost':>9}")
        print("-" * 78)
        for name in ("Breadth-first", "Uniform-cost"):
            strategy = STRATEGIES[name]
            for dominance, desc in (("path-cost", "g   (literal Fig 3.7)"),
                                    ("priority", "f   (correct for this f)")):
                node, trace = best_first_search(
                    problem, strategy.make_f(problem),
                    tiebreak=strategy.tiebreak, dominance=dominance)
                m = metrics(node, trace)
                cost = f"{m['cost']:g}" if m["found"] else "inf"
                print(f"{strategy.formula:<16}{desc:<26}{m['expansions']:>8}"
                      f"{m['generated']:>9}{m['peak_frontier']:>10}{cost:>9}")
        print("-" * 78)
    print("\nUniform-cost does not move, because for uniform-cost g IS f.")
    print("Breadth-first collapses. On the maze the literal version expands")
    print("many times more nodes than the maze has cells, because every")
    print("cheaper-but-deeper path re-opens a state it had already finished.")
    print("That gap is why breadth-first gets its own figure in the book")
    print("instead of staying a call to BEST-FIRST-SEARCH with f = depth.\n")


def demo_tree():
    """Fringe-by-fringe graphics for the classroom search tree."""
    for name in CORE_STRATEGIES:
        p = tree_problem()
        node, trace = run_strategy(STRATEGIES[name], p)
        stem = name.lower().replace("-", "_")
        out = plot_search_panels(p, trace, f"{name} ({STRATEGIES[name].formula}): "
                                 f"state graph after each pop, goal O",
                                 n_panels=min(9, len(trace)),
                                 outfile=OUTPUT_DIR / f"tree_{stem}_graph.png")
        print("wrote", out)
        out = plot_tree_panels(trace, f"{name}: the SEARCH TREE growing "
                               f"(same run as the panel above)",
                               n_panels=min(9, len(trace)),
                               outfile=OUTPUT_DIR / f"tree_{stem}_searchtree.png")
        print("wrote", out)


def demo_cutoff():
    """Show the difference between cutoff and failure, and what IDS repeats."""
    p = tree_problem()
    print("\n### Depth-limited search, L = 2, goal O sits at depth 3")
    node, trace = run_strategy(STRATEGIES["Depth-limited"], p)
    m = metrics(node, trace)
    print(f"result: {m['result'].upper()}  after {m['expansions']} expansions")
    print("Cutoff means 'the goal may still exist below the limit'.")
    print("Failure would mean 'the goal is nowhere in the reachable space'.")

    print("\n### Iterative deepening on the same tree")
    node, trace = run_strategy(STRATEGIES["Iterative deepening"], p)
    m = metrics(node, trace)
    per_limit: dict[int, int] = {}
    for step in trace:
        per_limit[step.depth_limit] = per_limit.get(step.depth_limit, 0) + 1
    print("iterations per depth limit:",
          ", ".join(f"L={k}: {v}" for k, v in sorted(per_limit.items())))
    print(f"total {m['expansions']} expansions, {m['generated']} nodes generated, "
          f"peak frontier {m['peak_frontier']}")
    print("Compare the peak frontier with breadth-first on the same tree: that "
          "gap is the entire reason iterative deepening exists.")


def demo_multi_goal():
    """Depth-first returns the first goal it pops, not the best one."""
    p = multi_goal_tree_problem()
    node, trace = run_strategy(STRATEGIES["Depth-first"], p)
    print("\n### Two goals, H and O. Depth-first stops at whichever it pops first.")
    print("goals:", sorted(p.goals))
    print("returned:", node.state, "at cost", f"{node.path_cost:g}")
    print("path:", " -> ".join(str(s) for s in node.solution()))
    print("The search stops here. It never looks at the other goal, and it "
          "never checks whether the other goal was cheaper.")
    return p, trace


def demo_explore_tree():
    explorer_window(tree_problem(),
                    list(STRATEGIES),
                    "Classroom search tree: A to O",
                    show_costs=True, tree_annotations=True)


def demo_explore_romania():
    explorer_window(romania_problem("Arad", "Bucharest"),
                    CORE_STRATEGIES,
                    "Romania state space: Arad to Bucharest",
                    show_costs=True, tree_annotations=False)


STATIC_DEMOS = {
    "romania": demo_romania,
    "compare": demo_compare,
    "grid": demo_grid,
    "tree": demo_tree,
    "cutoff": demo_cutoff,
    "reexpansion": demo_reexpansion,
    "multi-goal": demo_multi_goal,
}

WINDOW_DEMOS = {
    "explore-tree": demo_explore_tree,
    "explore-romania": demo_explore_romania,
}

DEMOS = {**STATIC_DEMOS, **WINDOW_DEMOS}


def main():
    ap = argparse.ArgumentParser(
        description="Best-first search visualizer for COMP 469 (AIMA Figure 3.7)")
    ap.add_argument("--demo", choices=list(DEMOS) + ["all"], default="all",
                    help="'all' runs every static demo and writes PNGs")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED,
                    help="seed for randomized action costs (default 469)")
    ap.add_argument("--random-costs", action="store_true",
                    help="replace the real Romania distances with random ones")
    ap.add_argument("--big", action="store_true",
                    help="lecture-hall font sizes")
    args = ap.parse_args()

    set_seed(args.seed)
    set_scale(1.35 if args.big else 1.0)

    if args.demo == "all":
        demo_compare(randomize=args.random_costs)
        demo_romania(randomize=args.random_costs)
        demo_tree()
        demo_grid()
        demo_cutoff()
        demo_reexpansion()
        demo_multi_goal()
        print("\nInteractive demos: --demo explore-tree | explore-romania")
        return

    fn = DEMOS[args.demo]
    if args.demo in ("romania", "compare"):
        fn(randomize=args.random_costs)
    else:
        fn()


if __name__ == "__main__":
    main()
