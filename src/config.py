# Game Configuration
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Worm colors
WORM_COLOR = (139, 69, 19)  # Brown
WORM_BODY_COLOR = (160, 82, 45)  # Saddle brown

# Tool indicator colors
DRILL_INDICATOR_COLOR = (255, 255, 0)  # Yellow
TORCH_INDICATOR_COLOR = (255, 165, 0)  # Orange
LASER_INDICATOR_COLOR = (0, 255, 255)  # Cyan
DYNAMITE_INDICATOR_COLOR = (255, 0, 0)  # Red

# Terrain settings
TILE_SIZE = 8
UI_HEIGHT = int(SCREEN_HEIGHT * 0.15)  # 15% of screen height for UI
MAP_WIDTH = SCREEN_WIDTH // TILE_SIZE  # Full width 
MAP_HEIGHT = (SCREEN_HEIGHT - UI_HEIGHT) // TILE_SIZE  # Leave UI space at top

# Worm settings
WORM_SPEED = 100  # pixels per second (horizontal movement)
WORM_RADIUS = 12

# Physics settings
GRAVITY = 400  # pixels per second squared
JUMP_VELOCITY = -250  # negative because Y increases downward
TERMINAL_VELOCITY = 300  # maximum falling speed
GROUND_FRICTION = 0.8  # friction when on ground
MAX_SLOPE_ANGLE = 45  # maximum slope angle in degrees that worm can climb

# Fall damage settings
FALL_DAMAGE_START_HEIGHT = 50  # Minimum fall distance (pixels) to take damage
FALL_DAMAGE_VELOCITY_THRESHOLD = 100  # Minimum velocity to cause fall damage
FALL_DAMAGE_MULTIPLIER = 0.8  # Damage scaling factor for fall distance

# Tool settings
DRILL_WIDTH = WORM_RADIUS * 3  # Drill is 3x wider than worm
DRILL_DEPTH = 40  # How deep the drill goes in pixels
DYNAMITE_RADIUS = 96  # Tripled explosion radius for bigger craters
DYNAMITE_COUNT_START = 10  # Starting number of dynamites
DYNAMITE_FUSE_TIME = 2.0  # Seconds until explosion
DYNAMITE_MIN_THROW = 50  # Minimum throw distance
DYNAMITE_MAX_THROW = 200  # Maximum throw distance
TORCH_RADIUS = 30  # Cone-shaped area
TORCH_RANGE = 80  # How far the torch cone extends
TORCH_GAS_COST = 10  # Gas units per torch use
TORCH_CONE_ANGLE = 60  # Degrees for cone spread
LASER_WIDTH = 16  # Doubled from 8

# Tool damage settings
DRILL_DAMAGE = 50  # Damage per drill hit
LASER_DAMAGE = 10  # Damage per laser hit
TORCH_DAMAGE = 30  # Damage per torch hit
DYNAMITE_BASE_DAMAGE = 70  # Base damage for dynamite explosion
# Dynamite damage is calculated as: max(10, DYNAMITE_BASE_DAMAGE - distance_from_explosion)

# Explosion system settings
EXPLOSION_PARTICLE_DENSITY = 0.8  # Particles per radius unit
EXPLOSION_DURATION = 800  # milliseconds
EXPLOSION_MIN_DAMAGE = 10  # Minimum damage from any explosion

# Death and respawn settings
RESPAWN_TIME = 2.0  # seconds until respawn
SPAWN_PROTECTION_TIME = 2.0  # seconds of invulnerability after respawn
TOMBSTONE_RESOURCE_PERCENTAGE = 0.2  # 20% of resources drop as loot
MIN_SPAWN_DISTANCE = 100  # Minimum distance from other worms when spawning

# Power charging
POWER_CHARGE_RATE = 100  # Power units per second when charging
MAX_POWER = 100  # Maximum power level

# Gas system
STARTING_GAS = 100
MAX_GAS = 200
GAS_BOTTLE_AMOUNT = 50  # Gas gained from finding a bottle
GAS_REFILL_AMOUNT = 50  # Gas refilled when collecting a gas bottle

# Battle timer system
BATTLE_TIMER_DEFAULT = 300  # Default 5 minutes in seconds
BATTLE_TIMER_WARNING_TIME = 60  # Flash warning when <1 minute remaining
BATTLE_TIMER_FLASH_RATE = 0.5  # Flash every 0.5 seconds during warning