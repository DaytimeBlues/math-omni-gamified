"""
User Profile & Persistence

Tracks student progress, error history, and mastery levels.
Used by the adaptive difficulty system to personalize content.

DeepSeek Security Fixes Applied:
- Atomic writes (temp file + os.replace)
- Automatic backup before overwrite
- Specific exception handling
"""

import pickle
import os
import shutil
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Profile storage path
PROFILE_DIR = Path(__file__).parent.parent
PROFILE_PATH = PROFILE_DIR / "user_profile.pkl"
BACKUP_DIR = PROFILE_DIR / "backups"


@dataclass
class ErrorRecord:
    """Record of a specific error."""
    target: int
    chosen: int
    timestamp: datetime
    problem_type: str  # "addition", "subtraction"


@dataclass
class StudentProfile:
    """
    Persistent student data.
    """
    name: str = "Student"
    eggs: int = 0
    
    # Mastery scores (0.0 to 1.0) per world/skill
    mastery: Dict[str, float] = field(default_factory=dict)
    
    # Error history for adaptive distractors
    # key: problem_type, value: list of ErrorRecord
    errors: Dict[str, List[ErrorRecord]] = field(default_factory=lambda: {"addition": [], "subtraction": [], "counting": []})
    
    # Unlocked levels (highest level completed)
    progress: Dict[str, int] = field(default_factory=lambda: {"W1": 1, "W2": 1, "W3": 1})

    def record_error(self, target: int, chosen: int, problem_type: str):
        """Log a mistake to inform future distractors."""
        if problem_type not in self.errors:
            self.errors[problem_type] = []
        
        self.errors[problem_type].append(ErrorRecord(
            target=target,
            chosen=chosen,
            timestamp=datetime.now(),
            problem_type=problem_type
        ))
        
        # Cap history at 100 items per type to prevent bloat
        if len(self.errors[problem_type]) > 100:
            self.errors[problem_type] = self.errors[problem_type][-100:]

    def get_frequent_errors(self, problem_type: str, limit: int = 3) -> List[int]:
        """Return the most frequent wrong answers (for this type)."""
        if problem_type not in self.errors:
            return []
            
        # Simple frequency count
        counts = {}
        for record in self.errors[problem_type]:
            counts[record.chosen] = counts.get(record.chosen, 0) + 1
            
        # Sort by frequency
        sorted_errors = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [err[0] for err in sorted_errors[:limit]]

    def save(self) -> bool:
        """
        Save profile to disk using atomic write pattern.
        
        DeepSeek Security Fix:
        1. Write to temp file first
        2. Create backup of existing file
        3. Atomic rename (os.replace)
        
        Returns True on success, False on failure.
        """
        temp_path = PROFILE_PATH.with_suffix('.pkl.tmp')
        
        try:
            # 1. Write to temporary file
            with open(temp_path, 'wb') as f:
                pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # 2. Create backup if main file exists
            if PROFILE_PATH.exists():
                self._create_backup()
            
            # 3. Atomic replace (safe even on crash)
            os.replace(temp_path, PROFILE_PATH)
            print(f"[Profile] Saved successfully to {PROFILE_PATH}")
            return True
            
        except (pickle.PickleError, OSError) as e:
            print(f"[Profile] CRITICAL: Save failed - {e}")
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            return False
    
    def _create_backup(self):
        """Create a dated backup of the current profile."""
        try:
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = BACKUP_DIR / f"user_profile_{timestamp}.pkl"
            shutil.copy2(PROFILE_PATH, backup_path)
            
            # Keep only last 5 backups
            backups = sorted(BACKUP_DIR.glob("user_profile_*.pkl"))
            for old_backup in backups[:-5]:
                old_backup.unlink()
        except OSError as e:
            print(f"[Profile] Backup warning: {e}")

    @classmethod
    def load(cls) -> 'StudentProfile':
        """Load profile from disk or create new."""
        if PROFILE_PATH.exists():
            try:
                with open(PROFILE_PATH, 'rb') as f:
                    return pickle.load(f)
            except (pickle.UnpicklingError, EOFError) as e:
                print(f"[Profile] Corrupted file, attempting backup recovery: {e}")
                return cls._recover_from_backup()
            except Exception as e:
                print(f"[Profile] Load failed, creating new: {e}")
        return cls()
    
    @classmethod
    def _recover_from_backup(cls) -> 'StudentProfile':
        """Attempt to recover from most recent backup."""
        if not BACKUP_DIR.exists():
            return cls()
        
        backups = sorted(BACKUP_DIR.glob("user_profile_*.pkl"), reverse=True)
        for backup in backups:
            try:
                with open(backup, 'rb') as f:
                    print(f"[Profile] Recovered from backup: {backup.name}")
                    return pickle.load(f)
            except Exception:
                continue
        
        print("[Profile] No valid backups found, starting fresh")
        return cls()
