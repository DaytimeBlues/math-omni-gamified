# PROJECT.md - Math Omni Constitution

## What This Is
**Project:** Sidereal Voyager (Math Omni v2)  
**Goal:** Year 1 Math learning app for a 5-year-old, aligned with ACARA v9.0 Australian Curriculum.  
**Target User:** Primary school children (Foundation → Year 1)

---

## Tech Stack
- **UI Framework:** PyQt6 (desktop app, not web)
- **Async Bridge:** qasync (Qt + asyncio integration)
- **Database:** SQLite via aiosqlite
- **TTS:** VoiceBank (177 pre-recorded WAV clips) - NO dynamic TTS
- **Testing:** pytest with custom pytest_asyncio shim

---

## Architecture Decisions (Don't Change Without Discussion)

| Decision | Rationale |
|----------|-----------|
| **Local-First** | No cloud AI in the core game loop. All pedagogy logic runs locally. |
| **VoiceBank for TTS** | Pre-recorded clips are faster and more reliable than dynamic TTS. |
| **ServiceContainer DI** | Dependency injection for testability and decoupling. |
| **Fusion Qt Style** | Windows native style fights QSS. Fusion is consistent. |
| **Single Event Loop** | All async operations share one event loop per session. |

---

## Design Rules (Apply Always)

| Rule | Value |
|------|-------|
| Minimum touch target | 80px |
| Font family | Lexend (fallback: Segoe UI) |
| Background | Cream gradient (#FEF9E7 → #F5E6C8) |
| Hover animation | OutElastic easing |
| Transition animation | InExpo easing |
| Button corners | 25px border-radius |
| Shadows | Soft drop shadow (blur: 20px, offset: 8px) |

---

## Patterns to Follow

```python
# ✅ Async task creation
from core.utils import safe_create_task
safe_create_task(some_async_function())

# ✅ Logging (not print)
import logging
logger = logging.getLogger(__name__)
logger.info("Message here")

# ✅ Async fixtures in tests
@pytest.fixture
async def db():
    await service.initialize()
    yield service
    await service.close()

# ✅ Child-safe error dialogs (ChatGPT 5.2)
from main import show_oops
show_oops(window, "Something went wrong.", retry_coro=init_async)

# ✅ Database write serialization (ChatGPT 5.2)
async with self._write_lock:
    await self._retry_locked(write_operation)
```

---

## Mistakes We've Made (Don't Repeat)

| Mistake | What Went Wrong | Correct Approach |
|---------|-----------------|------------------|
| `asyncio.run()` in fixtures | Creates new event loop each call, breaks connection state | Use shared `event_loop` fixture |
| Mixing sync/async in PyQt6 | Crashes without qasync bridge | Always use qasync, never raw asyncio in UI code |
| Cloud AI (Gemini Tutor) in core loop | Violated local-first principle | Removed by design decision |
| Print statements for debugging | Not captured in log files | Use `logger.info()` for all output |
| Hardcoded 5s sleep for audio | Clips have variable duration | Use `mutagen` or WAV header for duration |
| `safe_create_task` for cleanup | Loop closes before DB finishes | Use `loop.run_until_complete(cleanup())` |
| Unvalidated mode strings | Could accept any string, causing KeyError | Use `VALID_MODES` set for validation |
| No timeout on DB operations | Could hang forever | Use `asyncio.wait_for(fn(), timeout=10.0)` |

---

## File Structure (Key Locations)

```
sidereal-voyager/
├── main.py                 # Entry point (orchestration only)
├── config.py               # All constants and settings
├── PROJECT.md              # This file (constitution)
├── core/
│   ├── database.py         # SQLite service
│   ├── voice_bank.py       # TTS phrase management
│   ├── audio_service.py    # SFX and music
│   ├── problem_factory.py  # Problem generation
│   └── user_profile.py     # Student progress
├── ui/
│   ├── game_manager.py     # Main controller/coordinator
│   ├── landing_page_view.py # Curriculum hub
│   ├── premium_activity_view.py # Problem-solving screen
│   └── design_tokens.py    # Colors, fonts, gradients
└── tests/
    └── test_database.py    # Database tests
```

---

## LLM Council Protocol

When consulting external LLMs (DeepSeek, Z.ai, ChatGPT, Codex, Gemini):

1. **One prompt at a time** - Never run parallel prompts that touch the same files
2. **Describe the codebase first** - Share this PROJECT.md as context
3. **Ask for review, not rewrites** - Request specific improvements, not full file replacements
4. **Integrate manually** - Copy specific fixes, don't paste entire files
5. **Update Tribal Knowledge** - If an LLM finds a bug pattern, add it above

---

## Current Phase
**Phase 4:** Year 1 Curriculum Landing Page (Complete)  
**Next:** Testing & Polish

---

*Last Updated: 2026-01-05*
