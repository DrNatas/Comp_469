"""
Shared Pac-Man environment for the COMP 469 Chapter 2 agent demonstrations.

This file intentionally contains the environment, sensors, actuators, graphics,
scorekeeping, and ghost behavior.  The five small agent files contain the
actual Chapter 2 agent programs that students should study.

The graphics preserve the original lecture-demo appearance: blue hollow walls,
a central ghost house, animated Pac-Man and ghosts, pellets, power pellets,
and a black score panel.

This is a shared module and is not run directly. From this directory, install
Pygame and run one of the five *_agent_ch2.py files:
    Windows PowerShell: py -m pip install pygame
    Windows PowerShell: py 01_simple_reflex_agent_ch2.py
    Linux: python3 -m venv .venv && .venv/bin/python -m pip install pygame
    Linux: .venv/bin/python 01_simple_reflex_agent_ch2.py
"""

from __future__ import annotations

import math
import random
import sys
from collections import deque
from time import perf_counter
from dataclasses import dataclass
from typing import Iterable, Type

import pygame

TILE_SIZE = 30
HUD_HEIGHT = 96
FPS = 60
# Normal demonstration speed: larger values mean fewer moves per second.
PLAYER_STEP_MS = 600
GHOST_STEP_MS = 700

# These values are used only by agents that support fast training mode.
FAST_PLAYER_STEP_MS = 28
FAST_GHOST_STEP_MS = 40
GHOST_SENSOR_RANGE = 5

BLACK = (0, 0, 0)
MAZE_BLUE = (15, 35, 255)
WHITE = (245, 245, 245)
YELLOW = (255, 230, 0)
RED = (245, 70, 55)
PINK = (255, 185, 220)
CYAN = (60, 220, 255)
ORANGE = (255, 155, 45)
GREEN = (60, 220, 100)
GRAY = (175, 175, 175)
FRIGHTENED_BLUE = (45, 80, 230)

# Legend:
# # wall
# . regular pellet
# o power pellet
# P Pac-Man start
# 1-4 ghost starts inside ghost house
# = ghost-house door
# space open corridor
LEVEL = [
    "#################",
    "#o.....###.....o#",
    "#.###.........#.#",
    "#.....###.###...#",
    "###.#.......#.###",
    "#...# #===###...#",
    "#.#.# #2 1#.#.#.#",
    "#...# #####.#...#",
    "#o......P......o#",
    "#################",
]

DIRECTIONS = {
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
    "UP": (0, -1),
    "DOWN": (0, 1),
}
DIRECTION_ORDER = tuple(DIRECTIONS.values())
STOP = (0, 0)


def action_name(action: tuple[int, int]) -> str:
    if action == STOP:
        return "STOP"
    return next(
        (name for name, value in DIRECTIONS.items() if value == action),
        str(action),
    )


def manhattan(first: tuple[int, int], second: tuple[int, int]) -> int:
    return abs(first[0] - second[0]) + abs(first[1] - second[1])


@dataclass(frozen=True)
class Percept:
    """The current sensor input supplied to an agent program.

    The maze and remaining food are visible, as in the game display. Ghosts are
    perceived only within a limited sensor radius, which allows the
    model-based agent to demonstrate memory of temporarily unseen state.
    """

    player: tuple[int, int]
    pellets: frozenset[tuple[int, int]]
    power_pellets: frozenset[tuple[int, int]]
    visible_ghosts: tuple[tuple[int, int], ...]
    visible_ghost_directions: tuple[tuple[int, int], ...]
    legal_actions: tuple[tuple[int, int], ...]
    frightened: bool
    current_direction: tuple[int, int]
    score: int
    step_count: int
    columns: int


@dataclass(frozen=True)
class Transition:
    """Feedback describing one agent action and its immediate consequence."""

    before: Percept
    action: tuple[int, int]
    reward: float
    after: Percept
    done: bool
    outcome: str


class WorldKnowledge:
    """Read-only prior knowledge about the static maze and action effects."""

    def __init__(self, grid: list[list[str]]):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    def wrap_col(self, col: int) -> int:
        return col % self.cols

    def is_wall(self, position: tuple[int, int]) -> bool:
        row, col = position
        if row < 0 or row >= self.rows:
            return True
        if col < 0 or col >= self.cols:
            return False
        return self.grid[row][col] == "#"

    def is_ghost_door(self, position: tuple[int, int]) -> bool:
        row, col = position
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        return self.grid[row][col] == "="

    def successor(
        self,
        position: tuple[int, int],
        action: tuple[int, int],
        allow_door: bool = False,
    ) -> tuple[int, int]:
        dx, dy = action
        candidate = position[0] + dy, self.wrap_col(position[1] + dx)
        if self.is_wall(candidate):
            return position
        if self.is_ghost_door(candidate) and not allow_door:
            return position
        return candidate

    def legal_actions_from(
        self,
        position: tuple[int, int],
        allow_door: bool = False,
    ) -> tuple[tuple[int, int], ...]:
        return tuple(
            action
            for action in DIRECTION_ORDER
            if self.successor(position, action, allow_door) != position
        )

    def neighbors(
        self,
        position: tuple[int, int],
        blocked: set[tuple[int, int]] | None = None,
    ) -> Iterable[tuple[tuple[int, int], tuple[int, int]]]:
        blocked = blocked or set()
        for action in self.legal_actions_from(position):
            next_position = self.successor(position, action)
            if next_position not in blocked:
                yield next_position, action

    def shortest_path(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
        blocked: set[tuple[int, int]] | None = None,
        trace: bool = False,
    ) -> list[tuple[int, int]]:
        """Minimal planning service used by the goal-based demonstration.

        The Chapter 2 agent invokes planning. The internal search mechanics are
        support code; detailed search algorithms belong to Chapter 3.

        When ``trace`` is true, print the breadth-first-search expansions so
        students can see how a plan is constructed in the terminal.
        """

        search_started = perf_counter()
        if trace:
            print("\n[PLANNER] Searching for a path...")
            print(f"[PLANNER] Start={start}; goal={goal}")
            print(f"[PLANNER] Blocked cells: {sorted(blocked or set())}")

        if start == goal:
            if trace:
                elapsed = perf_counter() - search_started
                print(f"[PLANNER] Path found in {elapsed:.4f} seconds.")
                print("[PLANNER] Total cost: 0")
                print("[PLANNER] Number of nodes expanded: 0")
                print("[PLANNER] Number of unique nodes expanded: 1")
            return []

        queue = deque([start])
        parent: dict[
            tuple[int, int],
            tuple[tuple[int, int], tuple[int, int]] | None,
        ] = {start: None}

        expansions = 0
        while queue:
            position = queue.popleft()
            expansions += 1
            if trace:
                print(
                    f"[PLANNER] Expand #{expansions}: {position}; "
                    f"frontier={len(queue)}"
                )
            for next_position, action in self.neighbors(position, blocked):
                if next_position in parent:
                    if trace:
                        print(
                            f"           {action_name(action)} -> "
                            f"{next_position} (already discovered)"
                        )
                    continue
                parent[next_position] = (position, action)
                if trace:
                    print(
                        f"           {action_name(action)} -> "
                        f"{next_position} (add to frontier)"
                    )
                if next_position == goal:
                    actions: list[tuple[int, int]] = []
                    cursor = next_position
                    while parent[cursor] is not None:
                        previous, step_action = parent[cursor]
                        actions.append(step_action)
                        cursor = previous
                    actions.reverse()
                    if trace:
                        elapsed = perf_counter() - search_started
                        print(f"[PLANNER] Path found in {elapsed:.4f} seconds.")
                        print(f"[PLANNER] Total cost: {len(actions)}")
                        print(
                            f"[PLANNER] Number of nodes expanded: {expansions}"
                        )
                        print(
                            "[PLANNER] Number of unique nodes expanded: "
                            f"{len(parent)}"
                        )
                        print(
                            f"[PLANNER] Goal found after {expansions} "
                            f"expansions: {len(actions)} actions"
                        )
                        print(
                            "[PLANNER] Plan: "
                            + " -> ".join(action_name(item) for item in actions)
                        )
                    return actions
                queue.append(next_position)

        if trace:
            elapsed = perf_counter() - search_started
            print(f"[PLANNER] Path not found in {elapsed:.4f} seconds.")
            print("[PLANNER] Total cost: 0")
            print(f"[PLANNER] Number of nodes expanded: {expansions}")
            print(
                "[PLANNER] Number of unique nodes expanded: "
                f"{len(parent)}"
            )
            print(
                f"[PLANNER] No path found after {expansions} expansions."
            )
        return []

    def maze_distance(
        self,
        start: tuple[int, int],
        targets: set[tuple[int, int]] | frozenset[tuple[int, int]],
    ) -> int:
        if not targets:
            return 10_000
        if start in targets:
            return 0

        queue = deque([(start, 0)])
        visited = {start}
        while queue:
            position, distance = queue.popleft()
            for next_position, _ in self.neighbors(position):
                if next_position in visited:
                    continue
                if next_position in targets:
                    return distance + 1
                visited.add(next_position)
                queue.append((next_position, distance + 1))
        return 10_000


class Chapter2Agent:
    """Base interface implemented by the five Chapter 2 agent programs."""

    AGENT_NAME = "Chapter 2 Agent"
    PROGRAM_LOCATION = "choose_action()"
    CHAPTER2_CONCEPT = "Percept to action"
    SUPPORTS_FAST_TRAINING = False

    def __init__(self, world: WorldKnowledge):
        self.world = world
        self.last_reason = "Waiting for the first percept."

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        raise NotImplementedError

    def observe_transition(self, transition: Transition) -> None:
        """Learning agents may use feedback; other agents ignore it."""

    def observe_external_feedback(
        self,
        reward: float,
        percept: Percept,
        done: bool,
        outcome: str,
    ) -> None:
        """Receive delayed feedback such as collision or eating a ghost."""

    def reset_episode(self) -> None:
        """Reset episode-specific state while preserving learned knowledge."""

    def clear_learning(self) -> None:
        """Erase learned knowledge. Non-learning agents do nothing."""

    def hud_lines(self) -> tuple[str, ...]:
        return ()


class Entity:
    def __init__(self, row: int, col: int, color: tuple[int, int, int]):
        self.row = row
        self.col = col
        self.prev_row = row
        self.prev_col = col
        self.color = color
        self.direction = STOP

    @property
    def position(self) -> tuple[int, int]:
        return self.row, self.col

    def get_pixel_center(self, progress: float) -> tuple[float, float]:
        start_col = self.prev_col
        if abs(self.col - self.prev_col) > 1:
            start_col = self.col - self.direction[0]

        start_x = start_col * TILE_SIZE + TILE_SIZE // 2
        start_y = self.prev_row * TILE_SIZE + TILE_SIZE // 2
        end_x = self.col * TILE_SIZE + TILE_SIZE // 2
        end_y = self.row * TILE_SIZE + TILE_SIZE // 2

        return (
            start_x + (end_x - start_x) * progress,
            start_y + (end_y - start_y) * progress,
        )


class PacMan(Entity):
    def __init__(self, row: int, col: int):
        super().__init__(row, col, YELLOW)

    def draw(self, screen: pygame.Surface, progress: float) -> None:
        x, y = self.get_pixel_center(progress)
        radius = TILE_SIZE // 2 - 3
        pygame.draw.circle(screen, self.color, (int(x), int(y)), radius)

        cycle = (pygame.time.get_ticks() % 300) / 150.0
        if cycle > 1.0:
            cycle = 2.0 - cycle
        mouth_angle = 2 + 43 * cycle

        facing = {
            (1, 0): 0,
            (-1, 0): 180,
            (0, -1): 90,
            (0, 1): 270,
        }.get(self.direction, 0)

        start_rad = math.radians(facing - mouth_angle)
        end_rad = math.radians(facing + mouth_angle)
        points = [(x, y)]
        for index in range(11):
            angle = start_rad + (end_rad - start_rad) * (index / 10.0)
            points.append(
                (
                    x + (radius + 2) * math.cos(angle),
                    y - (radius + 2) * math.sin(angle),
                )
            )
        pygame.draw.polygon(screen, BLACK, points)


class Ghost(Entity):
    def __init__(
        self,
        row: int,
        col: int,
        color: tuple[int, int, int],
        release_delay_ms: int,
    ):
        super().__init__(row, col, color)
        self.spawn = (row, col)
        self.release_delay_ms = release_delay_ms
        self.released = False
        self.direction = DIRECTIONS["UP"]

    def draw(
        self,
        screen: pygame.Surface,
        progress: float,
        frightened: bool = False,
    ) -> None:
        x, y = self.get_pixel_center(progress)
        x_i, y_i = int(x), int(y)
        radius = TILE_SIZE // 2 - 3
        body_color = FRIGHTENED_BLUE if frightened else self.color

        pygame.draw.circle(screen, body_color, (x_i, y_i - 3), radius)
        pygame.draw.rect(
            screen,
            body_color,
            (x_i - radius, y_i - 3, radius * 2, radius + 6),
        )

        for index in range(3):
            pygame.draw.circle(
                screen,
                BLACK,
                (x_i - radius + 5 + index * (radius - 2), y_i + radius + 1),
                4,
            )

        eye_y = y_i - 6
        pygame.draw.circle(screen, WHITE, (x_i - 6, eye_y), 5)
        pygame.draw.circle(screen, WHITE, (x_i + 6, eye_y), 5)
        dx, dy = self.direction
        pupil_color = WHITE if frightened else MAZE_BLUE
        pygame.draw.circle(screen, pupil_color, (x_i - 6 + dx * 2, eye_y + dy * 2), 2)
        pygame.draw.circle(screen, pupil_color, (x_i + 6 + dx * 2, eye_y + dy * 2), 2)


class Game:
    def __init__(
        self,
        agent_class: Type[Chapter2Agent],
        level: list[str] | None = None,
    ):
        pygame.init()

        # Use a caller-supplied level for demonstrations, or the shared level
        # when an agent does not provide a custom one.
        self.level = level if level is not None else LEVEL
        self.rows = len(self.level)
        self.cols = len(self.level[0])
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE + HUD_HEIGHT

        self.grid, self.start, self.ghost_spawns, initial_pellets, initial_power = (
            self._parse_level()
        )
        self.initial_pellets = frozenset(initial_pellets)
        self.initial_power_pellets = frozenset(initial_power)
        self.world = WorldKnowledge(self.grid)
        self.agent = agent_class(self.world)

        pygame.display.set_caption(f"Pac-Man - {self.agent.AGENT_NAME}")
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 22, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 13)
        self.tiny_font = pygame.font.SysFont("consolas", 12)

        self.episode_number = 0
        self.training_mode = False
        self.reset_world()
        self.maze_bg = self.create_maze_surface()

    def _parse_level(self):
        grid: list[list[str]] = []
        start: tuple[int, int] | None = None
        ghost_spawns: list[tuple[int, int, int]] = []
        pellets: set[tuple[int, int]] = set()
        power: set[tuple[int, int]] = set()

        for row_index, raw_row in enumerate(self.level):
            row: list[str] = []
            for col_index, cell in enumerate(raw_row):
                row.append(cell if cell in {"#", "="} else " ")
                if cell == ".":
                    pellets.add((row_index, col_index))
                elif cell == "o":
                    power.add((row_index, col_index))
                elif cell == "P":
                    start = (row_index, col_index)
                elif cell in "1234":
                    ghost_spawns.append((int(cell) - 1, row_index, col_index))
            grid.append(row)

        if start is None:
            raise ValueError("LEVEL must contain P")
        ghost_spawns.sort()
        return grid, start, ghost_spawns, pellets, power

    def reset_world(self) -> None:
        self.episode_number += 1
        self.pellets = set(self.initial_pellets)
        self.power_pellets = set(self.initial_power_pellets)
        self.player = PacMan(*self.start)
        colors = [RED, CYAN, PINK, ORANGE]
        delays = [1200, 3000, 5200, 7600]
        self.ghosts = [
            Ghost(row, col, colors[index % len(colors)], delays[index])
            for index, row, col in self.ghost_spawns
        ]

        self.score = 0
        self.step_count = 0
        self.game_over = False
        self.win = False
        self.paused = False
        self.player_timer = 0
        self.ghost_timer = 0
        self.terminal_timer = 0
        self.start_time = pygame.time.get_ticks()
        self.frightened_until = 0
        self.last_action = STOP
        self.last_outcome = "RUNNING"
        self.agent.reset_episode()

    def create_maze_surface(self) -> pygame.Surface:
        scale = 4
        surf = pygame.Surface(
            (self.width * scale, self.rows * TILE_SIZE * scale)
        )
        surf.fill(BLACK)

        blue_width = 20 * scale
        blue_radius = blue_width // 2
        black_width = 14 * scale
        black_radius = black_width // 2
        tile = TILE_SIZE * scale

        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != "#":
                    continue
                x = col * tile + tile // 2
                y = row * tile + tile // 2
                pygame.draw.circle(surf, MAZE_BLUE, (x, y), blue_radius)
                if col < self.cols - 1 and self.grid[row][col + 1] == "#":
                    pygame.draw.line(
                        surf, MAZE_BLUE, (x, y), (x + tile, y), blue_width
                    )
                if row < self.rows - 1 and self.grid[row + 1][col] == "#":
                    pygame.draw.line(
                        surf, MAZE_BLUE, (x, y), (x, y + tile), blue_width
                    )

        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != "#":
                    continue
                x = col * tile + tile // 2
                y = row * tile + tile // 2
                pygame.draw.circle(surf, BLACK, (x, y), black_radius)
                if col < self.cols - 1 and self.grid[row][col + 1] == "#":
                    pygame.draw.line(
                        surf, BLACK, (x, y), (x + tile, y), black_width
                    )
                if row < self.rows - 1 and self.grid[row + 1][col] == "#":
                    pygame.draw.line(
                        surf, BLACK, (x, y), (x, y + tile), black_width
                    )

        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == "=":
                    y_door = row * tile + tile // 2
                    pygame.draw.line(
                        surf,
                        PINK,
                        (col * tile + 3 * scale, y_door),
                        (col * tile + tile - 3 * scale, y_door),
                        4 * scale,
                    )

        return pygame.transform.smoothscale(
            surf, (self.width, self.rows * TILE_SIZE)
        )

    def visible_ghosts(self):
        positions: list[tuple[int, int]] = []
        directions: list[tuple[int, int]] = []
        for ghost in self.ghosts:
            if not ghost.released:
                continue
            if manhattan(self.player.position, ghost.position) <= GHOST_SENSOR_RANGE:
                positions.append(ghost.position)
                directions.append(ghost.direction)
        return tuple(positions), tuple(directions)

    def sense_environment(self) -> Percept:
        visible_positions, visible_directions = self.visible_ghosts()
        return Percept(
            player=self.player.position,
            pellets=frozenset(self.pellets),
            power_pellets=frozenset(self.power_pellets),
            visible_ghosts=visible_positions,
            visible_ghost_directions=visible_directions,
            legal_actions=self.world.legal_actions_from(self.player.position),
            frightened=self.ghosts_are_frightened(),
            current_direction=self.player.direction,
            score=self.score,
            step_count=self.step_count,
            columns=self.cols,
        )

    def ghosts_are_frightened(self) -> bool:
        return pygame.time.get_ticks() < self.frightened_until

    def activate_power_pellet(self) -> None:
        self.frightened_until = pygame.time.get_ticks() + 7000

    def move_entity(
        self,
        entity: Entity,
        action: tuple[int, int],
        allow_door: bool = False,
    ) -> None:
        next_position = self.world.successor(entity.position, action, allow_door)
        entity.row, entity.col = next_position
        entity.direction = action

    def update_player(self) -> None:
        before = self.sense_environment()
        action = self.agent.choose_action(before)
        if action not in before.legal_actions:
            action = STOP

        score_before = self.score
        if action != STOP:
            self.move_entity(self.player, action)
        self.last_action = action
        self.step_count += 1

        position = self.player.position
        if position in self.pellets:
            self.pellets.remove(position)
            self.score += 10
        if position in self.power_pellets:
            self.power_pellets.remove(position)
            self.score += 50
            self.activate_power_pellet()

        reward = float(self.score - score_before) - 0.2
        outcome = "STEP"
        if not self.pellets and not self.power_pellets:
            self.win = True
            self.game_over = True
            self.last_outcome = "WIN"
            reward += 100.0
            outcome = "WIN"

        after = self.sense_environment()
        self.agent.observe_transition(
            Transition(before, action, reward, after, self.game_over, outcome)
        )

    def release_ghosts(self) -> None:
        elapsed = pygame.time.get_ticks() - self.start_time
        for ghost in self.ghosts:
            if not ghost.released and elapsed >= ghost.release_delay_ms:
                ghost.released = True

    def find_ghost_door(self) -> tuple[int, int] | None:
        for row, cells in enumerate(self.grid):
            for col, cell in enumerate(cells):
                if cell == "=":
                    return row, col
        return None

    def ghost_house_exit_action(self, ghost: Ghost) -> tuple[int, int]:
        door = self.find_ghost_door()
        if door is None:
            return DIRECTIONS["UP"]
        door_row, door_col = door
        if ghost.col < door_col:
            return DIRECTIONS["RIGHT"]
        if ghost.col > door_col:
            return DIRECTIONS["LEFT"]
        if ghost.row >= door_row:
            return DIRECTIONS["UP"]
        return DIRECTIONS["UP"]

    def choose_ghost_direction(self, ghost: Ghost) -> tuple[int, int]:
        if not ghost.released:
            return STOP

        door = self.find_ghost_door()
        if door is not None:
            door_row, door_col = door
            if ghost.row >= door_row and abs(ghost.col - door_col) <= 3:
                action = self.ghost_house_exit_action(ghost)
                if action in self.world.legal_actions_from(
                    ghost.position, allow_door=True
                ):
                    return action

        valid = list(self.world.legal_actions_from(ghost.position))
        if not valid:
            return STOP

        reverse = (-ghost.direction[0], -ghost.direction[1])
        non_reverse = [action for action in valid if action != reverse]
        if non_reverse:
            valid = non_reverse

        if self.ghosts_are_frightened():
            return max(
                valid,
                key=lambda action: manhattan(
                    self.world.successor(ghost.position, action),
                    self.player.position,
                ),
            )

        if random.random() < 0.70:
            return min(
                valid,
                key=lambda action: manhattan(
                    self.world.successor(ghost.position, action),
                    self.player.position,
                ),
            )
        return random.choice(valid)

    def update_ghosts(self) -> None:
        self.release_ghosts()
        for ghost in self.ghosts:
            if not ghost.released:
                continue
            action = self.choose_ghost_direction(ghost)
            if action == STOP:
                continue
            next_position = self.world.successor(
                ghost.position, action, allow_door=True
            )
            allow_door = self.world.is_ghost_door(next_position)
            self.move_entity(ghost, action, allow_door=allow_door)

    def reset_ghost(self, ghost: Ghost) -> None:
        ghost.row, ghost.col = ghost.spawn
        ghost.prev_row, ghost.prev_col = ghost.spawn
        ghost.released = False
        ghost.direction = DIRECTIONS["UP"]
        ghost.release_delay_ms = (
            pygame.time.get_ticks() - self.start_time + 2500
        )

    def check_collision(self, player_progress: float, ghost_progress: float) -> None:
        if self.game_over:
            return

        player_x, player_y = self.player.get_pixel_center(player_progress)
        for ghost in self.ghosts:
            if not ghost.released:
                continue
            ghost_x, ghost_y = ghost.get_pixel_center(ghost_progress)
            if math.hypot(player_x - ghost_x, player_y - ghost_y) >= TILE_SIZE // 2:
                continue

            if self.ghosts_are_frightened():
                self.score += 200
                self.agent.observe_external_feedback(
                    200.0,
                    self.sense_environment(),
                    False,
                    "ATE_GHOST",
                )
                self.reset_ghost(ghost)
            else:
                self.game_over = True
                self.win = False
                self.last_outcome = "CAUGHT"
                self.agent.observe_external_feedback(
                    -200.0,
                    self.sense_environment(),
                    True,
                    "CAUGHT",
                )
                return

    def handle_input(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
            if event.key == pygame.K_r:
                self.reset_world()
            if event.key == pygame.K_c:
                self.agent.clear_learning()
                self.reset_world()
            if (
                event.key == pygame.K_t
                and self.agent.SUPPORTS_FAST_TRAINING
            ):
                self.training_mode = not self.training_mode

    def update(self, elapsed_ms: int) -> None:
        if self.paused:
            return

        if self.game_over:
            if self.training_mode and self.agent.SUPPORTS_FAST_TRAINING:
                self.terminal_timer += elapsed_ms
                if self.terminal_timer >= 100:
                    self.reset_world()
            return

        player_step = (
            FAST_PLAYER_STEP_MS if self.training_mode else PLAYER_STEP_MS
        )
        ghost_step = FAST_GHOST_STEP_MS if self.training_mode else GHOST_STEP_MS

        self.player_timer += elapsed_ms
        self.ghost_timer += elapsed_ms

        while self.player_timer >= player_step and not self.game_over:
            self.player.prev_row = self.player.row
            self.player.prev_col = self.player.col
            self.update_player()
            self.player_timer -= player_step

        while self.ghost_timer >= ghost_step and not self.game_over:
            for ghost in self.ghosts:
                ghost.prev_row = ghost.row
                ghost.prev_col = ghost.col
            self.update_ghosts()
            self.ghost_timer -= ghost_step

        player_progress = min(1.0, self.player_timer / max(player_step, 1))
        ghost_progress = min(1.0, self.ghost_timer / max(ghost_step, 1))
        self.check_collision(player_progress, ghost_progress)

    def draw_maze_dynamic(self) -> None:
        self.screen.blit(self.maze_bg, (0, 0))
        for row, col in self.pellets:
            pygame.draw.circle(
                self.screen,
                WHITE,
                (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2),
                3,
            )

        pulse = 7 + int(
            2 * (1 + math.sin(pygame.time.get_ticks() / 150)) / 2
        )
        for row, col in self.power_pellets:
            pygame.draw.circle(
                self.screen,
                WHITE,
                (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2),
                pulse,
            )

    def draw_hud(self) -> None:
        hud_y = self.rows * TILE_SIZE
        pygame.draw.rect(self.screen, BLACK, (0, hud_y, self.width, HUD_HEIGHT))

        score_surface = self.font.render(f"SCORE: {self.score}", True, YELLOW)
        self.screen.blit(score_surface, (14, hud_y + 8))

        agent_surface = self.small_font.render(
            self.agent.AGENT_NAME,
            True,
            GREEN,
        )
        self.screen.blit(
            agent_surface,
            (self.width - agent_surface.get_width() - 14, hud_y + 10),
        )

        program_text = f"PROGRAM: {self.agent.PROGRAM_LOCATION}"
        program_surface = self.tiny_font.render(program_text, True, WHITE)
        self.screen.blit(program_surface, (14, hud_y + 39))

        reason = self.agent.last_reason[:75]
        reason_surface = self.tiny_font.render(f"DECISION: {reason}", True, WHITE)
        self.screen.blit(reason_surface, (14, hud_y + 57))

        extra = " | ".join(self.agent.hud_lines())[:75]
        if self.training_mode:
            extra = (extra + " | FAST TRAINING").strip(" |")
        if extra:
            extra_surface = self.tiny_font.render(extra, True, GRAY)
            self.screen.blit(extra_surface, (14, hud_y + 75))

    def draw_overlay(self) -> None:
        if not self.game_over and not self.paused:
            return

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        self.screen.blit(overlay, (0, 0))

        if self.paused and not self.game_over:
            title = "PAUSED"
            color = WHITE
            subtitle = "Space: resume"
        else:
            title = "AGENT WINS!" if self.win else "AGENT CAUGHT"
            color = GREEN if self.win else RED
            subtitle = "R: restart"
            if self.agent.SUPPORTS_FAST_TRAINING:
                subtitle += "   T: fast training"

        title_surface = self.font.render(title, True, color)
        subtitle_surface = self.small_font.render(subtitle, True, WHITE)
        self.screen.blit(
            title_surface,
            (
                self.width // 2 - title_surface.get_width() // 2,
                self.rows * TILE_SIZE // 2 - 20,
            ),
        )
        self.screen.blit(
            subtitle_surface,
            (
                self.width // 2 - subtitle_surface.get_width() // 2,
                self.rows * TILE_SIZE // 2 + 16,
            ),
        )

    def draw(self) -> None:
        self.screen.fill(BLACK)
        self.draw_maze_dynamic()

        player_step = (
            FAST_PLAYER_STEP_MS if self.training_mode else PLAYER_STEP_MS
        )
        ghost_step = FAST_GHOST_STEP_MS if self.training_mode else GHOST_STEP_MS
        player_progress = min(1.0, self.player_timer / max(player_step, 1))
        ghost_progress = min(1.0, self.ghost_timer / max(ghost_step, 1))

        self.player.draw(self.screen, player_progress)
        frightened = self.ghosts_are_frightened()
        for ghost in self.ghosts:
            ghost.draw(
                self.screen,
                ghost_progress,
                frightened=frightened and ghost.released,
            )

        self.draw_hud()
        self.draw_overlay()
        pygame.display.flip()

    def run(self) -> None:
        while True:
            elapsed_ms = self.clock.tick(FPS)
            self.handle_input()
            self.update(elapsed_ms)
            self.draw()


def run_agent(
    agent_class: Type[Chapter2Agent],
    level: list[str] | None = None,
) -> None:
    """Run an agent, optionally using a custom classroom level."""

    Game(agent_class, level=level).run()
