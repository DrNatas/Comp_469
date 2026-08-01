"""
COMP 469 - Chapter 2: Replanning Agent Demonstration

This agent explicitly separates:
1. goal formulation,
2. planning toward the goal,
3. execution of the resulting action sequence.

IMPORTANT NOTE FOR STUDENTS:
This goal-based agent is also a PLANNING AGENT. It is called goal-based
because it chooses actions to reach an explicit goal, and it is a planning
agent because it creates and stores a sequence of future actions before
executing them.

This separate demonstration focuses on REPLANNING. Before every Pac-Man move,
the agent prints the current plan check. When a new plan is needed, it prints
every breadth-first-search expansion and the resulting path in the terminal.
Only after that output is printed does the game execute the selected move.

The helper ``world.shortest_path()`` is deliberately treated as a black-box
planning service. Chapter 2 introduces why a goal-based agent plans; Chapter 3
teaches the search algorithms in detail.

Run from this directory:
    Windows PowerShell: py -m pip install pygame
    Windows PowerShell: py 06_replanning_agent_ch2.py
    Linux: python3 -m venv .venv && .venv/bin/python -m pip install pygame
    Linux: .venv/bin/python 06_replanning_agent_ch2.py
"""

from __future__ import annotations

from collections import deque

from pacman_chapter2_engine import (
    Chapter2Agent,
    Percept,
    STOP,
    action_name,
    manhattan,
    run_agent,
)


# =============================================================================
# CHAPTER 2 AGENT PROGRAM STARTS HERE
# =============================================================================
class ReplanningAgent(Chapter2Agent):
    """A planning agent that visibly replans before moving.

    It formulates a goal, creates a multi-step plan, and then executes that
    plan one action at a time.
    """

    AGENT_NAME = "REPLANNING AGENT"
    PROGRAM_LOCATION = "formulate_goal() -> make_plan() -> choose_action()"
    CHAPTER2_CONCEPT = "Current state + explicit goal -> predicted future actions"
    # Set to False if you want a quiet terminal while the game runs.
    SHOW_PLANNING_TRACE = True
    SHOW_REPLAN_TRACE = True

    def __init__(self, world):
        super().__init__(world)
        self.current_goal: tuple[int, int] | None = None
        self.goal_description = "NONE"
        self.plan: deque[tuple[int, int]] = deque()

    def reset_episode(self) -> None:
        self.current_goal = None
        self.goal_description = "NONE"
        self.plan.clear()

    # -------------------------------------------------------------------------
    # GOAL FORMULATION: define a desirable future state.
    # -------------------------------------------------------------------------
    def formulate_goal(self, percept: Percept) -> tuple[int, int] | None:
        # When ghosts are frightened, the desired state is a ghost location.
        if percept.frightened and percept.visible_ghosts:
            self.goal_description = "EAT FRIGHTENED GHOST"
            return min(
                percept.visible_ghosts,
                key=lambda ghost: self.world.maze_distance(
                    percept.player,
                    {ghost},
                ),
            )

        # When visible danger is close, reaching a power pellet becomes the goal.
        nearest_visible_ghost = min(
            (
                self.world.maze_distance(percept.player, {ghost})
                for ghost in percept.visible_ghosts
            ),
            default=10_000,
        )
        if percept.power_pellets and nearest_visible_ghost <= 5:
            self.goal_description = "REACH POWER PELLET"
            return min(
                percept.power_pellets,
                key=lambda pellet: self.world.maze_distance(
                    percept.player,
                    {pellet},
                ),
            )

        # Otherwise the desired state is the location of the nearest food.
        food = set(percept.pellets) | set(percept.power_pellets)
        if food:
            self.goal_description = "COLLECT FOOD"
            return min(
                food,
                key=lambda pellet: self.world.maze_distance(
                    percept.player,
                    {pellet},
                ),
            )

        self.goal_description = "NO REMAINING GOAL"
        return None

    def danger_cells(self, percept: Percept) -> set[tuple[int, int]]:
        """Current predicted consequences to avoid during planning."""

        if percept.frightened:
            return set()

        danger = set(percept.visible_ghosts)
        for ghost in percept.visible_ghosts:
            for action in self.world.legal_actions_from(ghost):
                danger.add(self.world.successor(ghost, action))
        danger.discard(percept.player)
        return danger

    # -------------------------------------------------------------------------
    # PLANNING: find an action sequence that reaches the formulated goal.
    # -------------------------------------------------------------------------
    def make_plan(self, percept: Percept) -> None:
        self.current_goal = self.formulate_goal(percept)
        self.plan.clear()

        if self.current_goal is None:
            self.last_reason = "No goal remains."
            return

        blocked = self.danger_cells(percept)
        actions = self.world.shortest_path(
            percept.player,
            self.current_goal,
            blocked,
            trace=self.SHOW_PLANNING_TRACE,
        )

        # If conservative planning has no route, retry while blocking only the
        # currently visible ghost squares.
        if not actions and percept.player != self.current_goal:
            actions = self.world.shortest_path(
                percept.player,
                self.current_goal,
                set(percept.visible_ghosts) if not percept.frightened else set(),
                trace=self.SHOW_PLANNING_TRACE,
            )

        self.plan.extend(actions)
        self.last_reason = (
            f"Goal={self.goal_description} at {self.current_goal}; "
            f"planned {len(self.plan)} steps"
        )

    def goal_is_valid(self, percept: Percept) -> bool:
        if self.current_goal is None:
            return False
        if self.goal_description == "EAT FRIGHTENED GHOST":
            return (
                percept.frightened
                and self.current_goal in percept.visible_ghosts
            )
        if self.goal_description == "REACH POWER PELLET":
            return self.current_goal in percept.power_pellets
        if self.goal_description == "COLLECT FOOD":
            return (
                self.current_goal in percept.pellets
                or self.current_goal in percept.power_pellets
            )
        return False

    # -------------------------------------------------------------------------
    # ACTION SELECTION: execute the plan or replan when the world changes.
    # -------------------------------------------------------------------------
    def choose_action(self, percept: Percept) -> tuple[int, int]:
        if not percept.legal_actions:
            self.last_reason = "No legal action -> STOP"
            return STOP

        need_new_plan = (
            not self.goal_is_valid(percept)
            or not self.plan
            or self.plan[0] not in percept.legal_actions
        )

        if not need_new_plan and not percept.frightened:
            next_position = self.world.successor(percept.player, self.plan[0])
            if next_position in self.danger_cells(percept):
                need_new_plan = True

        if need_new_plan:
            self.make_plan(percept)

        if self.plan and self.plan[0] in percept.legal_actions:
            action = self.plan.popleft()
            self.last_reason = (
                f"Execute plan for {self.goal_description}: "
                f"{action_name(action)}; {len(self.plan)} steps remain"
            )
            return action

        # This fallback is used only when no goal-directed route is available.
        action = percept.legal_actions[0]
        self.last_reason = (
            f"No goal path available -> fallback {action_name(action)}"
        )
        return action

    def hud_lines(self) -> tuple[str, ...]:
        return (
            f"goal={self.goal_description}",
            f"target={self.current_goal}",
            f"plan length={len(self.plan)}",
        )


# =============================================================================
# CHAPTER 2 AGENT PROGRAM ENDS HERE
# =============================================================================


if __name__ == "__main__":
    run_agent(ReplanningAgent)
