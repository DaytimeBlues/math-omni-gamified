# Math Omni - Foundation Year Learning App

A mathematics learning application for Foundation Year (Prep) students in Australia, designed for the HP Omni with touch/stylus support.

## Features

- **PyQt6 Native UI** with Windows Ink support for HP Omni stylus
- **Heuristic Stroke Analysis** - accepts tally marks (|||||) as valid answers
- **Growth Mindset Feedback** - never says "wrong", uses gentle redirects
- **Scaffolding System** - offers help when child pauses or struggles
- **Text-to-Speech** - voice feedback from pedagogical agent

## Curriculum Alignment (ACARA)

| Module | Code | Description |
|--------|------|-------------|
| Counting | ACMNA001 | Counting sequences 1-20 |
| Subitising | ACMNA002 | Instant recognition of small quantities |
| Number Match | ACMNA003 | Connect numerals to quantities |
| Addition | ACMNA004 | Simple addition using counting |
| Measurement | ACMMG006 | Direct/indirect comparison |

## Installation

```bash
# Clone the repository
git clone https://github.com/YourUsername/math-omni-foundation.git
cd math-omni-foundation

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

## Requirements

- Python 3.10+
- Windows (for HP Omni stylus support)
- PyQt6
- pyttsx3 (offline text-to-speech)

## Project Structure

```
math-omni-foundation/
├── main.py              # Application entry point
├── config.py            # Tunable parameters & feedback bank
├── requirements.txt     # Dependencies
├── core/
│   └── agent.py         # TTS + Growth mindset feedback
└── ui/
    ├── main_window.py   # Split-screen layout
    └── scratchpad.py    # Touch/stylus canvas
```

## Pedagogical Philosophy

This app uses the **Concrete-Pictorial-Abstract (CPA)** framework:
1. **Concrete**: Digital manipulatives on screen
2. **Pictorial**: Visual representations
3. **Abstract**: Numerals only after conceptual understanding

Based on Carol Dweck's **Growth Mindset** research - we praise effort, not intelligence.

## License

MIT
