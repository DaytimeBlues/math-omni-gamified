"""
Personalized Audio - Pre-generated clips for the child.
Faster and more reliable than runtime TTS for common phrases.
"""
import os
import random
from pathlib import Path
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

ASSETS_DIR = Path(__file__).parent.parent / "assets" / "audio"

PERSONALIZED_CLIPS = {
    "welcome": "welcome_child.mp3",
    "great_job": "great_job_child.mp3",
    "amazing": "amazing_child.mp3",
    "goodbye": "goodbye_child.mp3",
    "try_again": "try_again_child.mp3",
    "well_done": "well_done_child.mp3",
    "keep_going": "keep_going_child.mp3",
}

SUCCESS_CLIPS = ["great_job", "amazing", "well_done"]
ENCOURAGEMENT_CLIPS = ["try_again", "keep_going"]

class PersonalizedAudio:
    """Plays pre-generated personalized audio clips."""
    
    def __init__(self):
        self._player = QMediaPlayer()
        self._output = QAudioOutput()
        self._player.setAudioOutput(self._output)
        self._output.setVolume(1.0)
        self._resolved_paths: dict[str, str] = {}
        
        for clip_name, filename in PERSONALIZED_CLIPS.items():
            path = ASSETS_DIR / filename
            if path.exists():
                self._resolved_paths[clip_name] = str(path)
    
    def _get_path(self, clip_name: str) -> str | None:
        return self._resolved_paths.get(clip_name)
    
    def play(self, clip_name: str) -> bool:
        path = self._get_path(clip_name)
        if not path:
            return False
        self._player.setSource(QUrl.fromLocalFile(path))
        self._player.play()
        return True
    
    def play_random_success(self) -> bool:
        return self.play(random.choice(SUCCESS_CLIPS))
    
    def play_random_encouragement(self) -> bool:
        return self.play(random.choice(ENCOURAGEMENT_CLIPS))
    
    def stop(self):
        self._player.stop()
    
    def has_clip(self, clip_name: str) -> bool:
        return self._get_path(clip_name) is not None
