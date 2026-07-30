"""
Simple Reflex Pac-Man Agent
============================

This version is intended for an introductory AI lesson. Pac-Man is controlled
by a SIMPLE REFLEX AGENT: it selects an action using only the percept it
receives right now and a short list of condition-action rules.

The agent does NOT:
    * remember earlier percepts or actions,
    * build an internal model of the world,
    * search for paths, or
    * calculate utilities for future outcomes.

Because it has no memory or planning, the agent can become stuck in a loop.
That limitation is useful for demonstrating why more advanced agents exist.

Install:
    python -m pip install pygame

Run:
    python simple_reflex_pacman_agent.py

Controls:
    Space - pause/resume
    R     - restart
    Esc   - quit
"""

from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass

import pygame

TILE_SIZE = 30
HUD_HEIGHT = 60
FPS = 60

BLACK = (0, 0, 0)
MAZE_BLUE = (15, 35, 255)
WHITE = (245, 245, 245)
YELLOW = (255, 230, 0)
RED = (245, 70, 55)
PINK = (255, 185, 220)
CYAN = (60, 220, 255)
ORANGE = (255, 155, 45)
GREEN = (60, 220, 100)
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
    "#.#.# #   #.#.#.#",
    "#...# #####.#...#",
    "#o......P......0#",
    "#################",
]

DIRECTIONS = {
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
    "UP": (0, -1),
    "DOWN": (0, 1),
}

DIRECTION_ORDER = list(DIRECTIONS.values())


@dataclass(frozen=True)
class Percept:
    """Everything Pac-Man can sense during one decision.

    A simple reflex agent may inspect this current percept, but it may not
    remember an older percept and compare the two.
    """

    player: tuple[int, int]
    pellets: frozenset[tuple[int, int]]
    power_pellets: frozenset[tuple[int, int]]
    active_ghosts: tuple[tuple[int, int], ...]
    ghosts_frightened: bool
    legal_actions: tuple[tuple[int, int], ...]
    columns: int


class Entity:
    def __init__(self, row: int, col: int, color: tuple[int, int, int]):
        self.row = row
        self.col = col
        self.prev_row = row
        self.prev_col = col
        self.color = color
        self.direction = (0, 0)

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

        x = start_x + (end_x - start_x) * progress
        y = start_y + (end_y - start_y) * progress

        return x, y


class PacMan(Entity):
    def __init__(self, row: int, col: int):
        super().__init__(row, col, YELLOW)

    def draw(self, screen: pygame.Surface, progress: float) -> None:
        x, y = self.get_pixel_center(progress)
        radius = TILE_SIZE // 2 - 3

        # Draw a perfect solid yellow circle
        pygame.draw.circle(screen, self.color, (int(x), int(y)), radius)

        # Calculate mouth animation based on global time
        time_ms = pygame.time.get_ticks()
        # Cycle goes 0.0 to 1.0 and back down to 0.0
        cycle = (time_ms % 300) / 150.0 
        if cycle > 1.0:
            cycle = 2.0 - cycle
            
        # Mouth opens from 2 degrees up to 45 degrees
        mouth_angle = 2 + (43 * cycle)

        facing = {
            (1, 0): 0,
            (-1, 0): 180,
            (0, -1): 90,
            (0, 1): 270,
        }.get(self.direction, 0)

        start_rad = math.radians(facing - mouth_angle)
        end_rad = math.radians(facing + mouth_angle)

        # Draw a black polygon wedge to "cut out" the mouth
        points = [(x, y)]
        for i in range(11):
            a = start_rad + (end_rad - start_rad) * (i / 10.0)
            # Add +2 to radius to ensure the wedge fully clears the circle's edge
            points.append((x + (radius + 2) * math.cos(a), y - (radius + 2) * math.sin(a)))
            
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

    def draw(self, screen: pygame.Surface, progress: float, frightened: bool = False) -> None:
        x, y = self.get_pixel_center(progress)
        radius = TILE_SIZE // 2 - 3
        body_color = FRIGHTENED_BLUE if frightened else self.color

        pygame.draw.circle(screen, body_color, (x, y - 3), radius)
        pygame.draw.rect(
            screen,
            body_color,
            (x - radius, y - 3, radius * 2, radius + 6),
        )

        for i in range(3):
            pygame.draw.circle(
                screen,
                BLACK,
                (x - radius + 5 + i * (radius - 2), y + radius + 1),
                4,
            )

        eye_y = y - 6
        pygame.draw.circle(screen, WHITE, (x - 6, eye_y), 5)
        pygame.draw.circle(screen, WHITE, (x + 6, eye_y), 5)

        dx, dy = self.direction
        pupil_color = WHITE if frightened else MAZE_BLUE
        pygame.draw.circle(screen, pupil_color, (x - 6 + dx * 2, eye_y + dy * 2), 2)
        pygame.draw.circle(screen, pupil_color, (x + 6 + dx * 2, eye_y + dy * 2), 2)


class SimpleReflexPacManAgent:
    """Pac-Man controlled exclusively by condition-action rules.

    The rules are evaluated from top to bottom. The first matching rule
    determines the action. ``last_reason`` is only explanatory diagnostic
    text; the agent never reads it when making a decision.
    """

    def __init__(self) -> None:
        self.last_reason = "Waiting for first percept."

    @staticmethod
    def next_position(
        percept: Percept,
        action: tuple[int, int],
    ) -> tuple[int, int]:
        """Return the square reached by one action.

        Pac-Man tunnels wrap around horizontally, so the column uses modulo.
        This calculation looks only one move ahead; it is not pathfinding.
        """

        dx, dy = action
        row, col = percept.player
        return row + dy, (col + dx) % percept.columns

    @staticmethod
    def is_next_to(
        first: tuple[int, int],
        second: tuple[int, int],
    ) -> bool:
        """Test whether two squares touch vertically or horizontally."""

        row_difference = abs(first[0] - second[0])
        column_difference = abs(first[1] - second[1])
        return row_difference + column_difference <= 1

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        """Apply simple condition-action rules to the current percept."""

        # RULE 1: IF no movement is possible, THEN stay still.
        if not percept.legal_actions:
            self.last_reason = "No legal move."
            return (0, 0)

        # Create a one-step view of each legal action. This is derived entirely
        # from the current percept and is discarded after this decision.
        destinations = {
            action: self.next_position(percept, action)
            for action in percept.legal_actions
        }

        # RULE 2: IF ghosts are frightened and one is one move away,
        # THEN move onto that ghost to eat it.
        if percept.ghosts_frightened:
            for action in percept.legal_actions:
                if destinations[action] in percept.active_ghosts:
                    self.last_reason = "Rule 2: eat adjacent frightened ghost."
                    return action

        # RULE 3: IF a dangerous ghost is nearby, THEN take the first legal
        # action that does not place Pac-Man on or next to a ghost.
        #
        # Notice that the agent does not compare scores or predict what a ghost
        # will do. It simply checks whether this rule's condition is true.
        if not percept.ghosts_frightened:
            ghost_near_player = any(
                self.is_next_to(percept.player, ghost)
                for ghost in percept.active_ghosts
            )
            if ghost_near_player:
                for action in percept.legal_actions:
                    destination = destinations[action]
                    destination_is_safe = all(
                        not self.is_next_to(destination, ghost)
                        for ghost in percept.active_ghosts
                    )
                    if destination_is_safe:
                        self.last_reason = "Rule 3: move away from nearby ghost."
                        return action

        # RULE 4: IF a power pellet is one move away, THEN eat it.
        for action in percept.legal_actions:
            if destinations[action] in percept.power_pellets:
                self.last_reason = "Rule 4: eat adjacent power pellet."
                return action

        # RULE 5: IF a regular pellet is one move away, THEN eat it.
        for action in percept.legal_actions:
            if destinations[action] in percept.pellets:
                self.last_reason = "Rule 5: eat adjacent pellet."
                return action

        # RULE 6 (default): take the first legal action. The fixed action order
        # is LEFT, RIGHT, UP, DOWN. No earlier action is remembered.
        self.last_reason = "Rule 6: take first legal action."
        return percept.legal_actions[0]


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pac-Man as a Simple Reflex Agent")

        self.rows = len(LEVEL)
        self.cols = max(len(row) for row in LEVEL)
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE + HUD_HEIGHT

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 23, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 14)

        self.reset()
        
        # Pre-render the 4x supersampled wall background once
        self.maze_bg = self.create_maze_surface()

    def reset(self) -> None:
        self.grid: list[list[str]] = []
        self.pellets: set[tuple[int, int]] = set()
        self.power_pellets: set[tuple[int, int]] = set()
        self.ghosts: list[Ghost] = []

        self.score = 0  
        self.game_over = False
        self.win = False
        self.paused = False
        self.player_timer = 0
        self.ghost_timer = 0
        self.start_time = pygame.time.get_ticks()
        self.frightened_until = 0

        ghost_colors = [RED, CYAN, PINK, ORANGE]
        release_delays = [1200, 3000, 5200, 7600]

        for row_index, raw_row in enumerate(LEVEL):
            row = raw_row.ljust(self.cols)
            grid_row = []

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
                    self.player = PacMan(row_index, col_index)
                elif cell in "1234":
                    ghost_index = int(cell) - 1
                    self.ghosts.append(
                        Ghost(
                            row_index,
                            col_index,
                            ghost_colors[ghost_index],
                            release_delays[ghost_index],
                        )
                    )

            self.grid.append(grid_row)

        # The environment creates the agent, but the agent receives no direct
        # reference to the Game. It can act only on the Percept passed to it.
        self.agent = SimpleReflexPacManAgent()

    def create_maze_surface(self) -> pygame.Surface:
        """
        Renders the maze background at 4x resolution and shrinks it using
        smoothscale. This creates a flawlessly anti-aliased double-wall look.
        """
        scale = 4
        surf_width = self.width * scale
        surf_height = (self.rows * TILE_SIZE) * scale
        surf = pygame.Surface((surf_width, surf_height))
        surf.fill(BLACK)
        
        blue_width = 20 * scale
        blue_radius = blue_width // 2
        black_width = 14 * scale
        black_radius = black_width // 2
        t_size = TILE_SIZE * scale

        # Pass 1: Solid Blue Lines
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != "#":
                    continue
                
                x = col * t_size + t_size // 2
                y = row * t_size + t_size // 2
                
                pygame.draw.circle(surf, MAZE_BLUE, (x, y), blue_radius)
                
                if col < self.cols - 1 and self.grid[row][col+1] == "#":
                    pygame.draw.line(surf, MAZE_BLUE, (x, y), (x + t_size, y), blue_width)
                    
                if row < self.rows - 1 and self.grid[row+1][col] == "#":
                    pygame.draw.line(surf, MAZE_BLUE, (x, y), (x, y + t_size), blue_width)

        # Pass 2: Hollow Black Lines
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != "#":
                    continue
                
                x = col * t_size + t_size // 2
                y = row * t_size + t_size // 2
                
                pygame.draw.circle(surf, BLACK, (x, y), black_radius)
                
                if col < self.cols - 1 and self.grid[row][col+1] == "#":
                    pygame.draw.line(surf, BLACK, (x, y), (x + t_size, y), black_width)
                    
                if row < self.rows - 1 and self.grid[row+1][col] == "#":
                    pygame.draw.line(surf, BLACK, (x, y), (x, y + t_size), black_width)

        # Ghost House Door
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == "=":
                    y_door = row * t_size + t_size // 2
                    x_start = col * t_size + 3 * scale
                    x_end = col * t_size + t_size - 3 * scale
                    pygame.draw.line(surf, PINK, (x_start, y_door), (x_end, y_door), 4 * scale)

        # Downscale for perfection
        return pygame.transform.smoothscale(surf, (self.width, self.rows * TILE_SIZE))

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

    def legal_actions(
        self,
        entity: Entity,
        allow_house_door: bool = False,
    ) -> tuple[tuple[int, int], ...]:
        actions = []

        for action in DIRECTION_ORDER:
            dx, dy = action
            next_row = entity.row + dy
            next_col = self.wrap_col(entity.col + dx)

            if self.is_wall(next_row, next_col):
                continue

            if self.is_ghost_door(next_row, next_col) and not allow_house_door:
                continue

            actions.append(action)

        return tuple(actions)

    def move_entity(self, entity: Entity, action: tuple[int, int]) -> None:
        dx, dy = action
        entity.row += dy
        entity.col = self.wrap_col(entity.col + dx)
        entity.direction = action

    def sense_environment(self) -> Percept:
        """Build the agent's current percept.

        Released ghosts are included because they can interact with Pac-Man.
        Ghosts waiting inside the house are not currently a threat.
        """

        return Percept(
            player=self.player.position,
            pellets=frozenset(self.pellets),
            power_pellets=frozenset(self.power_pellets),
            active_ghosts=tuple(
                ghost.position for ghost in self.ghosts if ghost.released
            ),
            ghosts_frightened=self.ghosts_are_frightened(),
            legal_actions=self.legal_actions(self.player),
            columns=self.cols,
        )

    def ghosts_are_frightened(self) -> bool:
        return pygame.time.get_ticks() < self.frightened_until

    def activate_power_pellet(self) -> None:
        self.frightened_until = pygame.time.get_ticks() + 7000

    def update_player(self) -> None:
        percept = self.sense_environment()
        action = self.agent.choose_action(percept)

        if action in percept.legal_actions:
            self.move_entity(self.player, action)

        position = self.player.position

        if position in self.pellets:
            self.pellets.remove(position)
            self.score += 10

        if position in self.power_pellets:
            self.power_pellets.remove(position)
            self.score += 50
            self.activate_power_pellet()

        if not self.pellets and not self.power_pellets:
            self.win = True
            self.game_over = True

    def release_ghosts(self) -> None:
        elapsed = pygame.time.get_ticks() - self.start_time

        for ghost in self.ghosts:
            if not ghost.released and elapsed >= ghost.release_delay_ms:
                ghost.released = True

    def ghost_house_exit_action(self, ghost: Ghost) -> tuple[int, int]:
        door = self.find_ghost_door()

        if door is None:
            return DIRECTIONS["UP"]

        door_row, door_col = door

        if ghost.col < door_col:
            return DIRECTIONS["RIGHT"]
        if ghost.col > door_col:
            return DIRECTIONS["LEFT"]
        if ghost.row > door_row:
            return DIRECTIONS["UP"]

        return DIRECTIONS["UP"]

    def find_ghost_door(self) -> tuple[int, int] | None:
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if cell == "=":
                    return row_index, col_index
        return None

    def choose_ghost_direction(self, ghost: Ghost) -> tuple[int, int]:
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

        if random.random() < 0.70:
            return min(
                valid,
                key=lambda action: (
                    abs((ghost.row + action[1]) - self.player.row)
                    + abs(self.wrap_col(ghost.col + action[0]) - self.player.col)
                ),
            )

        return random.choice(valid)

    def update_ghosts(self) -> None:
        self.release_ghosts()

        for ghost in self.ghosts:
            if not ghost.released:
                continue

            action = self.choose_ghost_direction(ghost)
            if action != (0, 0):
                allow_door = self.is_ghost_door(
                    ghost.row + action[1],
                    self.wrap_col(ghost.col + action[0]),
                )
                legal = self.legal_actions(
                    ghost,
                    allow_house_door=allow_door,
                )
                if action in legal:
                    self.move_entity(ghost, action)

    def reset_ghost(self, ghost: Ghost) -> None:
        ghost.row, ghost.col = ghost.spawn
        ghost.prev_row, ghost.prev_col = ghost.spawn
        ghost.released = False
        ghost.direction = DIRECTIONS["UP"]
        ghost.release_delay_ms = (
            pygame.time.get_ticks() - self.start_time + 2500
        )

    def check_collision(self, player_progress: float, ghost_progress: float) -> None:
        px, py = self.player.get_pixel_center(player_progress)

        for ghost in self.ghosts:
            if not ghost.released:
                continue

            gx, gy = ghost.get_pixel_center(ghost_progress)
            
            # Calculate actual pixel distance between the two entities
            distance = math.hypot(px - gx, py - gy)

            # Trigger collision only if their centers are within half a tile of each other
            if distance < TILE_SIZE // 2:
                if self.ghosts_are_frightened():
                    self.score += 200
                    self.reset_ghost(ghost)
                else:
                    self.game_over = True
                    self.win = False
                    return

    def handle_input(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                if event.key == pygame.K_r:
                    self.reset()

    def update(self, elapsed_ms: int) -> None:
        if self.game_over or self.paused:
            return

        self.player_timer += elapsed_ms
        self.ghost_timer += elapsed_ms

        while self.player_timer >= 135:
            self.player.prev_row = self.player.row
            self.player.prev_col = self.player.col
            self.update_player()
            self.player_timer -= 135

        while self.ghost_timer >= 180:
            for ghost in self.ghosts:
                ghost.prev_row = ghost.row
                ghost.prev_col = ghost.col
            self.update_ghosts()
            self.ghost_timer -= 180

        # Calculate exact visual positions and check pixel-perfect collision every frame
        player_progress = min(1.0, self.player_timer / 135.0)
        ghost_progress = min(1.0, self.ghost_timer / 180.0)
        self.check_collision(player_progress, ghost_progress)

    def draw_hud(self) -> None:
        hud_y_start = self.rows * TILE_SIZE
        pygame.draw.rect(self.screen, BLACK, (0, hud_y_start, self.width, HUD_HEIGHT))

        score_surface = self.font.render(f"SCORE:  {self.score}", True, YELLOW)
        self.screen.blit(score_surface, (14, hud_y_start + 15))

        info = "SIMPLE REFLEX AGENT"
        if self.ghosts_are_frightened():
            remaining = max(0.0, (self.frightened_until - pygame.time.get_ticks()) / 1000)
            info += f" | POWER MODE {remaining:.1f}s"

        info_surface = self.small_font.render(info, True, GREEN)
        self.screen.blit(info_surface, (self.width - info_surface.get_width() - 20, hud_y_start + 23))

    def draw_maze_dynamic(self) -> None:
        # Blit the cached supersampled walls
        self.screen.blit(self.maze_bg, (0, 0))
        
        # Draw dynamic items (pellets) over the background
        for row in range(self.rows):
            for col in range(self.cols):
                x_c = col * TILE_SIZE + TILE_SIZE // 2
                y_c = row * TILE_SIZE + TILE_SIZE // 2

                if (row, col) in self.pellets:
                    pygame.draw.circle(self.screen, WHITE, (x_c, y_c), 3)

                if (row, col) in self.power_pellets:
                    pulse = 7 + int(2 * (1 + math.sin(pygame.time.get_ticks() / 150)) / 2)
                    pygame.draw.circle(self.screen, WHITE, (x_c, y_c), pulse)

    def draw_overlay(self) -> None:
        if not self.game_over and not self.paused:
            return

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        self.screen.blit(overlay, (0, 0))

        if self.paused and not self.game_over:
            title = "PAUSED"
            color = WHITE
            subtitle = "Press Space to resume"
        else:
            title = "AGENT WINS!" if self.win else "AGENT CAUGHT"
            color = GREEN if self.win else RED
            subtitle = "Press R to restart"

        title_surface = self.font.render(title, True, color)
        subtitle_surface = self.small_font.render(subtitle, True, WHITE)

        self.screen.blit(
            title_surface,
            (
                self.width // 2 - title_surface.get_width() // 2,
                self.height // 2 - 26,
            ),
        )
        self.screen.blit(
            subtitle_surface,
            (
                self.width // 2 - subtitle_surface.get_width() // 2,
                self.height // 2 + 10,
            ),
        )

    def draw(self) -> None:
        self.screen.fill(BLACK)
        
        self.draw_maze_dynamic()
        
        player_progress = min(1.0, self.player_timer / 135.0)
        self.player.draw(self.screen, player_progress)

        ghost_progress = min(1.0, self.ghost_timer / 180.0)
        frightened = self.ghosts_are_frightened()
        for ghost in self.ghosts:
            ghost.draw(self.screen, ghost_progress, frightened=frightened and ghost.released)
            
        self.draw_hud()
        self.draw_overlay()
        pygame.display.flip()

    def run(self) -> None:
        while True:
            elapsed_ms = self.clock.tick(FPS)
            self.handle_input()
            self.update(elapsed_ms)
            self.draw()


if __name__ == "__main__":
    Game().run()
