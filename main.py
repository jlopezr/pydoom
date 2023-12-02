import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 640, 480
FPS = 60

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Define the player
player_pos = [5, 5]
player_angle = 0

# Define the map
MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Define a function to cast a ray
def cast_ray(angle):
    # Calculate the direction of the ray
    dx = math.cos(angle)
    dy = math.sin(angle)

    # Step along the ray until we hit a wall
    for i in range(100):
        x = player_pos[0] + dx * i
        y = player_pos[1] + dy * i

        # If we're outside the map, stop
        if x < 0 or y < 0 or x >= len(MAP[0]) or y >= len(MAP):
            return i

        # If we've hit a wall, stop
        if MAP[int(y)][int(x)] == 1:
            return i

    return i

# Define a function to render the raycast
def render_raycast():
    # Create a new surface
    surface = pygame.Surface((WIDTH, HEIGHT))

    # Cast a ray for each column of the screen
    for x in range(WIDTH):
        distance = cast_ray(player_angle + x / WIDTH - 0.5)
        # Draw a line with height inversely proportional to the distance
        height = HEIGHT / distance
        pygame.draw.line(surface, (255, 255, 255), (x, HEIGHT // 2 - height // 2), (x, HEIGHT // 2 + height // 2))

    return surface

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Render the raycast and blit it onto the screen
    raycast = render_raycast()
    screen.blit(raycast, (0, 0))

    pygame.display.flip()
    pygame.time.Clock().tick(FPS)