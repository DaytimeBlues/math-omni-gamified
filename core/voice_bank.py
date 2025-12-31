"""
Voice Bank - Pre-recorded TTS Phrase Management

Loads and plays pre-generated Gemini 2.5 Pro TTS audio clips.

Categories:
- welcome, success_*, wrong_*, hints_*, instructions
- level_*, celebration_*, farewell, numbers, items_*
"""

import random
import yaml
import hashlib
from pathlib import Path
from typing import List, Tuple

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl


SCRIPT_DIR = Path(__file__).parent.parent
VOICE_BANK_DIR = SCRIPT_DIR / "assets" / "audio" / "voice_bank_wav"
VOICE_BANK_YAML = SCRIPT_DIR / "assets" / "voice_bank.yaml"
DEFAULT_DURATION = 2.5


def phrase_to_filename(category: str, index: int, text: str) -> str:
    """Generate consistent filename matching the generator."""
    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    clean_cat = category.replace("_", "-")
    return f"{clean_cat}_{index:02d}_{text_hash}.wav"


class VoiceBank:
    """
    Manages pre-recorded TTS phrases.
    
    Usage:
        bank = VoiceBank()
        bank.play_random("success_high")  # Plays random enthusiastic success
        bank.play_random("wrong_gentle")  # Plays gentle encouragement
    """
    
    def __init__(self):
        self._phrases: dict[str, list[Tuple[str, Path, float]]] = {}
        self._player = QMediaPlayer()
        self._output = QAudioOutput()
        self._player.setAudioOutput(self._output)
        self._output.setVolume(1.0)
        
        self._load_phrases()
    
    def _load_phrases(self):
        """Load phrase catalog and verify audio files exist."""
        if not VOICE_BANK_YAML.exists():
            print(f"[VoiceBank] YAML not found: {VOICE_BANK_YAML}")
            return
        
        with open(VOICE_BANK_YAML, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        total = 0
        available = 0
        
        for category, phrase_list in data.items():
            if not isinstance(phrase_list, list):
                continue
            
            self._phrases[category] = []
            
            for i, text in enumerate(phrase_list, start=1):
                filename = phrase_to_filename(category, i, text)
                audio_path = VOICE_BANK_DIR / filename
                
                total += 1
                if audio_path.exists():
                    duration = self._get_duration(audio_path)
                    self._phrases[category].append((text, audio_path, duration))
                    available += 1
        
        print(f"[VoiceBank] Loaded {available}/{total} phrases")

    def _get_duration(self, audio_path: Path) -> float:
        """Read WAV file duration from header."""
        if not audio_path.exists():
            return 0.0

        import wave
        try:
            with wave.open(str(audio_path), 'rb') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                return frames / float(rate)
        except Exception:
            return DEFAULT_DURATION
    
    def get_categories(self) -> list[str]:
        """Get all available categories."""
        return list(self._phrases.keys())
    
    def get_phrases(self, category: str) -> list[str]:
        """Get all phrases in a category."""
        if category not in self._phrases:
            return []
        return [text for text, _, _ in self._phrases[category]]
    
    def has_category(self, category: str) -> bool:
        """Check if category has any available audio."""
        return category in self._phrases and len(self._phrases[category]) > 0
    
    def play_random(self, category: str) -> float:
        """Play a random phrase and return its duration (seconds)."""
        if not self.has_category(category):
            return 0.0
        
        _, audio_path, duration = random.choice(self._phrases[category])
        self._player.setSource(QUrl.fromLocalFile(str(audio_path)))
        self._player.play()
        return duration
    
    def play_specific(self, category: str, index: int = 0) -> float:
        """Play a specific phrase by index and return its duration."""
        if not self.has_category(category):
            return 0.0
        
        if index >= len(self._phrases[category]):
            index = 0
        
        _, audio_path, duration = self._phrases[category][index]
        self._player.setSource(QUrl.fromLocalFile(str(audio_path)))
        self._player.play()
        return duration
    
    def play_number(self, n: int) -> float:
        """Play a number (1-20). Returns duration in seconds."""
        if n < 1 or n > 20:
            return 0.0
        return self.play_specific("numbers", n - 1)
    
    def stop(self):
        """Stop current playback."""
        self._player.stop()


# Convenience mappings for game logic
SUCCESS_CATEGORIES = ["success_basic", "success_medium", "success_high", "success_personalized"]
WRONG_CATEGORIES = ["wrong_gentle", "wrong_supportive", "wrong_encouraging"]
HINT_CATEGORIES = ["hints_basic", "hints_advanced", "hints_together"]


def get_success_category(streak: int = 0) -> str:
    """Get appropriate success category based on streak."""
    if streak >= 3:
        return "success_streak"
    elif streak >= 2:
        return random.choice(["success_high", "success_personalized"])
    elif streak >= 1:
        return "success_medium"
    else:
        return random.choice(["success_basic", "success_medium"])


def get_wrong_category(attempts: int = 1) -> str:
    """Get appropriate encouragement category based on attempts."""
    if attempts >= 3:
        return "wrong_supportive"
    elif attempts >= 2:
        return "wrong_encouraging"
    else:
        return "wrong_gentle"


def get_hint_category(hint_level: int = 1) -> str:
    """Get appropriate hint category based on level."""
    if hint_level >= 3:
        return "hints_together"
    elif hint_level >= 2:
        return "hints_advanced"
    else:
        return "hints_basic"
