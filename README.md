# Year 1 Math App 🥚

A gamified math learning platform for Year 1 children (ages 5-6), aligned with Australian Curriculum (ACARA v9.0).

## Features

- 🎮 **Tap-based gameplay** - Large 80px+ touch targets for small hands
- 🧠 **Adaptive difficulty** - Progressive scaling from counting 1-3 to operations up to 20
- 🥚 **Egg economy** - Earn eggs for correct answers (persists via SQLite)
- 🔊 **Offline Voice Prompts** - Pre-recorded voice bank (no internet required)
- 🎨 **Accessibility-first** - Dyslexia-friendly fonts, high contrast, debounce protection

## Tech Stack

- **UI Framework:** PyQt6 + qasync
- **Database:** SQLite (aiosqlite)
- **Audio:** Offline voice bank (WAV/MP3)
- **Target Platform:** Windows

## Installation

```bash
git clone https://github.com/DaytimeBlues/Year_1_Math_app.git
cd Year_1_Math_app
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Architecture

```
main.py → GameManager → MapView / ActivityView
    ↓
DatabaseService + AudioService + ProblemFactory
    ↓
VoiceBank (offline audio) + Director (state machine)
```

## License

MIT - See [LICENSE](LICENSE) for details.
