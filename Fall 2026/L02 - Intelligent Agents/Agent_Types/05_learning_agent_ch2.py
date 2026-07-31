"""
COMP 469 - Chapter 2: Learning Agent

This demonstration stays at the conceptual level used in Chapter 2.  It does
not present a full reinforcement-learning algorithm.  Instead, it makes the
four required components explicit:

1. performance_element()  - selects an external action,
2. learning_element()     - changes the action preferences,
3. critic()               - interprets feedback from the environment,
4. problem_generator()    - occasionally proposes exploratory actions.

The performance element is a small learned preference table.  Any reflex,
model-based, goal-based, or utility-based performance element could be placed
inside the same learning-agent architecture.

Run from this directory:
    Windows PowerShell: py -m pip install pygame
    Windows PowerShell: py 05_learning_agent_ch2.py
    Linux: python3 -m venv .venv && .venv/bin/python -m pip install pygame
    Linux: .venv/bin/python 05_learning_agent_ch2.py
"""

from __future__ import annotations

import random
from collections import defaultdict

from pacman_chapter2_engine import (
    Chapter2Agent,
    DIRECTION_ORDER,
    Percept,
    STOP,
    Transition,
    action_name,
    manhattan,
    run_agent,
)

StateKey = tuple[
    tuple[int, int],
    bool,
    tuple[bool, bool, bool, bool],
    tuple[bool, bool, bool, bool],
]


# =============================================================================
# CHAPTER 2 AGENT PROGRAM STARTS HERE
# =============================================================================
class LearningAgent(Chapter2Agent):
    """A Chapter 2 learning-agent architecture with four named components."""

    AGENT_NAME = "LEARNING AGENT"
    PROGRAM_LOCATION = (
        "performance_element() + learning_element() + critic() + problem_generator()"
    )
    CHAPTER2_CONCEPT = "Feedback modifies the performance element"
    SUPPORTS_FAST_TRAINING = True

    def __init__(self, world):
        super().__init__(world)
        self.preferences: dict[
            StateKey,
            dict[tuple[int, int], float],
        ] = defaultdict(dict)
        self.alpha = 0.25
        self.epsilon = 0.30
        self.episode = 0
        self.last_state: StateKey | None = None
        self.last_action: tuple[int, int] = STOP
        self.last_feedback = 0.0
        self.last_component = "Waiting for the first percept."
        self.random = random.Random(469)

    def reset_episode(self) -> None:
        self.episode += 1
        self.last_state = None
        self.last_action = STOP
        self.last_feedback = 0.0
        self.last_component = "New episode; learned preferences preserved."

    def clear_learning(self) -> None:
        self.preferences.clear()
        self.epsilon = 0.30
        self.episode = 0
        self.last_reason = "Learning memory cleared."

    def state_key(self, percept: Percept) -> StateKey:
        """Create a compact factored representation of the current situation."""

        food = set(percept.pellets) | set(percept.power_pellets)
        food_mask: list[bool] = []
        danger_mask: list[bool] = []

        # The masks use the fixed LEFT, RIGHT, UP, DOWN action order so the
        # same factored situation always produces the same state key.
        for action in DIRECTION_ORDER:
            destination = self.world.successor(percept.player, action)
            legal = action in percept.legal_actions
            food_mask.append(legal and destination in food)
            danger_mask.append(
                legal
                and any(
                    manhattan(destination, ghost) <= 1
                    for ghost in percept.visible_ghosts
                )
                and not percept.frightened
            )

        return (
            percept.player,
            percept.frightened,
            tuple(food_mask),
            tuple(danger_mask),
        )

    def preference(self, state: StateKey, action: tuple[int, int]) -> float:
        return self.preferences[state].get(action, 0.0)

    # -------------------------------------------------------------------------
    # PERFORMANCE ELEMENT: chooses the agent's external action.
    # -------------------------------------------------------------------------
    def performance_element(
        self,
        percept: Percept,
        state: StateKey,
    ) -> tuple[int, int]:
        """Exploit the action with the strongest learned preference."""

        if not percept.legal_actions:
            return STOP

        # An untrained tie is broken by a small built-in reflex.  This is the
        # initial knowledge that allows the agent to act before it has learned.
        destinations = {
            action: self.world.successor(percept.player, action)
            for action in percept.legal_actions
        }
        food = set(percept.pellets) | set(percept.power_pellets)

        def initial_bias(action: tuple[int, int]) -> float:
            destination = destinations[action]
            bias = 0.0
            if destination in food:
                bias += 0.20
            if any(
                manhattan(destination, ghost) <= 1
                for ghost in percept.visible_ghosts
            ) and not percept.frightened:
                bias -= 0.50
            if action == percept.current_direction:
                bias += 0.02
            return bias

        return max(
            percept.legal_actions,
            key=lambda action: (
                self.preference(state, action) + initial_bias(action),
                -percept.legal_actions.index(action),
            ),
        )

    # -------------------------------------------------------------------------
    # PROBLEM GENERATOR: proposes exploratory actions that may teach the agent.
    # -------------------------------------------------------------------------
    def problem_generator(self, percept: Percept) -> tuple[int, int] | None:
        if percept.legal_actions and self.random.random() < self.epsilon:
            return self.random.choice(percept.legal_actions)
        return None

    # -------------------------------------------------------------------------
    # CRITIC: converts external performance feedback into a learning signal.
    # -------------------------------------------------------------------------
    def critic(self, transition: Transition) -> float:
        return transition.reward

    # -------------------------------------------------------------------------
    # LEARNING ELEMENT: modifies the performance element's preferences.
    # -------------------------------------------------------------------------
    def learning_element(
        self,
        state: StateKey,
        action: tuple[int, int],
        feedback: float,
    ) -> None:
        old_preference = self.preference(state, action)
        self.preferences[state][action] = old_preference + self.alpha * (
            feedback - old_preference
        )

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        if not percept.legal_actions:
            self.last_reason = "Performance element: no legal action -> STOP"
            return STOP

        state = self.state_key(percept)
        exploratory_action = self.problem_generator(percept)

        if exploratory_action is not None:
            action = exploratory_action
            self.last_component = "Problem generator proposed exploration."
            self.last_reason = (
                f"Problem generator -> explore {action_name(action)}"
            )
        else:
            action = self.performance_element(percept, state)
            value = self.preference(state, action)
            self.last_component = "Performance element used learned preferences."
            self.last_reason = (
                f"Performance element -> {action_name(action)} "
                f"(preference={value:.2f})"
            )

        self.last_state = state
        self.last_action = action
        return action

    def observe_transition(self, transition: Transition) -> None:
        if self.last_state is None or self.last_action == STOP:
            return

        feedback = self.critic(transition)
        self.learning_element(self.last_state, self.last_action, feedback)
        self.last_feedback = feedback
        self.last_component = (
            "Critic supplied feedback; learning element changed preference."
        )

        if transition.done:
            self.epsilon = max(0.05, self.epsilon * 0.97)

    def observe_external_feedback(
        self,
        reward: float,
        percept: Percept,
        done: bool,
        outcome: str,
    ) -> None:
        if self.last_state is None or self.last_action == STOP:
            return

        self.learning_element(self.last_state, self.last_action, reward)
        self.last_feedback = reward
        self.last_component = (
            f"Critic reported {outcome}; learning element updated preference."
        )
        self.last_reason = (
            f"Critic feedback={reward:.1f} after {action_name(self.last_action)}"
        )
        if done:
            self.epsilon = max(0.05, self.epsilon * 0.97)

    def hud_lines(self) -> tuple[str, ...]:
        learned_actions = sum(len(actions) for actions in self.preferences.values())
        return (
            f"episode={self.episode}",
            f"learned states={len(self.preferences)}",
            f"preferences={learned_actions}",
            f"epsilon={self.epsilon:.2f}",
            f"critic={self.last_feedback:.1f}",
        )


# =============================================================================
# CHAPTER 2 AGENT PROGRAM ENDS HERE
# =============================================================================


if __name__ == "__main__":
    run_agent(LearningAgent)
