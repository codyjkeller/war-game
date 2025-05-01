import pygame
import math
import random
import os # Import os module for path handling
from collections import deque # For potential future pathfinding (BFS/A*)

# Initialize Pygame
pygame.init()
pygame.mixer.init() # Initialize mixer for sound

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("WW1 Trenches")

# Asset Paths (create these folders and add your assets)
# Ensure these directories exist and contain your image and sound files.
# Example structure:
# your_game_folder/
# |- ww1_game.py
# |- images/
# |  |- player.png
# |  |- bullet.png
# |  |- enemy_basic.png
# |  |- enemy_tanky.png
# |  |- obstacle_sandbags.png
# |  |- obstacle_barbedwire.png
# |  |- flag.png
# |  |- tile_grass.png
# |  |- tile_trench.png
# |  |- tile_crater.png
# |- sounds/
#    |- shoot.wav
#    |- hit.wav
#    |- death.wav
#    |- background_music.ogg

IMG_DIR = os.path.join(os.path.dirname(__file__), 'images')
SOUND_DIR = os.path.join(os.path.dirname(__file__), 'sounds')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)  # For trenches and ground
GRAY = (169, 169, 169)  # For obstacles
DARK_GRAY = (100, 100, 100) # For menu text

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
VICTORY = 3
game_state = MENU # Start in the menu state

# Tilemap settings
TILE_SIZE = 50 # Size of each tile in pixels

# Player variables
player_size = 40
try:
    player_img = pygame.image.load(os.path.join(IMG_DIR, 'player.png')).convert_alpha()
    player_img = pygame.transform.scale(player_img, (player_size, player_size))
except pygame.error as e:
    print(f"Warning: Could not load player image: {e}. Using placeholder.")
    player_img = pygame.Surface([player_size, player_size])
    player_img.fill(WHITE)

player_speed = 5
player_health = 10
player_lives = 3
player_invincible = False  # Basic invincibility after respawn
invincibility_duration = 60  # frames
invincibility_timer = 0
player_animation_speed = 5 # Frames per animation frame

# Bullet variables
bullet_size = 10
try:
    bullet_img = pygame.image.load(os.path.join(IMG_DIR, 'bullet.png')).convert_alpha()
    bullet_img = pygame.transform.scale(bullet_img, (bullet_size, bullet_size))
except pygame.error as e:
    print(f"Warning: Could not load bullet image: {e}. Using placeholder.")
    bullet_img = pygame.Surface([bullet_size, bullet_size])
    bullet_img.fill(BLACK)

bullet_speed = 7
all_bullets = pygame.sprite.Group()

# Enemy variables
enemy_size = 40
# Load enemy images (different types)
enemy_images = {}
try:
    enemy_images['basic'] = pygame.image.load(os.path.join(IMG_DIR, 'enemy_basic.png')).convert_alpha()
    enemy_images['basic'] = pygame.transform.scale(enemy_images['basic'], (enemy_size, enemy_size))
except pygame.error as e:
    print(f"Warning: Could not load basic enemy image: {e}. Using placeholder.")
    enemy_images['basic'] = pygame.Surface([enemy_size, enemy_size])
    enemy_images['basic'].fill(RED)

# Add more enemy types here if you have images
# try:
#     enemy_images['tanky'] = pygame.image.load(os.path.join(IMG_DIR, 'enemy_tanky.png')).convert_alpha()
#     enemy_images['tanky'] = pygame.transform.scale(enemy_images['tanky'], (enemy_size + 10, enemy_size + 10)) # Example: larger tanky enemy
# except pygame.error as e:
#     print(f"Warning: Could not load tanky enemy image: {e}. Using placeholder.")
#     enemy_images['tanky'] = pygame.Surface([enemy_size + 10, enemy_size + 10])
#     enemy_images['tanky'].fill((100, 0, 0)) # Darker red

enemy_speed = 2
enemy_health = {'basic': 3, 'tanky': 6} # Health for different enemy types
all_enemies = pygame.sprite.Group()

# Obstacle variables
obstacle_size = TILE_SIZE # Obstacles align with tiles
# Load obstacle images
obstacle_images = {}
try:
    obstacle_images['sandbags'] = pygame.image.load(os.path.join(IMG_DIR, 'obstacle_sandbags.png')).convert_alpha()
    obstacle_images['sandbags'] = pygame.transform.scale(obstacle_images['sandbags'], (obstacle_size, obstacle_size))
except pygame.error as e:
    print(f"Warning: Could not load sandbags obstacle image: {e}. Using placeholder.")
    obstacle_images['sandbags'] = pygame.Surface([obstacle_size, obstacle_size])
    obstacle_images['sandbags'].fill(GRAY)

# Add more obstacle types here
# try:
#     obstacle_images['barbedwire'] = pygame.image.load(os.path.join(IMG_DIR, 'obstacle_barbedwire.png')).convert_alpha()
#     obstacle_images['barbedwire'] = pygame.transform.scale(obstacle_images['barbedwire'], (obstacle_size, obstacle_size))
# except pygame.error as e:
#     print(f"Warning: Could not load barbed wire image: {e}. Using placeholder.")
#     obstacle_images['barbedwire'] = pygame.Surface([obstacle_size, obstacle_size])
#     obstacle_images['barbedwire'].fill(DARK_GRAY)


all_obstacles = pygame.sprite.Group()

# Flag variable (Victory condition)
flag_size = 50
try:
    flag_img = pygame.image.load(os.path.join(IMG_DIR, 'flag.png')).convert_alpha()
    flag_img = pygame.transform.scale(flag_img, (flag_size, flag_size))
except pygame.error as e:
    print(f"Warning: Could not load flag image: {e}. Using placeholder.")
    flag_img = pygame.Surface([flag_size, flag_size])
    flag_img.fill(GREEN)

flag_rect = flag_img.get_rect(center=(SCREEN_WIDTH // 2, 75))  # Enemy trench area

# Font for text
font = pygame.font.Font(None, 36)
menu_font = pygame.font.Font(None, 72)

# Sound Effects (Load your sound files)
shoot_sound = None
hit_sound = None
death_sound = None
try:
    shoot_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'shoot.wav'))
except pygame.error as e:
    print(f"Warning: Could not load shoot sound: {e}")

try:
    hit_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'hit.wav'))
except pygame.error as e:
    print(f"Warning: Could not load hit sound: {e}")

try:
    death_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'death.wav'))
except pygame.error as e:
    print(f"Warning: Could not load death sound: {e}")

# Background Music (Load your music file)
try:
    pygame.mixer.music.load(os.path.join(SOUND_DIR, 'background_music.ogg'))
    pygame.mixer.music.play(-1) # Play indefinitely
except pygame.error as e:
    print(f"Warning: Could not load background music: {e}")


# --- Tilemap and Level Data ---

# Tile types
TILE_GRASS = 0
TILE_TRENCH = 1
TILE_CRATER = 2 # Example of a decorative tile

# Tile images
tile_images = {}
try:
    tile_images[TILE_GRASS] = pygame.image.load(os.path.join(IMG_DIR, 'tile_grass.png')).convert()
    tile_images[TILE_GRASS] = pygame.transform.scale(tile_images[TILE_GRASS], (TILE_SIZE, TILE_SIZE))
except pygame.error as e:
    print(f"Warning: Could not load grass tile image: {e}. Using placeholder.")
    tile_images[TILE_GRASS] = pygame.Surface([TILE_SIZE, TILE_SIZE])
    tile_images[TILE_GRASS].fill((100, 150, 50)) # Greenish-brown

try:
    tile_images[TILE_TRENCH] = pygame.image.load(os.path.join(IMG_DIR, 'tile_trench.png')).convert()
    tile_images[TILE_TRENCH] = pygame.transform.scale(tile_images[TILE_TRENCH], (TILE_SIZE, TILE_SIZE))
except pygame.error as e:
    print(f"Warning: Could not load trench tile image: {e}. Using placeholder.")
    tile_images[TILE_TRENCH] = pygame.Surface([TILE_SIZE, TILE_SIZE])
    tile_images[TILE_TRENCH].fill(BROWN)

try:
    tile_images[TILE_CRATER] = pygame.image.load(os.path.join(IMG_DIR, 'tile_crater.png')).convert_alpha() # Crater might have transparency
    tile_images[TILE_CRATER] = pygame.transform.scale(tile_images[TILE_CRATER], (TILE_SIZE, TILE_SIZE))
except pygame.error as e:
    print(f"Warning: Could not load crater tile image: {e}. Using placeholder.")
    tile_images[TILE_CRATER] = pygame.Surface([TILE_SIZE, TILE_SIZE])
    tile_images[TILE_CRATER].fill((80, 70, 60)) # Darker brown

# Level Data Structure
# Each level is a dictionary containing:
# - 'tilemap': A 2D list representing the tile types.
# - 'player_start': (x, y) tuple for player's starting position (in pixels).
# - 'enemy_positions': A list of dictionaries, each with 'type' and 'pos' (x, y in pixels).
# - 'obstacle_positions': A list of dictionaries, each with 'type' and 'pos' (x, y in pixels).
# - 'flag_position': (x, y) tuple for the flag's position (in pixels).

LEVELS = [
    {
        'tilemap': [
            [TILE_TRENCH] * (SCREEN_WIDTH // TILE_SIZE),
            [TILE_GRASS] * (SCREEN_WIDTH // TILE_SIZE),
            [TILE_GRASS] * (SCREEN_WIDTH // TILE_SIZE),
            [TILE_CRATER] + [TILE_GRASS] * (SCREEN_WIDTH // TILE_SIZE - 2) + [TILE_CRATER],
            [TILE_GRASS] * (SCREEN_WIDTH // TILE_SIZE),
            [TILE_GRASS] * (SCREEN_WIDTH // TILE_SIZE),
            [TILE_CRATER] + [TILE_GRASS] * (SCREEN_WIDTH // TILE_SIZE - 2) + [TILE_CRATER],
            [TILE_GRASS] * (SCREEN_WIDTH // TILE_SIZE),
            [TILE_GRASS] * (SCREEN_WIDTH // TILE_SIZE),
            [TILE_TRENCH] * (SCREEN_WIDTH // TILE_SIZE),
        ],
        'player_start': (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75),
        'enemy_positions': [
            {'type': 'basic', 'pos': (random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT // 3))},
            {'type': 'basic', 'pos': (random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT // 3))},
            {'type': 'basic', 'pos': (random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT // 3))},
            {'type': 'basic', 'pos': (random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT // 3))},
            {'type': 'basic', 'pos': (random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT // 3))},
        ],
        'obstacle_positions': [
            {'type': 'sandbags', 'pos': (200, 300)}, {'type': 'sandbags', 'pos': (400, 350)}, {'type': 'sandbags', 'pos': (600, 300)},
            {'type': 'sandbags', 'pos': (250, 450)}, {'type': 'sandbags', 'pos': (550, 450)},
            {'type': 'sandbags', 'pos': (150, 200)}, {'type': 'sandbags', 'pos': (650, 200)}
        ],
        'flag_position': (SCREEN_WIDTH // 2, 75)
    },
    # Add more levels here
    # {
    #     'tilemap': [ ... ],
    #     'player_start': ( ... ),
    #     'enemy_positions': [ ... ],
    #     'obstacle_positions': [ ... ],
    #     'flag_position': ( ... )
    # }
]

current_level_index = 0

# --- Classes ---

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos):
        super().__init__()
        self.original_image = player_img.copy() # Keep a copy for rotation
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = start_pos  # Start position from level data
        self.speed = player_speed
        self.health = player_health
        self.lives = player_lives
        self.invincible = False
        self.invincibility_timer = 0
        self.angle = 0 # Player rotation angle
        self.animation_frame = 0
        self.animation_timer = 0
        self.is_moving = False # Flag for animation
        self.mask = pygame.mask.from_surface(self.image) # Create mask for pixel-perfect collision


        # If you have animation frames, load them here
        # self.walk_frames = {
        #     'up': [pygame.image.load(os.path.join(IMG_DIR, f'player_up_{i}.png')).convert_alpha() for i in range(num_up_frames)],
        #     'down': [pygame.image.load(os.path.join(IMG_DIR, f'player_down_{i}.png')).convert_alpha() for i in range(num_down_frames)],
        #     'left': [pygame.image.load(os.path.join(IMG_DIR, f'player_left_{i}.png')).convert_alpha() for i in range(num_left_frames)],
        #     'right': [pygame.image.load(os.path.join(IMG_DIR, f'player_right_{i}.png')).convert_alpha() for i in range(num_right_frames)],
        # }
        # self.current_direction = 'down' # Default direction

    def update(self):
        # Store previous position for collision rollback
        prev_pos = self.rect.topleft

        # Movement
        self.is_moving = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
            self.is_moving = True
            # self.current_direction = 'up' # For animation
        if keys[pygame.K_s]:
            self.rect.y += self.speed
            self.is_moving = True
            # self.current_direction = 'down' # For animation
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.is_moving = True
            # self.current_direction = 'left' # For animation
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.is_moving = True
            # self.current_direction = 'right' # For animation

        # Keep player on screen (within the playable area, excluding trenches)
        # Assuming trenches are the top and bottom 100 pixels
        playable_area_top = 100
        playable_area_bottom = SCREEN_HEIGHT - 100
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(playable_area_top, min(self.rect.y, playable_area_bottom - self.rect.height))


        # Aiming and Rotation
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Calculate angle between player and mouse
        self.angle = math.degrees(math.atan2(mouse_y - self.rect.centery, mouse_x - self.rect.centerx))
        # Rotate the player image
        self.image = pygame.transform.rotate(self.original_image, -self.angle) # Rotate counter-clockwise
        self.rect = self.image.get_rect(center=self.rect.center) # Update rect center after rotation
        self.mask = pygame.mask.from_surface(self.image) # Update mask after rotation


        # Animation (Basic implementation)
        # if self.is_moving and hasattr(self, 'walk_frames'):
        #     self.animation_timer += 1
        #     if self.animation_timer >= player_animation_speed:
        #         self.animation_timer = 0
        #         self.animation_frame = (self.animation_frame + 1) % len(self.walk_frames[self.current_direction])
        #         self.image = self.walk_frames[self.current_direction][self.animation_frame]
        #         self.mask = pygame.mask.from_surface(self.image) # Update mask for animation frames
        # else:
        #     # Reset animation or set to idle frame
        #     self.animation_frame = 0
        #     self.animation_timer = 0
        #     # Set to a default idle image based on direction
        #     # if hasattr(self, 'walk_frames') and self.current_direction in self.walk_frames and self.walk_frames[self.current_direction]:
        #     #     self.image = self.walk_frames[self.current_direction][0] # Use first frame as idle
        #     #     self.mask = pygame.mask.from_surface(self.image) # Update mask for idle frame


        # Handle invincibility
        if self.invincible:
            self.invincibility_timer -= 1
            # Basic visual feedback for invincibility (flashing)
            if self.invincibility_timer % 10 < 5:
                self.image.set_alpha(100) # Make partially transparent
            else:
                self.image.set_alpha(255) # Fully opaque

            if self.invincibility_timer <= 0:
                self.invincible = False
                self.image.set_alpha(255) # Ensure full opacity when invincibility ends

        return prev_pos # Return previous position for collision handling

    def shoot(self):
        # Create a bullet instance at the player's center, with the current angle
        bullet = Bullet(self.rect.centerx, self.rect.centery, self.angle)
        all_bullets.add(bullet)
        if shoot_sound:
            shoot_sound.play()

    def take_damage(self, amount):
        if not self.invincible:
            self.health -= amount
            if hit_sound:
                hit_sound.play()
            if self.health <= 0:
                self.lives -= 1
                if death_sound:
                    death_sound.play()
                if self.lives > 0:
                    self.respawn()
                else:
                    global game_state
                    game_state = GAME_OVER

    def respawn(self):
        # Respawn at the player start position defined in the current level
        self.rect.center = LEVELS[current_level_index]['player_start']
        self.health = player_health
        self.invincible = True
        self.invincibility_timer = invincibility_duration

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.original_image = bullet_img.copy() # Keep original for rotation
        self.image = pygame.transform.rotate(self.original_image, -angle) # Rotate bullet to match shooting angle
        self.rect = self.image.get_rect(center=(x, y))
        self.angle_rad = math.radians(angle)  # Store angle in radians for calculations
        self.speed = bullet_speed
        self.vel_x = self.speed * math.cos(self.angle_rad)
        self.vel_y = self.speed * math.sin(self.angle_rad)
        self.trail = []  # For bullet trail
        self.mask = pygame.mask.from_surface(self.image) # Create mask for pixel-perfect collision


    def update(self):
        # Move the bullet
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Add current position to trail
        self.trail.append((self.rect.centerx, self.rect.centery))
        # Limit trail length
        if len(self.trail) > 15:  # Adjust trail length as needed
            self.trail.pop(0)

        # Remove bullet if it goes off screen
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

    def draw_trail(self, surface):
        if len(self.trail) > 1:
            # Draw the trail as connected lines
            # You could make the trail fade out by varying alpha or color
            pygame.draw.lines(surface, BLACK, False, self.trail, 2)  # False means not closed loop, 2 is line thickness

class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, start_pos):
        super().__init__()
        self.enemy_type = enemy_type
        self.original_image = enemy_images.get(enemy_type, enemy_images['basic']).copy() # Get image based on type, default to basic
        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=start_pos) # Start position from level data
        self.speed = enemy_speed # Basic speed for now, could be type-dependent
        self.health = enemy_health.get(enemy_type, enemy_health['basic']) # Get health based on type
        self.shoot_timer = random.randint(60, 180)  # Enemies shoot at random intervals (frames)
        self.is_dead = False # Flag for death animation/removal
        self.death_animation_timer = 0
        self.death_animation_duration = 30 # frames
        self.mask = pygame.mask.from_surface(self.image) # Create mask for pixel-perfect collision

        # Pathfinding variables (placeholders)
        self.path = None # List of grid coordinates representing the path
        self.target_grid_pos = None # Grid position the enemy is moving towards
        self.pathfinding_timer = 0 # Timer to recalculate path
        self.pathfinding_interval = 120 # Recalculate path every 2 seconds (adjust as needed)

        # Cover system variables (placeholders)
        self.in_cover = False
        self.cover_spot = None # Grid position of the cover spot

        # If you have enemy animation frames, load them here

    def update(self, player_rect):
        if self.is_dead:
            # Handle death animation (if any)
            self.death_animation_timer += 1
            if self.death_animation_timer >= self.death_animation_duration:
                self.kill() # Remove enemy after death animation

            # Basic visual for death (fade out)
            alpha = max(0, 255 - (self.death_animation_timer / self.death_animation_duration) * 255)
            self.image.set_alpha(alpha)

            return # Stop further updates if dead

        # --- Enemy AI ---

        # Basic movement towards player (will be replaced by pathfinding)
        # direction_x = player_rect.centerx - self.rect.centerx
        # direction_y = player_rect.centery - self.rect.centery
        # distance = math.hypot(direction_x, direction_y)

        # if distance > 0:
        #     # Normalize direction vector
        #     direction_x /= distance
        #     direction_y /= distance

        #     # Apply movement
        #     self.rect.x += direction_x * self.speed
        #     self.rect.y += direction_y * self.speed

        # --- Pathfinding (Conceptual Implementation) ---
        # This is a simplified example. A full A* implementation is complex.

        self.pathfinding_timer += 1
        if self.pathfinding_timer >= self.pathfinding_interval or self.path is None:
             # Recalculate path to player's current grid position
             player_grid_pos = (player_rect.centerx // TILE_SIZE, player_rect.centery // TILE_SIZE)
             enemy_grid_pos = (self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE)
             self.path = find_path(enemy_grid_pos, player_grid_pos, LEVELS[current_level_index]['tilemap']) # Call a pathfinding function
             self.pathfinding_timer = 0 # Reset timer
             if self.path and len(self.path) > 1:
                 self.target_grid_pos = self.path[1] # Set the next grid cell as target

        # Move towards the next grid position in the path
        if self.path and len(self.path) > 1:
            target_pixel_pos = (self.target_grid_pos[0] * TILE_SIZE + TILE_SIZE // 2,
                                self.target_grid_pos[1] * TILE_SIZE + TILE_SIZE // 2)

            move_direction_x = target_pixel_pos[0] - self.rect.centerx
            move_direction_y = target_pixel_pos[1] - self.rect.centery
            move_distance = math.hypot(move_direction_x, move_direction_y)

            if move_distance > self.speed: # Move if not already very close
                 move_direction_x /= move_distance
                 move_direction_y /= move_distance
                 self.rect.x += move_direction_x * self.speed
                 self.rect.y += move_direction_y * self.speed
            else: # Reached the target grid cell, move to the next one in the path
                 if len(self.path) > 2:
                     self.target_grid_pos = self.path[2]
                     self.path.pop(0) # Remove the current grid cell from the path
                 else:
                     self.path = None # Reached the end of the path


        # --- Cover System (Conceptual Implementation) ---
        # if not self.in_cover and self.health < enemy_health.get(self.enemy_type, enemy_health['basic']) / 2: # Seek cover if damaged
        #     self.cover_spot = find_nearby_cover(self.rect.center, LEVELS[current_level_index]['tilemap'], all_obstacles) # Find a cover spot
        #     if self.cover_spot:
        #         self.path = find_path((self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE), self.cover_spot, LEVELS[current_level_index]['tilemap'])
        #         self.in_cover = True

        # if self.in_cover and self.path is None: # Reached cover
        #     # Stay in cover for a while, maybe shoot from cover
        #     pass # Implement cover behavior

        # if self.in_cover and player_rect.colliderect(self.rect.inflate(200, 200)): # Leave cover if player is close
        #     self.in_cover = False
        #     self.cover_spot = None
        #     self.path = None # Clear path to cover


        # Rotate enemy to face player (even with pathfinding, for shooting)
        direction_x = player_rect.centerx - self.rect.centerx
        direction_y = player_rect.centery - self.rect.centery
        self.angle = math.degrees(math.atan2(direction_y, direction_x))
        self.image = pygame.transform.rotate(self.original_image, -self.angle) # Rotate counter-clockwise
        self.rect = self.image.get_rect(center=self.rect.center) # Update rect center after rotation
        self.mask = pygame.mask.from_surface(self.image) # Update mask after rotation


        # Shooting at player (basic implementation)
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot(player_rect)
            self.shoot_timer = random.randint(60, 180)  # Reset timer

    def shoot(self, player_rect):
        # Calculate angle towards player
        angle = math.degrees(math.atan2(player_rect.centery - self.rect.centery, player_rect.centerx - self.rect.centerx))
        bullet = Bullet(self.rect.centerx, self.rect.centery, angle)
        all_bullets.add(bullet)
        # Enemy shoot sound (optional)
        # if enemy_shoot_sound:
        #     enemy_shoot_sound.play()

    def take_damage(self, amount):
        self.health -= amount
        if hit_sound:
            hit_sound.play() # Use player hit sound for now
        if self.health <= 0 and not self.is_dead:
            self.is_dead = True
            self.death_animation_timer = 0
            # Trigger death animation or remove immediately
            # self.kill() # Remove immediately if no death animation

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_type, x, y):
        super().__init__()
        self.obstacle_type = obstacle_type
        self.image = obstacle_images.get(obstacle_type, obstacle_images['sandbags']) # Get image based on type, default to sandbags
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image) # Create mask for pixel-perfect collision

# --- Pathfinding Helper (Simplified BFS Example - Not A*) ---
# This is a very basic Breadth-First Search (BFS) for demonstration.
# A* is more efficient for finding the shortest path in most cases.

def is_walkable(grid_x, grid_y, tilemap, obstacles):
    """Checks if a grid position is walkable (not an obstacle or trench)."""
    if grid_x < 0 or grid_x >= len(tilemap[0]) or grid_y < 0 or grid_y >= len(tilemap):
        return False # Out of bounds

    tile_type = tilemap[grid_y][grid_x]
    if tile_type == TILE_TRENCH:
        return False # Trenches are not walkable for enemies in No Man's Land

    # Check for collision with obstacles
    temp_rect = pygame.Rect(grid_x * TILE_SIZE, grid_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    for obstacle in obstacles:
        if temp_rect.colliderect(obstacle.rect): # Simple rect collision for grid check
             return False # Collides with an obstacle

    return True

def find_path(start_grid, end_grid, tilemap):
    """
    Finds a path from start_grid to end_grid using Breadth-First Search (BFS).
    Returns a list of grid coordinates representing the path, or None if no path exists.
    """
    rows = len(tilemap)
    cols = len(tilemap[0])

    # Check if start or end is unwalkable
    if not is_walkable(start_grid[0], start_grid[1], tilemap, all_obstacles) or \
       not is_walkable(end_grid[0], end_grid[1], tilemap, all_obstacles):
        return None

    queue = deque([(start_grid, [start_grid])]) # Queue stores (current_node, path_to_node)
    visited = set()
    visited.add(start_grid)

    while queue:
        (current_x, current_y), path = queue.popleft()

        if (current_x, current_y) == end_grid:
            return path # Found the path

        # Define possible movements (8 directions)
        movements = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dx, dy in movements:
            next_x, next_y = current_x + dx, current_y + dy

            if is_walkable(next_x, next_y, tilemap, all_obstacles) and (next_x, next_y) not in visited:
                visited.add((next_x, next_y))
                queue.append(((next_x, next_y), path + [(next_x, next_y)]))

    return None # No path found

# --- Cover System Helper (Placeholder) ---

def find_nearby_cover(position, tilemap, obstacles):
    """
    Finds a nearby cover spot for an enemy.
    This is a placeholder and needs a proper implementation.
    Could involve checking tiles around the enemy for obstacles that block line of sight to the player.
    """
    # Example: Find the closest obstacle tile
    closest_obstacle = None
    min_dist = float('inf')

    for obstacle in obstacles:
        dist = math.hypot(position[0] - obstacle.rect.centerx, position[1] - obstacle.rect.centery)
        if dist < min_dist:
            min_dist = dist
            closest_obstacle = obstacle

    if closest_obstacle:
        # Return the grid position of the closest obstacle as a potential cover spot
        return (closest_obstacle.rect.centerx // TILE_SIZE, closest_obstacle.rect.centery // TILE_SIZE)
    return None # No cover found

# --- Game Setup Function ---

def reset_game():
    """Resets the game state to start a new game for the current level."""
    global game_state
    game_state = PLAYING

    # Clear existing sprites
    all_sprites.empty()
    all_enemies.empty()
    all_bullets.empty()
    all_obstacles.empty()
    all_tiles.empty() # Clear tiles as well

    # Load level data
    level_data = LEVELS[current_level_index]

    # Create tilemap
    all_tiles = pygame.sprite.Group()
    for row_index, row in enumerate(level_data['tilemap']):
        for col_index, tile_type in enumerate(row):
            if tile_type in tile_images:
                tile = Tile(tile_images[tile_type], col_index * TILE_SIZE, row_index * TILE_SIZE)
                all_tiles.add(tile)
                all_sprites.add(tile) # Add tiles to all_sprites for drawing


    # Create player
    player = Player(level_data['player_start'])
    all_sprites.add(player)

    # Create enemies
    for enemy_info in level_data['enemy_positions']:
        enemy = Enemy(enemy_info['type'], enemy_info['pos'])
        all_enemies.add(enemy)
        all_sprites.add(enemy)

    # Create obstacles
    for obstacle_info in level_data['obstacle_positions']:
        obstacle = Obstacle(obstacle_info['type'], obstacle_info['pos'][0], obstacle_info['pos'][1])
        all_obstacles.add(obstacle)
        all_sprites.add(obstacle)

    # Update flag position for the current level
    global flag_rect
    flag_rect.center = level_data['flag_position']


    return player # Return the newly created player instance

# --- Drawing Functions ---

def draw_menu():
    screen.fill(BROWN)
    title_text = menu_font.render("WW1 Trenches", True, DARK_GRAY)
    start_text = font.render("Press SPACE to Start", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()

def draw_game_over():
    screen.fill(BLACK)
    game_over_text = menu_font.render("Game Over", True, RED)
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()

def draw_victory():
    screen.fill(GREEN)
    if current_level_index < len(LEVELS) - 1:
        victory_text = menu_font.render("Level Complete!", True, BLACK)
        next_level_text = font.render("Press R for Next Level", True, BLACK)
    else:
        victory_text = menu_font.render("Final Victory!", True, BLACK)
        next_level_text = font.render("Press R to Play Again", True, BLACK)

    screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2 - victory_text.get_height() // 2))
    screen.blit(next_level_text, (SCREEN_WIDTH // 2 - next_level_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()


def draw_game(screen, player):
    # Drawing order: Tiles, then sprites (obstacles, enemies, player), then bullets/trails, then UI
    screen.fill(BROWN)  # Default background color

    # Draw tilemap
    all_tiles.draw(screen)

    # Draw sprites (obstacles, enemies, player)
    # Draw obstacles first so player/enemies appear on top
    all_obstacles.draw(screen)
    all_enemies.draw(screen)
    # Draw player
    screen.blit(player.image, player.rect)


    # Draw bullet trails
    for bullet in all_bullets:
        bullet.draw_trail(screen)

    # Draw flag
    screen.blit(flag_img, flag_rect)

    # Draw UI (Health and Lives)
    health_text = font.render(f"Health: {player.health}", True, WHITE)
    screen.blit(health_text, (10, 10))
    lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
    screen.blit(lives_text, (10, 50))

    pygame.display.flip()


# --- Game Loop ---

running = True
clock = pygame.time.Clock()

# Initial game setup (will be triggered by menu)
player = None # Player is created when game starts from menu
all_tiles = pygame.sprite.Group() # Initialize all_tiles group

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_level_index = 0 # Start at the first level
                    player = reset_game() # Start the game
        elif game_state == PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click to shoot
                    player.shoot()
        elif game_state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: # Press R to restart
                    current_level_index = 0 # Go back to the first level on game over
                    player = reset_game() # Reset game and get the new player instance
        elif game_state == VICTORY:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: # Press R for next level or restart after final victory
                    if current_level_index < len(LEVELS) - 1:
                        current_level_index += 1 # Advance to the next level
                        player = reset_game()
                    else:
                        current_level_index = 0 # Go back to the first level after final victory
                        player = reset_game()


    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        # Update
        # Store player's position before update
        prev_player_pos = player.update()
        all_bullets.update()
        all_enemies.update(player.rect) # Pass player rect to enemy update

        # Collision Detection

        # Player collision with enemies (take damage)
        # Use collide_mask for more accurate collision if using non-rectangular sprites
        enemy_hits = pygame.sprite.spritecollide(player, all_enemies, False, pygame.sprite.collide_mask)
        for enemy in enemy_hits:
            player.take_damage(1)  # Player takes 1 damage per hit

        # Bullet collision with enemies (damage enemy)
        bullet_enemy_hits = pygame.sprite.groupcollide(all_bullets, all_enemies, True, False, pygame.sprite.collide_mask)  # Remove bullet, don't remove enemy yet
        for bullet, enemies_hit in bullet_enemy_hits.items():
            for enemy in enemies_hit:
                enemy.take_damage(1) # Enemy takes 1 damage per hit

        # Bullet collision with obstacles (remove bullet)
        pygame.sprite.groupcollide(all_bullets, all_obstacles, True, False, pygame.sprite.collide_mask) # Remove bullet, don't remove obstacle

        # Player collision with obstacles (prevent movement - improved)
        player_obstacle_hits = pygame.sprite.spritecollide(player, all_obstacles, False, pygame.sprite.collide_mask)
        if player_obstacle_hits:
            # If collision occurs, revert player to previous position
            player.rect.topleft = prev_player_pos
            # Then, try moving only in x direction and check for collision
            player.rect.x = prev_player_pos[0] + (player.rect.x - prev_player_pos[0]) # Apply only x movement
            if pygame.sprite.spritecollide(player, all_obstacles, False, pygame.sprite.collide_mask):
                player.rect.x = prev_player_pos[0] # Revert x if still colliding

            # Then, try moving only in y direction and check for collision
            player.rect.y = prev_player_pos[1] + (player.rect.y - prev_player_pos[1]) # Apply only y movement
            if pygame.sprite.spritecollide(player, all_obstacles, False, pygame.sprite.collide_mask):
                 player.rect.y = prev_player_pos[1] # Revert y if still colliding


        # Check for victory condition (player reaches flag)
        if player.rect.colliderect(flag_rect):
            game_state = VICTORY


        # Check if all enemies are defeated (optional victory condition)
        # if not all_enemies:
        #     game_state = VICTORY

        # Drawing
        draw_game(screen, player)

    elif game_state == GAME_OVER:
        draw_game_over()

    elif game_state == VICTORY:
        draw_victory()


    clock.tick(60)  # Limit frame rate to 60 FPS

pygame.quit()
