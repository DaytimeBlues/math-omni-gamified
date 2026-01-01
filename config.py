"""
Application Configuration - v2.1 Premium Design System
"Functional prototype → Product" pivot.

DESIGN UPDATE (Premium UX):
- Warm, soft color palette (reduced cognitive load)
- Juicy 3D buttons with CSS-driven depth
- Dynamic gradient backgrounds via QPainter
- Touch-optimized accessibility
"""

# =============================================================================
# ACCESSIBILITY CONSTANTS (HCI Research)
# =============================================================================
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
# PREMIUM PALETTE (Warm & Soft) - v2.1
# Replaces harsh "developer defaults" with harmonious, low-contrast palette.
# =============================================================================
COLORS = {
    # Canvas
    'canvas': '#FFF9F0',            # Warm Cloud - main background
    'canvas_gradient': '#FFF0E1',   # Peachier bottom gradient
    
    # Primary (Mango Pop - main actions)
    'primary': '#FF9F43',           # Mango Pop
    'primary_shadow': '#E67E22',    # Deep Mango - 3D button side
    'primary_hover': '#FFAF60',     # Lighter on hover
    
    # Secondary (Soft Sky - navigation, map)
    'secondary': '#48DBFB',         # Soft Sky
    'secondary_shadow': '#0ABDE3',  # Ocean Depth - 3D side
    
    # Accent (Golden Egg - rewards)
    'accent': '#FDCB6E',            # Golden Egg
    'accent_highlight': '#FFEAA7',  # Flash color for reward pop
    
    # Feedback
    'success': '#00B894',           # Mint Leaf
    'error': '#FF6B6B',             # Soft Coral
    
    # Locked/Disabled
    'locked': '#DCDDE1',            # Light grey
    'locked_shadow': '#B2BEC3',     # Darker grey
    
    # Text
    'text': '#2D3436',              # Ink Grey (never pure black)
    'text_light': '#636E72',        # Secondary text
    
    # Legacy aliases (backwards compatibility)
    'background': '#FFF9F0',
    'background_start': '#FFF9F0',
    'background_end': '#FFF0E1',
    'focus': '#48DBFB',
}

# =============================================================================
# TYPOGRAPHY
# =============================================================================
FONT_FAMILY = "Lexend"      # Dyslexia-friendly (fallback: Segoe UI)
FONT_SIZE_BODY = 22
FONT_SIZE_HEADING = 32

# =============================================================================
# ECONOMY
# =============================================================================
REWARD_CORRECT = 10
REWARD_COMPLETION = 50
MAP_LEVELS_COUNT = 10

# =============================================================================
# AUDIO CONFIGURATION
# =============================================================================
VOLUME_SFX = 0.6
VOLUME_MUSIC = 0.3
VOLUME_MUSIC_DUCKED = 0.1
VOLUME_VOICE = 1.0
SFX_CACHE_MAX = 20

# =============================================================================
# PREMIUM STYLESHEETS (Juicy 3D Buttons)
# =============================================================================
STYLES = {
    # Primary action button (Submit, Next, Answer options)
    "premium_button": """
        QPushButton {
            background-color: #FF9F43;
            color: white;
            border: none;
            border-radius: 25px;
            border-bottom: 8px solid #E67E22;
            padding: 15px 30px;
            font-family: 'Lexend', 'Segoe UI', sans-serif;
            font-size: 28px;
            font-weight: bold;
            margin-top: 0px;
            outline: none;
        }
        QPushButton:hover {
            background-color: #FFAF60;
            margin-top: 2px;
            border-bottom: 6px solid #E67E22;
        }
        QPushButton:pressed {
            background-color: #E67E22;
            border-bottom: 0px solid transparent;
            margin-top: 8px;
            padding-top: 15px;
        }
        QPushButton:disabled {
            background-color: #BDC3C7;
            border-bottom: 8px solid #95A5A6;
            color: #ECF0F1;
        }
    """,
    
    # Secondary button (Navigation, Back)
    "secondary_button": """
        QPushButton {
            background-color: #48DBFB;
            color: white;
            border: none;
            border-radius: 25px;
            border-bottom: 6px solid #0ABDE3;
            padding: 12px 24px;
            font-family: 'Lexend', 'Segoe UI', sans-serif;
            font-size: 22px;
            font-weight: bold;
            margin-top: 0px;
        }
        QPushButton:hover {
            background-color: #74E0FC;
            margin-top: 2px;
            border-bottom: 4px solid #0ABDE3;
        }
        QPushButton:pressed {
            background-color: #0ABDE3;
            border-bottom: 0px solid transparent;
            margin-top: 6px;
        }
    """,
    
    # Success state (Correct answer)
    "success_button": """
        QPushButton {
            background-color: #00B894;
            color: white;
            border: none;
            border-radius: 25px;
            border-bottom: 8px solid #00896C;
            padding: 15px 30px;
            font-family: 'Lexend', 'Segoe UI', sans-serif;
            font-size: 28px;
            font-weight: bold;
        }
    """,
    
    # Error state (Wrong answer shake)
    "error_button": """
        QPushButton {
            background-color: #FF6B6B;
            color: white;
            border: none;
            border-radius: 25px;
            border-bottom: 8px solid #E65A5A;
            padding: 15px 30px;
            font-family: 'Lexend', 'Segoe UI', sans-serif;
            font-size: 28px;
            font-weight: bold;
        }
    """,
    
    # Egg counter pill
    "egg_counter": """
        QLabel {
            background-color: #FFF4D9;
            color: #D35400;
            border: 3px solid #FDCB6E;
            border-radius: 20px;
            padding: 8px 20px;
            font-weight: 900;
            font-size: 22px;
        }
    """,
    
    # Egg counter flash (reward pop)
    "egg_counter_flash": """
        QLabel {
            background-color: #FFEAA7;
            color: #D35400;
            border: 3px solid #FDCB6E;
            border-radius: 20px;
            padding: 8px 20px;
            font-weight: 900;
            font-size: 22px;
        }
    """,
    
    # Map node (circular level buttons)
    "map_node": """
        QPushButton {
            border-radius: 40px;
            min-width: 80px;
            min-height: 80px;
            max-width: 80px;
            max-height: 80px;
            background-color: #48DBFB;
            border-bottom: 6px solid #0ABDE3;
            font-size: 24px;
            font-weight: bold;
            color: white;
        }
        QPushButton:hover {
            background-color: #74E0FC;
            margin-top: 2px;
            border-bottom: 4px solid #0ABDE3;
        }
        QPushButton:pressed {
            background-color: #0ABDE3;
            border-bottom: 0px solid transparent;
            margin-top: 6px;
        }
        QPushButton:disabled {
            background-color: #DCDDE1;
            border-bottom: 6px solid #B2BEC3;
            color: #95A5A6;
        }
    """,
    
    # Current level (pulsing, unlocked)
    "map_node_current": """
        QPushButton {
            border-radius: 40px;
            min-width: 80px;
            min-height: 80px;
            max-width: 80px;
            max-height: 80px;
            background-color: #FF9F43;
            border: 3px solid #E67E22;
            border-bottom: 6px solid #E67E22;
            font-size: 24px;
            font-weight: bold;
            color: white;
        }
    """,
}

