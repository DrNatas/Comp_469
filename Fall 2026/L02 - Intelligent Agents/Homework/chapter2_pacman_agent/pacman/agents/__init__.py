"""Reference agents you compare your own agent against.

PROVIDED INFRASTRUCTURE. Do not edit this package.

These exist so your trial report has something to measure against. They map
onto the agent types in AIMA 4e Section 2.4:

- ``RandomAgent``      : no rules at all, the control condition.
- ``SimpleReflexAgent``: Figure 2.10. Condition-action rules over the
                         current percept only. No memory, no lookahead.

Your agent in ``agent.py`` is the next step up: it keeps internal state and
ranks actions with a utility function.
"""

from .random_agent import RandomAgent
from .simple_reflex import SimpleReflexAgent

__all__ = ["RandomAgent", "SimpleReflexAgent"]
