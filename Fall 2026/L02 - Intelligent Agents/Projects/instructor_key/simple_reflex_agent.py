"""Part 2 - Simple reflex agent (AIMA 4e Figure 2.10).

Every decision is a short, ordered list of condition-action rules applied to
the CURRENT percept only. There is no internal state: this agent cannot
tell "I already cleared this corridor" from "this corridor was always
empty", so watch it in the window -- once the easy pellets near it are gone
it will pace back and forth. That failure mode is exactly why AIMA moves on
to model-based reflex agents next (Part 3).
"""

from __future__ import annotations

from dataclasses import dataclass

from pacman.maze import DIRECTION_NAMES, MazeModel

AGENT_NAME = "simple_reflex"


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


class SimpleReflexAgent:
    percept_class = Percept

    def __init__(self, maze: MazeModel):
        self.maze = maze
        self.last_reason = "Waiting for first percept."

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        if not percept.legal_actions:
            self.last_reason = "No legal move."
            return (0, 0)

        ghosts = set(percept.released_ghosts)
        landing = {
            action: self.maze.step(percept.player, action)
            for action in percept.legal_actions
        }

        # Rule 1: never step onto a dangerous ghost if another option exists.
        safe = [
            action
            for action, tile in landing.items()
            if percept.frightened or tile not in ghosts
        ]
        if not safe:
            safe = list(percept.legal_actions)
            rule = "cornered"
        else:
            rule = "safe"

        # Rule 2: eat an adjacent frightened ghost.
        if percept.frightened:
            for action in safe:
                if landing[action] in ghosts:
                    return self._commit(action, "eat frightened ghost")

        # Rule 3: step onto an adjacent power pellet, then an adjacent pellet.
        for action in safe:
            if landing[action] in percept.power_pellets:
                return self._commit(action, "adjacent power pellet")
        for action in safe:
            if landing[action] in percept.pellets:
                return self._commit(action, "adjacent pellet")

        # Rule 4: otherwise keep going straight if that is still safe.
        if percept.current_direction in safe:
            return self._commit(percept.current_direction, f"continue ({rule})")

        # Rule 5: otherwise take the first safe action.
        return self._commit(safe[0], f"default ({rule})")

    def _commit(self, action: tuple[int, int], rule: str) -> tuple[int, int]:
        self.last_reason = f"{DIRECTION_NAMES[action]} | rule: {rule}"
        return action
