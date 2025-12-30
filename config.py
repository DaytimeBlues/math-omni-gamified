"""
Application Configuration - v2.1 "Omni Kids" Design Language
Contains all tunable parameters for the gamified learning platform.

DESIGN UPDATE (Gemini + ChatGPT):
- Warm, accessible color palette
- Larger touch targets
- CVD-friendly design principles
"""

# =============================================================================
# ACCESSIBILITY CONSTANTS (HCI Research)
# =============================================================================
# Bumped to 100px for even safer touch targets
MIN_TOUCH_TARGET = 100
BUTTON_GAP = 40              # More air space
DEBOUNCE_DELAY_MS = 300      # Prevent rage clicks

# =============================================================================
# CONTENT ASSETS
# =============================================================================
CONCRETE_ITEMS = [
    {'name': 'apples', 'emoji': '🍎'},
    {'name': 'stars', 'emoji': '⭐'},
    {'name': 'cats', 'emoji': '🐱'},
    {'name': 'cars', 'emoji': '🚗'},
    {'name': 'ducks', 'emoji': '🦆'},
    {'name': 'fish', 'emoji': '🐟'},
    {'name': 'flowers', 'emoji': '🌸'},
    {'name': 'hearts', 'emoji': '❤️'},
]

# =============================================================================
# "OMNI KIDS" COLOR PALETTE (Gemini + ChatGPT Reviewed)
# Warm, accessible, CVD-friendly
# =============================================================================
COLORS = {
    # Background gradient (warm sunrise effect)
    'background_start': '#FFF8E7',  # Cream Puff
    'background_end': '#F0E6D2',    # Slightly darker cream
    'background': '#FFF8E7',         # Fallback solid
    
    # Primary (Sky Buddy - inviting blue)
    'primary': '#4DA8DA',
    'primary_dark': '#2B8BC0',       # For 3D edge
    'primary_hover': '#64B5E3',      # Lighter on hover
    
    # Accent (Sunshine - rewards, highlights)
    'accent': '#FFB347',
    'accent_dark': '#E69A2E',
    
    # Success (Minty Fresh - warm teal, CVD distinct)
    'success': '#00C897',
    'success_dark': '#009E77',
    
    # Error (Soft Coral - friendly "oops")
    'error': '#FF6B6B',
    'error_dark': '#E65A5A',
    
    # Locked (Pebble Gray)
    'locked': '#E0E0E0',
    'locked_dark': '#BDBDBD',
    
    # Text
    'text': '#2C3E50',              # Midnight (softer than black)
    'text_light': '#5D6D7E',        # Slate
    
    # Focus ring (accessibility)
    'focus': '#4DA8DA',
}

# =============================================================================
# TYPOGRAPHY
# =============================================================================
FONT_FAMILY = "Lexend"      # Dyslexia-friendly (fallback: Comic Sans MS)
FONT_SIZE_BODY = 22         # Bumped up
FONT_SIZE_HEADING = 32      # Bumped up

# =============================================================================
# ECONOMY
# =============================================================================
REWARD_CORRECT = 10          # Eggs per correct answer
REWARD_COMPLETION = 50       # Bonus for completing a level
MAP_LEVELS_COUNT = 10        # Levels per map

# =============================================================================
# VOICE CONFIGURATION
# =============================================================================
VOICE_TYPE = 'edge-tts'
VOICE_NAME = 'en-US-JennyNeural'
