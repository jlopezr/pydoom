import pygame
import sys
import math
import time
from enum import Enum

class TextureMode(Enum):
    FLAT = 1
    TEXTURES = 2
    LIT_TEXTURES = 3

# Return a new image that is a lighter version of the given image.
def lighten_image(image, amount=(40, 40, 40)):
    lighter_image = image.copy()
    lighter_image.fill(amount, special_flags=pygame.BLEND_RGBA_ADD)
    return lighter_image

# Normalize an angle to the range -π to π
def normalize_angle(angle):
    while angle <= -math.pi:
        angle += 2 * math.pi
    while angle > math.pi:
        angle -= 2 * math.pi
    return angle

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 640, 480
FPS = 60
SPEED = 0.05

# Define the player
player_pos = [5, 5.5]
player_angle = 0
god_mode = False
texture_mode = TextureMode.FLAT
objects_mode = False

# Define the map
MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [1, 0, 1, 1, 1, 0, 1, 1, 0, 3],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 4],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 5],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Define the colors for the walls
COLOR_MAP = {
    1: (255, 255, 255),  # White
    2: (255, 0, 0),      # Red
    3: (0, 0, 255),      # Blue
    4: (0, 255, 0),      # Green
    5: (255, 255, 0),    # Yellow
}

FLOOR_COLOR = (100, 100, 100)
CEILING_COLOR = (50, 50, 50)

# Load the wall texture
TEXTURE_MAP = {
    1: pygame.image.load('wall2.jpeg'),
    2: pygame.image.load('wall.png'),
    3: pygame.image.load('wall3.jpeg'),
    4: pygame.image.load('wall4.jpeg'),
    5: pygame.image.load('wall5.jpeg'),
}

# Generate a lighter version of the map
TEXTURE_LIT_MAP = {key: lighten_image(image) for key, image in TEXTURE_MAP.items()}

# Load objects textures
OBJECTS_TEXTURES = {
    1: pygame.image.load('guard1.png')
}

# Define the objects
objects = [
    {
        'pos': (7, 5.5),
        'texture': OBJECTS_TEXTURES[1]
    }
]

# Define the map size in pixels
MAP_WIDTH = len(MAP[0]) * 10
MAP_HEIGHT = len(MAP) * 10

# Define the screen size
SCREEN_WIDTH = WIDTH + MAP_WIDTH
SCREEN_HEIGHT = max(HEIGHT, MAP_HEIGHT)

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
    hit_pos = None
    wall_value = None
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
            wall_value = MAP[y][x]
            # Calculate the exact hit position
            if hit_side == 0:  # Ray hit a vertical wall
                hit_pos = player_pos[1] + ((x - player_pos[0] + (1 - step_x) / 2) / dx) * dy
            else:  # Ray hit a horizontal wall
                hit_pos = player_pos[0] + ((y - player_pos[1] + (1 - step_y) / 2) / dy) * dx
            break

    # Calculate distance of perpendicular ray (Euclidean distance will give fisheye effect!)
    if hit_side is None:
        perp_wall_dist = 0  # or some other default value
    elif hit_side == 0:
        perp_wall_dist = (x - player_pos[0] + (1 - step_x) / 2) / dx
    else:
        perp_wall_dist = (y - player_pos[1] + (1 - step_y) / 2) / dy
    return perp_wall_dist, hit_side, wall_value, hit_pos

def render_line(x, distance, hit_side, wall_value,  hit_pos):
        # Draw a line with height inversely proportional to the distance
        if distance == 0:
            height = HEIGHT
        else:
            height = HEIGHT / distance
        
        base_color = COLOR_MAP.get(wall_value, (0, 0, 0))

        # Scale the color by a factor that decreases with distance
        # The max() function is used to avoid division by zero
        color = tuple(int(c / max(distance / 1.5, 1)) for c in base_color)
        
        pygame.draw.line(raycast_surface, color, (x, HEIGHT // 2 - height // 2), (x, HEIGHT // 2 + height // 2))

def render_texture(x, distance, hit_side, wall_value, hit_pos):

    if hit_pos is not None:

        # Look up the wall texture
        if texture_mode == TextureMode.LIT_TEXTURES and hit_side == 0:
            wall_texture = TEXTURE_LIT_MAP.get(wall_value)                    
        else:
            wall_texture = TEXTURE_MAP.get(wall_value)

        # Look up the texture column
        tx = hit_pos
        tx = int(tx * wall_texture.get_width())

        # Calculate the height of the wall slice
        height = int(HEIGHT / max(distance, 0.0001))

        # Scale the texture column to the height of the wall slice
        tx = tx % wall_texture.get_width()
        column = pygame.transform.scale(wall_texture.subsurface((tx, 0, 1, wall_texture.get_height())), (1, height))

        # Draw the texture column
        raycast_surface.blit(column, (x, HEIGHT // 2 - height // 2))            

# Define a function to render the raycast
def render_raycast(save_distances=False):

    # Fill the top half of the surface with the ceiling color
    raycast_surface.fill(CEILING_COLOR, (0, 0, raycast_surface.get_width(), raycast_surface.get_height() // 2))

    # Fill the bottom half of the surface with the floor color
    raycast_surface.fill(FLOOR_COLOR, (0, raycast_surface.get_height() // 2, raycast_surface.get_width(), raycast_surface.get_height() // 2))

    # Create a list to store the distances
    distances = []

    # Start the timer
    start_time = time.time()

    # Cast a ray for each column of the screen
    for x in range(WIDTH):
        distance, hit, wall_value, hit_pos = cast_ray(player_angle + x / WIDTH - 0.5) # FOV is 1 radian. Subtract 0.5 to center the ray
        distances.append((distance, hit))

        if texture_mode == TextureMode.FLAT:
            render_line(x, distance, hit, wall_value, hit_pos)
        else:
            render_texture(x, distance, hit, wall_value, hit_pos)

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

# Define a function to render the objects
def render_objects():
    for obj in objects:
        # Calculate the distance to the object
        dx = obj['pos'][0] - player_pos[0]
        dy = obj['pos'][1] - player_pos[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Calculate the angle to the object
        angle = math.atan2(dy, dx)

        # Calculate the angle difference between the player's angle and the angle to the object
        angle_diff = angle - player_angle

        # Calculate the projected object height
        projected_height = HEIGHT / distance

        # Calculate the projected object width
        projected_width = projected_height

        # Calculate the x position of the object on the screen. FOV 1 is 1 radian
        #x = (angle_diff * WIDTH / math.pi) + (WIDTH / 2) - (projected_width / 2)
        x = (angle_diff * WIDTH / 1) + (WIDTH / 2) - (projected_width / 2)

        # Calculate the y position of the object on the screen
        y = (SCREEN_HEIGHT - projected_height) / 2

        # Scale the object to the projected height
        scaled_obj = pygame.transform.scale(obj['texture'], (int(projected_width), int(projected_height)))

        # Draw the object
        raycast_surface.blit(scaled_obj, (x, y))

# Define a function to render the map
def render_map():
    # Fill the map surface with black
    map_surface.fill((0, 0, 0))

    # Draw the map
    for y in range(len(MAP)):
        for x in range(len(MAP[y])):
            if MAP[y][x] > 0:
                pygame.draw.rect(map_surface, COLOR_MAP.get(MAP[y][x],(0,0,0)), pygame.Rect(x * 10, y * 10, 10, 10))

    # Draw the player
    pygame.draw.circle(map_surface, (255, 0, 0), (int(player_pos[0] * 10), int(player_pos[1] * 10)), 5)

    # Draw the player's direction
    dx = math.cos(player_angle) * 20
    dy = math.sin(player_angle) * 20
    pygame.draw.line(map_surface, (255, 0, 0), (int(player_pos[0] * 10), int(player_pos[1] * 10)), (int(player_pos[0] * 10 + dx), int(player_pos[1] * 10 + dy)))

    # Draw the objects
    for obj in objects:
        pygame.draw.circle(map_surface, (0, 255, 0), (int(obj['pos'][0] * 10), int(obj['pos'][1] * 10)), 5)

# Game loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Get the current state of the keyboard
    keys = pygame.key.get_pressed()
    new_pos = list(player_pos)
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
    if keys[pygame.K_t]:
        texture_mode = TextureMode((texture_mode.value % 3) + 1) # Cycle over texture modes
        pygame.time.wait(500)
    if keys[pygame.K_o]:
        objects_mode = not objects_mode  # Toggle objects mode
        pygame.time.wait(500)
    if keys[pygame.K_p]:
        render_raycast(True)
        pygame.time.wait(500)
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()

    # Check if the new position is inside a wall    
    if god_mode or MAP[int(new_pos[1])][int(new_pos[0])] == 0:
        # If god mode is enabled or the new position is not inside a wall, update the player's position
        player_pos = new_pos

    # Render the raycast and blit it onto the screen
    render_raycast()
    if objects_mode:
        render_objects()
    screen.blit(raycast_surface, (0, (SCREEN_HEIGHT - HEIGHT) // 2))

    # Render the map and blit it onto the screen
    render_map()
    screen.blit(map_surface, (WIDTH, (SCREEN_HEIGHT - MAP_HEIGHT) // 2))

    # Calculate the FPS
    fps = clock.get_fps()

    # Render the FPS as text
    txt = f'FPS: {fps:.2f} God: {god_mode} {player_pos[0]:.2f} {player_pos[1]:.2f} {math.degrees(player_angle):.2f}º'
    fps_text_shadow = font.render(txt, True, (0, 0, 0))
    screen.blit(fps_text_shadow, (11, 11))  # Offset by 1 pixel
    fps_text = font.render(txt, True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)