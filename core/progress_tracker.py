"""
Progress Tracker - JSON-based Session Persistence
Saves learning progress so parents can see growth over time.

PARENT VALUE:
"Show me how she did yesterday vs. today" is the #1 feature
request from parents. This simple JSON file provides that.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class SessionRecord:
    """A single learning session record."""
    date: str
    duration_minutes: float
    problems_attempted: int
    problems_correct: int
    module: str = "counting"
    
    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage."""
        if self.problems_attempted == 0:
            return 0.0
        return (self.problems_correct / self.problems_attempted) * 100


class ProgressTracker:
    """
    Tracks and persists learning progress to JSON.
    
    FILE LOCATION:
    Saved to user's home directory to persist across app updates.
    """
    
    def __init__(self, save_dir: Optional[str] = None):
        """
        Initialize the progress tracker.
        
        Args:
            save_dir: Directory to save progress file. 
                      Defaults to user's home directory.
        """
        if save_dir is None:
            save_dir = os.path.expanduser("~")
        
        self.save_path = os.path.join(save_dir, "math_omni_progress.json")
        self.history: List[Dict] = []
        
        # Current session tracking
        self._session_start = None
        self._problems_attempted = 0
        self._problems_correct = 0
        self._current_module = "counting"
        
        # Load existing progress
        self._load()
    
    def _load(self):
        """Load progress from JSON file."""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as f:
                    self.history = json.load(f)
                print(f"[ProgressTracker] Loaded {len(self.history)} sessions")
        except Exception as e:
            print(f"[ProgressTracker] Could not load progress: {e}")
            self.history = []
    
    def _save(self):
        """Save progress to JSON file."""
        try:
            with open(self.save_path, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"[ProgressTracker] Could not save progress: {e}")
    
    def start_session(self, module: str = "counting"):
        """
        Start a new learning session.
        
        Called when the app launches or a new module begins.
        """
        self._session_start = datetime.now()
        self._problems_attempted = 0
        self._problems_correct = 0
        self._current_module = module
    
    def record_attempt(self, correct: bool):
        """
        Record a problem attempt.
        
        Args:
            correct: Whether the answer was correct.
        """
        self._problems_attempted += 1
        if correct:
            self._problems_correct += 1
    
    def end_session(self):
        """
        End the current session and save to file.
        
        Called when the app closes.
        """
        if self._session_start is None:
            return
        
        duration = (datetime.now() - self._session_start).total_seconds() / 60
        
        record = SessionRecord(
            date=self._session_start.strftime("%Y-%m-%d %H:%M"),
            duration_minutes=round(duration, 1),
            problems_attempted=self._problems_attempted,
            problems_correct=self._problems_correct,
            module=self._current_module
        )
        
        self.history.append(asdict(record))
        self._save()
        
        print(f"[ProgressTracker] Session saved: {self._problems_correct}/{self._problems_attempted} correct")
    
    def get_stats(self) -> Dict:
        """
        Get summary statistics for parent dashboard.
        
        Returns:
            Dict with total sessions, problems, accuracy, streak, etc.
        """
        if not self.history:
            return {
                "total_sessions": 0,
                "total_problems": 0,
                "total_correct": 0,
                "overall_accuracy": 0,
                "total_minutes": 0,
            }
        
        total_problems = sum(s.get("problems_attempted", 0) for s in self.history)
        total_correct = sum(s.get("problems_correct", 0) for s in self.history)
        total_minutes = sum(s.get("duration_minutes", 0) for s in self.history)
        
        return {
            "total_sessions": len(self.history),
            "total_problems": total_problems,
            "total_correct": total_correct,
            "overall_accuracy": round((total_correct / total_problems * 100) if total_problems > 0 else 0, 1),
            "total_minutes": round(total_minutes, 1),
        }
    
    def get_recent_sessions(self, count: int = 5) -> List[Dict]:
        """Get the most recent sessions."""
        return self.history[-count:]
