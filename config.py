"""
Application Configuration - PyQt6 Version
Contains all tunable parameters for the learning application.
"""

# =============================================================================
# VISUAL CONFIGURATION - PyQt6 Compatible Colors (hex strings)
# =============================================================================

COLORS = {
    'background': '#f2f2f8',       # Soft off-white
    'primary': '#3399e6',          # Friendly blue  
    'secondary': '#e68033',        # Warm orange
    'success': '#4dcc66',          # Celebratory green
    'canvas': '#ffffff',           # Pure white scratchpad
    'stroke': '#262650',           # Dark purple-blue for drawing
}

# Font sizes designed for children
FONT_SIZES = {
    'problem_text': 32,    # Very large for easy reading
    'button_text': 20,     # Readable at arm's length
    'feedback_text': 18,   # Clear feedback messages
}

# Minimum touch target size (in pixels) - Apple HIG recommends 44pt
MIN_TOUCH_TARGET = 80

# =============================================================================
# TIMING CONFIGURATION (Scaffolding Triggers)
# =============================================================================

TIMING = {
    'idle_prompt_seconds': 8.0,     # Wait before offering help
    'stroke_complete_delay': 0.3,   # Brief lift detection
    'celebration_duration': 2.0,    # Animation time
}

# =============================================================================
# PEDAGOGICAL CONFIGURATION
# =============================================================================

MAX_ATTEMPTS_BEFORE_SCAFFOLDING = 2
ERASE_FRUSTRATION_THRESHOLD = 3

# =============================================================================
# ACARA CURRICULUM CODES
# =============================================================================

CURRICULUM = {
    'counting': 'ACMNA001',
    'subitising': 'ACMNA002',
    'numeral_quantity': 'ACMNA003',
    'addition': 'ACMNA004',
    'measurement': 'ACMMG006',
}

# =============================================================================
# GROWTH MINDSET FEEDBACK BANK
# =============================================================================

FEEDBACK = {
    'effort_acknowledged': [
        "I see you're working hard on this!",
        "You're thinking carefully, that's wonderful!",
        "I can see you're trying different ideas!",
        "What great concentration!",
        "You're really giving this your best!",
    ],
    
    'scaffolding_offer': [
        "Would you like to count together?",
        "Let's try touching each one as we count.",
        "Want me to show you one way to start?",
        "Let's look at this part together.",
        "How about we count the ones you've drawn?",
    ],
    
    'success_specific': [
        "You counted every single one correctly!",
        "Your drawing shows exactly the right amount!",
        "You matched the number perfectly!",
        "Look at that! You did it all by yourself!",
        "That's exactly right! Your hard work paid off!",
    ],
    
    'gentle_redirect': [
        "Hmm, let's count these again together!",
        "I wonder if we missed one? Let's check!",
        "So close! Let's look one more time.",
        "That was a good try! Let's see if we can find another way.",
    ],
}
