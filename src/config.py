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
UI_HEIGHT = int(SCREEN_HEIGHT * 0.12)  # 12% of screen height for UI
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

# Power charging
POWER_CHARGE_RATE = 100  # Power units per second when charging
MAX_POWER = 100  # Maximum power level

# Gas system
STARTING_GAS = 100
MAX_GAS = 200
GAS_BOTTLE_AMOUNT = 50  # Gas gained from finding a bottle
GAS_REFILL_AMOUNT = 50  # Gas refilled when collecting a gas bottle