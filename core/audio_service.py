"""
Async Audio Service - Cross-Platform QtMultimedia

Uses edge-tts for neural voice synthesis and QMediaPlayer for playback.
Replaces previous Windows-specific PowerShell implementation.

FIXES APPLIED (AI Review):
- Replaced PowerShell with QMediaPlayer (Z.ai, DeepSeek)
- Cross-platform support for Future Tablets/Linux
"""

import os
import hashlib
import asyncio
import edge_tts
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from PyQt6.QtCore import QUrl, QObject, pyqtSignal

CACHE_DIR = os.path.join("cache", "audio")
SFX_DIR = os.path.join("assets", "sfx")


class AudioService(QObject):
    """
    Async audio manager using QtMultimedia (Cross-Platform).
    Handles both TTS (QMediaPlayer) and SFX (QSoundEffect).
    """
    
    def __init__(self):
        super().__init__()
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.voice = "en-US-JennyNeural"
        
        # TTS Setup
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # State
        self._playback_future = None
        
        # Connect signals
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.player.errorOccurred.connect(self._on_error)

        # SFX Setup
        self.sfx = {}
        self._load_sfx()

    def _load_sfx(self):
        """Preload sound effects for low-latency playback."""
        effects = {
            'correct': 'correct.wav',
            'wrong': 'wrong.wav',
            'click': 'click.wav',
            'win': 'win.wav'
        }
        
        for name, filename in effects.items():
            path = os.path.join(SFX_DIR, filename)
            if os.path.exists(path):
                effect = QSoundEffect()
                effect.setSource(QUrl.fromLocalFile(os.path.abspath(path)))
                effect.setVolume(0.6)
                self.sfx[name] = effect
            else:
                print(f"[AudioService] Warning: SFX file not found: {path}")

    def play_sfx(self, name: str):
        """Play a preloaded sound effect."""
        if name in self.sfx:
            # If already playing, stop to restart (allows rapid tapping)
            if self.sfx[name].isPlaying():
                self.sfx[name].stop()
            self.sfx[name].play()

    async def speak(self, text: str):
        """Generate and play speech asynchronously."""
        if not text:
            return
            
        # If already speaking, stop previous (cancel future)
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.stop()
            if self._playback_future and not self._playback_future.done():
                self._playback_future.cancel()
        
        try:
            filename = self._get_hash(text)
            filepath = os.path.join(CACHE_DIR, filename)
            abs_path = os.path.abspath(filepath)

            # Generate if missing
            if not os.path.exists(filepath):
                communicate = edge_tts.Communicate(text, self.voice)
                await communicate.save(filepath)

            # Play using QtMultimedia
            await self._play_audio(abs_path)
            
        except Exception as e:
            print(f"[AudioService] Error: {e}")
            # Ensure future is cleaned up if error occurs before play
            if self._playback_future and not self._playback_future.done():
                try:
                    self._playback_future.set_result(False)
                except asyncio.InvalidStateError:
                    pass

    async def _play_audio(self, abs_path: str):
        """Play audio file and await completion."""
        # Create a future to await
        self._playback_future = asyncio.Future()
        
        url = QUrl.fromLocalFile(abs_path)
        self.player.setSource(url)
        self.player.play()
        
        # Wait for the signal handler to resolve the future
        try:
            await self._playback_future
        except asyncio.CancelledError:
            self.player.stop()

    def _on_media_status_changed(self, status):
        """Handle media status changes to resolve the async future."""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self._playback_future and not self._playback_future.done():
                try:
                    self._playback_future.set_result(True)
                except asyncio.InvalidStateError:
                    pass
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
             if self._playback_future and not self._playback_future.done():
                try:
                    self._playback_future.set_exception(Exception("Invalid Media"))
                except asyncio.InvalidStateError:
                    pass

    def _on_error(self):
        """Handle player errors."""
        err_msg = self.player.errorString()
        print(f"[AudioService] Player Error: {err_msg}")
        if self._playback_future and not self._playback_future.done():
            try:
                self._playback_future.set_exception(Exception(f"QtPlayer Error: {err_msg}"))
            except asyncio.InvalidStateError:
                pass

    def _get_hash(self, text: str) -> str:
        return f"{hashlib.md5(text.encode()).hexdigest()}.mp3"
    
    @property
    def is_speaking(self) -> bool:
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
    
    async def cleanup(self) -> None:
        """Lifecycle cleanup."""
        self.player.stop()
        if self._playback_future and not self._playback_future.done():
            self._playback_future.cancel()
