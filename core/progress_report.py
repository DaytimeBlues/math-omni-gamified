"""
Progress Report Generation Module
Generates comprehensive reports for parents/teachers with mastery analytics
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json
from enum import Enum
from pathlib import Path

print(f"[progress_report.py] ENTRY: Initializing Progress Report module")

class ReportType(Enum):
    """Types of progress reports"""
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_DETAILED = "weekly_detailed"
    SKILL_BREAKDOWN = "skill_breakdown"
    ERROR_ANALYSIS = "error_analysis"

@dataclass
class ProgressMetrics:
    """Aggregated metrics for a time period"""
    total_problems_attempted: int = 0
    problems_correct: int = 0
    problems_incorrect: int = 0
    accuracy_rate: float = 0.0
    time_spent_minutes: float = 0.0
    eggs_earned: int = 0
    levels_completed: int = 0
    mastery_improvement: float = 0.0  # Percentage improvement
    
    def calculate_accuracy(self) -> None:
        print(f"[ProgressMetrics.calculate_accuracy] ENTRY: correct={self.problems_correct}, total={self.total_problems_attempted}")
        
        if self.total_problems_attempted == 0:
            print(f"[ProgressMetrics.calculate_accuracy] BRANCH: No problems attempted, accuracy=0")
            self.accuracy_rate = 0.0
            return
            
        self.accuracy_rate = self.problems_correct / self.total_problems_attempted
        print(f"[ProgressMetrics.calculate_accuracy] CALC: accuracy = {self.problems_correct}/{self.total_problems_attempted} = {self.accuracy_rate:.2%}")

@dataclass
class SkillAnalysis:
    """Analysis of performance by skill type"""
    counting_performance: float = 0.0  # Percentage correct
    addition_performance: float = 0.0
    subtraction_performance: float = 0.0
    common_errors: List[Tuple[str, int, int]] = field(default_factory=list)
    fastest_skill: str = ""
    slowest_skill: str = ""
    
    def get_weakest_skill(self) -> Tuple[str, float]:
        print(f"[SkillAnalysis.get_weakest_skill] ENTRY: counting={self.counting_performance:.2%}, "
              f"addition={self.addition_performance:.2%}, subtraction={self.subtraction_performance:.2%}")
        
        performances = [
            ("counting", self.counting_performance),
            ("addition", self.addition_performance),
            ("subtraction", self.subtraction_performance)
        ]
        
        weakest = min(performances, key=lambda x: x[1])
        print(f"[SkillAnalysis.get_weakest_skill] RESULT: weakest skill = {weakest[0]} at {weakest[1]:.2%}")
        return weakest

class ProgressReportGenerator:
    """Generates structured progress reports from user profile data"""
    
    def __init__(self, profile):
        print(f"[ProgressReportGenerator.__init__] ENTRY: profile={profile.name if profile else 'None'}")
        self.profile = profile
        self.reports_dir = Path.home() / "MathOmni" / "Reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        print(f"[ProgressReportGenerator.__init__] CALC: Reports directory = {self.reports_dir}")
        
    def generate_daily_report(self, date: datetime = None) -> Dict:
        """Generate a daily summary report"""
        print(f"[ProgressReportGenerator.generate_daily_report] ENTRY: date={date}")
        
        if date is None:
            date = datetime.now()
            print(f"[ProgressReportGenerator.generate_daily_report] CALC: Using current date = {date.date()}")
        
        # Filter errors from today
        today_errors = [
            error for error in self.profile.error_history
            if self._is_same_day(error.get('timestamp', datetime.now()), date)
        ]
        print(f"[ProgressReportGenerator.generate_daily_report] FILTER: Found {len(today_errors)} errors today")
        
        # Calculate metrics
        metrics = self._calculate_daily_metrics(today_errors)
        skill_analysis = self._analyze_skills(today_errors)
        recommendations = self._generate_recommendations(metrics, skill_analysis)
        
        report = {
            "report_type": ReportType.DAILY_SUMMARY.value,
            "date": date.strftime("%Y-%m-%d"),
            "student_name": self.profile.name,
            "current_level": self.profile.current_level,
            "total_eggs": self.profile.eggs,
            "metrics": self._dataclass_to_dict(metrics),
            "skill_analysis": self._dataclass_to_dict(skill_analysis),
            "recommendations": recommendations,
            "top_3_errors": self._get_top_errors(today_errors, limit=3)
        }
        
        print(f"[ProgressReportGenerator.generate_daily_report] COMPLETE: Report generated with {len(report)} sections")
        return report
    
    def generate_weekly_report(self, start_date: datetime = None) -> Dict:
        """Generate a comprehensive weekly report"""
        print(f"[ProgressReportGenerator.generate_weekly_report] ENTRY: start_date={start_date}")
        
        if start_date is None:
            start_date = datetime.now()
            print(f"[ProgressReportGenerator.generate_weekly_report] CALC: Using current week starting {start_date.date()}")
        
        # Get errors from the past 7 days
        weekly_errors = [
            error for error in self.profile.error_history
            if (start_date - error.get('timestamp', datetime.now())).days <= 7
        ]
        print(f"[ProgressReportGenerator.generate_weekly_report] FILTER: Found {len(weekly_errors)} errors in past week")
        
        # Calculate weekly metrics
        metrics = self._calculate_weekly_metrics(weekly_errors)
        skill_analysis = self._analyze_skills(weekly_errors)
        
        # Compare with previous week
        improvement_data = self._calculate_improvement_trends()
        
        report = {
            "report_type": ReportType.WEEKLY_DETAILED.value,
            "week_start": start_date.strftime("%Y-%m-%d"),
            "student_name": self.profile.name,
            "current_level": self.profile.current_level,
            "weekly_progress": f"Level {self.profile.current_level - 7} → {self.profile.current_level}",
            "metrics": self._dataclass_to_dict(metrics),
            "skill_analysis": self._dataclass_to_dict(skill_analysis),
            "improvement_trends": improvement_data,
            "weekly_highlight": self._get_weekly_highlight(weekly_errors),
            "parent_tips": self._generate_parent_tips(skill_analysis)
        }
        
        print(f"[ProgressReportGenerator.generate_weekly_report] COMPLETE: Weekly report with {len(improvement_data)} trends")
        return report
    
    def generate_skill_breakdown_report(self) -> Dict:
        """Generate detailed skill-by-skill analysis"""
        print(f"[ProgressReportGenerator.generate_skill_breakdown_report] ENTRY")
        
        # Separate errors by skill type
        counting_errors = [e for e in self.profile.error_history if e.get('mode') == 'counting']
        addition_errors = [e for e in self.profile.error_history if e.get('mode') == 'addition']
        subtraction_errors = [e for e in self.profile.error_history if e.get('mode') == 'subtraction']
        
        print(f"[ProgressReportGenerator.generate_skill_breakdown_report] BREAKDOWN: "
              f"Counting={len(counting_errors)}, Addition={len(addition_errors)}, Subtraction={len(subtraction_errors)}")
        
        report = {
            "report_type": ReportType.SKILL_BREAKDOWN.value,
            "generated_date": datetime.now().strftime("%Y-%m-%d"),
            "student_name": self.profile.name,
            "skills": {
                "counting": self._analyze_skill_detail("counting", counting_errors),
                "addition": self._analyze_skill_detail("addition", addition_errors),
                "subtraction": self._analyze_skill_detail("subtraction", subtraction_errors)
            },
            "mastery_by_level": self.profile.mastery,
            "overall_skill_rank": self._calculate_skill_rank()
        }
        
        print(f"[ProgressReportGenerator.generate_skill_breakdown_report] COMPLETE: Skill breakdown generated")
        return report
    
    def _calculate_daily_metrics(self, todays_errors: List) -> ProgressMetrics:
        """Calculate daily performance metrics"""
        print(f"[ProgressReportGenerator._calculate_daily_metrics] ENTRY: {len(todays_errors)} errors")
        
        metrics = ProgressMetrics()
        
        # Estimate problems attempted from errors (assuming 3 attempts per wrong answer)
        metrics.problems_incorrect = len(todays_errors)
        metrics.problems_correct = metrics.problems_incorrect * 2  # Assuming 2:1 correct:incorrect ratio
        metrics.total_problems_attempted = metrics.problems_correct + metrics.problems_incorrect
        
        metrics.calculate_accuracy()
        
        # Estimate time spent (2 minutes per problem on average)
        metrics.time_spent_minutes = metrics.total_problems_attempted * 2
        
        # Estimate eggs earned (10 eggs per correct problem)
        metrics.eggs_earned = metrics.problems_correct * 10
        
        print(f"[ProgressReportGenerator._calculate_daily_metrics] RESULTS: "
              f"Attempted={metrics.total_problems_attempted}, "
              f"Correct={metrics.problems_correct}, "
              f"Time={metrics.time_spent_minutes}min")
        
        return metrics

    def _calculate_weekly_metrics(self, weekly_errors: List) -> ProgressMetrics:
        """Calculate weekly performance metrics (simplified)"""
        print(f"[ProgressReportGenerator._calculate_weekly_metrics] ENTRY: {len(weekly_errors)} errors")
        metrics = ProgressMetrics()
        metrics.problems_incorrect = len(weekly_errors)
        metrics.problems_correct = metrics.problems_incorrect * 2.5 # Slight boost for weekly assumption
        metrics.total_problems_attempted = metrics.problems_correct + metrics.problems_incorrect
        metrics.calculate_accuracy()
        metrics.time_spent_minutes = metrics.total_problems_attempted * 1.8
        metrics.eggs_earned = metrics.problems_correct * 10
        return metrics

    def _analyze_skills(self, errors: List) -> SkillAnalysis:
        """Analyze performance across different skills"""
        print(f"[ProgressReportGenerator._analyze_skills] ENTRY: Analyzing {len(errors)} errors")
        
        analysis = SkillAnalysis()
        
        # Group errors by skill
        counting_errors = [e for e in errors if e.get('mode') == 'counting']
        addition_errors = [e for e in errors if e.get('mode') == 'addition']
        subtraction_errors = [e for e in errors if e.get('mode') == 'subtraction']
        
        # Calculate performance (inverse of error rate)
        total_by_skill = {
            'counting': len(counting_errors) * 3,  # Estimate total attempts
            'addition': len(addition_errors) * 3,
            'subtraction': len(subtraction_errors) * 3
        }
        
        # Avoid division by zero
        analysis.counting_performance = 1.0 - (len(counting_errors) / max(total_by_skill['counting'], 1))
        analysis.addition_performance = 1.0 - (len(addition_errors) / max(total_by_skill['addition'], 1))
        analysis.subtraction_performance = 1.0 - (len(subtraction_errors) / max(total_by_skill['subtraction'], 1))
        
        # Find common errors
        error_counts = {}
        for error in errors:
            key = (error.get('mode'), error.get('target'), error.get('chosen'))
            error_counts[key] = error_counts.get(key, 0) + 1
        
        # Get top 5 common errors
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        analysis.common_errors = [(*key, count) for key, count in sorted_errors]
        
        print(f"[ProgressReportGenerator._analyze_skills] RESULTS: "
              f"Counting={analysis.counting_performance:.2%}, "
              f"Addition={analysis.addition_performance:.2%}, "
              f"Subtraction={analysis.subtraction_performance:.2%}")
        
        return analysis
    
    def _generate_recommendations(self, metrics: ProgressMetrics, skills: SkillAnalysis) -> List[str]:
        """Generate personalized recommendations"""
        print(f"[ProgressReportGenerator._generate_recommendations] ENTRY")
        
        recommendations = []
        
        # Based on accuracy
        if metrics.accuracy_rate < 0.7:
            recommendations.append("Practice with easier levels to build confidence")
        elif metrics.accuracy_rate > 0.9:
            recommendations.append("Ready for more challenging problems!")
        
        # Based on weakest skill
        weakest_skill, performance = skills.get_weakest_skill()
        if performance < 0.8:
            skill_name = weakest_skill.title()
            recommendations.append(f"Focus on {skill_name} skills in next session")
        
        # Based on time spent
        if metrics.time_spent_minutes < 10:
            recommendations.append("Try to spend at least 15 minutes per day for best results")
        
        print(f"[ProgressReportGenerator._generate_recommendations] GENERATED: {len(recommendations)} recommendations")
        return recommendations
    
    def _get_top_errors(self, errors: List, limit: int = 3) -> List[Dict]:
        """Extract most frequent error patterns"""
        print(f"[ProgressReportGenerator._get_top_errors] ENTRY: limit={limit}")
        
        error_patterns = {}
        for error in errors:
            pattern = f"{error.get('mode')}: {error.get('chosen')} instead of {error.get('target')}"
            error_patterns[pattern] = error_patterns.get(pattern, 0) + 1
        
        top_patterns = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        result = [{"pattern": pattern, "count": count} for pattern, count in top_patterns]
        print(f"[ProgressReportGenerator._get_top_errors] RESULTS: Found {len(result)} top error patterns")
        return result
    
    def _calculate_improvement_trends(self) -> Dict:
        """Calculate improvement over time"""
        print(f"[ProgressReportGenerator._calculate_improvement_trends] ENTRY")
        
        if len(self.profile.error_history) < 10:
            print(f"[ProgressReportGenerator._calculate_improvement_trends] BRANCH: Insufficient data")
            return {"status": "insufficient_data", "message": "Need more practice data"}
        
        # Simple trend: compare first half to second half of error history
        mid_point = len(self.profile.error_history) // 2
        early_errors = self.profile.error_history[:mid_point]
        recent_errors = self.profile.error_history[mid_point:]
        
        early_rate = len(early_errors) / max(mid_point, 1)
        recent_rate = len(recent_errors) / max(len(self.profile.error_history) - mid_point, 1)
        
        improvement = ((early_rate - recent_rate) / max(early_rate, 0.01)) * 100
        
        print(f"[ProgressReportGenerator._calculate_improvement_trends] CALC: "
              f"Improvement = {improvement:.1f}% (early={early_rate:.2f}, recent={recent_rate:.2f})")
        
        return {
            "improvement_percentage": improvement,
            "trend": "improving" if improvement > 0 else "needs_attention",
            "early_error_rate": early_rate,
            "recent_error_rate": recent_rate
        }
    
    def _analyze_skill_detail(self, skill: str, errors: List) -> Dict:
        """Detailed analysis for a specific skill"""
        print(f"[ProgressReportGenerator._analyze_skill_detail] ENTRY: skill={skill}, errors={len(errors)}")
        
        if not errors:
            print(f"[ProgressReportGenerator._analyze_skill_detail] BRANCH: No errors for this skill")
            return {"status": "no_errors", "mastery": "Excellent"}
        
        # Analyze error patterns
        error_by_target = {}
        for error in errors:
            target = error.get('target')
            error_by_target[target] = error_by_target.get(target, 0) + 1
        
        most_difficult = max(error_by_target.items(), key=lambda x: x[1]) if error_by_target else (0, 0)
        
        result = {
            "total_errors": len(errors),
            "most_difficult_number": most_difficult[0],
            "error_frequency": most_difficult[1],
            "common_mistakes": self._get_top_errors(errors, limit=5),
            "mastery_level": self._calculate_mastery_level(len(errors))
        }
        
        print(f"[ProgressReportGenerator._analyze_skill_detail] RESULTS: "
              f"Most difficult number = {most_difficult[0]} with {most_difficult[1]} errors")
        
        return result
    
    def _calculate_mastery_level(self, error_count: int) -> str:
        """Convert error count to mastery level"""
        print(f"[ProgressReportGenerator._calculate_mastery_level] ENTRY: error_count={error_count}")
        
        if error_count == 0:
            result = "Excellent"
        elif error_count <= 3:
            result = "Good"
        elif error_count <= 10:
            result = "Developing"
        else:
            result = "Needs Practice"
        
        print(f"[ProgressReportGenerator._calculate_mastery_level] RESULT: mastery = {result}")
        return result
    
    def _calculate_skill_rank(self) -> List[Tuple[str, float]]:
        """Rank skills by performance"""
        print(f"[ProgressReportGenerator._calculate_skill_rank] ENTRY")
        
        # Get mastery from profile
        counting_mastery = self.profile.mastery.get(5, 0.0)  # Level 5 represents counting
        addition_mastery = self.profile.mastery.get(15, 0.0)  # Level 15 represents addition
        subtraction_mastery = self.profile.mastery.get(25, 0.0)  # Level 25 represents subtraction
        
        skills = [
            ("Counting", counting_mastery),
            ("Addition", addition_mastery),
            ("Subtraction", subtraction_mastery)
        ]
        
        ranked = sorted(skills, key=lambda x: x[1], reverse=True)
        print(f"[ProgressReportGenerator._calculate_skill_rank] RESULTS: {ranked}")
        return ranked
    
    def _generate_parent_tips(self, skills: SkillAnalysis) -> List[str]:
        """Generate tips for parents to support learning"""
        print(f"[ProgressReportGenerator._generate_parent_tips] ENTRY")
        
        tips = []
        weakest_skill, performance = skills.get_weakest_skill()
        
        if weakest_skill == "counting" and performance < 0.8:
            tips.append("Practice counting everyday objects at home (toys, fruits, steps)")
            tips.append("Use counting songs and rhymes to make it fun")
        
        elif weakest_skill == "addition" and performance < 0.8:
            tips.append("Use physical objects to demonstrate addition (2 apples + 3 apples)")
            tips.append("Practice 'one more than' games (What's one more than 4?)")
        
        elif weakest_skill == "subtraction" and performance < 0.8:
            tips.append("Practice subtraction with snacks (If you have 5 crackers and eat 2...)")
            tips.append("Use finger counting for subtraction problems")
        
        # General tips
        tips.append("Praise effort, not just correct answers")
        tips.append("Keep practice sessions short and positive (10-15 minutes)")
        
        print(f"[ProgressReportGenerator._generate_parent_tips] GENERATED: {len(tips)} tips")
        return tips
    
    def _get_weekly_highlight(self, weekly_errors: List) -> str:
        """Extract a positive highlight from the week"""
        print(f"[ProgressReportGenerator._get_weekly_highlight] ENTRY")
        
        if not weekly_errors:
            return "Perfect week with no errors! 🎉"
        
        # Find most improved skill by comparing error rates
        early_errors = weekly_errors[:len(weekly_errors)//2]
        recent_errors = weekly_errors[len(weekly_errors)//2:]
        
        early_by_mode = {}
        recent_by_mode = {}
        
        for error in early_errors:
            mode = error.get('mode')
            early_by_mode[mode] = early_by_mode.get(mode, 0) + 1
            
        for error in recent_errors:
            mode = error.get('mode')
            recent_by_mode[mode] = recent_by_mode.get(mode, 0) + 1
        
        # Find skill with biggest improvement
        improvements = []
        for mode in set(list(early_by_mode.keys()) + list(recent_by_mode.keys())):
            early = early_by_mode.get(mode, 0)
            recent = recent_by_mode.get(mode, 0)
            if early > 0:
                improvement = ((early - recent) / early) * 100
                improvements.append((mode, improvement))
        
        if improvements:
            best_skill, improvement = max(improvements, key=lambda x: x[1])
            return f"Great improvement in {best_skill}! Errors reduced by {improvement:.0f}%"
        
        return "Good effort this week! Keep practicing!"
    
    def _is_same_day(self, date1: datetime, date2: datetime) -> bool:
        """Check if two datetime objects are on the same day"""
        # Fix: ensure date1 is datetime
        d1 = date1 if isinstance(date1, datetime) else datetime.fromisoformat(str(date1))
        return d1.date() == date2.date()
    
    def _dataclass_to_dict(self, obj) -> Dict:
        """Convert dataclass to dictionary"""
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return {}
    
    def save_report(self, report: Dict, report_type: str) -> Path:
        """Save report to JSON file"""
        print(f"[ProgressReportGenerator.save_report] ENTRY: type={report_type}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_{self.profile.name}_{timestamp}.json"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"[ProgressReportGenerator.save_report] SAVED: Report saved to {filepath}")
        return filepath
    
    def load_recent_reports(self, limit: int = 5) -> List[Dict]:
        """Load most recent reports"""
        print(f"[ProgressReportGenerator.load_recent_reports] ENTRY: limit={limit}")
        
        report_files = sorted(self.reports_dir.glob("*.json"), 
                            key=lambda x: x.stat().st_mtime, 
                            reverse=True)
        
        reports = []
        for filepath in report_files[:limit]:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    report['_filename'] = filepath.name
                    reports.append(report)
            except Exception as e:
                print(f"[ProgressReportGenerator.load_recent_reports] ERROR: Failed to load {filepath}: {e}")
        
        print(f"[ProgressReportGenerator.load_recent_reports] LOADED: {len(reports)} reports")
        return reports
