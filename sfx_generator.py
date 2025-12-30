"""
SFX Generator
Generates simple synthetic sound effects (WAV) for Math Omni.
Run this script once to create the 'assets/sfx' directory and files.
"""
import wave
import math
import struct
import os
import random

SFX_DIR = os.path.join("assets", "sfx")
os.makedirs(SFX_DIR, exist_ok=True)

def generate_tone(filename, freq=440, duration=0.2, volume=0.5, type='sine'):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(os.path.join(SFX_DIR, filename), 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            
            if type == 'sine':
                value = math.sin(2.0 * math.pi * freq * t)
            elif type == 'square':
                value = 1.0 if math.sin(2.0 * math.pi * freq * t) > 0 else -1.0
            elif type == 'saw':
                value = 2.0 * (t * freq - math.floor(t * freq + 0.5))
            elif type == 'noise':
                value = random.uniform(-1, 1)
            else:
                value = 0
            
            # Simple envelope (attack/decay) to avoid clicking
            if i < 500: # Attack
                value *= (i / 500.0)
            if i > n_samples - 1000: # Decay
                value *= ((n_samples - i) / 1000.0)
                
            data = struct.pack('<h', int(value * volume * 32767.0))
            wav_file.writeframes(data)

def generate_assets():
    print(f"Generating SFX in {SFX_DIR}...")
    
    # Correct: High pitch "Ding" (Sine, E6)
    generate_tone("correct.wav", freq=1318.51, duration=0.4, volume=0.6, type='sine')
    
    # Wrong: Low pitch "Buzz" (Sawtooth, A2)
    generate_tone("wrong.wav", freq=110.0, duration=0.3, volume=0.4, type='saw')
    
    # Click: Short tick (Noise)
    generate_tone("click.wav", freq=0, duration=0.05, volume=0.3, type='noise')
    
    # Level Complete: Major Triad Arpeggio (C Major)
    print("Generating win sequence...")
    sample_rate = 44100
    with wave.open(os.path.join(SFX_DIR, "win.wav"), 'w') as wav:
        wav.setnchannels(1) 
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        notes = [523.25, 659.25, 783.99, 1046.50] # C5, E5, G5, C6
        duration = 0.15
        
        for freq in notes:
            n_samples = int(sample_rate * duration)
            for i in range(n_samples):
                t = float(i) / sample_rate
                value = math.sin(2.0 * math.pi * freq * t)
                # Decay
                value *= (1.0 - (i / n_samples))
                data = struct.pack('<h', int(value * 0.5 * 32767.0))
                wav.writeframes(data)
    
    print("Done!")

if __name__ == "__main__":
    generate_assets()
