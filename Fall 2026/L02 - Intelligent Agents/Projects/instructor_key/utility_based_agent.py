"""Part 5 - Utility-based agent (AIMA 4e Figure 2.14).

This agent keeps everything Part 3 (model-based reflex) has -- internal
state built from the percept sequence -- and replaces its condition-action
RULES with a single UTILITY FUNCTION: every legal action is scored on one
numeric scale that blends several competing preferences (closer food is
good, closer danger is bad, repetition is mildly bad, and so on), and the
agent takes whichever action scores highest. That is the qualitative jump
from Part 4: a goal-based agent asks "does this satisfy the goal, or get me
closer to it"; a utility-based agent asks "how good is this, all things
considered" and can trade one desideratum off against another inside a
single number.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from pacman.maze import DIRECTION_NAMES, MazeModel

AGENT_NAME = "utility_based"


@dataclass(frozen=True)
class Percept:
    player: tuple[int, int]
    current_direction: tuple[int, int]
    pellets: frozenset[tuple[int, int]]
    power_pellets: frozenset[tuple[int, int]]
    released_ghosts: tuple[tuple[int, int], ...]
    legal_actions: tuple[tuple[int, int], ...]
    frightened_time_remaining: float

    @property
    def frightened(self) -> bool:
        return self.frightened_time_remaining > 0.0


@dataclass(frozen=True)
class UtilityWeights:
    """Named preferences. This is the agent's utility function, not the
    environment's performance measure (AIMA 4e Section 2.2 keeps those
    separate on purpose; so does this codebase -- see pacman/rules.py)."""

    food_distance: float = -1.0
    regular_pellet: float = 0.0
    power_pellet: float = 0.0

    ghost_catch_frightened: float = 100.0
    ghost_close_frightened: float = 0.0     # negative: closer is *more* attractive
    ghost_collision: float = -5000.0
    ghost_one_step: float = -30.0
    ghost_two_steps: float = 0.0
    ghost_three_steps: float = -2.0
    ghost_safe_distance: float = 0.0
    ghost_safe_distance_cap: float = 0.0

    continuation: float = 0.0
    revisit_per_visit: float = -0.5
    backtrack: float = -0.5


class UtilityBasedAgent:
    percept_class = Percept

    def __init__(self, maze: MazeModel):
        self.maze = maze
        self.weights = UtilityWeights()
        self.last_reason = "Waiting for first percept."

        self.visit_counts: dict[tuple[int, int], int] = {}
        self.position_history: deque[tuple[int, int]] = deque(maxlen=4)
        self.revisit_decisions = 0
        self.backtrack_decisions = 0

    def update_internal_state(self, percept: Percept) -> None:
        position = percept.player
        self.visit_counts[position] = self.visit_counts.get(position, 0) + 1
        self.position_history.append(position)

    def evaluate_action(
        self, percept: Percept, action: tuple[int, int]
    ) -> tuple[float, dict[str, float]]:
        if action not in percept.legal_actions:
            raise ValueError(f"{action} is not in percept.legal_actions")

        w = self.weights
        landing = self.maze.step(percept.player, action)

        food = frozenset(percept.pellets) | frozenset(percept.power_pellets)
        food_distance_steps = self.maze.distance(landing, food)
        ghosts = frozenset(percept.released_ghosts)
        ghost_distance_steps = (
            self.maze.distance(landing, ghosts) if ghosts else 10_000
        )

        contributions: dict[str, float] = {}

        contributions["food_distance"] = w.food_distance * food_distance_steps
        contributions["regular_pellet"] = (
            w.regular_pellet if landing in percept.pellets else 0.0
        )
        contributions["power_pellet"] = (
            w.power_pellet if landing in percept.power_pellets else 0.0
        )

        ghost_term = 0.0
        if ghosts:
            if percept.frightened:
                if landing in ghosts:
                    ghost_term += w.ghost_catch_frightened
                else:
                    ghost_term += w.ghost_close_frightened * ghost_distance_steps
            else:
                if landing in ghosts:
                    ghost_term += w.ghost_collision
                elif ghost_distance_steps == 1:
                    ghost_term += w.ghost_one_step
                elif ghost_distance_steps == 2:
                    ghost_term += w.ghost_two_steps
                elif ghost_distance_steps == 3:
                    ghost_term += w.ghost_three_steps
                else:
                    capped = min(ghost_distance_steps, w.ghost_safe_distance_cap)
                    ghost_term += w.ghost_safe_distance * capped
        contributions["ghost"] = ghost_term

        contributions["continuation"] = (
            w.continuation if action == percept.current_direction else 0.0
        )

        revisit_count = self.visit_counts.get(landing, 0)
        contributions["revisit"] = w.revisit_per_visit * revisit_count

        two_ago = (
            self.position_history[-2] if len(self.position_history) >= 2 else None
        )
        contributions["backtrack"] = w.backtrack if landing == two_ago else 0.0

        contributions["food_distance_steps"] = float(food_distance_steps)
        contributions["ghost_distance_steps"] = float(ghost_distance_steps)
        contributions["revisit_count"] = float(revisit_count)

        weighted_keys = (
            "food_distance",
            "regular_pellet",
            "power_pellet",
            "ghost",
            "continuation",
            "revisit",
            "backtrack",
        )
        total = sum(contributions[key] for key in weighted_keys)
        return float(total), contributions

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        if not percept.legal_actions:
            self.last_reason = "No legal move."
            return (0, 0)

        self.update_internal_state(percept)

        best_action = percept.legal_actions[0]
        best_utility = float("-inf")
        best_contributions: dict[str, float] = {}

        for action in percept.legal_actions:
            utility, contributions = self.evaluate_action(percept, action)
            if utility > best_utility:
                best_utility = utility
                best_action = action
                best_contributions = contributions

        landing = self.maze.step(percept.player, best_action)
        if self.visit_counts.get(landing, 0) > 1:
            self.revisit_decisions += 1
        two_ago = (
            self.position_history[-2] if len(self.position_history) >= 2 else None
        )
        if landing == two_ago:
            self.backtrack_decisions += 1

        memory = best_contributions["revisit"] + best_contributions["backtrack"]
        self.last_reason = (
            f"{DIRECTION_NAMES[best_action]} | U={best_utility:.1f} | "
            f"food={best_contributions['food_distance_steps']:.0f} | "
            f"ghost={best_contributions['ghost_distance_steps']:.0f} | "
            f"memory={memory:.1f}"
        )
        return best_action
