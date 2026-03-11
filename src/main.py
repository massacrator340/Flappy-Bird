"""Main execution script for the Flappy Bird game loop."""
import sys

import pygame

from background import Ground, Sky


def main():
    """Initialize the game engine and manage the real-time event loop."""
    screen_width = 1024
    screen_height = 768

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()
    fps = 60

    velocity = 1
    filename_sky = "background-day.png"
    filename_ground = "base.png"

    sky = Sky(filename_sky, 0, 0, screen)
    ground = Ground(filename_ground, 0, sky.get_height(), screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        sky.draw()
        ground.update(velocity)

        pygame.display.update()
        clock.tick(fps)


main()
