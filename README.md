# Math Omni - Foundation Year Learning App

A mathematics learning application for Foundation Year (Prep) students in Australia, designed for the HP Omni with touch/stylus support.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/DaytimeBlues/math-omni-foundation.git
cd math-omni-foundation

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

## 🖊️ HP Omni Setup Instructions

Before running the app on your HP Omni, verify these settings:

### 1. Check Windows Pen Service
```
Services → "Tablet PC Input Service" → Running
```

### 2. Test Stylus First
Open Windows **Paint** and draw. If the pen works there, it will work in Math Omni.

### 3. Pen Button Configuration
The barrel button (side button) activates "Help Mode":
- **Settings → Devices → Pen & Windows Ink**
- Ensure "Use your pen as a mouse" is enabled

### 4. Full-Screen Toggle
- Press **F11** to toggle full-screen mode
- Press **Escape** to exit the app

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **Stroke Counting** | Draws 5 lines = answer is 5 |
| **Growth Mindset** | Never says "wrong", uses gentle redirects |
| **Voice Feedback** | Text-to-speech encouragement |
| **Progress Tracking** | Saves sessions to `~/math_omni_progress.json` |
| **Cloud AI** | Optional Gemini 2.0 for contextual hints |

## 🔑 Optional: Gemini AI Integration

For cloud-powered scaffolding (when child is confused):

```bash
# Set API key before running
set GEMINI_API_KEY=your_api_key_here
python main.py
```

The app works **fully offline** without the API key.

## 📊 Progress Data

Learning progress is saved to:
```
C:\Users\<username>\math_omni_progress.json
```

Example data:
```json
{
  "date": "2024-12-28 19:30",
  "duration_minutes": 15.5,
  "problems_attempted": 12,
  "problems_correct": 9,
  "module": "counting"
}
```

## 🎓 Curriculum Alignment (ACARA)

| Module | Code | Description |
|--------|------|-------------|
| Counting | ACMNA001 | Counting sequences 1-20 |
| Subitising | ACMNA002 | Instant recognition of small quantities |
| Number Match | ACMNA003 | Connect numerals to quantities |

## 📁 Project Structure

```
math-omni-foundation/
├── main.py              # Application entry point
├── config.py            # Tunable parameters
├── requirements.txt     # Dependencies
├── assets/              # Sound effects
├── core/
│   ├── agent.py         # TTS + Growth mindset feedback
│   ├── gemini_tutor.py  # Cloud AI integration
│   └── progress_tracker.py  # JSON persistence
└── ui/
    ├── main_window.py   # Split-screen layout
    ├── scratchpad.py    # Touch/stylus canvas
    └── celebration.py   # Star animation on success
```

## 📝 Troubleshooting

| Problem | Solution |
|---------|----------|
| Pen not working | Check Windows Tablet PC Input Service |
| No sound | Ensure Windows volume is up, speakers connected |
| App crashes on start | Run `pip install -r requirements.txt` again |
| Cloud hints not working | Set `GEMINI_API_KEY` environment variable |

## License

MIT
