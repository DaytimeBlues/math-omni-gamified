"""
Design Tokens - Math Omni (Sidereal Voyager)
Central source of truth for all UI styling.
"""

from typing import Dict

# =============================================================================
# TYPOGRAPHY
# =============================================================================
FONT_FAMILY = "Lexend"      # Dyslexia-friendly (fallback: Segoe UI)
FONT_SIZE_BODY = 22
FONT_SIZE_HEADING = 32

# =============================================================================
# LAYOUT
# =============================================================================
MIN_TOUCH_TARGET = 100
BUTTON_GAP = 40

# =============================================================================
# PALETTE (Warm & Soft) - v2.1
# =============================================================================
COLORS: Dict[str, str] = {
    # Canvas
    'canvas': '#FFF9F0',            # Warm Cloud - main background
    'canvas_gradient': '#FFF0E1',   # Peachier bottom gradient
    
    # Primary (Mango Pop - main actions)
    'primary': '#FF9F43',           # Mango Pop
    'primary_shadow': '#E67E22',    # Deep Mango - 3D button side
    'primary_dark': '#E67E22',      # Alias for premium_ui compatibility
    'primary_hover': '#FFAF60',     # Lighter on hover
    
    # Secondary (Soft Sky - navigation, map)
    'secondary': '#48DBFB',         # Soft Sky
    'secondary_shadow': '#0ABDE3',  # Ocean Depth - 3D side
    
    # Accent (Golden Egg - rewards)
    'accent': '#FDCB6E',            # Golden Egg
    'accent_highlight': '#FFEAA7',  # Flash color for reward pop
    'accent_dark': '#D4A84B',       # Dark accent for borders
    
    # Feedback
    'success': '#00B894',           # Mint Leaf
    'success_dark': '#00856A',      # Dark success for borders
    'error': '#FF6B6B',             # Soft Coral
    'error_dark': '#D63031',        # Dark error for borders
    
    # Locked/Disabled
    'locked': '#DCDDE1',            # Light grey
    'locked_shadow': '#B2BEC3',     # Darker grey
    'locked_dark': '#B2BEC3',       # Alias for premium_ui
    
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
# STYLESHEETS (Juicy 3D Buttons)
# =============================================================================
STYLES: Dict[str, str] = {
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
            outline: none;
        }
        QPushButton:pressed {
            background-color: #E67E22;
            border-bottom: 0px solid transparent;
            margin-top: 8px;
            padding-top: 15px;
            outline: none;
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
    
    # Header Card
    "header_card": """
        QFrame#HeaderCard {
            background-color: #FFFEF8;
            border-radius: 20px;
            padding: 15px 25px;
        }
    """,
    
    # Premium Question Card
    "question_card": """
        QFrame#QuestionCard {
            background-color: #FFFFFF;
            border-radius: 30px;
            border: 4px solid #F5E6C8;
        }
    """
}

# =============================================================================
# GRADIENTS
# =============================================================================
PREMIUM_BG_GRADIENT = """
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #FEF9E7,
        stop:0.5 #FAF0DC,
        stop:1 #F5E6C8
    );
"""

# =============================================================================
# DOMAIN GRADIENTS (Sidereal Voyager Edition)
# =============================================================================
DOMAIN_GRADIENTS = {
    # 1) Aurora Sky (Counting)
    "counting": """
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0    #D7F4FE,
            stop:0.55 #BBF1FB,
            stop:1    #97EFF7
        );
        border: 4px solid #97EFF7;
    """,
    # 2) Mango Burst (Addition)
    "addition": """
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0    #FFEACC,
            stop:0.55 #FCCC9C,
            stop:1    #F7A164
        );
        border: 4px solid #F7A164;
    """,
    # 3) Mint Nebula (Subtraction)
    "subtraction": """
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0    #D0FBEB,
            stop:0.55 #B6F7E1,
            stop:1    #94F0D9
        );
        border: 4px solid #94F0D9;
    """,
    # 4) Twilight Plum (Patterns)
    "patterns": """
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0    #E6DAFB,
            stop:0.55 #D7C2F4,
            stop:1    #C7A5E9
        );
        border: 4px solid #C7A5E9;
    """
}

# =============================================================================
# PHYSICS CONFIGURATION
# =============================================================================
ANIM_CONFIG = {
    'bob_speed': 50,            # Timer interval (ms)
    'bob_amplitude': 12,        # Pixels to move up/down
    'bob_step': 0.4,            # Pixels per tick
    'warp_duration': 350,       # ms for click transition
    'drop_stagger': 150,        # ms delay between cards appearing
}
