"""
GameEngine: owns the frog and all vehicles, and runs one frame's worth
of game logic.

Tasks implemented:
- Correct collision detection
- 3 lives
- Frog respawn after collision
- Game Over when lives are lost
- Goal detection
- Score tracking
- 30-second game timer
"""

import random

import pygame

from game.frog import Frog
from game.vehicle import Vehicle
from game.collisions import check_collision
from game.renderer import (
    GRID_COLS,
    GRID_ROWS,
    GOAL_ROW,
    ROAD_ROWS,
    START_ROW,
    CELL_SIZE,
    WIDTH,
    HEIGHT,
)

LANE_SPEEDS = [1.5, -2, 2, -2.5, 1.5, -2]

GAME_TIME = 30


class GameEngine:
    def __init__(self):
        self.lives = 3
        self.score = 0
        self.game_over = False

        self.start_time = pygame.time.get_ticks()

        self._build_entities()

    def _build_entities(self):
        start_col = GRID_COLS // 2

        self.frog = Frog(
            col=start_col,
            row=START_ROW,
            start_col=start_col,
            start_row=START_ROW,
            cols=GRID_COLS,
            start_row_limit=START_ROW,
        )

        frog_x_range = (
            start_col * CELL_SIZE,
            start_col * CELL_SIZE + CELL_SIZE
        )

        self.vehicles = []

        for i, row in enumerate(ROAD_ROWS):
            speed = LANE_SPEEDS[i % len(LANE_SPEEDS)]

            vehicle_width = 40 if i % 2 == 0 else 70
            spacing = 300
            count = 2

            for _attempt in range(20):
                phase = random.randint(0, spacing - 1)
                positions = []
                safe = True

                for n in range(count):
                    offset = phase + n * spacing

                    x = (
                        offset
                        if speed > 0
                        else WIDTH - offset - vehicle_width
                    )

                    positions.append(x)

                    if not (
                        x + vehicle_width <= frog_x_range[0]
                        or x >= frog_x_range[1]
                    ):
                        safe = False

                if safe:
                    break

            for x in positions:
                self.vehicles.append(
                    Vehicle(
                        x=x,
                        row=row,
                        width=vehicle_width,
                        height=CELL_SIZE - 8,
                        speed=speed,
                    )
                )

    def handle_keydown(self, key):
        if self.game_over:
            if key == pygame.K_r:
                self.lives = 3
                self.score = 0
                self.game_over = False
                self.start_time = pygame.time.get_ticks()
                self._build_entities()
            return

        if key == pygame.K_UP:
            self.frog.move(0, -1)

        elif key == pygame.K_DOWN:
            self.frog.move(0, 1)

        elif key == pygame.K_LEFT:
            self.frog.move(-1, 0)

        elif key == pygame.K_RIGHT:
            self.frog.move(1, 0)

        elif key == pygame.K_r:
            self.lives = 3
            self.score = 0
            self.game_over = False
            self.start_time = pygame.time.get_ticks()
            self._build_entities()

    def update(self):
        if self.game_over:
            return

        # Calculate elapsed time in seconds.
        elapsed_time = (
            pygame.time.get_ticks() - self.start_time
        ) / 1000

        # Game ends when 30 seconds have passed.
        if elapsed_time >= GAME_TIME:
            self.game_over = True
            return

        # Move vehicles.
        for v in self.vehicles:
            v.update(road_width_px=WIDTH)

        # Check collision.
        if check_collision(self.frog, self.vehicles):
            self.lives -= 1
            self.frog.reset()

            if self.lives <= 0:
                self.game_over = True
                return

        # Check goal.
        if self.frog.row == GOAL_ROW:
            self.score += 1
            self.frog.reset()

    def draw(self, surface, font):
        from game import renderer

        elapsed_time = (
            pygame.time.get_ticks() - self.start_time
        ) / 1000

        remaining_time = max(0, GAME_TIME - int(elapsed_time))

        renderer.draw_scene(
            surface,
            self.frog,
            self.vehicles,
            font,
            self.lives,
            self.score,
            remaining_time
        )

        if self.game_over:
            if remaining_time == 0:
                message = "TIME UP - Press R to restart"
            else:
                message = "GAME OVER - Press R to restart"

            renderer.draw_banner(
                surface,
                font,
                message
            )