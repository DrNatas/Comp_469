"""Reference agents you compare your own agents against.

PROVIDED INFRASTRUCTURE. Do not edit this package.

- ``RandomAgent``         : no rules at all, the control condition.
- ``GreedyBaselineAgent`` : walks toward the nearest food, blind to ghosts.
                            A weak external control. Not a model answer for
                            any of the six parts you build.

Everything you actually build for this project -- the table-driven, simple
reflex, model-based reflex, goal-based, utility-based, and learning agents
from AIMA 4e Section 2.4 -- lives in the six ``*_agent.py`` files at the
project root, not here.
"""

from .greedy_baseline import GreedyBaselineAgent
from .random_agent import RandomAgent

__all__ = ["RandomAgent", "GreedyBaselineAgent"]
