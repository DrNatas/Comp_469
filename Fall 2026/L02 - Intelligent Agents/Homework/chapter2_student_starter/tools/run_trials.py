#!/usr/bin/env python3
"""Run paired baseline/modified trials without opening a Pygame window.

The AI learning objectives remain Chapter 2 concepts. This file is support
instrumentation only: it supplies repeatable environment consequences for the
performance-measure comparison.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import importlib.util
import random
import statistics
import sys
import types
from pathlib import Path
from typing import Any


def install_pygame_import_stub() -> None:
    """Allow importing the agent files on systems where pygame is absent."""
    try:
        __import__("pygame")
        return
    except ModuleNotFoundError:
        pass

    pygame = types.ModuleType("pygame")
    pygame.time = types.SimpleNamespace(get_ticks=lambda: 0)
    sys.modules["pygame"] = pygame


def load_agent_module(path: Path, module_name: str) -> Any:
    install_pygame_import_stub()
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class HeadlessGame:
    """Small deterministic-time adapter for the supplied Pac-Man rules."""

    PLAYER_PERIOD_MS = 135
    GHOST_PERIOD_MS = 180
    POWER_DURATION_MS = 7000

    def __init__(self, module: Any, seed: int):
        self.module = module
        self.rng = random.Random(seed)
        self.time_ms = 0
        self.start_time = 0
        self.rows = len(module.LEVEL)
        self.cols = max(len(row) for row in module.LEVEL)
        self.grid: list[list[str]] = []
        self.pellets: set[tuple[int, int]] = set()
        self.power_pellets: set[tuple[int, int]] = set()
        self.ghosts: list[Any] = []
        self.score = 0
        self.game_over = False
        self.win = False
        self.frightened_until = 0
        self.decisions = 0
        self.position_visits: dict[tuple[int, int], int] = {}
        self.immediate_backtracks = 0
        self.previous_player_position: tuple[int, int] | None = None

        ghost_colors = [module.RED, module.CYAN, module.PINK, module.ORANGE]
        release_delays = [1200, 3000, 5200, 7600]

        for row_index, raw_row in enumerate(module.LEVEL):
            row = raw_row.ljust(self.cols)
            grid_row: list[str] = []
            for col_index, cell in enumerate(row):
                if cell == "#":
                    grid_row.append("#")
                elif cell == "=":
                    grid_row.append("=")
                else:
                    grid_row.append(" ")

                if cell == ".":
                    self.pellets.add((row_index, col_index))
                elif cell == "o":
                    self.power_pellets.add((row_index, col_index))
                elif cell == "P":
                    self.player = module.PacMan(row_index, col_index)
                elif cell in "1234":
                    ghost_index = int(cell) - 1
                    self.ghosts.append(
                        module.Ghost(
                            row_index,
                            col_index,
                            ghost_colors[ghost_index],
                            release_delays[ghost_index],
                        )
                    )
            self.grid.append(grid_row)

        self.agent = module.PacManAgent(self)
        self.position_visits[self.player.position] = 1

    def wrap_col(self, col: int) -> int:
        return col % self.cols

    def is_wall(self, row: int, col: int) -> bool:
        if row < 0 or row >= self.rows:
            return True
        if col < 0 or col >= self.cols:
            return False
        return self.grid[row][col] == "#"

    def is_ghost_door(self, row: int, col: int) -> bool:
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        return self.grid[row][col] == "="

    def legal_actions(self, entity: Any, allow_house_door: bool = False):
        actions = []
        for action in self.module.DIRECTION_ORDER:
            dx, dy = action
            next_row = entity.row + dy
            next_col = self.wrap_col(entity.col + dx)
            if self.is_wall(next_row, next_col):
                continue
            if self.is_ghost_door(next_row, next_col) and not allow_house_door:
                continue
            actions.append(action)
        return tuple(actions)

    def move_entity(self, entity: Any, action: tuple[int, int]) -> None:
        dx, dy = action
        entity.prev_row = entity.row
        entity.prev_col = entity.col
        entity.row += dy
        entity.col = self.wrap_col(entity.col + dx)
        entity.direction = action

    def ghosts_are_frightened(self) -> bool:
        return self.time_ms < self.frightened_until

    def sense_environment(self) -> Any:
        field_names = {field.name for field in dataclasses.fields(self.module.Percept)}
        values: dict[str, Any] = {
            "player": self.player.position,
            "pellets": frozenset(self.pellets),
            "power_pellets": frozenset(self.power_pellets),
            "legal_actions": self.legal_actions(self.player),
        }
        if "ghosts" in field_names:
            values["ghosts"] = tuple(ghost.position for ghost in self.ghosts)
        if "current_direction" in field_names:
            values["current_direction"] = self.player.direction
        if "released_ghosts" in field_names:
            values["released_ghosts"] = tuple(
                ghost.position for ghost in self.ghosts if ghost.released
            )
        if "frightened_time_remaining" in field_names:
            values["frightened_time_remaining"] = max(
                0.0,
                (self.frightened_until - self.time_ms) / 1000.0,
            )
        return self.module.Percept(**values)

    def release_ghosts(self) -> None:
        elapsed = self.time_ms - self.start_time
        for ghost in self.ghosts:
            if not ghost.released and elapsed >= ghost.release_delay_ms:
                ghost.released = True

    def find_ghost_door(self) -> tuple[int, int] | None:
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if cell == "=":
                    return row_index, col_index
        return None

    def ghost_house_exit_action(self, ghost: Any) -> tuple[int, int]:
        door = self.find_ghost_door()
        if door is None:
            return self.module.DIRECTIONS["UP"]
        door_row, door_col = door
        if ghost.col < door_col:
            return self.module.DIRECTIONS["RIGHT"]
        if ghost.col > door_col:
            return self.module.DIRECTIONS["LEFT"]
        if ghost.row > door_row:
            return self.module.DIRECTIONS["UP"]
        return self.module.DIRECTIONS["UP"]

    def choose_ghost_direction(self, ghost: Any) -> tuple[int, int]:
        if not ghost.released:
            return (0, 0)

        door = self.find_ghost_door()
        if door is not None:
            door_row, door_col = door
            if ghost.row >= door_row and abs(ghost.col - door_col) <= 3:
                action = self.ghost_house_exit_action(ghost)
                if action in self.legal_actions(ghost, allow_house_door=True):
                    return action

        valid = list(self.legal_actions(ghost))
        if not valid:
            return (0, 0)

        reverse = (-ghost.direction[0], -ghost.direction[1])
        non_reverse = [action for action in valid if action != reverse]
        if non_reverse:
            valid = non_reverse

        if self.ghosts_are_frightened():
            return max(
                valid,
                key=lambda action: (
                    abs((ghost.row + action[1]) - self.player.row)
                    + abs(self.wrap_col(ghost.col + action[0]) - self.player.col)
                ),
            )

        if self.rng.random() < 0.70:
            return min(
                valid,
                key=lambda action: (
                    abs((ghost.row + action[1]) - self.player.row)
                    + abs(self.wrap_col(ghost.col + action[0]) - self.player.col)
                ),
            )
        return self.rng.choice(valid)

    def reset_ghost(self, ghost: Any) -> None:
        ghost.row, ghost.col = ghost.spawn
        ghost.prev_row, ghost.prev_col = ghost.spawn
        ghost.released = False
        ghost.direction = self.module.DIRECTIONS["UP"]
        ghost.release_delay_ms = self.time_ms + 2500

    def resolve_collision(self, swaps: set[tuple[tuple[int, int], tuple[int, int]]]) -> None:
        for ghost in self.ghosts:
            if not ghost.released:
                continue
            same_tile = ghost.position == self.player.position
            crossed = (ghost.position, self.player.position) in swaps
            if not same_tile and not crossed:
                continue
            if self.ghosts_are_frightened():
                self.score += 200
                self.reset_ghost(ghost)
            else:
                self.game_over = True
                self.win = False
                return

    def update_player(self) -> tuple[tuple[int, int], tuple[int, int]]:
        old_position = self.player.position
        percept = self.sense_environment()
        action = self.agent.choose_action(percept)
        self.decisions += 1

        if action in percept.legal_actions:
            self.move_entity(self.player, action)

        new_position = self.player.position
        if self.previous_player_position is not None and new_position == self.previous_player_position:
            self.immediate_backtracks += 1
        self.previous_player_position = old_position
        self.position_visits[new_position] = self.position_visits.get(new_position, 0) + 1

        if new_position in self.pellets:
            self.pellets.remove(new_position)
            self.score += 10
        if new_position in self.power_pellets:
            self.power_pellets.remove(new_position)
            self.score += 50
            self.frightened_until = self.time_ms + self.POWER_DURATION_MS
        if not self.pellets and not self.power_pellets:
            self.win = True
            self.game_over = True
        return old_position, new_position

    def update_ghosts(self) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        self.release_ghosts()
        moves: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for ghost in self.ghosts:
            if not ghost.released:
                continue
            old_position = ghost.position
            action = self.choose_ghost_direction(ghost)
            if action != (0, 0):
                allow_door = self.is_ghost_door(
                    ghost.row + action[1],
                    self.wrap_col(ghost.col + action[0]),
                )
                if action in self.legal_actions(ghost, allow_house_door=allow_door):
                    self.move_entity(ghost, action)
            moves.append((old_position, ghost.position))
        return moves

    def run(self, max_decisions: int, max_time_ms: int) -> dict[str, Any]:
        next_player = self.PLAYER_PERIOD_MS
        next_ghost = self.GHOST_PERIOD_MS

        while (
            not self.game_over
            and self.decisions < max_decisions
            and self.time_ms < max_time_ms
        ):
            event_time = min(next_player, next_ghost)
            self.time_ms = event_time
            player_due = next_player == event_time
            ghosts_due = next_ghost == event_time

            old_player = self.player.position
            old_ghosts = {id(ghost): ghost.position for ghost in self.ghosts}

            if player_due:
                self.update_player()
                next_player += self.PLAYER_PERIOD_MS
            if ghosts_due and not self.game_over:
                self.update_ghosts()
                next_ghost += self.GHOST_PERIOD_MS

            swaps: set[tuple[tuple[int, int], tuple[int, int]]] = set()
            if player_due and ghosts_due:
                for ghost in self.ghosts:
                    old_ghost = old_ghosts[id(ghost)]
                    if old_player == ghost.position and self.player.position == old_ghost:
                        swaps.add((ghost.position, self.player.position))
            if not self.game_over:
                self.resolve_collision(swaps)

        outcome = "win" if self.win else "caught" if self.game_over else "timeout"
        repeat_visits = sum(max(0, count - 1) for count in self.position_visits.values())
        performance = (
            (2000.0 if self.win else 0.0)
            + self.score
            - (1000.0 if outcome == "caught" else 0.0)
            - 0.20 * self.decisions
            - 2.0 * self.immediate_backtracks
        )
        return {
            "score": self.score,
            "outcome": outcome,
            "decisions": self.decisions,
            "elapsed_seconds": round(self.time_ms / 1000.0, 3),
            "repeat_visits": repeat_visits,
            "immediate_backtracks": self.immediate_backtracks,
            "performance": round(performance, 3),
        }


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for agent_name in sorted({row["agent"] for row in rows}):
        group = [row for row in rows if row["agent"] == agent_name]
        summaries.append(
            {
                "agent": agent_name,
                "trials": len(group),
                "win_rate": round(sum(row["outcome"] == "win" for row in group) / len(group), 3),
                "average_score": round(statistics.fmean(row["score"] for row in group), 3),
                "average_decisions": round(statistics.fmean(row["decisions"] for row in group), 3),
                "average_backtracks": round(statistics.fmean(row["immediate_backtracks"] for row in group), 3),
                "average_performance": round(statistics.fmean(row["performance"] for row in group), 3),
            }
        )
    return summaries


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--modified", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/trials.csv"))
    parser.add_argument("--summary", type=Path, default=Path("results/summary.csv"))
    parser.add_argument("--seed-start", type=int, default=1)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--max-decisions", type=int, default=1000)
    parser.add_argument("--max-time-ms", type=int, default=180000)
    args = parser.parse_args()

    modules = {
        "baseline": load_agent_module(args.baseline, "chapter2_baseline_agent"),
        "modified": load_agent_module(args.modified, "chapter2_modified_agent"),
    }

    rows: list[dict[str, Any]] = []
    for seed in range(args.seed_start, args.seed_start + args.count):
        for agent_name, module in modules.items():
            game = HeadlessGame(module, seed)
            result = game.run(args.max_decisions, args.max_time_ms)
            rows.append({"seed": seed, "agent": agent_name, **result})

    summary_rows = summarize(rows)
    write_csv(args.output, rows)
    write_csv(args.summary, summary_rows)

    for row in summary_rows:
        print(
            f"{row['agent']}: win_rate={row['win_rate']:.3f}, "
            f"avg_score={row['average_score']:.1f}, "
            f"avg_decisions={row['average_decisions']:.1f}, "
            f"avg_backtracks={row['average_backtracks']:.1f}, "
            f"avg_performance={row['average_performance']:.1f}"
        )


if __name__ == "__main__":
    main()
