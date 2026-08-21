"""COMP 469 - Chapter 2: Intelligent Agents
Pac-Man agent program.

THIS IS THE ONLY FILE YOU EDIT.

Everything in the ``pacman/`` package is the task environment and is off
limits. Read ``ASSIGNMENT.md`` before you start.

What the starter does right now
-------------------------------
It runs, and it eats pellets, and it dies almost immediately. That is on
purpose. As written it is a simple reflex agent that cannot see ghosts,
cannot see which way it is facing, cannot tell whether frightened mode is
active, and remembers nothing between decisions.

Your job is to turn it into a model-based, utility-based agent.

The sensor rule
---------------
The environment fills in exactly the fields your ``Percept`` dataclass
declares, and nothing else. If your agent cannot see something, it is
because you did not ask for it. The full list of things this environment
can report is:

    player                      (row, col) of Pac-Man
    current_direction           (dx, dy) of the last move taken
    pellets                     frozenset of remaining pellet tiles
    power_pellets               frozenset of remaining power pellet tiles
    ghosts                      every ghost, including ones still in the house
    released_ghosts             only ghosts that are out and able to move
    legal_actions               actions that do not walk into a wall
    frightened_time_remaining   seconds of frightened mode left, 0.0 if off

The static maze
---------------
``self.maze`` is prior knowledge of a known environment: walls, corridors,
and the distance between two tiles. It holds no live game state, so you
cannot reach ghosts or the score through it. Useful members:

    self.maze.step(position, action)     -> position after taking action
    self.maze.distance(start, goals)     -> steps to the nearest goal tile
    self.maze.legal_actions_from(pos)    -> actions that avoid walls
    self.maze.wrap_col(col)              -> columns wrap around the maze

``distance`` is provided infrastructure. Call it as often as you like. Do
NOT reimplement it, and do not write DFS, BFS, uniform-cost, greedy, or A*
anywhere in this file. Search algorithms are Chapter 3; this assignment is
graded on agent structure.
"""

from __future__ import annotations

from dataclasses import dataclass

from pacman.maze import DIRECTION_NAMES, DIRECTIONS, MazeModel

AGENT_NAME = "student"


# =====================================================================
# TODO(CH2-1)  The percept
# =====================================================================
# Add the three sensor fields this agent needs and currently lacks:
#   current_direction, released_ghosts, frightened_time_remaining
# Keep the four fields that are already here. Use the exact names from
# the sensor list in the module docstring; the environment matches on
# name, and an unknown name raises an error that names the offender.
#
# Type hints for the new fields:
#   current_direction:         tuple[int, int]
#   released_ghosts:           tuple[tuple[int, int], ...]
#   frightened_time_remaining: float
# =====================================================================
@dataclass(frozen=True)
class Percept:
    """Everything the agent senses on this turn. Nothing else is available."""

    player: tuple[int, int]
    pellets: frozenset[tuple[int, int]]
    power_pellets: frozenset[tuple[int, int]]
    legal_actions: tuple[tuple[int, int], ...]

    @property
    def frightened(self) -> bool:
        """True while power-pellet mode is active.

        This works once you add ``frightened_time_remaining`` in CH2-1.
        """
        return getattr(self, "frightened_time_remaining", 0.0) > 0.0


# =====================================================================
# TODO(CH2-2)  Named utility weights
# =====================================================================
# The starter policy below hides its preferences in bare numbers such as
# -2.0 and 500.0. Move every one of them here and give it a name, then
# add weights for the terms you introduce. A reader should be able to
# tell what this agent wants by reading this class alone.
#
# You need, at minimum, weights covering:
#   distance to the nearest food        eating a regular pellet
#   eating a power pellet               chasing a frightened ghost
#   being caught by a ghost             a ghost one / two / three steps away
#   keeping a safe distance             continuing in the same direction
#   revisiting a tile                   reversing into the tile you just left
#
# Tune the numbers however you like. Defend your choices in the write-up.
# =====================================================================
@dataclass(frozen=True)
class UtilityWeights:
    """Named preferences. This is the agent's utility function, not the
    environment's performance measure. The two are different on purpose;
    see AIMA 4e Section 2.2."""

    food_distance: float = -2.0
    regular_pellet: float = 25.0
    power_pellet: float = 80.0
    # TODO(CH2-2): add the remaining named weights here.


class PacManAgent:
    """A model-based, utility-based agent program (AIMA 4e Figures 2.11-2.14).

    The environment calls ``choose_action`` once per turn with a fresh
    ``Percept`` and expects one action back. That is the entire interface.
    """

    percept_class = Percept

    def __init__(self, maze: MazeModel):
        self.maze = maze
        self.weights = UtilityWeights()
        self.last_reason = "Waiting for first percept."

        # =============================================================
        # TODO(CH2-3)  Internal state
        # =============================================================
        # A simple reflex agent has none, which is why it paces back and
        # forth once a corridor is empty. Add a compact summary of the
        # percept sequence so this agent can tell "I have been here" from
        # "this is new". Two structures are enough:
        #
        #   self.visit_counts: dict[tuple[int, int], int]
        #       how many times each tile has been occupied
        #   self.position_history: collections.deque, maxlen=4
        #       the last few tiles, so you can spot an immediate reversal
        #
        # Also add two counters you will report on:
        #   self.revisit_decisions, self.backtrack_decisions
        # =============================================================

    # -----------------------------------------------------------------
    # TODO(CH2-4)  Update internal state
    # -----------------------------------------------------------------
    def update_internal_state(self, percept: Percept) -> None:
        """Fold this percept into memory. Called once per turn, before
        any action is evaluated.

        Record that ``percept.player`` has been visited and append it to
        the position history.
        """
        raise NotImplementedError("CH2-4: update_internal_state")

    # -----------------------------------------------------------------
    # TODO(CH2-5)  Evaluate one action
    # -----------------------------------------------------------------
    def evaluate_action(
        self,
        percept: Percept,
        action: tuple[int, int],
    ) -> tuple[float, dict[str, float]]:
        """Score a single legal action.

        Returns ``(total_utility, contributions)`` where ``contributions``
        maps a term name to the signed number it added. Splitting scoring
        out from choosing is what lets you explain a decision instead of
        just making one.

        ``contributions`` must contain at least these keys:

            food_distance   revisit          food_distance_steps
            regular_pellet  backtrack        ghost_distance_steps
            power_pellet    continuation     revisit_count
            ghost

        The first two columns are weighted values that sum into the total.
        The third column is raw evidence, not weighted, used for reporting.

        Behaviour to implement:
          - Work out the landing tile with ``self.maze.step``.
          - Pull food and ghost distances from ``self.maze.distance``.
          - When frightened, closer ghosts should be more attractive, and
            landing on one should be worth a lot.
          - When not frightened, landing on a ghost is disastrous, and
            ghosts one, two, or three steps away are progressively less
            alarming. Beyond that, more space is mildly good; cap it so
            the agent does not just run to the far corner and idle.
          - Penalise a tile in proportion to how often it has been
            visited, and penalise reversing straight back into the tile
            occupied two turns ago.
          - Raise ValueError if ``action`` is not in ``percept.legal_actions``.
        """
        raise NotImplementedError("CH2-5: evaluate_action")

    # -----------------------------------------------------------------
    # TODO(CH2-6) and TODO(CH2-7)  Select and explain
    # -----------------------------------------------------------------
    def choose_action(self, percept: Percept) -> tuple[int, int]:
        """Return one action from ``percept.legal_actions``.

        Replace the starter policy below.

        CH2-6 requirements:
          - If there are no legal actions, set ``last_reason`` to a string
            containing "No legal" and return ``(0, 0)``.
          - Otherwise call ``update_internal_state`` exactly once, score
            every legal action with ``evaluate_action``, and return the
            best one. Iterate in ``percept.legal_actions`` order and keep
            strictly-greater comparison so ties break deterministically.
          - The returned action must always be legal.

        CH2-7 requirements:
          - Set ``self.last_reason`` to a single line containing the
            direction name and the tokens "U=", "food=", "ghost=", and
            "memory=", where memory is the summed revisit and backtrack
            contribution. This string is drawn live in the game window,
            so keep it short.
        """
        # ---------------- starter policy, replace this ----------------
        # A simple reflex agent: it walks toward the nearest food and is
        # completely unaware of ghosts, of its own heading, and of
        # anywhere it has already been.
        if not percept.legal_actions:
            self.last_reason = "No legal move."
            return (0, 0)

        food = set(percept.pellets) | set(percept.power_pellets)
        best_action = percept.legal_actions[0]
        best_utility = float("-inf")
        best_distance = 0

        for action in percept.legal_actions:
            landing = self.maze.step(percept.player, action)
            food_distance = self.maze.distance(landing, food)

            utility = -2.0 * food_distance
            if landing in percept.pellets:
                utility += 25.0
            if landing in percept.power_pellets:
                utility += 80.0

            if utility > best_utility:
                best_utility = utility
                best_action = action
                best_distance = food_distance

        self.last_reason = (
            f"{DIRECTION_NAMES[best_action]} | U={best_utility:.1f} | "
            f"food={best_distance} | starter policy"
        )
        return best_action
        # -------------- end of starter policy to replace --------------
