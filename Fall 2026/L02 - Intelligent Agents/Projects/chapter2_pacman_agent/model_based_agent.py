"""Part 3 - Model-based reflex agent (AIMA 4e Figures 2.11 / 2.12).

This agent adds exactly one thing on top of Part 2: internal state,
updated every turn from the percept sequence, that lets it distinguish "I
have already cleared this tile" from "this tile just happens to be
empty". It is still a REFLEX agent -- action selection is still a short
list of condition-action rules, not a scored search over alternatives
(that upgrade is Part 5). The rules just get to consult memory as one
more condition now.

Rules 1-3 below (ghost avoidance, eating a frightened ghost, taking an
adjacent pellet) are carried over from Part 2 -- you already built this
logic once, so it is filled in for you. What is new, and what you TODO
here, is the internal state itself and the rule that uses it.

TODO(CH2-3a), TODO(CH2-3b), TODO(CH2-3c) mark what to do.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from pacman.maze import DIRECTION_NAMES, MazeModel

AGENT_NAME = "model_based"


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


class ModelBasedAgent:
    percept_class = Percept

    def __init__(self, maze: MazeModel):
        self.maze = maze
        self.last_reason = "Waiting for first percept."

        # =============================================================
        # TODO(CH2-3a)  Internal state
        # =============================================================
        # A simple reflex agent has none, which is why it paces once a
        # corridor is empty. Add:
        #
        #   self.visit_counts: dict[tuple[int, int], int]
        #       how many times each tile has been occupied
        #   self.position_history: collections.deque, maxlen=4
        #       the last few tiles, so you can spot an immediate reversal
        #   self.revisit_decisions: int, starts at 0
        #   self.backtrack_decisions: int, starts at 0
        # =============================================================

    # -------------------------------------------------------------
    # TODO(CH2-3b)  Update internal state
    # -------------------------------------------------------------
    def update_internal_state(self, percept: Percept) -> None:
        """Fold this percept into memory. Called once per turn, before any
        action is chosen. Record that percept.player has been visited
        (increment its count in visit_counts) and append it to
        position_history."""
        raise NotImplementedError("CH2-3b: update_internal_state")

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        if not percept.legal_actions:
            self.last_reason = "No legal move."
            return (0, 0)

        self.update_internal_state(percept)

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

        # =============================================================
        # TODO(CH2-3c)  Use your memory
        # =============================================================
        # Rule 4: avoid reversing into the tile you occupied two turns
        # ago (self.position_history[-2], if it has at least 2 entries)
        # UNLESS that is the only safe option left. Build a
        # `non_backtrack` list from `safe` accordingly (fall back to
        # `safe` itself if excluding the backtrack tile leaves nothing).
        #
        # Rule 5: among what's left in `non_backtrack`, pick the action
        # whose landing tile has been visited the FEWEST times
        # (self.visit_counts.get(tile, 0)). Break ties by keeping the
        # first one found, iterating in percept.legal_actions order --
        # min() with a key function already does this.
        #
        # Bookkeeping: increment self.revisit_decisions if the tile you
        # end up choosing has visit_counts > 0, and increment
        # self.backtrack_decisions if it equals the two-turns-ago tile.
        #
        # Finish with: return self._commit(best_action, f"least-visited
        # ({rule})")
        # =============================================================
        raise NotImplementedError("CH2-3c: memory-driven selection")

    def _commit(self, action: tuple[int, int], rule: str) -> tuple[int, int]:
        self.last_reason = f"{DIRECTION_NAMES[action]} | rule: {rule}"
        return action
