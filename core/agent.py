"""
Pedagogical Agent - Text-to-Speech + Growth Mindset Feedback
Combines audio output with educational feedback logic.

PEDAGOGICAL FOUNDATION:
Based on Carol Dweck's Growth Mindset research (Stanford University):
- Praise EFFORT, not intelligence
- View mistakes as learning opportunities
- Encourage process over outcome

Also implements Vygotsky's Zone of Proximal Development:
- Scaffolding: Provide just enough support for success
- Gradually release responsibility as competence grows
"""

import random
import pyttsx3
from threading import Thread
import sys
sys.path.append('..')
from config import FEEDBACK, MAX_ATTEMPTS_BEFORE_SCAFFOLDING


class PedagogicalAgent:
    """
    The pedagogical agent that provides supportive, growth-oriented feedback
    with voice output.
    
    PERSONALITY DESIGN:
    Warm, patient, and encouraging. Never expresses disappointment or
    frustration. Celebrates effort and reframes mistakes as discoveries.
    Think of a kind, enthusiastic kindergarten teacher.
    """
    
    def __init__(self):
        self.attempt_count = 0
        self.consecutive_errors = 0
        
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self._configure_voice()
    
    def _configure_voice(self):
        """
        Configure voice for optimal child engagement.
        
        VOICE SELECTION:
        - Slower rate for processing time
        - Attempt to select friendly-sounding voice
        """
        # Reduce speech rate (150 wpm for clarity)
        self.engine.setProperty('rate', 150)
        
        # Try to select a friendly voice
        voices = self.engine.getProperty('voices')
        for voice in voices:
            # Prefer female voices (ZIra on Windows)
            if 'zira' in voice.name.lower() or 'female' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
    
    def speak(self, text: str, block: bool = False):
        """
        Speak the given text.
        
        Args:
            text: The message to speak
            block: If True, wait for speech to complete
        """
        if block:
            self._speak_sync(text)
        else:
            # Run in background thread to keep UI responsive
            thread = Thread(target=self._speak_sync, args=(text,))
            thread.daemon = True
            thread.start()
    
    def _speak_sync(self, text: str):
        """Internal synchronous speech method."""
        self.engine.say(text)
        self.engine.runAndWait()
    
    def stop(self):
        """Stop any currently playing speech."""
        self.engine.stop()
    
    def reset_for_new_problem(self):
        """
        Reset tracking for a new problem.
        
        Each problem is a fresh start—we don't carry over "failure" state.
        """
        self.attempt_count = 0
        self.consecutive_errors = 0
    
    def get_effort_feedback(self) -> str:
        """Return feedback acknowledging the child's effort."""
        return random.choice(FEEDBACK['effort_acknowledged'])
    
    def get_success_feedback(self) -> str:
        """Return celebration feedback for correct answer."""
        self.consecutive_errors = 0
        return random.choice(FEEDBACK['success_specific'])
    
    def get_gentle_redirect(self) -> str:
        """Return feedback for incorrect answer that encourages retry."""
        self.attempt_count += 1
        self.consecutive_errors += 1
        return random.choice(FEEDBACK['gentle_redirect'])
    
    def should_offer_scaffolding(self) -> bool:
        """Determine if we should offer additional support."""
        return self.consecutive_errors >= MAX_ATTEMPTS_BEFORE_SCAFFOLDING
    
    def get_scaffolding_offer(self) -> str:
        """Return an offer to help."""
        return random.choice(FEEDBACK['scaffolding_offer'])
    
    def get_idle_prompt(self) -> str:
        """Return a gentle prompt for an inactive child."""
        prompts = [
            "I'm here whenever you're ready!",
            "I wonder what you're thinking about?",
            "Take your time! There's no rush.",
            "Would you like to try drawing something?",
            "I can help if you'd like!",
        ]
        return random.choice(prompts)
    
    def evaluate_answer(self, expected: int, drawn: int) -> tuple:
        """
        Evaluate the child's drawn answer.
        
        Args:
            expected: The correct numerical answer
            drawn: The quantity from the child's drawing
        
        Returns:
            Tuple of (is_correct, feedback_message)
        
        GENEROSITY IN INTERPRETATION:
        Being off by 1 might mean they miscounted (understandable at 5)
        rather than lacking conceptual understanding.
        """
        if drawn == expected:
            return (True, self.get_success_feedback())
        
        # Close enough (off by 1)
        elif abs(drawn - expected) == 1:
            self.attempt_count += 1
            self.consecutive_errors += 1
            return (False, f"So close! You drew {drawn} and we needed {expected}. Let's try once more!")
        
        # More than needed
        elif drawn > expected:
            self.attempt_count += 1
            self.consecutive_errors += 1
            return (False, f"Wow, you drew {drawn}! That's more than {expected}. Can you try with fewer?")
        
        # Fewer than needed
        else:
            self.attempt_count += 1
            self.consecutive_errors += 1
            return (False, f"I see {drawn} things. We need {expected}. Keep going, you can add more!")
