"""
Audio Service - SFX Player Only (v4 Architecture)

Static audio playback via VoiceBank. This service handles UI sound effects only.
All voice audio is handled by VoiceBank (177 pre-generated clips).

Removed in v4:
- Dynamic TTS (AudioService.speak)
- Gemini API calls (_generate_tts)
- TTS cache management
- GOOGLE_API_KEY dependency
"""
import os
from typing import Optional
from pathlib import Path
from collections import OrderedDict

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from PyQt6.QtCore import QUrl, QObject

from core.sfx import get_sfx_path

SFX_CACHE_MAX = 20


class SFXCache:
    """LRU cache for SFX to prevent memory leaks."""
    
    def __init__(self, max_size: int = SFX_CACHE_MAX):
        self._cache: OrderedDict[str, QSoundEffect] = OrderedDict()
        self._max_size = max_size
    
    def get(self, name: str) -> Optional[QSoundEffect]:
        if name in self._cache:
            # Move to end (most recently used)
            effect = self._cache.pop(name)
            self._cache[name] = effect
            return effect
        
        # Load new effect
        path = get_sfx_path(name)
        if not path or not os.path.exists(path):
            return None
        
        effect = QSoundEffect()
        effect.setSource(QUrl.fromLocalFile(path))
        effect.setVolume(0.6)
        
        self._cache[name] = effect
        
        # Enforce size limit
        if len(self._cache) > self._max_size:
            _, old_effect = self._cache.popitem(last=False)
            old_effect.stop()
            old_effect.deleteLater()
        
        return effect


class AudioService(QObject):
    """
    Simplified audio service for SFX and background music only.
    
    Voice playback is handled by VoiceBank (177 pre-generated clips).
    This service provides:
    - UI sound effects (button clicks, success/error chimes)
    - Background music playback
    - Audio ducking for voice priority
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # SFX Channel (LRU cached for low latency)
        self._sfx_cache = SFXCache()
        
        # Music Channel
        self.music_player = QMediaPlayer()
        self.music_output = QAudioOutput()
        self.music_player.setAudioOutput(self.music_output)
        self.music_output.setVolume(0.3)

    def play_sfx(self, sfx_name: str) -> None:
        """Fire-and-forget SFX playback with LRU cache."""
        effect = self._sfx_cache.get(sfx_name)
        if effect:
            effect.play()

    def duck_music(self, active: bool) -> None:
        """Lower music volume when voice is active."""
        target_vol = 0.1 if active else 0.3
        self.music_output.setVolume(target_vol)

    def play_music(self, music_path: str, loop: bool = True) -> None:
        """Start background music playback."""
        if not Path(music_path).exists():
            print(f"[Audio] Music file not found: {music_path}")
            return
        
        self.music_player.setSource(QUrl.fromLocalFile(music_path))
        if loop:
            self.music_player.setLoops(QMediaPlayer.Loops.Infinite)
        self.music_player.play()

    def stop_music(self) -> None:
        """Stop background music."""
        self.music_player.stop()

    def cleanup(self) -> None:
        """Lifecycle cleanup."""
        self.music_player.stop()
