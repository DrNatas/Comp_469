"""Part 1 - Table-driven agent (AIMA 4e Section 2.4, TABLE-DRIVEN-AGENT).

THE ONLY FILE-LEVEL RULE: the whole agent is a lookup table built once, in
``__init__``, from a percept key to an action. There are no
condition-action rules and no internal state; ``choose_action`` does
nothing but hash the percept and look it up.

Read pacman/maze.py's ``SENSOR_FIELDS`` list (also in every other agent
file's docstring) before you pick your percept fields. You are free to
declare any of them here -- the environment will happily fill in
``pellets`` or ``ghosts`` too. But think before you do: the table needs one
entry per DISTINCT VALUE those fields can take, and ``pellets`` alone has
as many distinct values as there are subsets of the maze's pellets. That
is the whole point AIMA makes with this design: it does not scale, so
every other agent in this project trades the table for something computed
on the fly. Part of your write-up asks you to work out just how large a
table with the bigger fields would need to be -- you do not have to build
that version, just the arithmetic.

TODO(CH2-1a), TODO(CH2-1b), TODO(CH2-1c) mark what to do. Delete each
marker once that piece is done.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from pacman.maze import DIRECTION_NAMES, DIRECTION_ORDER, MazeModel

AGENT_NAME = "table_driven"


# =====================================================================
# TODO(CH2-1a)  The percept
# =====================================================================
# Declare exactly two fields here, using these exact names (the
# environment matches on name; anything else raises an error that names
# the offender):
#
#   current_direction:  tuple[int, int]
#   legal_actions:       tuple[tuple[int, int], ...]
#
# Nothing else. A bigger percept is legal but defeats the point of this
# part -- see the module docstring.
# =====================================================================
@dataclass(frozen=True)
class Percept:
    ...  # TODO(CH2-1a): replace this with the two fields above.


def _all_nonempty_subsets(items: tuple) -> list[tuple]:
    """Every non-empty subset of ``items``, order preserved. Provided --
    this is bookkeeping, not the exercise."""
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

    # -------------------------------------------------------------
    # TODO(CH2-1b)  Build the table
    # -------------------------------------------------------------
    def _build_table(self) -> dict[tuple, tuple[int, int]]:
        """Return a dict mapping ``(current_direction, legal_actions)`` to
        one action, covering every combination your agent might see.

        Enumerate every ``current_direction`` value the environment can
        report -- the four entries of ``DIRECTION_ORDER`` plus ``(0, 0)``
        for the very first turn -- crossed with every entry from
        ``_all_nonempty_subsets(DIRECTION_ORDER)`` for ``legal_actions``.
        For each combination, pick a sensible action: for instance,
        continue in ``current_direction`` when that is one of the legal
        options, and fall back to the first legal action otherwise. This
        has to be a literal lookup table built with loops here, in
        ``__init__`` -- not logic evaluated later in ``choose_action``.
        """
        raise NotImplementedError("CH2-1b: _build_table")

    # -------------------------------------------------------------
    # TODO(CH2-1c)  Look it up
    # -------------------------------------------------------------
    def choose_action(self, percept: Percept) -> tuple[int, int]:
        """Look up ``(percept.current_direction, percept.legal_actions)``
        in ``self.table`` and return what you find.

        Requirements:
          - If there are no legal actions, set ``last_reason`` to a string
            containing "No legal" and return ``(0, 0)``.
          - A table-driven agent cannot enumerate every percept sequence,
            so if the key is missing (or somehow maps to something no
            longer legal), do not crash: increment ``self.table_misses``
            and fall back to ``percept.legal_actions[0]``.
          - Set ``self.last_reason`` to a short line with the direction
            name, e.g. ``f"{DIRECTION_NAMES[action]} | table lookup"``.
        """
        raise NotImplementedError("CH2-1c: choose_action")
