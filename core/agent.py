"""
Pedagogical Agent - Text-to-Speech + Growth Mindset Feedback
Combines audio output with educational feedback logic.

VOICE OPTIONS:
- edge-tts: Microsoft Neural voices (natural, requires internet)
- pyttsx3: Windows SAPI voices (robotic, works offline)

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
import asyncio
import logging
import tempfile
import os
import subprocess
from threading import Thread
import sys

logger = logging.getLogger(__name__)

# Ensure config is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config import FEEDBACK, MAX_ATTEMPTS_BEFORE_SCAFFOLDING, VOICE_TYPE, VOICE_NAME
except ImportError:
    # Fallback for standalone testing or if config structure differs
    FEEDBACK = {
        'effort_acknowledged': ["Great effort!", "I love how hard you're trying!"],
        'success_specific': ["You did it!", "That's exactly right!"],
        'gentle_redirect': ["Not quite, let's try again.", "Almost there! Give it another go."],
        'scaffolding_offer': ["Would you like a hint?", "I can help you with this one!"]
    }
    MAX_ATTEMPTS_BEFORE_SCAFFOLDING = 3
    VOICE_TYPE = 'pyttsx3'
    VOICE_NAME = None

# Conditional imports based on voice type
EDGE_TTS_AVAILABLE = False
if VOICE_TYPE == 'edge-tts':
    try:
        import edge_tts
        EDGE_TTS_AVAILABLE = True
    except ImportError:
        logger.info("edge-tts not installed, falling back to pyttsx3")

# We use pyttsx3 as a fallback or if explicitly requested
try:
    import pyttsx3
except ImportError:
    if not EDGE_TTS_AVAILABLE:
        logger.critical("No TTS engine available (install pyttsx3 or edge-tts)")

class PedagogicalAgent:
    """
    The pedagogical agent that provides supportive, growth-oriented feedback
    with voice output.
    """
    
    def __init__(self):
        self.attempt_count = 0
        self.consecutive_errors = 0
        
        # Initialize TTS engine based on config
        if EDGE_TTS_AVAILABLE:
            self.voice_type = 'edge-tts'
            self.voice_name = VOICE_NAME
            self._temp_audio_file = os.path.join(tempfile.gettempdir(), "math_omni_speech.mp3")
        else:
            self.voice_type = 'pyttsx3'
            try:
                self.engine = pyttsx3.init()
                self._configure_pyttsx3_voice()
            except Exception as e:
                logger.exception("Failed to init pyttsx3: %s", e)
                self.engine = None
    
    def _configure_pyttsx3_voice(self):
        """Configure pyttsx3 voice for optimal child engagement."""
        if not self.engine: return
        self.engine.setProperty('rate', 150)
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'zira' in voice.name.lower() or 'female' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
    
    def speak(self, text: str, block: bool = False):
        """Speak the given text."""
        if block:
            self._speak_sync(text)
        else:
            thread = Thread(target=self._speak_sync, args=(text,))
            thread.daemon = True
            thread.start()
    
    def _speak_sync(self, text: str):
        """Internal synchronous speech method."""
        if self.voice_type == 'edge-tts':
            self._speak_edge_tts(text)
        elif self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
    
    def _speak_edge_tts(self, text: str):
        """Generate and play speech using edge-tts."""
        async def generate_audio():
            communicate = edge_tts.Communicate(text, self.voice_name)
            await communicate.save(self._temp_audio_file)
        
        try:
            asyncio.run(generate_audio())
            # Play using powershell to play the mp3 file
            subprocess.run(
                ['powershell', '-c', 
                 f'Add-Type -AssemblyName presentationCore; ' +
                 f'$player = New-Object System.Windows.Media.MediaPlayer; ' +
                 f'$player.Open("{self._temp_audio_file}"); ' +
                 f'$player.Play(); Start-Sleep -Seconds 10'],
                capture_output=True,
                timeout=30
            )
        except Exception as e:
            logger.exception("edge-tts playback error: %s", e)
        
        if self._temp_audio_file and os.path.exists(self._temp_audio_file):
            try:
                os.remove(self._temp_audio_file)
            except OSError:
                pass
    
    def stop(self):
        """Stop any currently playing speech."""
        if self.voice_type != 'edge-tts' and self.engine:
            self.engine.stop()
    
    def reset_for_new_problem(self):
        """Reset tracking for a new problem."""
        self.attempt_count = 0
        self.consecutive_errors = 0
    
    def get_effort_feedback(self) -> str:
        """Return feedback acknowledging the child's effort."""
        return random.choice(FEEDBACK.get('effort_acknowledged', ["Great effort!"]))
    
    def get_success_feedback(self) -> str:
        """Return celebration feedback for correct answer."""
        self.consecutive_errors = 0
        return random.choice(FEEDBACK.get('success_specific', ["Well done!"]))
    
    def get_gentle_redirect(self) -> str:
        """Return feedback for incorrect answer that encourages retry."""
        self.attempt_count += 1
        self.consecutive_errors += 1
        return random.choice(FEEDBACK.get('gentle_redirect', ["Let's try again!"]))
    
    def should_offer_scaffolding(self) -> bool:
        """Determine if we should offer additional support."""
        return self.consecutive_errors >= MAX_ATTEMPTS_BEFORE_SCAFFOLDING
    
    def get_scaffolding_offer(self) -> str:
        """Return an offer to help."""
        return random.choice(FEEDBACK.get('scaffolding_offer', ["Would you like some help?"]))
    
    def get_idle_prompt(self) -> str:
        """Return a gentle prompt for an inactive child."""
        prompts = [
            "I'm here whenever you're ready!",
            "I wonder what you're thinking about?",
            "Take your time! There's no rush.",
            "I can help if you'd like!",
        ]
        return random.choice(prompts)
    
    def evaluate_answer(self, expected: int, drawn: int) -> tuple:
        """Evaluate the child's drawn answer."""
        if drawn == expected:
            return (True, self.get_success_feedback())
        
        self.attempt_count += 1
        self.consecutive_errors += 1
        
        if abs(drawn - expected) == 1:
            return (False, f"So close! You drew {drawn} and we needed {expected}. Let's try once more!")
        elif drawn > expected:
            return (False, f"Wow, you drew {drawn}! That's more than {expected}. Can you try with fewer?")
        else:
            return (False, f"I see {drawn} things. We need {expected}. Keep going, you can add more!")
