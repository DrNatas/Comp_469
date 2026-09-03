"""Part 2 - Simple reflex agent (AIMA 4e Figure 2.10).

Every decision must be a short, ORDERED list of condition-action rules
applied to the CURRENT percept only. No internal state is allowed in this
part -- that is what Part 3 adds. Once you finish this one, run it in the
window (``python tools/play.py --agent simple_reflex``) and watch it clear
the pellets near it quickly, then pace back and forth once that corridor
is empty: it cannot tell "I already cleared this" from "this was always
empty", because both look like the same percept. That failure is exactly
why AIMA moves on to model-based reflex agents next.

TODO(CH2-2a) and TODO(CH2-2b) mark what to do.
"""

from __future__ import annotations

from dataclasses import dataclass

from pacman.maze import DIRECTION_NAMES, MazeModel

AGENT_NAME = "simple_reflex"


# =====================================================================
# TODO(CH2-2a)  The percept
# =====================================================================
# Add the three fields this agent needs and currently lacks, using these
# exact names:
#   current_direction:          tuple[int, int]
#   released_ghosts:            tuple[tuple[int, int], ...]
#   frightened_time_remaining:  float
# Keep the four fields already here.
# =====================================================================
@dataclass(frozen=True)
class Percept:
    player: tuple[int, int]
    pellets: frozenset[tuple[int, int]]
    power_pellets: frozenset[tuple[int, int]]
    legal_actions: tuple[tuple[int, int], ...]

    @property
    def frightened(self) -> bool:
        """True while power-pellet mode is active. Works once you add
        frightened_time_remaining above."""
        return getattr(self, "frightened_time_remaining", 0.0) > 0.0


class SimpleReflexAgent:
    percept_class = Percept

    def __init__(self, maze: MazeModel):
        self.maze = maze
        self.last_reason = "Waiting for first percept."

    # -------------------------------------------------------------
    # TODO(CH2-2b)  The rules
    # -------------------------------------------------------------
    def choose_action(self, percept: Percept) -> tuple[int, int]:
        """Apply, in order, the first rule that fires:

          1. If there are no legal actions, set last_reason to a string
             containing "No legal" and return (0, 0).
          2. Never step onto a tile occupied by a dangerous (non-frightened)
             released ghost, UNLESS every legal action does (then you have
             no choice -- take any legal action).
          3. If frightened, and a ghost is on an adjacent (safe-filtered)
             tile, step onto it.
          4. Otherwise, if an adjacent tile has a power pellet, take it.
          5. Otherwise, if an adjacent tile has a regular pellet, take it.
          6. Otherwise, keep going in ``percept.current_direction`` if that
             is still one of your safe options.
          7. Otherwise, take the first safe action.

        Use ``self.maze.step(percept.player, action)`` to find the tile
        each action lands on. Use ``self._commit`` to set last_reason and
        return a chosen action in one place, so every branch reports the
        same way -- see its docstring.
        """
        raise NotImplementedError("CH2-2b: choose_action")

    def _commit(self, action: tuple[int, int], rule: str) -> tuple[int, int]:
        """Set last_reason to e.g. 'RIGHT | rule: adjacent pellet' and
        return action. Call this from every branch of choose_action
        instead of setting last_reason by hand in each one."""
        self.last_reason = f"{DIRECTION_NAMES[action]} | rule: {rule}"
        return action
