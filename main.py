import pygame
import sys
import math
import time

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 640, 480
FPS = 60
SPEED = 0.05

# Define the player
player_pos = [5, 5]
player_angle = 0
god_mode = False

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

# Load the wall texture
wall_texture = pygame.image.load('wall.png')

# Create a font object
font = pygame.font.Font(None, 24)  # Change the size as needed

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create a new surface
raycast_surface = pygame.Surface((WIDTH, HEIGHT))

# Create a new surface
map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))

# Define a function to clamp values between a minimum and maximum
def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def cast_ray(angle):
    # Calculate the direction of the ray
    dx = math.cos(angle)
    dy = math.sin(angle)

    # Calculate the length of the ray from one x or y-side to next x or y-side
    delta_dist_x = abs(1 / (dx if dx != 0 else 1e-5))
    delta_dist_y = abs(1 / (dy if dy != 0 else 1e-5))

    # Calculate step direction and initial side distance
    if dx < 0:
        step_x = -1
        side_dist_x = (player_pos[0] - int(player_pos[0])) * delta_dist_x
    else:
        step_x = 1
        side_dist_x = (int(player_pos[0]) + 1 - player_pos[0]) * delta_dist_x

    if dy < 0:
        step_y = -1
        side_dist_y = (player_pos[1] - int(player_pos[1])) * delta_dist_y
    else:
        step_y = 1
        side_dist_y = (int(player_pos[1]) + 1 - player_pos[1]) * delta_dist_y

    # Perform DDA
    x, y = int(player_pos[0]), int(player_pos[1])
    hit_side = None
    while MAP[y][x] == 0:
        # Jump to next map square
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            x += step_x
            hit_side = 0
        else:
            side_dist_y += delta_dist_y
            y += step_y
            hit_side = 1

        # Check if ray has hit a wall
        if MAP[y][x] > 0:
            break

    # Calculate distance of perpendicular ray (Euclidean distance will give fisheye effect!)
    if hit_side is None:
        perp_wall_dist = 0  # or some other default value
    elif hit_side == 0:
        perp_wall_dist = (x - player_pos[0] + (1 - step_x) / 2) / dx
    else:
        perp_wall_dist = (y - player_pos[1] + (1 - step_y) / 2) / dy
    return perp_wall_dist, hit_side

# Define a function to render the raycast
def render_raycast(save_distances=False):

    # Fill the render surface with black
    raycast_surface.fill((0, 0, 0))

    # Create a list to store the distances
    distances = []

    # Start the timer
    start_time = time.time()

    # Cast a ray for each column of the screen
    for x in range(WIDTH):
        distance, hit  = cast_ray(player_angle + x / WIDTH - 0.5)
        distances.append((distance, hit))

        # if hit is not None:
        #     # Look up the texture column
        #     tx, _ = hit
        #     tx = int(tx * wall_texture.get_width())

        #     # Calculate the height of the wall slice
        #     height = int(HEIGHT / max(distance, 0.0001))

        #     # Scale the texture column to the height of the wall slice
        #     column = pygame.transform.scale(wall_texture.subsurface((tx, 0, 1, wall_texture.get_height())), (1, height))

        #     # Draw the texture column
        #     surface.blit(column, (x, HEIGHT // 2 - height // 2))            
        
        # Draw a line with height inversely proportional to the distance
        if distance == 0:
            height = HEIGHT
        else:
            height = HEIGHT / distance

        # Calculate a grayscale color based on the distance
        color = 255 - min(distance * 50, 255)
        color = clamp(color, 0, 255) # distance can be a small negative number, so we clamp it

        pygame.draw.line(raycast_surface, (color, color, color), (x, HEIGHT // 2 - height // 2), (x, HEIGHT // 2 + height // 2))


    # End the timer and calculate the elapsed time
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds

    # If save_distances is True, write the distances to a file
    if save_distances:
        with open('distances.txt', 'w') as f:
            f.write(f'Rendering took {elapsed_time} milliseconds\n')
            f.write(f'Player position: {player_pos} {player_angle}\n')
            for distance in distances:
                f.write(str(distance) + '\n')

# Define a function to render the map
def render_map():

    # Fill the map surface with black
    map_surface.fill((0, 0, 0))

    # Draw the map
    for y in range(len(MAP)):
        for x in range(len(MAP[y])):
            if MAP[y][x] == 1:
                pygame.draw.rect(map_surface, (255, 255, 255), pygame.Rect(x * 10, y * 10, 10, 10))

    # Draw the player
    pygame.draw.circle(map_surface, (255, 0, 0), (int(player_pos[0] * 10), int(player_pos[1] * 10)), 5)

    # Draw the player's direction
    dx = math.cos(player_angle) * 20
    dy = math.sin(player_angle) * 20
    pygame.draw.line(map_surface, (255, 0, 0), (int(player_pos[0] * 10), int(player_pos[1] * 10)), (int(player_pos[0] * 10 + dx), int(player_pos[1] * 10 + dy)))

# Game loop
clock = pygame.time.Clock()
new_pos = [0, 0]
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Get the current state of the keyboard
    keys = pygame.key.get_pressed()
    new_pos[0] = player_pos[0]
    new_pos[1] = player_pos[1]
    if keys[pygame.K_w]:
        new_pos[0] += math.cos(player_angle) * SPEED
        new_pos[1] += math.sin(player_angle) * SPEED
    if keys[pygame.K_s]:
        new_pos[0] -= math.cos(player_angle) * SPEED
        new_pos[1] -= math.sin(player_angle) * SPEED
    if keys[pygame.K_d]:
        new_pos[0] -= math.sin(player_angle) * SPEED
        new_pos[1] += math.cos(player_angle) * SPEED
    if keys[pygame.K_a]:
        new_pos[0] += math.sin(player_angle) * SPEED
        new_pos[1] -= math.cos(player_angle) * SPEED
    if keys[pygame.K_LEFT]:
        player_angle -= 0.1
    if keys[pygame.K_RIGHT]:
        player_angle += 0.1
    if keys[pygame.K_g]:
        god_mode = not god_mode  # Toggle god mode
        pygame.time.wait(500)
    if keys[pygame.K_p]:
        render_raycast(True)
        pygame.time.wait(500)

    # Check if the new position is inside a wall
    if god_mode or MAP[int(new_pos[1])][int(new_pos[0])] == 0:
        # If god mode is enabled or the new position is not inside a wall, update the player's position
        player_pos = new_pos

    # Render the raycast and blit it onto the screen
    render_raycast()
    screen.blit(raycast_surface, (0, (SCREEN_HEIGHT - HEIGHT) // 2))

    # Render the map and blit it onto the screen
    render_map()    
    screen.blit(map_surface, (WIDTH, (SCREEN_HEIGHT - MAP_HEIGHT) // 2))

    # Calculate the FPS
    fps = clock.get_fps()

    # Render the FPS as text (shadow)
    fps_text_shadow = font.render(f'FPS: {fps:.2f}', True, (0, 0, 0))
    screen.blit(fps_text_shadow, (11, 11))  # Offset by 1 pixel
    
    # Render the FPS as text
    fps_text = font.render(f'FPS: {fps:.2f}', True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)