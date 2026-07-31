"""
COMP 469 - Chapter 2: Model-Based Reflex Agent

The agent maintains internal state and uses two explicitly labeled models:
- transition_model(): how the world changes and what the last action does,
- sensor_model(): how the current percept corrects the internal state.

After updating its state, the agent still uses condition-action rules.  It does
not formulate goals, search for a path, maximize utility, or learn parameters.

Run from this directory:
    Windows PowerShell: py -m pip install pygame
    Windows PowerShell: py 02_model_based_reflex_agent_ch2.py
    Linux: python3 -m venv .venv && .venv/bin/python -m pip install pygame
    Linux: .venv/bin/python 02_model_based_reflex_agent_ch2.py
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pacman_chapter2_engine import (
    Chapter2Agent,
    Percept,
    STOP,
    GHOST_SENSOR_RANGE,
    action_name,
    manhattan,
    run_agent,
)


@dataclass
class InternalState:
    """The agent's current best guess about relevant hidden state."""

    estimated_player: tuple[int, int] | None = None
    remembered_ghosts: dict[tuple[int, int], tuple[int, int]] = field(
        default_factory=dict
    )
    ghost_ages: dict[tuple[int, int], int] = field(default_factory=dict)
    visit_count: dict[tuple[int, int], int] = field(default_factory=dict)
    last_action: tuple[int, int] = STOP


# =============================================================================
# CHAPTER 2 AGENT PROGRAM STARTS HERE
# =============================================================================
class ModelBasedReflexAgent(Chapter2Agent):
    """Update internal state, then fire a condition-action rule."""

    AGENT_NAME = "MODEL-BASED REFLEX AGENT"
    PROGRAM_LOCATION = "update_state() -> choose_action()"
    CHAPTER2_CONCEPT = "Percept history -> internal state -> reflex rule"

    def __init__(self, world):
        super().__init__(world)
        self.state = InternalState()

    def reset_episode(self) -> None:
        self.state = InternalState()

    # -------------------------------------------------------------------------
    # TRANSITION MODEL: predicts how hidden state changes between percepts.
    # -------------------------------------------------------------------------
    def transition_model(self) -> None:
        if self.state.estimated_player is not None and self.state.last_action != STOP:
            self.state.estimated_player = self.world.successor(
                self.state.estimated_player,
                self.state.last_action,
            )

        predicted: dict[tuple[int, int], tuple[int, int]] = {}
        predicted_ages: dict[tuple[int, int], int] = {}
        for position, direction in self.state.remembered_ghosts.items():
            next_position = self.world.successor(position, direction)
            if next_position == position:
                next_position = position
                direction = STOP
            age = self.state.ghost_ages.get(position, 0) + 1
            if age <= 4:  # Forget stale guesses after four percept cycles.
                predicted[next_position] = direction
                predicted_ages[next_position] = age

        self.state.remembered_ghosts = predicted
        self.state.ghost_ages = predicted_ages

    # -------------------------------------------------------------------------
    # SENSOR MODEL: uses the current percept to correct the prediction.
    # -------------------------------------------------------------------------
    def sensor_model(self, percept: Percept) -> None:
        self.state.estimated_player = percept.player
        self.state.visit_count[percept.player] = (
            self.state.visit_count.get(percept.player, 0) + 1
        )

        # If a predicted ghost should be inside the current sensor range but is
        # not perceived there, the sensor model rejects that old prediction.
        visible_positions = set(percept.visible_ghosts)
        for remembered_position in list(self.state.remembered_ghosts):
            should_be_visible = (
                manhattan(percept.player, remembered_position)
                <= GHOST_SENSOR_RANGE
            )
            if should_be_visible and remembered_position not in visible_positions:
                self.state.remembered_ghosts.pop(remembered_position, None)
                self.state.ghost_ages.pop(remembered_position, None)

        for position, direction in zip(
            percept.visible_ghosts,
            percept.visible_ghost_directions,
        ):
            self.state.remembered_ghosts[position] = direction
            self.state.ghost_ages[position] = 0

    def update_state(self, percept: Percept) -> None:
        self.transition_model()
        self.sensor_model(percept)

    def predicted_danger_cells(self) -> set[tuple[int, int]]:
        danger: set[tuple[int, int]] = set()
        for position in self.state.remembered_ghosts:
            danger.add(position)
            for action in self.world.legal_actions_from(position):
                danger.add(self.world.successor(position, action))
        return danger

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        self.update_state(percept)

        if not percept.legal_actions:
            self.state.last_action = STOP
            self.last_reason = "RULE 1 fired: no legal action -> STOP"
            return STOP

        destinations = {
            action: self.world.successor(percept.player, action)
            for action in percept.legal_actions
        }
        danger = self.predicted_danger_cells()

        # RULE 2: IF the model predicts danger, THEN choose the first action
        # whose destination is outside predicted danger.
        if danger:
            for action in percept.legal_actions:
                if destinations[action] not in danger:
                    self.state.last_action = action
                    self.last_reason = (
                        "RULE 2 fired: internal model predicts danger -> "
                        f"{action_name(action)}"
                    )
                    return action

        # RULE 3: IF a power pellet is adjacent, THEN eat it.
        for action in percept.legal_actions:
            if destinations[action] in percept.power_pellets:
                self.state.last_action = action
                self.last_reason = (
                    f"RULE 3 fired: adjacent power pellet -> {action_name(action)}"
                )
                return action

        # RULE 4: IF a pellet is adjacent, THEN eat it.
        for action in percept.legal_actions:
            if destinations[action] in percept.pellets:
                self.state.last_action = action
                self.last_reason = (
                    f"RULE 4 fired: adjacent pellet -> {action_name(action)}"
                )
                return action

        # RULE 5: IF an unvisited successor exists, THEN explore the first one.
        for action in percept.legal_actions:
            if self.state.visit_count.get(destinations[action], 0) == 0:
                self.state.last_action = action
                self.last_reason = (
                    "RULE 5 fired: internal state marks cell unvisited -> "
                    f"{action_name(action)}"
                )
                return action

        # RULE 6: OTHERWISE choose the least-visited successor.
        action = min(
            percept.legal_actions,
            key=lambda candidate: self.state.visit_count.get(
                destinations[candidate],
                0,
            ),
        )
        self.state.last_action = action
        visits = self.state.visit_count.get(destinations[action], 0)
        self.last_reason = (
            f"RULE 6 fired: least-visited cell ({visits}) -> {action_name(action)}"
        )
        return action

    def hud_lines(self) -> tuple[str, ...]:
        return (
            f"visited={len(self.state.visit_count)}",
            f"remembered ghosts={len(self.state.remembered_ghosts)}",
            "transition model + sensor model",
        )


# =============================================================================
# CHAPTER 2 AGENT PROGRAM ENDS HERE
# =============================================================================


if __name__ == "__main__":
    run_agent(ModelBasedReflexAgent)
