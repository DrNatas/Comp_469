"""
COMP 469 - Chapter 2: Simple Reflex Agent

This file contains only the Chapter 2 agent program.  The shared module
pacman_chapter2_engine.py supplies the environment, graphics, sensors, and
actuators.

A simple reflex agent:
- acts only on the current percept,
- uses ordered condition-action rules,
- stores no percept history,
- has no internal world model,
- has no explicit goal, utility function, or learning process.

Run from this directory:
    Windows PowerShell: python -m pip install pygame
    Windows PowerShell: python 01_simple_reflex_agent_ch2.py 1
    Linux: python3 -m venv .venv && .venv/bin/python -m pip install pygame
    Linux: .venv/bin/python 01_simple_reflex_agent_ch2.py 1

Custom level demonstrations (run one level at a time):
    Level 1: python 01_simple_reflex_agent_ch2.py 1
    Level 2: python 01_simple_reflex_agent_ch2.py 2

If no level number is supplied, Level 1 is used automatically.
"""

from pacman_chapter2_engine import (
    Chapter2Agent,
    Percept,
    STOP,
    action_name,
    manhattan,
    run_agent,
)


# =============================================================================
# CUSTOM CLASSROOM LEVELS
# =============================================================================
# The simple reflex agent sees only its current percept. These two levels make
# that limitation visible: the agent can collect a nearby pellet, but it does
# not understand that a longer route is needed to collect food elsewhere.
#
# Symbols: # wall, . pellet, o power pellet, P Pac-Man, 1-4 ghosts.
CUSTOM_LEVELS = {
    1: [
        "#################",
        "#P..............#",
        "#.#############.#",
        "#...o.......o...#",
        "#################",
    ],
    2: [
        "#################",
        "#P..............#",
        "#####.#########.#",
        "#...#...#.......#",
        "###.#####.#####.#",
        "#...............#",
        "#################",
    ],
}


# =============================================================================
# CHAPTER 2 AGENT PROGRAM STARTS HERE
# =============================================================================
class SimpleReflexAgent(Chapter2Agent):
    """Select an action from the current percept only."""

    AGENT_NAME = "SIMPLE REFLEX AGENT"
    PROGRAM_LOCATION = "SimpleReflexAgent.choose_action()"
    CHAPTER2_CONCEPT = "Current percept -> condition-action rule -> action"

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        """Apply ordered IF-THEN rules to the current percept.

        ``last_reason`` is display-only diagnostic text.  The agent never reads
        it during a later decision, so it is not memory.
        """

        # RULE 1: IF no movement is possible, THEN stop.
        if not percept.legal_actions:
            self.last_reason = "RULE 1 fired: no legal action -> STOP"
            return STOP

        destinations = {
            action: self.world.successor(percept.player, action)
            for action in percept.legal_actions
        }

        # RULE 2: IF a frightened ghost is adjacent, THEN eat it.
        if percept.frightened:
            for action in percept.legal_actions:
                if destinations[action] in percept.visible_ghosts:
                    self.last_reason = (
                        f"RULE 2 fired: frightened ghost -> {action_name(action)}"
                    )
                    return action

        # RULE 3: IF a dangerous ghost is adjacent, THEN take the first move
        # that does not end on or next to a visible ghost.
        if not percept.frightened:
            ghost_is_adjacent = any(
                manhattan(percept.player, ghost) <= 1
                for ghost in percept.visible_ghosts
            )
            if ghost_is_adjacent:
                for action in percept.legal_actions:
                    destination = destinations[action]
                    safe = all(
                        manhattan(destination, ghost) > 1
                        for ghost in percept.visible_ghosts
                    )
                    if safe:
                        self.last_reason = (
                            f"RULE 3 fired: adjacent danger -> {action_name(action)}"
                        )
                        return action

        # RULE 4: IF a power pellet is adjacent, THEN eat it.
        for action in percept.legal_actions:
            if destinations[action] in percept.power_pellets:
                self.last_reason = (
                    f"RULE 4 fired: adjacent power pellet -> {action_name(action)}"
                )
                return action

        # RULE 5: IF a regular pellet is adjacent, THEN eat it.
        for action in percept.legal_actions:
            if destinations[action] in percept.pellets:
                self.last_reason = (
                    f"RULE 5 fired: adjacent pellet -> {action_name(action)}"
                )
                return action

        # RULE 6: IF the current direction remains legal, THEN continue.
        if percept.current_direction in percept.legal_actions:
            self.last_reason = (
                "RULE 6 fired: continue current direction -> "
                f"{action_name(percept.current_direction)}"
            )
            return percept.current_direction

        # RULE 7: OTHERWISE take the first legal action in the fixed rule order.
        action = percept.legal_actions[0]
        self.last_reason = (
            f"RULE 7 fired: default first legal -> {action_name(action)}"
        )
        return action

    def hud_lines(self) -> tuple[str, ...]:
        return ("No memory", "No model", "No goal", "No utility")


# =============================================================================
# CHAPTER 2 AGENT PROGRAM ENDS HERE
# =============================================================================


if __name__ == "__main__":
    # Run level 1 by default. Choose level 2 from Terminal with:
    #     python 01_simple_reflex_agent_ch2.py 2
    import sys

    try:
        level_number = int(sys.argv[1])
    except (IndexError, ValueError):
        level_number = 1

    if level_number not in CUSTOM_LEVELS:
        raise SystemExit("Choose a custom level with 1 or 2.")

    print(f"Starting Simple Reflex demonstration Level {level_number}...")
    run_agent(SimpleReflexAgent, level=CUSTOM_LEVELS[level_number])
