"""
Gemini Tutor - Cloud AI Integration for Contextual Scaffolding
Uses Gemini 2.0 Flash to provide intelligent, vision-aware tutoring.

ARCHITECTURAL ROLE:
This is the "Guide" - handles conversational scaffolding and emotional support.
The local StrokeAnalyzer remains the "Grader" for instant answer checking.

Cloud is OPTIONAL:
- Returns None on any failure for graceful fallback to local agent
- Rate-limited to prevent API spam from excited 5-year-olds
- Short, clamped responses ensure child-appropriate feedback

PRIVACY NOTE:
Only the scratchpad canvas is sent to the cloud, never webcam/audio.
"""

from __future__ import annotations

import io
import time
from typing import Optional

from PIL import Image

# Optional import - app works without google.generativeai
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None


class GeminiTutor:
    """
    Cloud fallback helper for contextual scaffolding.
    Returns None on any failure so caller can gracefully fall back to local logic.
    
    DESIGN PRINCIPLES:
    1. Never crash the app on cloud failure
    2. Never return inappropriate content (verbosity clamp)
    3. Rate-limit to prevent API cost explosion
    """
    
    # Minimum seconds between cloud calls (prevents spam)
    RATE_LIMIT_SECONDS = 3.0
    
    # Maximum words in response (safety clamp)
    MAX_RESPONSE_WORDS = 15
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model_name: str = "gemini-2.0-flash-exp"
    ):
        """
        Initialize the Gemini tutor.
        
        Args:
            api_key: Google AI API key. If None, cloud features disabled.
            model_name: Gemini model to use.
        """
        self.enabled = False
        self.model = None
        self.session_active = False
        self._last_call_time = 0.0
        
        # Validate and configure
        if not api_key:
            print("[GeminiTutor] No API key provided - cloud features disabled")
            return
            
        if not GEMINI_AVAILABLE:
            print("[GeminiTutor] google-generativeai not installed - cloud disabled")
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            self.enabled = True
            print(f"[GeminiTutor] Initialized with model: {model_name}")
        except Exception as e:
            print(f"[GeminiTutor] Failed to initialize: {e}")
        
        # Child-friendly system instruction
        # PEDAGOGICAL CONSTRAINTS:
        # - Max 12 words keeps responses digestible for 5-year-olds
        # - "Never teach new concepts" prevents scope creep
        # - "Praise effort" aligns with Growth Mindset research
        self.system_instruction = (
            "You are 'Buddy', a math tutor for a 5-year-old Australian girl. "
            "Use max 12 words. Be excited and encouraging. "
            "Never teach new concepts. Praise effort not correctness. "
            "If the child is struggling, suggest counting together."
        )
    
    def _image_from_bytes(self, data: bytes) -> Image.Image:
        """Convert raw image bytes to PIL Image."""
        return Image.open(io.BytesIO(data)).convert("RGB")
    
    def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limit.
        
        Returns True if call is allowed, False if too soon.
        
        WHY RATE LIMITING:
        A 5-year-old clicking the help button repeatedly could
        generate dozens of API calls per minute. This protects
        both the parent's wallet and the API quota.
        """
        now = time.time()
        if now - self._last_call_time < self.RATE_LIMIT_SECONDS:
            return False
        self._last_call_time = now
        return True
    
    def analyze_canvas_context(
        self,
        canvas_bytes: bytes,
        target_number: int,
        current_strokes: int,
    ) -> Optional[str]:
        """
        Send scratchpad snapshot to Gemini for a contextual hint.
        
        Args:
            canvas_bytes: Raw PNG/JPEG bytes from widget.grab()
            target_number: The expected answer
            current_strokes: How many strokes the child has drawn
        
        Returns:
            A short hint string, or None to trigger local fallback.
        
        PEDAGOGICAL USE:
        Called when local heuristics detect confusion (e.g., 15 strokes
        for a question expecting 5). The AI can "see" the drawing and
        provide contextual guidance.
        """
        if not self.enabled or not self.model:
            return None
        
        if not self._check_rate_limit():
            print("[GeminiTutor] Rate limited, using local fallback")
            return None
        
        try:
            # Construct a focused prompt for the model
            prompt = (
                f"The child is trying to show the number {target_number}.\n"
                f"They have drawn {current_strokes} strokes on their scratchpad.\n"
                "Look at their drawing. Give ONE short, encouraging hint.\n"
                "Do not say 'wrong'. Suggest counting together if they seem confused."
            )
            
            image = self._image_from_bytes(canvas_bytes)
            
            response = self.model.generate_content(
                [self.system_instruction, prompt, image]
            )
            
            feedback = (response.text or "").strip()
            
            if not feedback:
                return None
            
            # SAFETY CLAMP: Truncate verbose responses
            # LLMs sometimes ignore word limits; this is our backstop
            words = feedback.split()
            if len(words) > self.MAX_RESPONSE_WORDS:
                # Use a safe fallback instead of truncating mid-sentence
                return "Let's try counting them together! One... two..."
            
            return feedback
            
        except Exception as exc:
            print(f"[GeminiTutor] Cloud error, falling back: {exc}")
            return None
    
    # =========================================================================
    # PUSH-TO-TALK SESSION MANAGEMENT
    # For future voice integration with Gemini Live API
    # =========================================================================
    
    def start_push_to_talk_session(self) -> None:
        """
        Called when barrel button is pressed.
        Activates cloud listening mode.
        
        FUTURE: Will integrate with Gemini Live API for real-time
        voice conversation. Currently just sets a flag.
        """
        if not self.session_active:
            self.session_active = True
            print(">> CLOUD SESSION STARTED [LISTENING]")
    
    def stop_push_to_talk_session(self) -> None:
        """
        Called when barrel button is released.
        Deactivates cloud listening mode.
        """
        if self.session_active:
            self.session_active = False
            print(">> CLOUD SESSION ENDED")
    
    @property
    def is_available(self) -> bool:
        """Check if cloud features are available."""
        return self.enabled and self.model is not None
