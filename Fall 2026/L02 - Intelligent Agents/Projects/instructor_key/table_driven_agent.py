"""Part 1 - Table-driven agent (AIMA 4e Section 2.4, TABLE-DRIVEN-AGENT).

The whole agent is a lookup table built once, in ``__init__``, from a percept
key to an action. There are no condition-action rules and no internal state;
``choose_action`` does nothing but hash the percept and look it up.

The percept here is deliberately tiny: ``current_direction`` and
``legal_actions``. Declaring ``pellets`` or ``ghosts`` too would be legal,
but the table would need one entry per DISTINCT VALUE those fields can take,
and ``pellets`` alone has as many distinct values as there are subsets of
the maze's pellets. That is the whole point AIMA makes with this design: it
does not scale, so every other agent in this project trades the table for
something computed on the fly.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from pacman.maze import DIRECTION_NAMES, DIRECTION_ORDER, MazeModel

AGENT_NAME = "table_driven"


@dataclass(frozen=True)
class Percept:
    current_direction: tuple[int, int]
    legal_actions: tuple[tuple[int, int], ...]


def _all_nonempty_subsets(items: tuple) -> list[tuple]:
    subsets = []
    for size in range(1, len(items) + 1):
        for combo in combinations(items, size):
            subsets.append(combo)
    return subsets


class TableDrivenAgent:
    percept_class = Percept

    def __init__(self, maze: MazeModel):
        self.maze = maze
        self.last_reason = "Waiting for first percept."
        self.table: dict[tuple, tuple[int, int]] = self._build_table()
        self.table_misses = 0

    def _build_table(self) -> dict[tuple, tuple[int, int]]:
        table: dict[tuple, tuple[int, int]] = {}
        directions_seen = (*DIRECTION_ORDER, (0, 0))
        for current_direction in directions_seen:
            for legal in _all_nonempty_subsets(DIRECTION_ORDER):
                if current_direction in legal:
                    action = current_direction
                else:
                    action = legal[0]
                table[(current_direction, legal)] = action
        return table

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        if not percept.legal_actions:
            self.last_reason = "No legal move."
            return (0, 0)

        key = (percept.current_direction, percept.legal_actions)
        action = self.table.get(key)
        if action is None or action not in percept.legal_actions:
            self.table_misses += 1
            action = percept.legal_actions[0]
            self.last_reason = (
                f"{DIRECTION_NAMES[action]} | table miss #{self.table_misses}"
            )
        else:
            self.last_reason = f"{DIRECTION_NAMES[action]} | table lookup"
        return action
