"""COMP 469 Lab 01 completed teaching code.

Generated as the instructor companion for the 3-hour Vacuum World agents lab.
Run with: python /tmp/COMP469_Lab01_Vacuum_World_Agents_completed_code.py
"""

# Cell 3
import random
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt

Position = Tuple[int, int]
ACTIONS = ["Suck", "Up", "Down", "Left", "Right", "NoOp"]

random.seed(469)
print("Setup complete. You are ready for Lab 01.")

# ------------------------------------------------------------------------

# Cell 6
@dataclass
class Percept:
    location: Position
    status: str


class VacuumEnvironment:
    def __init__(
        self,
        width: int = 5,
        height: int = 5,
        dirt_probability: float = 0.30,
        obstacle_probability: float = 0.0,
        start: Position = (0, 0),
        seed: Optional[int] = None,
    ):
        if seed is not None:
            random.seed(seed)

        self.width = width
        self.height = height
        self.start = start
        self.agent_location = start
        self.status: Dict[Position, str] = {}
        self.obstacles = set()
        self.score = 0
        self.steps = 0
        self.cleaned_count = 0

        for x in range(width):
            for y in range(height):
                location = (x, y)
                if location != start and random.random() < obstacle_probability:
                    self.obstacles.add(location)

        for x in range(width):
            for y in range(height):
                location = (x, y)
                if location in self.obstacles:
                    self.status[location] = "Obstacle"
                else:
                    self.status[location] = "Dirty" if random.random() < dirt_probability else "Clean"

        self.status[start] = "Clean"

    def in_bounds(self, location: Position) -> bool:
        x, y = location
        return 0 <= x < self.width and 0 <= y < self.height

    def is_accessible(self, location: Position) -> bool:
        return self.in_bounds(location) and location not in self.obstacles

    def get_percept(self) -> Percept:
        return Percept(self.agent_location, self.status[self.agent_location])

    def get_neighbors(self, location: Position) -> Dict[str, Position]:
        x, y = location
        candidates = {
            "Up": (x, y - 1),
            "Down": (x, y + 1),
            "Left": (x - 1, y),
            "Right": (x + 1, y),
        }
        return {
            action: next_location
            for action, next_location in candidates.items()
            if self.is_accessible(next_location)
        }

    def execute_action(self, action: str) -> None:
        if action not in ACTIONS:
            raise ValueError(f"Unknown action: {action}")

        self.steps += 1
        self.score -= 1

        if action == "NoOp":
            return

        if action == "Suck":
            if self.status[self.agent_location] == "Dirty":
                self.status[self.agent_location] = "Clean"
                self.score += 10
                self.cleaned_count += 1
            return

        x, y = self.agent_location
        moves = {
            "Up": (x, y - 1),
            "Down": (x, y + 1),
            "Left": (x - 1, y),
            "Right": (x + 1, y),
        }
        next_location = moves[action]

        if self.is_accessible(next_location):
            self.agent_location = next_location
        else:
            self.score -= 2

    def count_dirty_squares(self) -> int:
        return sum(1 for value in self.status.values() if value == "Dirty")

    def count_clean_squares(self) -> int:
        return sum(
            1
            for location, value in self.status.items()
            if value == "Clean" and location not in self.obstacles
        )

    def is_done(self) -> bool:
        return self.count_dirty_squares() == 0

    def copy_world(self):
        return dict(self.status), set(self.obstacles)

    def load_world(self, status: Dict[Position, str], obstacles: set) -> None:
        self.status = dict(status)
        self.obstacles = set(obstacles)
        self.agent_location = self.start
        self.score = 0
        self.steps = 0
        self.cleaned_count = 0


env = VacuumEnvironment(width=5, height=5, dirt_probability=0.35, obstacle_probability=0.10, seed=469)
print("Start:", env.agent_location)
print("Percept:", env.get_percept())
print("Dirty squares:", env.count_dirty_squares())
print("Obstacles:", len(env.obstacles))

# ------------------------------------------------------------------------

# Cell 8
def display_text(env: VacuumEnvironment) -> None:
    for y in range(env.height):
        row = []
        for x in range(env.width):
            location = (x, y)
            if location == env.agent_location:
                row.append("A")
            elif location in env.obstacles:
                row.append("#")
            elif env.status[location] == "Dirty":
                row.append("D")
            else:
                row.append(".")
        print(" ".join(row))
    print(f"Score: {env.score}, Steps: {env.steps}, Dirty left: {env.count_dirty_squares()}")


def plot_environment(env: VacuumEnvironment, title: str = "Vacuum World") -> None:
    grid = []
    for y in range(env.height):
        row = []
        for x in range(env.width):
            location = (x, y)
            if location in env.obstacles:
                row.append(2)
            elif env.status[location] == "Dirty":
                row.append(1)
            else:
                row.append(0)
        grid.append(row)

    plt.figure(figsize=(5, 5))
    plt.imshow(grid, cmap="Greys", vmin=0, vmax=2)
    ax = plt.gca()
    ax.set_xticks(range(env.width))
    ax.set_yticks(range(env.height))
    ax.set_xticks([i - 0.5 for i in range(1, env.width)], minor=True)
    ax.set_yticks([i - 0.5 for i in range(1, env.height)], minor=True)
    ax.grid(which="minor", color="black", linewidth=1)
    ax.scatter([env.agent_location[0]], [env.agent_location[1]], c="tab:blue", s=250)
    ax.set_title(title)
    plt.show()


display_text(env)
plot_environment(env, "Initial Vacuum World")

# ------------------------------------------------------------------------

# Cell 10
class Agent:
    name = "Base Agent"

    def choose_action(self, percept: Percept, environment: VacuumEnvironment) -> str:
        raise NotImplementedError


class RandomVacuumAgent(Agent):
    name = "Random Vacuum Agent"

    def choose_action(self, percept: Percept, environment: VacuumEnvironment) -> str:
        if percept.status == "Dirty":
            return "Suck"
        return random.choice(["Up", "Down", "Left", "Right"])


random_agent = RandomVacuumAgent()
print(random_agent.name, "chooses", random_agent.choose_action(env.get_percept(), env))

# ------------------------------------------------------------------------

# Cell 12
def run_simulation(
    agent: Agent,
    env: VacuumEnvironment,
    max_steps: int = 100,
    verbose: bool = False,
) -> dict:
    score_history = []
    dirty_history = []
    action_history = []

    for step in range(max_steps):
        # Get percept, choose action, execute action, and record history.
        percept = env.get_percept()
        action = agent.choose_action(percept, env)

        if action == "NoOp":
            break

        env.execute_action(action)

        score_history.append(env.score)
        dirty_history.append(env.count_dirty_squares())
        action_history.append(action)

        if verbose:
            print(f"step={step:02d} loc={percept.location} status={percept.status} action={action} score={env.score}")

        if env.is_done():
            break

    return {
        "agent": agent.name,
        "score": env.score,
        "steps": env.steps,
        "cleaned": env.cleaned_count,
        "dirty_left": env.count_dirty_squares(),
        "score_history": score_history,
        "dirty_history": dirty_history,
        "action_history": action_history,
    }


test_env = VacuumEnvironment(width=5, height=5, dirt_probability=0.35, obstacle_probability=0.0, seed=101)
test_result = run_simulation(RandomVacuumAgent(), test_env, max_steps=25)
test_result

# ------------------------------------------------------------------------

# Cell 14
class ReflexVacuumAgent(Agent):
    name = "Reflex Vacuum Agent"

    def choose_action(self, percept: Percept, environment: VacuumEnvironment) -> str:
        x, y = percept.location

        if percept.status == "Dirty":
            return "Suck"

        # Serpentine sweep: move right on even rows, left on odd rows, down at row ends.
        if y % 2 == 0:
            preferred = "Right" if x < environment.width - 1 else "Down"
        else:
            preferred = "Left" if x > 0 else "Down"

        legal_actions = environment.get_neighbors(percept.location)
        if preferred in legal_actions:
            return preferred

        # Obstacles can break the sweep, so use a deterministic fallback.
        for action in ["Right", "Down", "Left", "Up"]:
            if action in legal_actions:
                return action

        return "NoOp"


reflex_env = VacuumEnvironment(width=5, height=5, dirt_probability=0.35, obstacle_probability=0.0, seed=202)
reflex_result = run_simulation(ReflexVacuumAgent(), reflex_env, max_steps=100)
reflex_result

# ------------------------------------------------------------------------

# Cell 17
class ModelBasedVacuumAgent(Agent):
    name = "Model-Based Vacuum Agent"

    def __init__(self):
        self.visited = set()
        self.known_status: Dict[Position, str] = {}
        self.path_stack: List[Position] = []

    def action_toward(self, current: Position, target: Position) -> str:
        cx, cy = current
        tx, ty = target
        if tx == cx + 1 and ty == cy:
            return "Right"
        if tx == cx - 1 and ty == cy:
            return "Left"
        if tx == cx and ty == cy + 1:
            return "Down"
        if tx == cx and ty == cy - 1:
            return "Up"
        return "NoOp"

    def choose_action(self, percept: Percept, environment: VacuumEnvironment) -> str:
        location = percept.location
        self.visited.add(location)
        self.known_status[location] = percept.status

        if percept.status == "Dirty":
            self.known_status[location] = "Clean"
            return "Suck"

        neighbors = environment.get_neighbors(location)
        unvisited = [
            (action, next_location)
            for action, next_location in neighbors.items()
            if next_location not in self.visited
        ]

        if unvisited:
            action, next_location = unvisited[0]
            self.path_stack.append(location)
            return action

        while self.path_stack:
            previous_location = self.path_stack.pop()
            if previous_location in neighbors.values():
                return self.action_toward(location, previous_location)

        return "NoOp"


model_env = VacuumEnvironment(width=5, height=5, dirt_probability=0.35, obstacle_probability=0.10, seed=303)
model_result = run_simulation(ModelBasedVacuumAgent(), model_env, max_steps=100)
model_result

# ------------------------------------------------------------------------

# Cell 20
class GoalBasedVacuumAgent(Agent):
    name = "Goal-Based Vacuum Agent"

    def choose_action(self, percept: Percept, environment: VacuumEnvironment) -> str:
        if percept.status == "Dirty":
            return "Suck"

        dirty_locations = [
            location
            for location, status in environment.status.items()
            if status == "Dirty"
        ]

        if not dirty_locations:
            return "NoOp"

        path = self.bfs_to_nearest_dirty(percept.location, dirty_locations, environment)

        if path:
            return path[0]

        return "NoOp"

    def bfs_to_nearest_dirty(
        self,
        start: Position,
        dirty_locations: List[Position],
        environment: VacuumEnvironment,
    ) -> List[str]:
        dirty_set = set(dirty_locations)
        frontier = deque([(start, [])])
        visited = {start}

        while frontier:
            location, path_so_far = frontier.popleft()

            if location in dirty_set:
                return path_so_far

            for action, next_location in environment.get_neighbors(location).items():
                if next_location not in visited:
                    visited.add(next_location)
                    frontier.append((next_location, path_so_far + [action]))

        return []


goal_env = VacuumEnvironment(width=5, height=5, dirt_probability=0.35, obstacle_probability=0.10, seed=404)
goal_result = run_simulation(GoalBasedVacuumAgent(), goal_env, max_steps=100)
goal_result

# ------------------------------------------------------------------------

# Cell 23
def evaluate_agents(
    agent_factories,
    trials: int = 30,
    max_steps: int = 100,
    width: int = 5,
    height: int = 5,
    dirt_probability: float = 0.35,
    obstacle_probability: float = 0.10,
) -> List[dict]:
    rows = []

    for trial in range(trials):
        base_env = VacuumEnvironment(
            width=width,
            height=height,
            dirt_probability=dirt_probability,
            obstacle_probability=obstacle_probability,
            seed=1000 + trial,
        )
        status, obstacles = base_env.copy_world()

        for make_agent in agent_factories:
            env = VacuumEnvironment(width=width, height=height, dirt_probability=0.0, obstacle_probability=0.0)
            env.load_world(status, obstacles)
            agent = make_agent()
            result = run_simulation(agent, env, max_steps=max_steps)
            result["trial"] = trial
            rows.append(result)

    return rows


agent_factories = [
    lambda: RandomVacuumAgent(),
    lambda: ReflexVacuumAgent(),
    lambda: ModelBasedVacuumAgent(),
    lambda: GoalBasedVacuumAgent(),
]

results = evaluate_agents(agent_factories, trials=30, max_steps=100)
results[:4]

# ------------------------------------------------------------------------

# Cell 24
def summarize_results(results: List[dict]) -> Dict[str, dict]:
    summary = {}
    agent_names = sorted({row["agent"] for row in results})

    for agent_name in agent_names:
        rows = [row for row in results if row["agent"] == agent_name]
        summary[agent_name] = {
            "avg_score": sum(row["score"] for row in rows) / len(rows),
            "avg_steps": sum(row["steps"] for row in rows) / len(rows),
            "avg_cleaned": sum(row["cleaned"] for row in rows) / len(rows),
            "avg_dirty_left": sum(row["dirty_left"] for row in rows) / len(rows),
        }

    return summary


summary = summarize_results(results)
summary

# ------------------------------------------------------------------------

# Cell 26
def plot_summary_metric(summary: Dict[str, dict], metric: str, title: str, ylabel: str) -> None:
    names = list(summary.keys())
    values = [summary[name][metric] for name in names]

    plt.figure(figsize=(9, 4))
    plt.bar(names, values)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.show()


plot_summary_metric(summary, "avg_score", "Average Score by Agent", "Average score")
plot_summary_metric(summary, "avg_dirty_left", "Average Dirt Left by Agent", "Average dirty squares left")

# ------------------------------------------------------------------------

# Cell 29
# Extension workspace.
# Put your optional extension code here.
