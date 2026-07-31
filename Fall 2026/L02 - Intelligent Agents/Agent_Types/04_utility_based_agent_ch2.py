"""
COMP 469 - Chapter 2: Utility-Based Agent

The agent does not commit to an explicit goal or stored plan.  For every legal
move, it predicts a possible successor state, computes the expected utility of
that move, and selects the action with the highest value.

The example includes a simple uncertainty estimate: a visible ghost can choose
among several legal next positions, so the agent estimates the probability that
a ghost will occupy Pac-Man's candidate square on the next step.

Run from this directory:
    Windows PowerShell: py -m pip install pygame
    Windows PowerShell: py 04_utility_based_agent_ch2.py
    Linux: python3 -m venv .venv && .venv/bin/python -m pip install pygame
    Linux: .venv/bin/python 04_utility_based_agent_ch2.py
"""

from __future__ import annotations

from dataclasses import dataclass

from pacman_chapter2_engine import (
    Chapter2Agent,
    Percept,
    STOP,
    action_name,
    manhattan,
    run_agent,
)


@dataclass(frozen=True)
class UtilityBreakdown:
    action: tuple[int, int]
    immediate_reward: float
    food_progress: float
    expected_ghost_value: float
    movement_cost: float

    @property
    def total(self) -> float:
        return (
            self.immediate_reward
            + self.food_progress
            + self.expected_ghost_value
            + self.movement_cost
        )


# =============================================================================
# CHAPTER 2 AGENT PROGRAM STARTS HERE
# =============================================================================
class UtilityBasedAgent(Chapter2Agent):
    """Choose the legal action with maximum expected utility."""

    AGENT_NAME = "UTILITY-BASED AGENT"
    PROGRAM_LOCATION = "expected_utility() -> choose_action()"
    CHAPTER2_CONCEPT = "Possible outcomes -> utility -> maximum expected utility"

    def __init__(self, world):
        super().__init__(world)
        self.last_utilities: list[UtilityBreakdown] = []

    def ghost_collision_probability(
        self,
        candidate: tuple[int, int],
        percept: Percept,
    ) -> float:
        """Estimate collision probability from possible visible-ghost moves."""

        survival_probability = 1.0
        for ghost, direction in zip(
            percept.visible_ghosts,
            percept.visible_ghost_directions,
        ):
            legal = self.world.legal_actions_from(ghost)
            if not legal:
                possible_positions = [ghost]
                probabilities = [1.0]
            else:
                # Continuing in the same direction is treated as more likely.
                continuing = [action for action in legal if action == direction]
                if continuing and len(legal) > 1:
                    remaining_probability = 0.30
                    probabilities = []
                    possible_positions = []
                    for action in legal:
                        possible_positions.append(
                            self.world.successor(ghost, action)
                        )
                        if action == direction:
                            probabilities.append(0.70)
                        else:
                            probabilities.append(
                                remaining_probability / (len(legal) - 1)
                            )
                else:
                    possible_positions = [
                        self.world.successor(ghost, action)
                        for action in legal
                    ]
                    probabilities = [1.0 / len(legal)] * len(legal)

            ghost_hit_probability = sum(
                probability
                for position, probability in zip(
                    possible_positions,
                    probabilities,
                )
                if position == candidate
            )
            survival_probability *= 1.0 - ghost_hit_probability

        return 1.0 - survival_probability

    # -------------------------------------------------------------------------
    # UTILITY FUNCTION: assign desirability to one possible action outcome.
    # -------------------------------------------------------------------------
    def expected_utility(
        self,
        percept: Percept,
        action: tuple[int, int],
    ) -> UtilityBreakdown:
        candidate = self.world.successor(percept.player, action)
        food = set(percept.pellets) | set(percept.power_pellets)

        immediate_reward = 0.0
        if candidate in percept.pellets:
            immediate_reward += 10.0
        if candidate in percept.power_pellets:
            immediate_reward += 50.0
        if percept.frightened and candidate in percept.visible_ghosts:
            immediate_reward += 200.0

        # Compare how much closer this action moves Pac-Man to remaining food.
        old_food_distance = self.world.maze_distance(percept.player, food)
        new_food_distance = self.world.maze_distance(candidate, food)
        food_progress = 2.0 * (old_food_distance - new_food_distance)

        collision_probability = self.ghost_collision_probability(
            candidate,
            percept,
        )

        if percept.frightened:
            # Frightened ghosts are valuable outcomes rather than threats.
            nearest_ghost = min(
                (manhattan(candidate, ghost) for ghost in percept.visible_ghosts),
                default=10,
            )
            expected_ghost_value = max(0.0, 24.0 - 4.0 * nearest_ghost)
        else:
            expected_ghost_value = -500.0 * collision_probability
            nearest_ghost = min(
                (manhattan(candidate, ghost) for ghost in percept.visible_ghosts),
                default=10,
            )
            if nearest_ghost == 0:
                expected_ghost_value -= 1000.0
            elif nearest_ghost == 1:
                expected_ghost_value -= 250.0
            elif nearest_ghost == 2:
                expected_ghost_value -= 75.0

        movement_cost = -1.0
        if action == percept.current_direction:
            movement_cost += 0.25

        return UtilityBreakdown(
            action,
            immediate_reward,
            food_progress,
            expected_ghost_value,
            movement_cost,
        )

    # -------------------------------------------------------------------------
    # ACTION SELECTION: calculate utility for all legal actions and maximize it.
    # -------------------------------------------------------------------------
    def choose_action(self, percept: Percept) -> tuple[int, int]:
        if not percept.legal_actions:
            self.last_reason = "No legal action -> STOP"
            return STOP

        self.last_utilities = [
            self.expected_utility(percept, action)
            for action in percept.legal_actions
        ]
        best = max(self.last_utilities, key=lambda item: item.total)

        self.last_reason = (
            f"Max EU: {action_name(best.action)}={best.total:.1f} "
            f"(reward={best.immediate_reward:.1f}, "
            f"progress={best.food_progress:.1f}, "
            f"ghost={best.expected_ghost_value:.1f})"
        )
        return best.action

    def hud_lines(self) -> tuple[str, ...]:
        if not self.last_utilities:
            return ("No utility calculation yet",)
        ordered = sorted(
            self.last_utilities,
            key=lambda item: item.total,
            reverse=True,
        )
        utility_text = ", ".join(
            f"{action_name(item.action)}={item.total:.1f}"
            for item in ordered
        )
        return (f"EU scores: {utility_text}",)


# =============================================================================
# CHAPTER 2 AGENT PROGRAM ENDS HERE
# =============================================================================


if __name__ == "__main__":
    run_agent(UtilityBasedAgent)
