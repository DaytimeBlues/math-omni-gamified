"""
Scratchpad Canvas - PyQt6 Implementation with Native Stylus Support
The child's drawing workspace with Windows Ink integration.

PEDAGOGICAL PURPOSE:
The scratchpad is the child's "thinking space." It simulates paper where
they can work out problems using their natural drawing instincts. Unlike
multiple-choice tests that only reveal final answers, the scratchpad
captures the PROCESS of mathematical thinking.

TECHNICAL ADVANTAGE OF PyQt6:
QTabletEvent provides native access to stylus pressure, tilt, and precise
positioning—critical for palm rejection and a natural drawing experience
on the HP Omni.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor, QPainterPath, QTabletEvent
from dataclasses import dataclass, field
from typing import List, Optional
import sys
sys.path.append('..')
from config import COLORS, TIMING


@dataclass
class Stroke:
    """
    Represents a single continuous drawing stroke.
    
    WHAT IS A STROKE?
    A stroke begins when the stylus touches the screen and ends when lifted.
    This allows us to count discrete marks (e.g., tally counting).
    
    Five strokes = 5 (valid concrete representation in CPA framework)
    """
    points: List[QPointF] = field(default_factory=list)
    pressures: List[float] = field(default_factory=list)  # Stylus pressure data
    
    def add_point(self, point: QPointF, pressure: float = 1.0):
        """Add a point to this stroke's path."""
        self.points.append(point)
        self.pressures.append(pressure)
    
    @property
    def is_valid(self) -> bool:
        """A stroke needs at least 2 points to be meaningful."""
        return len(self.points) >= 2
    
    @property
    def bounding_width(self) -> float:
        """Width of the stroke's bounding box."""
        if not self.points:
            return 0
        xs = [p.x() for p in self.points]
        return max(xs) - min(xs)
    
    @property
    def bounding_height(self) -> float:
        """Height of the stroke's bounding box."""
        if not self.points:
            return 0
        ys = [p.y() for p in self.points]
        return max(ys) - min(ys)
    
    @property
    def is_dot(self) -> bool:
        """
        Is this stroke a small dot/tap?
        
        PEDAGOGICAL USE:
        Children often tap dots for counting instead of drawing lines.
        "• • • • •" is just as valid as "|||||" for representing 5.
        """
        return self.bounding_width < 30 and self.bounding_height < 30
    
    @property
    def is_tally(self) -> bool:
        """
        Is this stroke a tally mark (narrow but tall)?
        
        PEDAGOGICAL USE:
        Tally marks are natural counting representations for children.
        """
        return self.bounding_width < 50 and self.bounding_height > 40


class Scratchpad(QWidget):
    """
    A touch/stylus drawing canvas for mathematical thinking.
    
    DESIGN FOR SMALL HANDS:
    - Full widget area responds to touch
    - Thick stroke lines are visible and satisfying
    - No fiddly controls in the drawing area
    
    SIGNALS:
    - stroke_completed: Emitted when a stroke is finished (for effort detection)
    - idle_timeout: Emitted when no activity for configured duration
    """
    
    stroke_completed = pyqtSignal()  # Notify parent when drawing occurs
    idle_timeout = pyqtSignal()      # Notify parent when child pauses too long
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Track all strokes for analysis
        self.strokes: List[Stroke] = []
        self.current_stroke: Optional[Stroke] = None
        
        # Idle detection timer (triggers scaffolding)
        self.idle_timer = QTimer()
        self.idle_timer.setSingleShot(True)
        self.idle_timer.timeout.connect(self._on_idle)
        
        # Configure widget for drawing
        self.setMinimumSize(600, 400)
        self.setStyleSheet(f"background-color: {COLORS['canvas']};")
        
        # Enable tablet/stylus events
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
    
    # =========================================================================
    # STYLUS/TABLET EVENTS - Native Windows Ink Support
    # =========================================================================
    
    def tabletEvent(self, event: QTabletEvent):
        """
        Handle native stylus input from HP Omni pen.
        
        ADVANTAGE OVER MOUSE EVENTS:
        - Pressure sensitivity for natural line weight
        - Precise positioning (subpixel accuracy)
        - Palm rejection handled by the OS
        - Tilt detection (future use for angled strokes)
        """
        pos = event.position()
        pressure = event.pressure()  # 0.0 to 1.0
        
        if event.type() == event.Type.TabletPress:
            self._begin_stroke(pos, pressure)
            event.accept()
            
        elif event.type() == event.Type.TabletMove:
            self._continue_stroke(pos, pressure)
            event.accept()
            
        elif event.type() == event.Type.TabletRelease:
            self._end_stroke()
            event.accept()
    
    # =========================================================================
    # MOUSE EVENTS - Fallback for touch/testing
    # =========================================================================
    
    def mousePressEvent(self, event):
        """Fallback for mouse/touch when stylus not used."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._begin_stroke(QPointF(event.pos()), 1.0)
    
    def mouseMoveEvent(self, event):
        """Continue stroke on mouse drag."""
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._continue_stroke(QPointF(event.pos()), 1.0)
    
    def mouseReleaseEvent(self, event):
        """End stroke on mouse release."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._end_stroke()
    
    # =========================================================================
    # STROKE MANAGEMENT
    # =========================================================================
    
    def _begin_stroke(self, pos: QPointF, pressure: float):
        """
        Called when stylus/finger touches the screen.
        
        PEDAGOGICAL MOMENT:
        This is when the child commits to responding. We cancel the idle
        timer since they're actively engaged.
        """
        self.idle_timer.stop()
        self.current_stroke = Stroke()
        self.current_stroke.add_point(pos, pressure)
        self.update()
    
    def _continue_stroke(self, pos: QPointF, pressure: float):
        """
        Called as stylus/finger moves across the screen.
        
        RESPONSIVE FEEDBACK:
        We update immediately—any perceptible lag frustrates children
        who expect instant response (like crayons on paper).
        """
        if self.current_stroke:
            self.current_stroke.add_point(pos, pressure)
            self.update()
    
    def _end_stroke(self):
        """
        Called when stylus/finger lifts from the screen.
        
        PEDAGOGICAL MILESTONE:
        Each completed stroke is a discrete thinking artifact.
        """
        if self.current_stroke and self.current_stroke.is_valid:
            self.strokes.append(self.current_stroke)
            self.stroke_completed.emit()  # Notify parent for effort acknowledgment
        
        self.current_stroke = None
        self.update()
        
        # Start idle timer (will prompt child if no more activity)
        self._start_idle_timer()
    
    def _start_idle_timer(self):
        """
        Start timer to detect if child becomes stuck.
        
        SCAFFOLDING TRIGGER:
        If no activity within timeout, we assume the child might need help.
        """
        idle_ms = int(TIMING['idle_prompt_seconds'] * 1000)
        self.idle_timer.start(idle_ms)
    
    def _on_idle(self):
        """Called when child hasn't interacted for timeout duration."""
        self.idle_timeout.emit()
    
    # =========================================================================
    # PAINTING
    # =========================================================================
    
    def paintEvent(self, event):
        """
        Draw all strokes on the canvas.
        
        VISUAL DESIGN:
        - Thick lines (6px) for visibility and child satisfaction
        - Round caps/joins for natural, marker-like appearance
        - Dark purple-blue color for high contrast on white
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create pen for drawing strokes
        pen = QPen(QColor(COLORS['stroke']))
        pen.setWidth(6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        # Draw all completed strokes
        for stroke in self.strokes:
            if len(stroke.points) >= 2:
                path = QPainterPath()
                path.moveTo(stroke.points[0])
                for point in stroke.points[1:]:
                    path.lineTo(point)
                painter.drawPath(path)
        
        # Draw current in-progress stroke
        if self.current_stroke and len(self.current_stroke.points) >= 2:
            path = QPainterPath()
            path.moveTo(self.current_stroke.points[0])
            for point in self.current_stroke.points[1:]:
                path.lineTo(point)
            painter.drawPath(path)
    
    # =========================================================================
    # PUBLIC INTERFACE FOR ANSWER CHECKING
    # =========================================================================
    
    @property
    def stroke_count(self) -> int:
        """
        Returns the number of discrete strokes drawn.
        
        PRIMARY HEURISTIC:
        For counting problems, the number of strokes often = the child's answer.
        Drawing 5 lines means the child is representing "5".
        """
        return len(self.strokes)
    
    def get_quantity(self) -> int:
        """
        Interpret the drawing as a quantity.
        
        INTERPRETATION RULES:
        1. Count individual tally marks (lines)
        2. Count dots
        3. Fall back to total stroke count
        
        All representations show valid conceptual understanding.
        """
        tallies = sum(1 for s in self.strokes if s.is_tally)
        if tallies > 0:
            return tallies
        
        dots = sum(1 for s in self.strokes if s.is_dot)
        if dots > 0:
            return dots
        
        return len(self.strokes)
    
    def has_content(self) -> bool:
        """Check if the child has drawn anything."""
        return len(self.strokes) > 0
    
    def clear(self):
        """
        Clear all drawings from the canvas.
        
        Called when moving to a new problem or when child requests a reset.
        """
        self.strokes = []
        self.current_stroke = None
        self.idle_timer.stop()
        self.update()
