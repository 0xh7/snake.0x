import pygame


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TITLE = "Snake 0x"
FPS = 60

WORLD_WIDTH = 3000
WORLD_HEIGHT = 2400
CAMERA_SMOOTHING = 0.05

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (100, 100, 100)
BACKGROUND_COLOR = (15, 20, 30)
GRID_COLOR = (25, 35, 45)





GRID_SIZE = 40
INITIAL_SNAKE_LENGTH = 5


PLAYER_SPEED = 5
AI_SPEED = 4



FOOD_SPAWN_RATE = 0.05
MAX_FOOD_ITEMS = 200
GROWTH_PER_FOOD = 2
SCORE_FONT_SIZE = 24
BOUNDARY_WIDTH = 8

ENABLE_SELF_COLLISION = False
HEAD_DAMAGE_MULTIPLIER = 2.0
DROPPED_FOOD_COUNT = 10
COLLISION_BUFFER = 0
SELF_COLLISION_START_INDEX = 8
OTHER_COLLISION_BUFFER = 0

BOOST_SPEED_MULTIPLIER = 1.8
BOOST_SEGMENT_DROP_INTERVAL = 6
BOOST_MIN_LENGTH = 8
BOOST_COOLDOWN = 1.5
BOOST_FOOD_SIZE = 1
BOOST_EFFECT_QUALITY = 3
BOOST_LENGTH_COST = 2
BOOST_SCORE_REDUCTION = True

SKINS = [
    {"name": "Classic", "colors": [(0, 220, 0)], "pattern": "solid"},
    {"name": "Blue", "colors": [(0, 100, 255)], "pattern": "solid"},
    {"name": "Fire Red", "colors": [(255, 30, 0)], "pattern": "solid"},
    {"name": "Rainbow", "colors": [(255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 220, 0), (0, 80, 255), (150, 0, 255)], "pattern": "rainbow"},
    {"name": "Tiger", "colors": [(255, 180, 0), (10, 10, 10)], "pattern": "tiger"},
    {"name": "Ice", "colors": [(180, 230, 255), (230, 250, 255)], "pattern": "gradient"},
    {"name": "Gold", "colors": [(255, 215, 0), (218, 165, 32)], "pattern": "gradient"},
    {"name": "Neon", "colors": [(0, 255, 255), (255, 0, 255)], "pattern": "neon"},
    {"name": "Lava", "colors": [(255, 80, 0), (200, 0, 0), (60, 0, 0)], "pattern": "lava"}
]

PATTERN_COLORS = {
    "rainbow": [
        (255, 0, 0),
        (255, 128, 0),
        (255, 255, 0),
        (0, 255, 0),
        (0, 0, 255),
        (128, 0, 255),
        (255, 0, 255)
    ],
    "tiger": [(255, 180, 0), (0, 0, 0)],
    "neon": [(0, 255, 255), (255, 0, 255)],
    "lava": [(255, 60, 0), (180, 0, 0), (40, 0, 0)]
}

SCOREBOARD_ENTRIES = 10
MINIMAP_SIZE = 180
MINIMAP_POSITION = (20, 20)
MINIMAP_OPACITY = 160
MENU_BACKGROUND_COLOR = (8, 12, 20)
MENU_ACCENT_COLOR = (90, 140, 230)
BUTTON_COLOR = (30, 45, 80)
BUTTON_HOVER_COLOR = (50, 80, 130)
BUTTON_TEXT_COLOR = (235, 245, 255)
MENU_BACK_BUTTON_SIZE = (100, 40)
MENU_BACK_BUTTON_POS = (50, 50)

UI_ANIMATION_ENABLED = True
UI_HOVER_EFFECT = True
UI_BUTTON_SOUND = False
BUTTON_HOVER_ANIMATION_SPEED = 0.2
UI_FONT = "Arial"

SHOW_SNAKE_STATS = True
CUSTOM_FONTS = True
UI_ANIMATION_SPEED = 1.0
BORDER_DECORATION_DENSITY = 100

BOOST_EFFECT_COLOR = (255, 200, 70, 180)
DANGER_WARNING_COLOR = (220, 50, 50, 200)
BACKGROUND_PATTERN = True
PATTERN_COLOR = (40, 55, 85)
MAP_BORDER_COLOR = (70, 110, 180)
GLOW_INTENSITY = 3.0

MAP_DESIGN_STYLE = "modern"
BACKGROUND_PATTERN_STYLE = "dots"
MAP_DECORATION_DENSITY = 30

COOLDOWN_BAR_COLOR = (100, 180, 255)
COOLDOWN_BAR_BG_COLOR = (60, 60, 70)
COOLDOWN_BAR_HEIGHT = 5
COOLDOWN_BAR_BORDER_RADIUS = 2

ENABLE_LOADING_SCREEN = True
LOADING_SCREEN_BG_COLOR = (10, 15, 25)
LOADING_SCREEN_TEXT_COLOR = (200, 220, 255)

DEATH_EXPLOSION_PARTICLES = 50
PATTERN_DENSITY = 30

PARTICLE_MAX_COUNT = 300
FOOD_SPARKLE_COLOR = (255, 255, 100)
FLOATING_TEXT_DURATION = 1.0
DEATH_EXPLOSION_SIZE = 20

DEBUG_MODE = False
FPS_DISPLAY = True
SHOW_COLLISION_BOXES = False

GROWTH_RATE_SCALING = 1.0
AI_DIFFICULTY_SCALING = True

AUTO_COLLECT_NEARBY_FOOD = True
SPAWN_PROTECTION_TIME = 3.0
LEADERBOARD_SIZE = 5

EXIT_KEYS = [pygame.K_ESCAPE]

NUM_AI_SNAKES = 15
AI_VISION_RANGE = 200
AI_DECISION_RATE = 10
AI_AGGRESSION_FACTOR = 0.85
AI_TARGET_PLAYER_CHANCE = 0.3
AI_BOOST_AGGRESSIVENESS = 0.7
AI_FOOD_VALUE_WEIGHT = 2.0

DIFFICULTY_INCREASE_RATE = 0.001
MAX_DIFFICULTY = 2.0

SCORE_MULTIPLIER = 1.5
TIME_BONUS_FACTOR = 0.5
DIFFICULTY_SCORE_FACTOR = 1.2

MOUSE_TURN_SMOOTHNESS = 0.85
MOUSE_MOVEMENT_THRESHOLD = 20
