"""
Gemini 2.5 Pro TTS Generator

Generates high-quality TTS audio files from the voice_bank.yaml phrase list.
Uses Google's Gemini 2.5 Pro for natural, warm speech.

Usage:
    python generate_voice_bank.py

Prerequisites:
    pip install google-genai
    export GOOGLE_API_KEY=your_key_here
"""

import os
import yaml
import asyncio
import hashlib
from pathlib import Path

# Check for Google GenAI
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google-genai not installed. Run: pip install google-genai")


# Paths
SCRIPT_DIR = Path(__file__).parent
VOICE_BANK_YAML = SCRIPT_DIR / "assets" / "voice_bank.yaml"
OUTPUT_DIR = SCRIPT_DIR / "assets" / "audio" / "voice_bank"

# TTS Configuration
VOICE_NAME = "Aoede"  # Warm female voice for Gemini TTS
SAMPLE_RATE = 24000


def load_phrases() -> dict:
    """Load phrases from YAML file."""
    with open(VOICE_BANK_YAML, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def phrase_to_filename(category: str, index: int, text: str) -> str:
    """Generate a consistent filename for a phrase."""
    # Create short hash for uniqueness
    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    # Clean category name
    clean_cat = category.replace("_", "-")
    return f"{clean_cat}_{index:02d}_{text_hash}.mp3"


async def generate_audio_gemini(text: str, output_path: Path) -> bool:
    """
    Generate audio using Gemini 2.5 Pro TTS.
    
    Returns True if successful, False otherwise.
    """
    if not GENAI_AVAILABLE:
        print(f"[SKIP] google-genai not available: {text[:40]}...")
        return False
    
    try:
        client = genai.Client()
        
        # Use Gemini TTS endpoint
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=text,
            config=genai.types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=genai.types.SpeechConfig(
                    voice_config=genai.types.VoiceConfig(
                        prebuilt_voice_config=genai.types.PrebuiltVoiceConfig(
                            voice_name=VOICE_NAME,
                        )
                    )
                ),
            ),
        )
        
        # Save audio data
        audio_data = response.candidates[0].content.parts[0].inline_data.data
        with open(output_path, "wb") as f:
            f.write(audio_data)
        
        print(f"[OK] {output_path.name}")
        return True
        
    except Exception as e:
        print(f"[ERROR] {text[:30]}... - {e}")
        return False


async def generate_all_phrases():
    """Generate all TTS audio files from voice bank."""
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load phrases
    phrases = load_phrases()
    
    total = 0
    success = 0
    
    for category, phrase_list in phrases.items():
        if not isinstance(phrase_list, list):
            continue
            
        print(f"\n=== {category.upper()} ({len(phrase_list)} phrases) ===")
        
        for i, text in enumerate(phrase_list, start=1):
            filename = phrase_to_filename(category, i, text)
            output_path = OUTPUT_DIR / filename
            
            # Skip if already exists
            if output_path.exists():
                print(f"[SKIP] Already exists: {filename}")
                total += 1
                success += 1
                continue
            
            total += 1
            if await generate_audio_gemini(text, output_path):
                success += 1
            
            # Rate limiting
            await asyncio.sleep(0.5)
    
    print(f"\n=== COMPLETE ===")
    print(f"Total: {total}, Success: {success}, Failed: {total - success}")


def main():
    """Entry point."""
    if not GENAI_AVAILABLE:
        print("ERROR: Please install google-genai: pip install google-genai")
        print("Then set GOOGLE_API_KEY environment variable")
        return
    
    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: Please set GOOGLE_API_KEY environment variable")
        return
    
    print("=== Gemini 2.5 Pro TTS Voice Bank Generator ===")
    print(f"Input: {VOICE_BANK_YAML}")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    asyncio.run(generate_all_phrases())


if __name__ == "__main__":
    main()
