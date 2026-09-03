"""Part 4 - Goal-based agent (AIMA 4e Figure 2.13).

The structural addition this part asks for is an explicit GOAL and a GOAL
TEST, not a graded preference over many factors (that is Part 5). This
agent maintains one goal at a time -- either "reach food" or "get away from
a ghost" -- and picks whichever legal action's resulting state gets closest
to satisfying it, using the same ``self.maze.distance`` oracle every other
part uses. There is no numeric weighing of competing desires here: a state
either satisfies the goal or it does not, and short of that, closer is
better and further is worse. Nothing is scored on a blended scale.

This agent does not need the memory from Part 3 to do its job -- the goal
is recomputed fresh from each percept -- so it is intentionally left out.
"""

from __future__ import annotations

from dataclasses import dataclass

from pacman.maze import DIRECTION_NAMES, MazeModel

AGENT_NAME = "goal_based"


@dataclass(frozen=True)
class Percept:
    player: tuple[int, int]
    pellets: frozenset[tuple[int, int]]
    power_pellets: frozenset[tuple[int, int]]
    released_ghosts: tuple[tuple[int, int], ...]
    legal_actions: tuple[tuple[int, int], ...]
    frightened_time_remaining: float

    @property
    def frightened(self) -> bool:
        return self.frightened_time_remaining > 0.0


class GoalBasedAgent:
    percept_class = Percept

    #: How close a dangerous ghost has to be, in steps, before survival
    #: becomes the active goal instead of eating.
    DANGER_RADIUS = 2

    #: While fleeing, stop preferring "farther" once a landing tile is this
    #: many steps from every ghost. Without a cap, maximizing raw distance
    #: keeps pulling the agent deeper into whichever pocket is farthest by
    #: corridor-length -- often a dead end -- long after it is already safe.
    FLEE_SAFE_DISTANCE = 3

    def __init__(self, maze: MazeModel):
        self.maze = maze
        self.last_reason = "Waiting for first percept."

    def determine_goal(self, percept: Percept) -> tuple[str, frozenset]:
        """Return ``(kind, positions)``.

        ``kind`` is ``"seek"`` (reach one of ``positions``) or ``"flee"``
        (get more than ``DANGER_RADIUS`` steps from every position in
        ``positions``).
        """
        if not percept.frightened and percept.released_ghosts:
            nearest = self.maze.distance(percept.player, percept.released_ghosts)
            if nearest <= self.DANGER_RADIUS:
                return "flee", frozenset(percept.released_ghosts)

        food = frozenset(percept.pellets) | frozenset(percept.power_pellets)
        if percept.frightened and percept.released_ghosts:
            food = food | frozenset(percept.released_ghosts)
        if not food:
            food = frozenset({percept.player})
        return "seek", food

    def goal_test(self, position: tuple[int, int], goal: tuple[str, frozenset]) -> bool:
        """Has ``position`` achieved ``goal``?"""
        kind, positions = goal
        if kind == "seek":
            return position in positions
        return self.maze.distance(position, positions) > self.DANGER_RADIUS

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        if not percept.legal_actions:
            self.last_reason = "No legal move."
            return (0, 0)

        goal = self.determine_goal(percept)
        kind, positions = goal
        food = frozenset(percept.pellets) | frozenset(percept.power_pellets)

        best_action = percept.legal_actions[0]
        best_score = None
        best_achieved = False
        best_distance = 0

        for action in percept.legal_actions:
            landing = self.maze.step(percept.player, action)
            distance = self.maze.distance(landing, positions)
            achieved = self.goal_test(landing, goal)

            if kind == "seek":
                score = distance
            else:
                # Getting to FLEE_SAFE_DISTANCE away is what matters; once
                # that far, prefer the tile closer to food over the tile
                # that is merely farther still (see FLEE_SAFE_DISTANCE).
                safe_distance = min(distance, self.FLEE_SAFE_DISTANCE)
                food_distance = self.maze.distance(landing, food) if food else 0
                score = (-safe_distance, food_distance)

            if best_score is None or score < best_score:
                best_score = score
                best_action = action
                best_achieved = achieved
                best_distance = distance

        self.last_reason = (
            f"{DIRECTION_NAMES[best_action]} | goal={kind} | "
            f"achieved={best_achieved} | dist={best_distance}"
        )
        return best_action
