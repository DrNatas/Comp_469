"""
====================================================================
COMP 469 — Introduction to Artificial Intelligence  (CSUCI)
Best-First Search Visualizer
Faithful to Russell & Norvig, AIMA 4th ed., Figure 3.7
====================================================================

The point of this module is NOT to be a fast search library. It is to make
every line of Figure 3.7 *observable*:

    - which node is popped, and why (its f-value was minimum)
    - what the frontier looks like at every iteration
    - what the `reached` table remembers
    - exactly when a child is added, re-added (better path found), or pruned

Everything downstream (Breadth-First, Uniform-Cost, and Depth-First) uses the SAME
best-first framework with a different evaluation function. That is the central idea of AIMA §3.3.1 and this module
is built to make students feel it rather than just read it.

Usage
-----
    python3 bestfirst_viz.py --demo search-window                 # Run this demo in a desktop window (requires matplotlib) 
    python3 bestfirst_viz.py --demo romania-search-window        # Full interactive Romania state-space visual
    python bestfirst_viz.py            # runs all demos, writes PNGs
    python bestfirst_viz.py --demo romania
    python bestfirst_viz.py --demo compare
    python bestfirst_viz.py --demo grid

Run from Windows PowerShell:
    cd "C:\\path\\to\\Code"
    py -m pip install matplotlib
    py bestfirst_viz.py

Run from macOS Terminal:
    cd "/path/to/Code"
    python3 -m pip install matplotlib
    python3 bestfirst_viz.py

Replace the paths above with the folder containing this file. To run one
demo, add `--demo romania`, `--demo compare`, or `--demo grid` to the command.
The program prints a trace and saves its PNG visualizations in the output
folder configured by the demo functions.

In Jupyter:
    from bestfirst_viz import *
    p = romania_problem('Arad', 'Bucharest')
    node, trace = best_first_search(p, f_breadth_first(p))
    print_trace(trace)
    plot_search_panels(p, trace, title="Breadth-first search on Romania")
"""

from __future__ import annotations

import argparse
import heapq
import math
import textwrap
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterator

import matplotlib

# Use the desktop backend so the step-by-step demos can open a window.
# In Jupyter, the notebook may select its own backend.
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import Patch, PathPatch
from matplotlib.widgets import Button

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def set_window_title(fig, title="COMP 469 — CSU Channel Islands"):
    """Set the title shown in the desktop window's title bar."""
    manager = getattr(fig.canvas, "manager", None)
    if manager is not None and hasattr(manager, "set_window_title"):
        manager.set_window_title(title)


def add_figure_curly_brace(
    fig,
    x: float,
    y0: float,
    y1: float,
    width: float = 0.018,
    linewidth: float = 2.0,
    color: str = "#777777",
):
    """
    Draw a thin, resize-safe left curly brace in figure coordinates.

    Parameters
    ----------
    fig
        Matplotlib Figure receiving the brace.
    x
        Horizontal position of the brace's center/waist in figure coordinates.
    y0, y1
        Bottom and top positions in figure coordinates.
    width
        Horizontal width in figure coordinates. Smaller values make the brace
        skinnier without changing its height.
    linewidth
        Stroke width in points. This stays visually consistent as the window
        is resized.
    color
        Brace stroke color.

    Because the brace is drawn in ``fig.transFigure`` coordinates, it
    automatically tracks window resizing and remains aligned with UI elements
    positioned using figure-relative coordinates.
    """
    if y1 <= y0:
        raise ValueError("y1 must be greater than y0")

    height = y1 - y0
    middle = (y0 + y1) / 2.0

    # Left curly brace "{":
    # the tips are on the right, and the waist points to the left.
    x_right = x + width
    x_inner = x + width * 0.18
    x_left = x - width * 0.35

    upper_shoulder = middle + height * 0.13
    lower_shoulder = middle - height * 0.13

    vertices = [
        (x_right, y1),

        # Top tip to upper shoulder.
        (x_inner, y1),
        (x_inner, middle + height * 0.30),
        (x_inner, upper_shoulder),

        # Upper shoulder to center waist.
        (x_inner, middle + height * 0.06),
        (x_left, middle + height * 0.035),
        (x_left, middle),

        # Center waist to lower shoulder.
        (x_left, middle - height * 0.035),
        (x_inner, middle - height * 0.06),
        (x_inner, lower_shoulder),

        # Lower shoulder to bottom tip.
        (x_inner, middle - height * 0.30),
        (x_inner, y0),
        (x_right, y0),
    ]

    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
        MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
        MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
        MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
    ]

    patch = PathPatch(
        MplPath(vertices, codes),
        transform=fig.transFigure,
        fill=False,
        edgecolor=color,
        linewidth=linewidth,
        capstyle="round",
        joinstyle="round",
        clip_on=False,
        zorder=10,
    )
    fig.add_artist(patch)
    return patch

# ====================================================================
# PART 1 — The data structures named in Figure 3.7
# ====================================================================


class Node:
    """A node in the search TREE.

    Careful, students: a Node is not a state. A state is a place
    (e.g. 'Sibiu'). A Node is *one particular path* that arrives at that
    place, together with its cost. The same state can appear in many
    different nodes.
    """

    __slots__ = ("state", "parent", "action", "path_cost")

    def __init__(self, state, parent=None, action=None, path_cost=0.0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost  # this is g(n)

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
        return len(self.path()) - 1


FAILURE = Node("failure", path_cost=math.inf)


class PriorityQueue:
    """`frontier <- a priority queue ordered by f`

    Implemented with a binary heap. The `count` tiebreaker keeps ordering
    deterministic (FIFO among equal f), which matters a great deal when you
    want a whole class to reproduce the same trace.

    Note (worth 5 minutes of lecture): Figure 3.7 says "add child to
    frontier" without removing the older, worse entry for that state. So
    the frontier can hold *stale* duplicates. That is fine for correctness,
    because `reached` is the source of truth and any stale pop is discarded
    by the `reached` check on re-expansion. We keep the pseudocode's literal
    behavior and expose `.stale_count` so students can see the duplicates.
    """

    def __init__(self, f: Callable[[Node], float]):
        self.f = f
        self.heap: list[tuple[float, int, Node]] = []
        self._count = 0

    def add(self, node: Node) -> None:
        heapq.heappush(self.heap, (self.f(node), self._count, node))
        self._count += 1

    def pop(self) -> Node:
        return heapq.heappop(self.heap)[2]

    def top(self) -> Node:
        return self.heap[0][2]

    def __len__(self) -> int:
        return len(self.heap)

    def __bool__(self) -> bool:
        return bool(self.heap)

    def sorted_items(self) -> list[tuple[float, Node]]:
        """Frontier contents in pop order — for display only."""
        return [(pri, node) for pri, _, node in sorted(self.heap)]

    def stale_count(self, reached: dict) -> int:
        return sum(1 for _, _, n in self.heap if reached.get(n.state) is not n)


# ====================================================================
# PART 2 — Problem interface (AIMA §3.1)
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
    """4-connected grid with walls for comparing search strategies."""

    def __init__(self, grid: list[str], initial=None, goal=None, rng: random.Random | None = None):
        self.grid = [list(row) for row in grid]
        self.rng = rng or random.Random()
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
                        cost = self.rng.randint(1, 9)
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
# PART 3 — BEST-FIRST-SEARCH  (Figure 3.7, line for line)
# ====================================================================


@dataclass
class Step:
    """One full pass through the while-loop, recorded for replay."""

    i: int
    popped: Node
    priority: float
    is_goal: bool
    children: list[tuple[Node, str]] = field(default_factory=list)  # (child, verdict)
    frontier_after: list[tuple[float, Any]] = field(default_factory=list)
    reached_after: list = field(default_factory=list)
    expanded_so_far: list = field(default_factory=list)
    stale_in_frontier: int = 0


def expand(problem: Problem, node: Node) -> Iterator[Node]:
    """function EXPAND(problem, node) yields nodes"""
    s = node.state
    for action in problem.actions(s):
        s_prime = problem.result(s, action)
        cost = node.path_cost + problem.action_cost(s, action, s_prime)
        yield Node(state=s_prime, parent=node, action=action, path_cost=cost)


def best_first_search(problem: Problem, f: Callable[[Node], float], max_steps: int = 10_000):
    """function BEST-FIRST-SEARCH(problem, f) returns a solution node or failure

    Returns (solution_node_or_FAILURE, trace) where trace is a list of Step.
    The search logic below is unmodified pseudocode; every `trace`/`expanded`
    line is pure instrumentation and can be deleted without changing behavior.
    """
    node = Node(state=problem.initial)                      # node <- NODE(STATE=problem.INITIAL)
    frontier = PriorityQueue(f)                             # frontier <- a priority queue ordered by f
    frontier.add(node)                                      #   ...with node as an element
    reached = {problem.initial: node}                       # reached <- lookup table {INITIAL: node}

    trace, expanded, i = [], [], 0

    while frontier:                                         # while not IS-EMPTY(frontier) do
        node = frontier.pop()                               #   node <- POP(frontier)
        i += 1
        step = Step(i=i, popped=node, priority=f(node), is_goal=problem.is_goal(node.state))

        if problem.is_goal(node.state):                     #   if problem.IS-GOAL(node.STATE)
            expanded.append(node.state)
            step.frontier_after = [(p, n.state) for p, n in frontier.sorted_items()]
            step.reached_after = list(reached)
            step.expanded_so_far = list(expanded)
            trace.append(step)
            return node, trace                              #     then return node

        expanded.append(node.state)

        for child in expand(problem, node):                 #   for each child in EXPAND(problem, node)
            s = child.state                                 #     s <- child.STATE
            if s not in reached:                            #     if s is not in reached
                reached[s] = child                          #       reached[s] <- child
                frontier.add(child)                         #       add child to frontier
                step.children.append((child, "NEW"))
            elif child.path_cost < reached[s].path_cost:    #     or child.PATH-COST < reached[s].PATH-COST
                old = reached[s].path_cost
                reached[s] = child                          #       reached[s] <- child
                frontier.add(child)                         #       add child to frontier
                step.children.append((child, f"BETTER (g {old:g} -> {child.path_cost:g})"))
            else:
                step.children.append((child, f"PRUNED (have g={reached[s].path_cost:g})"))

        step.frontier_after = [(p, n.state) for p, n in frontier.sorted_items()]
        step.reached_after = list(reached)
        step.expanded_so_far = list(expanded)
        step.stale_in_frontier = frontier.stale_count(reached)
        trace.append(step)

        if i >= max_steps:
            break

    return FAILURE, trace                                   # return failure


# ====================================================================
# PART 4 — The search algorithms are ONE algorithm with different f's
# ====================================================================

def f_breadth_first(problem):
    """f(n) = depth  ->  breadth-first search"""
    return lambda n: n.depth()


def f_uniform_cost(problem):
    """f(n) = g(n)  ->  uniform-cost / Dijkstra"""
    return lambda n: n.path_cost


def f_depth_first(problem):
    """Priority that expands the deepest available node first."""
    return lambda n: -n.depth()


ALGORITHMS = {
    "Breadth-First  f = depth": f_breadth_first,
    "Uniform-Cost   f = g": f_uniform_cost,
    "Depth-First    f = -depth": f_depth_first,
}


# ====================================================================
# PART 5 — Text trace (the thing to read line-by-line in lab)
# ====================================================================


def print_trace(trace: list[Step], max_steps: int | None = None, width: int = 78) -> None:
    print("=" * width)
    print(f"{'BEST-FIRST-SEARCH trace':^{width}}")
    print("=" * width)
    for step in trace[: max_steps or len(trace)]:
        tag = "  <-- GOAL, return this node" if step.is_goal else ""
        print(f"\nIteration {step.i}")
        print(f"  POP  -> {step.popped.state}   (f = {step.priority:g}, "
              f"g = {step.popped.path_cost:g}){tag}")
        if step.is_goal:
            print(f"  path : {' -> '.join(step.popped.solution())}")
            print(f"  cost : {step.popped.path_cost:g}")
            break
        for child, verdict in step.children:
            print(f"      child {child.state:<16} g={child.path_cost:<7g} {verdict}")
        front = ", ".join(f"{s}({p:g})" for p, s in step.frontier_after[:8])
        more = "" if len(step.frontier_after) <= 8 else f", ... (+{len(step.frontier_after) - 8})"
        print(f"  frontier: [{front}{more}]")
        if step.stale_in_frontier:
            print(f"  ({step.stale_in_frontier} stale duplicate(s) sitting in the frontier)")
    print("\n" + "=" * width)


def summarize(problem: Problem, name: str, f) -> dict:
    node, trace = best_first_search(problem, f)
    solved = node is not FAILURE
    return {
        "algorithm": name,
        "found": solved,
        "cost": node.path_cost if solved else math.inf,
        "depth": node.depth() if solved else -1,
        "expanded": len(trace),
        "path": node.solution() if solved else [],
    }


def comparison_table(problem_or_factory, algorithms=ALGORITHMS) -> None:
    rows = []
    for name, maker in algorithms.items():
        problem = problem_or_factory() if callable(problem_or_factory) else problem_or_factory
        rows.append(summarize(problem, name, maker(problem)))
    print(f"\n{'Algorithm':<26}{'Cost':>8}{'Depth':>7}{'Expanded':>10}   Path")
    print("-" * 100)
    for r in rows:
        path = " -> ".join(str(s) for s in r["path"])
        if len(path) > 46:
            path = path[:43] + "..."
        print(f"{r['algorithm']:<26}{r['cost']:>8g}{r['depth']:>7}{r['expanded']:>10}   {path}")
    print("-" * 100)
    print("Each algorithm receives a newly randomized set of positive action costs.")
    print("Breadth-first and depth-first ignore cost when ordering the frontier; uniform-cost uses it.\n")
    return rows


# ====================================================================
# PART 6 — Visualization
# ====================================================================

C_UNSEEN = "#e9e9ec"
C_FRONTIER = "#ffb74d"
C_EXPANDED = "#90a4ae"
C_CURRENT = "#e53935"
C_PATH = "#2e7d32"
C_START = "#1e88e5"


def _graph_axes(ax, problem: GraphProblem):
    for a, nbrs in problem.graph.items():
        for b in nbrs:
            if a < b:
                (x1, y1), (x2, y2) = problem.locations[a], problem.locations[b]
                ax.plot([x1, x2], [y1, y2], color="#cfcfd4", lw=1.0, zorder=1)
    ax.set_aspect("equal")
    ax.axis("off")


def draw_graph_step(ax, problem: GraphProblem, step: Step, show_labels=True):
    _graph_axes(ax, problem)
    frontier_states = {s for _, s in step.frontier_after}
    fvals = {}
    for p, s in step.frontier_after:
        fvals.setdefault(s, p)
    path_states = set(step.popped.solution())

    for city, (x, y) in problem.locations.items():
        if city == step.popped.state:
            color, size = C_CURRENT, 190
        elif city in path_states:
            color, size = C_PATH, 130
        elif city in frontier_states:
            color, size = C_FRONTIER, 130
        elif city in step.expanded_so_far:
            color, size = C_EXPANDED, 110
        else:
            color, size = C_UNSEEN, 70
        ax.scatter([x], [y], s=size, c=color, edgecolors="#37474f", linewidths=0.7, zorder=3)
        if show_labels:
            label = city if not isinstance(city, tuple) else str(city)
            sub = f"\n{fvals[city]:g}" if city in fvals else ""
            ax.annotate(label + sub, (x, y), textcoords="offset points", xytext=(0, 9),
                        ha="center", fontsize=7.0, zorder=4)

    # bold the path currently being considered
    p = step.popped.path()
    for a, b in zip(p, p[1:]):
        (x1, y1), (x2, y2) = problem.locations[a.state], problem.locations[b.state]
        ax.plot([x1, x2], [y1, y2], color=C_PATH, lw=2.6, zorder=2)

    head = "GOAL FOUND" if step.is_goal else f"pop {step.popped.state}"
    ax.set_title(f"Step {step.i}: {head}  (f={step.priority:g}, g={step.popped.path_cost:g})",
                 fontsize=9)


def plot_search_panels(problem: GraphProblem, trace: list[Step], title: str,
                       n_panels: int = 9, outfile: str | None = None):
    """A contact sheet of the first N iterations — the workhorse lecture figure."""
    steps = trace[:n_panels]
    cols = 3
    rows = math.ceil(len(steps) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4.6 * cols, 4.0 * rows))
    axes = axes.ravel() if hasattr(axes, "ravel") else [axes]
    for ax, step in zip(axes, steps):
        draw_graph_step(ax, problem, step)
    for ax in axes[len(steps):]:
        ax.axis("off")

    legend = [
        Patch(facecolor=C_CURRENT, edgecolor="#37474f", label="just popped"),
        Patch(facecolor=C_FRONTIER, edgecolor="#37474f", label="on frontier (f shown)"),
        Patch(facecolor=C_EXPANDED, edgecolor="#37474f", label="already expanded"),
        Patch(facecolor=C_PATH, edgecolor="#37474f", label="path to popped node"),
        Patch(facecolor=C_UNSEEN, edgecolor="#37474f", label="not yet reached"),
    ]
    fig.legend(handles=legend, loc="lower center", ncol=5, frameon=False, fontsize=9)
    fig.suptitle(title, fontsize=13, y=0.995)
    fig.tight_layout(rect=[0, 0.045, 1, 0.975])
    if outfile:
        fig.savefig(outfile, dpi=140)
        plt.close(fig)
        return outfile
    return fig


def plot_grid_comparison(grid: list[str], outfile: str | None = None):
    """Side-by-side expanded-node maps: this is the figure students remember."""
    names = ["Breadth-First  f = depth", "Uniform-Cost   f = g",
             "Depth-First    f = -depth"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
    for ax, name in zip(axes, names):
        problem = GridProblem(grid)
        node, trace = best_first_search(problem, ALGORITHMS[name](problem))
        expanded = set(trace[-1].expanded_so_far)
        frontier = {s for _, s in trace[-1].frontier_after}
        path = set(node.solution()) if node is not FAILURE else set()

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
        cost = node.path_cost if node is not FAILURE else float("inf")
        ax.set_title(f"{name}\nexpanded {len(trace)} nodes | path cost {cost:g}", fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle("Best-first framework with three lecture evaluation functions — grey = nodes expanded", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
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
        print("ipywidgets not installed — run `pip install ipywidgets`, "
              "or use plot_search_panels() instead.")
        return

    def show(i=1):
        fig, ax = plt.subplots(figsize=(7.5, 6.5))
        draw_graph_step(ax, problem, trace[i - 1])
        display(fig)
        plt.close(fig)

    return interact(show, i=IntSlider(min=1, max=len(trace), step=1, value=1,
                                      description="iteration"))


# ====================================================================
# PART 7 — Problem instances
# ====================================================================

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
    """Return a topology-preserving graph with fresh symmetric positive costs."""
    rng = rng or random.Random()
    out = {state: {} for state in graph}
    assigned = {}
    for state, neighbors in graph.items():
        for neighbor in neighbors:
            edge = frozenset((state, neighbor))
            if edge not in assigned:
                assigned[edge] = rng.randint(low, high)
            out[state][neighbor] = assigned[edge]
    return out


def romania_problem(initial="Arad", goal="Bucharest",
                    rng: random.Random | None = None) -> GraphProblem:
    graph = randomized_graph_costs(ROMANIA_GRAPH, 10, 250, rng)
    return GraphProblem(initial, goal, graph, ROMANIA_LOCATIONS)


def _build_maze() -> list[str]:
    """A long barrier (only gap at the bottom) plus a concave 'cup' around the
    goal. Chosen so the *expansion counts* separate dramatically:
    different frontier-ordering rules explore the map in visibly different ways.
    """
    R, C = 19, 43
    g = [["."] * C for _ in range(R)]
    for r in range(0, 14):                      # barrier; gap at rows 14-18
        g[r][20] = "#"
    for c in range(28, 38):                     # cup enclosing the goal
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


def tree_problem(rng: random.Random | None = None) -> GraphProblem:
    rng = rng or random.Random()
    graph = {state: {} for state in TREE_LOCATIONS}
    for parent, children in TREE_GRAPH.items():
        for child in children:
            cost = rng.randint(1, 20)
            graph[parent][child] = cost
            graph[child][parent] = cost
    return GraphProblem("A", "O", graph, TREE_LOCATIONS)


def multi_goal_tree_problem() -> MultiGoalGraphProblem:
    """Tree with two goals: H and O. DFS reaches H first and stops."""
    p = tree_problem()
    return MultiGoalGraphProblem("A", {"H", "O"}, p.graph, p.locations)


# ====================================================================
# PART 8 — Demos
# ====================================================================


def demo_romania():
    """Run two lecture-scope Romania demonstrations with independent costs."""
    for label, maker, filename in (
        ("Breadth-first", f_breadth_first, "01_breadth_first_romania.png"),
        ("Uniform-cost", f_uniform_cost, "02_uniform_cost_romania.png"),
    ):
        p = romania_problem("Arad", "Bucharest")
        print(f"\n### {label} on Romania: Arad -> Bucharest")
        node, trace = best_first_search(p, maker(p))
        print_trace(trace)
        out = plot_search_panels(
            p, trace, f"{label}: Arad to Bucharest (random action costs)",
            n_panels=6, outfile=OUTPUT_DIR / filename,
        )
        print("wrote", out)
        print(f"Cost {node.path_cost:g} via {' -> '.join(node.solution())}")


def demo_compare():
    print("\n### One function, three lecture f-values — Arad -> Bucharest")
    comparison_table(lambda: romania_problem("Arad", "Bucharest"))


def demo_grid():
    print("\n### Grid maze: watch how much of the map each f explores")
    out = plot_grid_comparison(MAZE, outfile=OUTPUT_DIR / "03_grid_comparison.png")
    print("wrote", out)
    comparison_table(lambda: GridProblem(MAZE))


def demo_tree():
    """Create fringe-by-fringe graphics for the classroom search tree."""
    for name, maker in ALGORITHMS.items():
        p = tree_problem()
        node, trace = best_first_search(p, maker(p))
        filename = name.split()[0].lower().replace("-", "_")
        out = plot_search_panels(
            p, trace,
            f"{name}: fringe after each expansion (goal O)",
            n_panels=min(9, len(trace)),
            outfile=OUTPUT_DIR / f"tree_{filename}.png",
        )
        print("wrote", out)


def demo_bfs_window():
    """Open a window that steps through breadth-first search on the tree."""
    p = tree_problem()
    _, trace = best_first_search(p, f_breadth_first(p))
    index = [0]

    fig, ax = plt.subplots(figsize=(9, 6))
    set_window_title(fig)
    fig.subplots_adjust(bottom=0.16)

    def draw():
        ax.clear()
        draw_graph_step(ax, p, trace[index[0]])
        ax.set_title(
            f"Breadth-first search — step {index[0] + 1} of {len(trace)}\n"
            "Formula: f(n) = depth(n) — shallowest nodes first\n"
            "Red = popped | Orange = fringe/frontier | Gray = expanded"
        )
        fig.canvas.draw_idle()

    previous_ax = fig.add_axes((0.30, 0.03, 0.16, 0.07))
    next_ax = fig.add_axes((0.54, 0.03, 0.16, 0.07))
    previous = Button(previous_ax, "Previous")
    next_button = Button(next_ax, "Next")

    def go_previous(_event):
        index[0] = max(0, index[0] - 1)
        draw()

    def go_next(_event):
        index[0] = min(len(trace) - 1, index[0] + 1)
        draw()

    previous.on_clicked(go_previous)
    next_button.on_clicked(go_next)
    draw()
    plt.show()


def _search_window(problem, f, algorithm_name):
    """Open a Previous/Next window for one search strategy."""
    _, trace = best_first_search(problem, f)
    index = [0]
    fig, ax = plt.subplots(figsize=(9, 6))
    set_window_title(fig)
    fig.subplots_adjust(bottom=0.16)

    def draw():
        ax.clear()
        draw_graph_step(ax, problem, trace[index[0]])
        ax.set_title(
            f"{algorithm_name} — step {index[0] + 1} of {len(trace)}\n"
            "Red = popped | Orange = fringe/frontier | Gray = expanded"
        )
        fig.canvas.draw_idle()

    previous = Button(fig.add_axes((0.30, 0.03, 0.16, 0.07)), "Previous")
    next_button = Button(fig.add_axes((0.54, 0.03, 0.16, 0.07)), "Next")
    previous.on_clicked(lambda _event: (index.__setitem__(0, max(0, index[0] - 1)), draw()))
    next_button.on_clicked(lambda _event: (index.__setitem__(0, min(len(trace) - 1, index[0] + 1)), draw()))
    draw()
    plt.show()


def demo_uniform_window():
    p = tree_problem()
    _search_window(p, f_uniform_cost(p),
                   "Uniform-cost search — f(n) = g(n)\nlowest path cost first")


def demo_depth_window():
    p = tree_problem()
    _search_window(p, f_depth_first(p),
                   "Depth-first search — f(n) = −depth(n)\ndeepest available node first")


def demo_depth_limited_window():
    p = tree_problem()
    _search_window(p, lambda n: -n.depth() if n.depth() <= 2 else float("inf"),
                   "Depth-limited search — depth(n) ≤ 2\nDFS restricted to the depth limit")


def demo_iterative_window():
    p = tree_problem()
    _search_window(p, f_depth_first(p),
                   "Iterative deepening — depth limits 0, 1, 2, …\nDFS restarted at each limit")


def demo_bidirectional_window():
    p = tree_problem()
    _search_window(p, f_breadth_first(p),
                   "Bidirectional search — f(n) = depth(n)\nfrontiers grow from start and goal")


def demo_multi_goal_dfs_window():
    """Show that DFS returns the first goal and stops before the second."""
    p = multi_goal_tree_problem()
    node, trace = best_first_search(p, f_depth_first(p))
    print("DFS goals:", sorted(p.goals))
    print("First goal found:", node.state)
    print("The search stops here; it does not return the other goal in this run.")
    _search_window(
        p, f_depth_first(p),
        "DFS with goals H and O — stops at first goal"
    )


def demo_search_window():
    """Open one window with buttons for every available search strategy."""
    p = tree_problem()

    def make_choices(problem):
        return {
        "Breadth-first": (f_breadth_first(problem), "f(n) = depth(n) — shallowest first"),
        "Uniform-cost": (f_uniform_cost(problem), "f(n) = g(n) — lowest path cost first"),
        "Depth-first": (f_depth_first(problem), "f(n) = −depth(n) — deepest first"),
        "Depth-limited": (lambda n: -n.depth() if n.depth() <= 2 else float("inf"),
                          "depth(n) ≤ 2 — DFS with a depth limit"),
        "Iterative deepening": (f_depth_first(problem), "limits 0, 1, 2, … — repeated DFS"),
        "Bidirectional": (f_breadth_first(problem), "frontiers grow from start and goal"),
    }

    choices = make_choices(p)
    note_formulas = {
        "Breadth-first": "f(n) = depth(n)",
        "Uniform-cost": "f(n) = g(n)",
        "Depth-first": "f(n) = −depth(n)",
        "Depth-limited": "depth(n) ≤ 2",
        "Iterative deepening": "depth limits: 0, 1, 2, …",
        "Bidirectional": "f(n) = depth(n)",
    }

    notes = {
        "Breadth-first":
            "A minimum queue selects the shallowest node first.",

        "Uniform-cost":
            "The cost from the start node is used. Lowest accumulated cost wins.",

        "Depth-first": (
            "A is depth 0, so its priority is 0. B and C are depth 1, "
            "so their priorities are −1. Depth 2 produces −2, which is "
            "smaller than −1, so deeper nodes are selected first. The "
            "negative value is not a cost or an error; it makes a minimum "
            "queue behave like DFS."
        ),

        "Depth-limited":
            "DFS is allowed only while the node depth is within the selected "
            "limit. Nodes beyond the limit are not expanded.",

        "Iterative deepening":
            "DFS repeats with progressively larger depth limits until the "
            "goal is found.",

        "Bidirectional":
            "Two frontiers grow toward one another: one from the start and "
            "one from the goal.",

    }
    current = {"name": "Breadth-first", "index": 0, "trace": []}
    fig, ax = plt.subplots(figsize=(12, 7))
    set_window_title(fig)
    fig.subplots_adjust(left=0.24, right=0.68, bottom=0.16)
    formula_text = fig.text(0.72, 0.88, "", va="top", fontsize=11,
                             color="green", fontweight="bold",
                             wrap=True)
    # Thin vector brace spanning the four tree tiers. The coordinates are
    # figure-relative, so the brace remains aligned when the window is resized.
    # Reduce ``width`` to make it even skinnier; reduce ``linewidth`` for a
    # finer stroke.
    tier_bracket = add_figure_curly_brace(
        fig,
        x=0.222,
        y0=0.395,
        y1=0.705,
        width=0.012,
        linewidth=1.8,
        color="#777777",
    )
    tier_label = fig.text(0.205, 0.52, "m tiers", va="center", ha="center",
                          rotation=90, fontsize=9, color="#333333")
    notes_title_text = fig.text(
        0.72, 0.40, "NOTES",
        va="top",
        fontsize=9,
        color="#000000",
    )
    notes_formula_text = fig.text(
        0.72, 0.375, "",
        va="top",
        fontsize=9,
        color="blue",
    )
    notes_explanation_text = fig.text(
        0.72, 0.350, "",
        va="top",
        fontsize=9,
        color="#000000",
        wrap=True,
    )
    selection_text = fig.text(
        0.72, 0.295, "",
        va="top",
        fontsize=9,
        color="#000000",
        wrap=True,
    )
    tree_notation_text = fig.text(
        0.72, 0.235,
        "Tree notation: b = branching factor; m = maximum depth.",
        va="top",
        fontsize=9,
        color="#000000",
        wrap=True,
    )
    fringe_text = fig.text(0.72, 0.72, "", va="top", fontsize=10,
                           bbox={"facecolor": "#fff3e0", "edgecolor": "#f57c00"})

    def select(name):
        nonlocal p, choices
        p = tree_problem()
        choices = make_choices(p)
        current["name"] = name
        current["index"] = 0
        _, current["trace"] = best_first_search(p, choices[name][0])
        draw()

    def draw():
        trace = current["trace"]
        if not trace:
            _, trace = best_first_search(p, choices[current["name"]][0])
            current["trace"] = trace
        ax.clear()
        draw_graph_step(ax, p, trace[current["index"]])
        # Align each branching-growth label to the corresponding tree level.
        # x is expressed in axes coordinates, while y uses the tree's data
        # coordinates. This keeps the labels attached to A, B/C, D-G, and
        # H-O when the window is resized.
        level_labels = (
            (4, "1 node"),
            (3, "b nodes"),
            (2, "b² nodes"),
            (1, "bᵐ nodes"),
        )
        level_transform = ax.get_yaxis_transform()
        for y, label in level_labels:
            ax.text(
                1.02,
                y,
                label,
                transform=level_transform,
                va="center",
                ha="left",
                fontsize=9,
                color="#333333",
                clip_on=False,
            )
        ax.set_title(
            f"{current['name']} — step {current['index'] + 1} of {len(trace)}\n"
            "Red = popped | Orange = fringe | Gray = expanded"
        )
        fringe = trace[current["index"]].frontier_after
        calculations = "; ".join(
            f"f({state}) = {priority:g}" for priority, state in fringe
        )
        if not calculations:
            calculations = "No nodes currently in the fringe"
        formula_text.set_text(
            "FORMULA\n" + choices[current["name"]][1]
            + "\n\nCURRENT FRINGE CALCULATIONS\n" + calculations
        )
        notes_formula_text.set_text(
            note_formulas[current["name"]]
        )
        notes_explanation_text.set_text(
            notes[current["name"]]
        )

        if fringe:
            next_priority, next_state = fringe[0]
            selection_text.set_text(
                f"The next fringe node selected will be {next_state} "
                f"because it has the smallest priority: {next_priority:g}."
            )
        else:
            selection_text.set_text(
                "The fringe is empty."
            )
        if fringe:
            contents = "\n".join(f"{state}: priority {priority:g}" for priority, state in fringe)
        else:
            contents = "(empty)"
        fringe_text.set_text("FRINGE / FRONTIER\n" + contents)
        fig.canvas.draw_idle()

    names = list(choices)
    buttons = []  # Keep Button objects alive so every callback remains active.
    for row, name in enumerate(names):
        button = Button(fig.add_axes((0.02, 0.82 - row * 0.09, 0.18, 0.06)), name)
        button.on_clicked(lambda _event, selected=name: select(selected))
        buttons.append(button)
    previous = Button(fig.add_axes((0.36, 0.03, 0.16, 0.07)), "Previous")
    next_button = Button(fig.add_axes((0.58, 0.03, 0.16, 0.07)), "Next")
    previous.on_clicked(lambda _event: (current.__setitem__("index", max(0, current["index"] - 1)), draw()))
    next_button.on_clicked(lambda _event: (current.__setitem__("index", min(len(current["trace"]) - 1, current["index"] + 1)), draw()))
    buttons.extend([previous, next_button])
    select("Breadth-first")
    plt.show()


def draw_romania_step(ax, problem: GraphProblem, step: Step):
    """Draw one polished Romania-search iteration."""
    ax.clear()
    ax.set_facecolor("#fbfcfe")

    frontier_states = {state for _, state in step.frontier_after}
    frontier_values = {}
    for priority, state in step.frontier_after:
        frontier_values.setdefault(state, priority)

    expanded_states = set(step.expanded_so_far)
    path_nodes = step.popped.path()
    path_states = {node.state for node in path_nodes}
    path_edges = {
        frozenset((a.state, b.state))
        for a, b in zip(path_nodes, path_nodes[1:])
    }

    # Roads and action costs.
    drawn_edges = set()
    for city, neighbors in problem.graph.items():
        for neighbor, cost in neighbors.items():
            edge_key = frozenset((city, neighbor))
            if edge_key in drawn_edges:
                continue
            drawn_edges.add(edge_key)

            x1, y1 = problem.locations[city]
            x2, y2 = problem.locations[neighbor]
            on_path = edge_key in path_edges

            ax.plot(
                [x1, x2], [y1, y2],
                color=C_PATH if on_path else "#cfd4dc",
                linewidth=3.2 if on_path else 1.25,
                zorder=1,
            )

            mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
            ax.text(
                mx, my, f"{cost:g}",
                fontsize=7.2,
                color="#4b5563",
                ha="center",
                va="center",
                bbox={
                    "facecolor": "#ffffff",
                    "edgecolor": "#d1d5db",
                    "linewidth": 0.4,
                    "alpha": 0.95,
                    "boxstyle": "round,pad=0.14",
                },
                zorder=2,
            )

    # Cities.
    for city, (x, y) in problem.locations.items():
        if city == step.popped.state:
            color, size, lw = C_CURRENT, 245, 1.4
        elif city in path_states:
            color, size, lw = C_PATH, 175, 1.1
        elif city in frontier_states:
            color, size, lw = C_FRONTIER, 175, 1.1
        elif city in expanded_states:
            color, size, lw = C_EXPANDED, 145, 1.0
        elif city == problem.initial:
            color, size, lw = C_START, 155, 1.1
        elif city == problem.goal:
            color, size, lw = "#8e24aa", 155, 1.1
        else:
            color, size, lw = C_UNSEEN, 105, 0.9

        ax.scatter(
            [x], [y],
            s=size,
            c=color,
            edgecolors="#374151",
            linewidths=lw,
            zorder=4,
        )

        label_lines = [city]
        if city in frontier_values:
            label_lines.append(f"f={frontier_values[city]:g}")
        if city == problem.initial:
            label_lines.append("START")
        if city == problem.goal:
            label_lines.append("GOAL")

        ax.annotate(
            "\n".join(label_lines),
            (x, y),
            xytext=(0, 11),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7.8,
            color="#111827",
            fontweight="bold" if city in {problem.initial, problem.goal, step.popped.state} else "normal",
            zorder=5,
        )

    ax.set_aspect("equal")
    ax.set_xlim(50, 595)
    ax.set_ylim(240, 605)
    ax.axis("off")


def demo_romania_search_window():
    """Open an interactive Romania state-space visualizer with readable panels."""
    problem = romania_problem("Arad", "Bucharest")

    def make_romania_choices(problem):
        return {
            "Breadth-first": {
                "f": f_breadth_first(problem),
                "formula": "priority(n) = depth(n)",
                "description": "Select the shallowest frontier node first.",
                "priority_note": (
                    "Priority is the ordering key used by the minimum-priority queue. "
                    "The node with the smallest value is popped next. For breadth-first "
                    "search, smaller depth means earlier selection."
                ),
            },
            "Uniform-cost": {
                "f": f_uniform_cost(problem),
                "formula": "priority(n) = g(n)",
                "description": "Select the lowest accumulated path cost.",
                "priority_note": (
                    "For uniform-cost search, priority equals g(n), the total action "
                    "cost from Arad to node n. The smallest accumulated cost is selected."
                ),
            },
            "Depth-first": {
                "f": f_depth_first(problem),
                "formula": "priority(n) = -depth(n)",
                "description": "Select the deepest available frontier node first.",
                "priority_note": (
                    "Canonical depth-first search uses a LIFO stack. This shared "
                    "minimum-priority implementation uses -depth(n), so deeper nodes "
                    "have smaller, more negative priorities and are selected first."
                ),
            },
        }

    choices = make_romania_choices(problem)
    current = {"name": "Breadth-first", "trace": [], "solution": FAILURE, "index": 0}

    fig = plt.figure(figsize=(15.5, 9.2), facecolor="#f4f6f8")
    set_window_title(fig, "COMP 469 - Romania State-Space Search Visualizer")

    ax = fig.add_axes((0.17, 0.25, 0.55, 0.62), facecolor="#fbfcfe")
    info_ax = fig.add_axes((0.745, 0.10, 0.24, 0.80), facecolor="#ffffff")
    detail_ax = fig.add_axes((0.17, 0.055, 0.55, 0.155), facecolor="#ffffff")

    for panel in (info_ax, detail_ax):
        panel.set_xticks([])
        panel.set_yticks([])
        for spine in panel.spines.values():
            spine.set_edgecolor("#d1d5db")
            spine.set_linewidth(1.0)

    fig.text(0.45, 0.955, "Romania State-Space Search: Arad to Bucharest",
             ha="center", va="top", fontsize=16, fontweight="bold", color="#111827")

    algorithm_text = info_ax.text(0.05, 0.965, "", transform=info_ax.transAxes,
                                  va="top", fontsize=9.2, fontweight="bold",
                                  color="#166534", linespacing=1.2)
    step_text = info_ax.text(0.05, 0.705, "", transform=info_ax.transAxes,
                             va="top", fontsize=9.1, color="#111827", linespacing=1.25)
    frontier_text = info_ax.text(0.05, 0.505, "", transform=info_ax.transAxes,
                                 va="top", fontsize=8.2, family="monospace",
                                 color="#111827",
                                 bbox={"facecolor": "#fff7ed", "edgecolor": "#fb923c",
                                       "linewidth": 1.0, "boxstyle": "round,pad=0.45"})
    children_text = info_ax.text(0.05, 0.255, "", transform=info_ax.transAxes,
                                 va="top", fontsize=7.9, family="monospace",
                                 color="#111827", linespacing=1.15)

    calculation_text = detail_ax.text(0.02, 0.92, "", transform=detail_ax.transAxes,
                                      va="top", fontsize=7.8, family="monospace",
                                      color="#111827",
                                      bbox={"facecolor": "#eef6ff", "edgecolor": "#3b82f6",
                                            "linewidth": 0.9, "boxstyle": "round,pad=0.4"})
    solution_text = detail_ax.text(0.56, 0.92, "", transform=detail_ax.transAxes,
                                   va="top", fontsize=8.2, color="#111827",
                                   linespacing=1.18)

    legend = [
        Patch(facecolor=C_CURRENT, edgecolor="#374151", label="popped now"),
        Patch(facecolor=C_FRONTIER, edgecolor="#374151", label="frontier"),
        Patch(facecolor=C_EXPANDED, edgecolor="#374151", label="expanded"),
        Patch(facecolor=C_PATH, edgecolor="#374151", label="current path"),
        Patch(facecolor=C_UNSEEN, edgecolor="#374151", label="unreached"),
    ]
    fig.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.45, 0.215),
               ncol=5, frameon=False, fontsize=8.7)

    def run_selected_algorithm(name):
        nonlocal problem, choices
        problem = romania_problem("Arad", "Bucharest")
        choices = make_romania_choices(problem)
        current["name"] = name
        current["index"] = 0
        solution, trace = best_first_search(problem, choices[name]["f"])
        current["solution"] = solution
        current["trace"] = trace
        draw()

    def priority_calculation(node):
        depth = node.depth()
        g = node.path_cost
        if current["name"] == "Breadth-first":
            return f"depth={depth}, g={g:g} -> priority={depth}"
        if current["name"] == "Uniform-cost":
            return f"depth={depth}, g={g:g} -> priority={g:g}"
        return f"depth={depth}, g={g:g} -> priority={-depth}"

    def draw():
        trace = current["trace"]
        if not trace:
            return

        index = current["index"]
        step = trace[index]
        draw_romania_step(ax, problem, step)
        choice = choices[current["name"]]

        wrapped_note = textwrap.fill(choice["priority_note"], width=39)
        algorithm_text.set_text(
            f"{current['name']}\n{choice['formula']}\n{choice['description']}\n\n"
            f"WHAT PRIORITY MEANS\n{wrapped_note}"
        )
        step_text.set_text(
            f"ITERATION {index + 1} OF {len(trace)}\n"
            f"Popped node: {step.popped.state}\n"
            f"Priority key: {step.priority:g}\n"
            f"Path cost g(n): {step.popped.path_cost:g}\n"
            f"Depth: {step.popped.depth()}\n"
            f"Status: {'GOAL FOUND' if step.is_goal else 'Searching'}"
        )

        if step.frontier_after:
            lines = [f"{state:<11} p={priority:g}" for priority, state in step.frontier_after[:8]]
            if len(step.frontier_after) > 8:
                lines.append(f"... {len(step.frontier_after) - 8} more")
            frontier_body = "\n".join(lines)
        else:
            frontier_body = "(empty)"
        frontier_text.set_text("FRONTIER - NEXT POP ORDER\n" + frontier_body)

        if step.children:
            lines = [f"{child.state:<11} g={child.path_cost:<5g} {verdict}"
                     for child, verdict in step.children[:8]]
            if len(step.children) > 8:
                lines.append(f"... {len(step.children) - 8} more")
            child_body = "\n".join(lines)
        else:
            child_body = "(goal reached; no expansion)" if step.is_goal else "(none)"
        children_text.set_text("CHILD GENERATION\n" + child_body)

        reached_nodes = {}
        for prior_step in trace[: index + 1]:
            reached_nodes[prior_step.popped.state] = prior_step.popped
            for child, _verdict in prior_step.children:
                reached_nodes[child.state] = child

        calc_lines = ["PRIORITY CALCULATION",
                      f"Popped {step.popped.state}: {priority_calculation(step.popped)}"]
        if step.frontier_after:
            calc_lines.append("Next candidates:")
            for priority, state in step.frontier_after[:3]:
                node = reached_nodes.get(state)
                calc_lines.append(f"{state}: {priority_calculation(node) if node else f'priority={priority:g}'}")
        else:
            calc_lines.append("No remaining frontier candidates.")
        calculation_text.set_text("\n".join(calc_lines))

        solution = current["solution"]
        final_path = " -> ".join(solution.solution()) if solution is not FAILURE else "No solution"
        final_cost = f"{solution.path_cost:g}" if solution is not FAILURE else "infinity"
        current_path = " -> ".join(step.popped.solution())
        next_choice = (f"{step.frontier_after[0][1]} (priority {step.frontier_after[0][0]:g})"
                       if step.frontier_after else "none")
        solution_text.set_text(
            "PATH AND RESULT\n"
            f"Current: {textwrap.fill(current_path, width=34)}\n"
            f"Next: {next_choice}\n"
            f"Final: {textwrap.fill(final_path, width=34)}\n"
            f"Cost: {final_cost}   Iterations: {len(trace)}"
        )

        ax.set_title(
            f"{current['name']} - Step {index + 1} of {len(trace)}\n"
            "Road labels = action costs; city labels = frontier priorities",
            fontsize=11.2, color="#1f2937", pad=10,
        )
        fig.canvas.draw_idle()

    buttons = []
    fig.text(0.025, 0.89, "SEARCH ALGORITHMS", fontsize=9.5,
             fontweight="bold", color="#374151")
    for row, name in enumerate(choices):
        button_ax = fig.add_axes((0.02, 0.80 - row * 0.09, 0.125, 0.058))
        button = Button(button_ax, name, color="#e5e7eb", hovercolor="#d1d5db")
        button.label.set_fontsize(9.0)
        button.on_clicked(lambda _event, selected=name: run_selected_algorithm(selected))
        buttons.append(button)

    previous_ax = fig.add_axes((0.31, 0.005, 0.13, 0.04))
    next_ax = fig.add_axes((0.47, 0.005, 0.13, 0.04))
    previous_button = Button(previous_ax, "Previous", color="#e5e7eb", hovercolor="#d1d5db")
    next_button = Button(next_ax, "Next", color="#e5e7eb", hovercolor="#d1d5db")

    def previous_step(_event):
        current["index"] = max(0, current["index"] - 1)
        draw()

    def next_step(_event):
        current["index"] = min(len(current["trace"]) - 1, current["index"] + 1)
        draw()

    previous_button.on_clicked(previous_step)
    next_button.on_clicked(next_step)
    buttons.extend([previous_button, next_button])
    fig._romania_buttons = buttons
    run_selected_algorithm("Breadth-first")
    plt.show()


DEMOS = {"romania": demo_romania, "compare": demo_compare,
         "grid": demo_grid, "tree": demo_tree, "bfs-window": demo_bfs_window,
         "uniform-window": demo_uniform_window,
         "depth-window": demo_depth_window, "depth-limited-window": demo_depth_limited_window,
         "iterative-window": demo_iterative_window, "bidirectional-window": demo_bidirectional_window,
         "search-window": demo_search_window,
         "romania-search-window": demo_romania_search_window,
         "multi-goal-dfs-window": demo_multi_goal_dfs_window}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Best-first search visualizer (AIMA Fig 3.7)")
    ap.add_argument("--demo", choices=list(DEMOS) + ["all"], default="all")
    args = ap.parse_args()
    if args.demo == "all":
        for fn in DEMOS.values():
            fn()
    else:
        DEMOS[args.demo]()
