import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 640, 480
FPS = 60
SPEED = 0.05

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

# Define the map size in pixels
MAP_WIDTH = len(MAP[0]) * 10
MAP_HEIGHT = len(MAP) * 10

# Define the screen size
SCREEN_WIDTH = WIDTH + MAP_WIDTH
SCREEN_HEIGHT = max(HEIGHT, MAP_HEIGHT)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

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
def render_raycast(save_distances=False):
    # Create a new surface
    surface = pygame.Surface((WIDTH, HEIGHT))

    # Create a list to store the distances
    distances = []

    # Cast a ray for each column of the screen
    for x in range(WIDTH):
        distance = cast_ray(player_angle + x / WIDTH - 0.5)
        distances.append(distance)
        # Draw a line with height inversely proportional to the distance
        if distance == 0:
            height = HEIGHT
        else:
            height = HEIGHT / distance

        # Calculate a grayscale color based on the distance
        color = 255 - min(distance * 2, 255)

        pygame.draw.line(surface, (color, color, color), (x, HEIGHT // 2 - height // 2), (x, HEIGHT // 2 + height // 2))

    # If save_distances is True, write the distances to a file
    if save_distances:
        with open('distances.txt', 'w') as f:
            for distance in distances:
                f.write(str(distance) + '\n')

    return surface
# Define a function to render the map
def render_map():
    # Create a new surface
    surface = pygame.Surface((WIDTH, HEIGHT))

    # Draw the map
    for y in range(len(MAP)):
        for x in range(len(MAP[y])):
            if MAP[y][x] == 1:
                pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(x * 10, y * 10, 10, 10))

    # Draw the player
    pygame.draw.circle(surface, (255, 0, 0), (int(player_pos[0] * 10), int(player_pos[1] * 10)), 5)

    # Draw the player's direction
    dx = math.cos(player_angle) * 20
    dy = math.sin(player_angle) * 20
    pygame.draw.line(surface, (255, 0, 0), (int(player_pos[0] * 10), int(player_pos[1] * 10)), (int(player_pos[0] * 10 + dx), int(player_pos[1] * 10 + dy)))

    return surface

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Get the current state of the keyboard
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos[0] += math.cos(player_angle) * SPEED
        player_pos[1] += math.sin(player_angle) * SPEED
    if keys[pygame.K_s]:
        player_pos[0] -= math.cos(player_angle) * SPEED
        player_pos[1] -= math.sin(player_angle) * SPEED
    if keys[pygame.K_d]:
        player_pos[0] -= math.sin(player_angle) * SPEED
        player_pos[1] += math.cos(player_angle) * SPEED
    if keys[pygame.K_a]:
        player_pos[0] += math.sin(player_angle) * SPEED
        player_pos[1] -= math.cos(player_angle) * SPEED
    if keys[pygame.K_LEFT]:
        player_angle -= 0.1
    if keys[pygame.K_RIGHT]:
        player_angle += 0.1
    if keys[pygame.K_p]:
        render_raycast(True)
        pygame.time.wait(500)


    # Render the raycast and blit it onto the screen
    raycast = render_raycast()
    screen.blit(raycast, (0, (SCREEN_HEIGHT - HEIGHT) // 2))

    # Render the map and blit it onto the screen
    map_view = render_map()
    screen.blit(map_view, (WIDTH, (SCREEN_HEIGHT - MAP_HEIGHT) // 2))

    pygame.display.flip()
    pygame.time.Clock().tick(FPS)