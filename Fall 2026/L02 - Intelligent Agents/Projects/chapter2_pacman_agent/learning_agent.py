"""Part 6 - Learning agent (AIMA 4e Figure 2.15).

Figure 2.15 has four boxes: a PERFORMANCE ELEMENT that actually acts, a
CRITIC that judges how things went, a LEARNING ELEMENT that uses that
judgement to improve the performance element, and a PROBLEM GENERATOR that
occasionally suggests exploratory action so the agent does not just settle
on the first thing that worked. This part builds all four, mapped onto
what you already have:

    performance element  ->  a Part 5 UtilityBasedAgent, held as
                              ``self.performance_element``
    critic                ->  the environment's performance measure,
                              defined in pacman/rules.py and handed to you
                              as the ``performance`` argument to
                              ``learn()`` -- you do not compute it yourself
    learning element      ->  ``learn()``: keep new weights if they scored
                              better than your best so far, else revert
    problem generator      ->  ``propose_new_weights()``: a small random
                              nudge to a couple of weights, tried out for
                              one episode before the critic judges it

This is AIMA-appropriate hill-climbing over your Part 5 weights, not
reinforcement learning (that is Chapter 21, out of scope here). Nothing in
this file plays a single move differently from Part 5 -- ``choose_action``
just delegates. What is new is what happens BETWEEN episodes, driven by
``tools/train_learning_agent.py`` (provided), which is the only thing that
calls ``propose_new_weights()`` and ``learn()``.

TODO(CH2-6a) and TODO(CH2-6b) mark what to do. Everything else in this
file -- the naive starting weights, loading a previous training run,
``choose_action`` delegating to the performance element -- is plumbing,
provided so you can focus on the two methods that matter.
"""

from __future__ import annotations

import json
import random
from dataclasses import replace
from pathlib import Path

from pacman.maze import MazeModel
from utility_based_agent import Percept, UtilityBasedAgent, UtilityWeights

AGENT_NAME = "learning"

#: Where tools/train_learning_agent.py saves the outcome of a training run.
LEARNED_WEIGHTS_PATH = Path(__file__).resolve().parent / "results" / "learned_weights.json"

#: A deliberately weak starting point. It is cautious enough to survive --
#: the ghost weights are real -- but it has no sense of urgency and no
#: memory-driven preferences at all: no reward for continuing in a
#: direction, no penalty for revisiting a tile or backtracking. Left
#: untrained, it wanders the safe parts of the maze inefficiently and racks
#: up the per-decision cost in pacman/rules.py. That inefficiency, not
#: survival, is what training should fix. Compare it with UtilityWeights()
#: (Part 5's tuned defaults) after training and you are looking at the
#: learning element's work.
NAIVE_WEIGHTS = UtilityWeights(
    food_distance=-0.2,
    regular_pellet=25.0,
    power_pellet=80.0,
    ghost_catch_frightened=110.0,
    ghost_close_frightened=-1.5,
    ghost_collision=-2600.0,
    ghost_one_step=-300.0,
    ghost_two_steps=-70.0,
    ghost_three_steps=-20.0,
    ghost_safe_distance=0.0,
    ghost_safe_distance_cap=0.0,
    continuation=0.0,
    revisit_per_visit=0.0,
    backtrack=0.0,
)


def _load_trained_weights() -> UtilityWeights | None:
    """If tools/train_learning_agent.py has already produced a saved
    result, start from it instead of NAIVE_WEIGHTS. Used only when a
    LearningAgent is constructed with no explicit ``weights`` argument, so
    ``python tools/play.py --agent learning`` shows whatever training has
    accomplished so far, and a fresh checkout (no results/learned_weights
    .json yet) shows the naive starting point."""
    if not LEARNED_WEIGHTS_PATH.exists():
        return None
    try:
        payload = json.loads(LEARNED_WEIGHTS_PATH.read_text())
        fields = set(UtilityWeights.__dataclass_fields__)
        saved = {k: v for k, v in payload["best_weights"].items() if k in fields}
        return UtilityWeights(**saved)
    except (OSError, ValueError, KeyError, TypeError):
        return None


class LearningAgent:
    percept_class = Percept

    #: How hard the problem generator nudges a weight, as a fraction of
    #: that weight's own magnitude.
    PERTURBATION_STRENGTH = 0.15

    def __init__(
        self,
        maze: MazeModel,
        weights: UtilityWeights | None = None,
        seed: int = 0,
    ):
        self.performance_element = UtilityBasedAgent(maze)
        self.performance_element.weights = weights if weights is not None else (
            _load_trained_weights() or NAIVE_WEIGHTS
        )

        self.best_weights = self.performance_element.weights
        self.best_performance = float("-inf")
        self.episodes_seen = 0
        self.rng = random.Random(seed)

    @property
    def last_reason(self) -> str:
        return self.performance_element.last_reason

    @property
    def weights(self) -> UtilityWeights:
        return self.performance_element.weights

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        """Delegate straight to the performance element. Nothing about a
        single decision changes in this part."""
        return self.performance_element.choose_action(percept)

    # -------------------------------------------------------------
    # TODO(CH2-6a)  Problem generator
    # -------------------------------------------------------------
    def propose_new_weights(self) -> UtilityWeights:
        """Return ``self.best_weights`` with a small random nudge applied
        to one or two fields, and RETURN it -- do not mutate any state
        here and do not assign the result anywhere. The training harness
        decides whether and when to actually try a proposal, by setting
        ``self.performance_element.weights`` to what this returns.

        Suggested approach: use ``self.rng.sample`` to pick 1-2 field
        names from ``self.best_weights.__dataclass_fields__``, and for
        each one add Gaussian noise scaled by ``PERTURBATION_STRENGTH``
        times that field's own magnitude (``self.rng.gauss``). Build the
        new weights with ``replace(self.best_weights, **updates)`` (the
        ``replace`` already imported at the top of this file) rather than
        constructing a UtilityWeights from scratch, so every untouched
        field stays exactly as it was.
        """
        raise NotImplementedError("CH2-6a: propose_new_weights")

    # -------------------------------------------------------------
    # TODO(CH2-6b)  Critic + learning element
    # -------------------------------------------------------------
    def learn(self, performance: float) -> None:
        """Called once after each training episode with that episode's
        performance measure -- the critic's judgement, computed by the
        environment, not by you. The weights that produced this episode
        are sitting in ``self.performance_element.weights`` right now.

        If ``performance`` beats ``self.best_performance``, update
        ``self.best_performance`` and keep ``self.performance_element
        .weights`` as the new ``self.best_weights``. Otherwise, revert
        ``self.performance_element.weights`` back to ``self.best_weights``
        so a bad experiment does not stick around for the next episode.
        Either way, increment ``self.episodes_seen``.
        """
        raise NotImplementedError("CH2-6b: learn")
