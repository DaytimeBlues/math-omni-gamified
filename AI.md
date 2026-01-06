# AI.md - Institutional Memory for Year_1_Math

> **Update Protocol**: When a bug is discovered, fix the code AND add a rule here, then commit both together.

---

## Security Rules

| ID | Rule | Severity |
|----|------|----------|
| **S1** | Never use `pickle` for user data → Use JSON with `to_dict()`/`from_dict()` | CRITICAL |
| **S2** | Never use fixed temp filenames → Use `tempfile.NamedTemporaryFile()` | HIGH |
| **S3** | Never commit logs or hardcoded paths → Add to `.gitignore` | HIGH |

---

## Logic Rules

| ID | Rule | Context |
|----|------|---------|
| **L1** | `GameManager` owns answer validation, not Views | Views emit signals, GameManager processes |
| **L2** | `ProblemData.options` must always include the correct answer | Problem generation |
| **L3** | Use `profile.progress` dict, not non-existent `current_level` | Progress report generation |
| **L4** | Don't record errors to profile during practice mode | Prevents data pollution |
| **L5** | Don't overload signals with different types | Create separate signals for different purposes |
| **L6** | `_generate_distractors` returns `[target, d1, d2]` shuffled - don't add target again | Options generation |

---

## Concurrency Rules

| ID | Rule | Context |
|----|------|---------|
| **C1** | State guard required in `_process_answer` | Prevent double-processing |
| **C2** | File I/O must be async or offloaded to background thread | UI responsiveness |

---

## Framework Rules (PySide6)

| ID | Rule | Context |
|----|------|---------|
| **F1** | If PyQt6 DLL errors persist after reinstall, switch to PySide6 | Windows compatibility |
| **F2** | Migration: `PyQt6` → `PySide6`, `pyqtSignal` → `Signal` | Quick reference |
| **F3** | Always verify git remote URLs with `git remote -v` before documenting | Documentation accuracy |

---

## History

| Date | Rule Added | Trigger |
|------|------------|---------|
| 2026-01-05 | S1, L1-L3, C1 | Code review findings |
| 2026-01-06 | S2, S3, L4, L5, C2, F1-F3 | Deep code review + DLL migration |
