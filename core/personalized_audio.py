"""
Personalized Audio - Pre-generated clips for the child.

These are pre-generated TTS clips with the child's name baked in.
Faster and more reliable than runtime TTS for common phrases.
"""
import os
import random
from pathlib import Path
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

ASSETS_DIR = Path(__file__).parent.parent / "assets" / "audio"

# Map of audio clip types to files
PERSONALIZED_CLIPS = {
    "welcome": "welcome_aurelia.mp3",
    "great_job": "great_job_aurelia.mp3",
    "amazing": "amazing_aurelia.mp3",
    "goodbye": "goodbye_aurelia.mp3",
    "try_again": "try_again_aurelia.mp3",
    "well_done": "well_done_aurelia.mp3",
    "keep_going": "keep_going_aurelia.mp3",
}

# Groups for random selection
SUCCESS_CLIPS = ["great_job", "amazing", "well_done"]
ENCOURAGEMENT_CLIPS = ["try_again", "keep_going"]


class PersonalizedAudio:
    """
    Plays pre-generated personalized audio clips.
    
    Faster than runtime TTS and ensures correct pronunciation.
    """
    
    def __init__(self):
        self._player = QMediaPlayer()
        self._output = QAudioOutput()
        self._player.setAudioOutput(self._output)
        self._output.setVolume(1.0)

        # Cache resolved file paths to avoid repeated filesystem checks
        # during gameplay (micro-optimization, but this path is hot).
        self._resolved_paths: dict[str, str] = {}
        for clip_name, filename in PERSONALIZED_CLIPS.items():
            path = ASSETS_DIR / filename
            if path.exists():
                self._resolved_paths[clip_name] = str(path)
    
    def _get_path(self, clip_name: str) -> str | None:
        """Get full path for a clip name."""
        return self._resolved_paths.get(clip_name)
    
    def play(self, clip_name: str) -> bool:
        """
        Play a specific clip by name.
        Returns True if clip exists and started playing.
        """
        path = self._get_path(clip_name)
        if not path:
            return False
        
        self._player.setSource(QUrl.fromLocalFile(path))
        self._player.play()
        return True
    
    def play_random_success(self) -> bool:
        """Play a random success/celebration clip."""
        clip = random.choice(SUCCESS_CLIPS)
        return self.play(clip)
    
    def play_random_encouragement(self) -> bool:
        """Play a random encouragement clip."""
        clip = random.choice(ENCOURAGEMENT_CLIPS)
        return self.play(clip)
    
    def stop(self):
        """Stop current playback."""
        self._player.stop()
    
    def has_clip(self, clip_name: str) -> bool:
        """Check if a clip exists."""
        return self._get_path(clip_name) is not None
