"""Enhanced Knowledge Base for fast pattern matching without AI.

This knowledge base learns from patterns and provides instant detection
for common Kaggle notebook states, making analysis much faster.
"""
import re
import json
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime

class KaggleKnowledgeBase:
    """
    Enhanced knowledge base with comprehensive pattern matching.
    
    Features:
    - 100+ detection patterns
    - Learning from past analyses
    - Confidence scoring
    - Metric extraction
    - Pattern statistics
    """
    
    def __init__(self):
        """Initialize knowledge base with comprehensive patterns."""
        self.stats_file = Path(__file__).parent.parent / 'kb_stats.json'
        self.load_stats()
    
    # ==================== EMPTY STATE PATTERNS ====================
    EMPTY_PATTERNS = [
        # UI indicators
        r"no\s+input\s+attached",
        r"no\s+sections?\s+detected",
        r"no\s+sections?\s+selected",
        r"no\s+output\s+available",
        r"no\s+data\s+attached",
        r"attach\s+a\s+kaggle\s+dataset",
        r"draft\s+session",
        r"empty\s+notebook",
        r"notebook\s+is\s+empty",
        
        # Execution indicators
        r"not\s+executed",
        r"has\s+not\s+been\s+run",
        r"code\s+has\s+not\s+been\s+executed",
        r"no\s+execution\s+output",
        r"no\s+cell\s+output",
        r"cells?\s+not\s+run",
        
        # Visual indicators
        r"green\s+play\s+button",
        r"run\s+button\s+visible",
        r"no\s+\[\d+\]",  # No [1], [2] execution numbers
        r"no\s+execution\s+count",
        
        # Panel indicators
        r"right\s+panel\s+empty",
        r"sidebar\s+empty",
        r"no\s+files\s+generated",
        r"no\s+output\s+files",
    ]
    
    # ==================== RUNNING STATE PATTERNS ====================
    RUNNING_PATTERNS = [
        # Progress indicators
        r"epoch\s+(\d+)/(\d+)",  # Epoch 3/10
        r"\[(\d+)/(\d+)\]",  # [37/100]
        r"step\s+(\d+)/(\d+)",  # Step 50/100
        r"batch\s+(\d+)/(\d+)",  # Batch 37/100
        r"iteration\s+(\d+)/(\d+)",  # Iteration 450/1500
        
        # Percentage indicators
        r"(\d+)%\s*\|",  # 37% |
        r"(\d+)%\s+complete",  # 37% complete
        r"progress:\s*(\d+)%",  # Progress: 37%
        
        # Time indicators
        r"<\s*\d+:\d+",  # < 44:23 (time remaining)
        r"eta:\s*\d+:\d+",  # ETA: 44:23
        r"remaining:\s*\d+:\d+",  # Remaining: 44:23
        r"\d+:\d+<\d+:\d+",  # 15:30<44:23
        
        # Speed indicators
        r"\d+\.\d+\s*it/s",  # 0.02 it/s
        r"\d+\.\d+s/it",  # 2.5s/it
        r"\d+\.\d+\s*samples?/s",  # 45.2 samples/s
        r"\d+\.\d+\s*steps?/s",  # 1.5 steps/s
        
        # Status text
        r"running|executing|training\.\.\.",
        r"in\s+progress",
        r"currently\s+training",
        r"processing\.\.\.",
        
        # Training metrics (active)
        r"loss:\s*\d+\.\d+.*accuracy:\s*\d+\.\d+",
        r"train_loss:\s*\d+\.\d+",
        r"learning_rate:\s*\d+\.\d+e?-?\d*",
        r"lr:\s*\d+\.\d+e?-?\d*",
        
        # GPU/Memory indicators
        r"gpu\s+\d+%",
        r"memory:\s*\d+\.\d+\s*gb",
        r"cuda:\s*\d+",
        
        # Framework-specific
        r"tensorflow.*training",
        r"pytorch.*training",
        r"keras.*training",
        r"fit.*epoch",
        r"train_on_batch",
    ]
    
    # ==================== COMPLETE STATE PATTERNS ====================
    COMPLETE_PATTERNS = [
        # Completion text
        r"complete!|finished!|done!",
        r"training\s+complete",
        r"evaluation\s+complete",
        r"execution\s+complete",
        r"successfully\s+completed",
        r"all\s+done",
        
        # Model saving
        r"saved\s+model\s+to",
        r"model\s+saved",
        r"checkpoint\s+saved",
        r"weights\s+saved",
        r"saved\s+to\s+/kaggle/working",
        
        # Final metrics
        r"final\s+accuracy:\s*\d+",
        r"final\s+loss:\s*\d+",
        r"test\s+accuracy:\s*\d+",
        r"validation\s+accuracy:\s*\d+",
        r"best\s+accuracy:\s*\d+",
        r"best\s+model",
        r"best\s+score",
        
        # Progress completion
        r"epoch\s+(\d+)/(\1)",  # Epoch 10/10 (same number)
        r"100%\s*\|",  # 100% |
        r"\[(\d+)/(\1)\]",  # [100/100]
        r"all\s+epochs\s+completed",
        r"all\s+steps\s+completed",
        
        # Results
        r"results?:",
        r"final\s+results?",
        r"evaluation\s+results?",
        r"submission\s+ready",
        r"predictions?\s+saved",
    ]
    
    # ==================== ERROR STATE PATTERNS ====================
    ERROR_PATTERNS = [
        # Error keywords
        r"error:|exception:|traceback",
        r"fatal\s+error",
        r"critical\s+error",
        
        # Python exceptions
        r"keyerror|valueerror|runtimeerror|typeerror",
        r"attributeerror|indexerror|nameerror",
        r"importerror|modulenotfounderror",
        r"zerodivisionerror|assertionerror",
        r"filenotfounderror|permissionerror",
        
        # Status text
        r"failed|failure",
        r"crashed|crash",
        r"terminated\s+with\s+error",
        r"execution\s+failed",
        
        # Resource errors
        r"cuda\s+out\s+of\s+memory",
        r"out\s+of\s+memory",
        r"memory\s+error",
        r"resource\s+exhausted",
        r"disk\s+quota\s+exceeded",
        
        # File errors
        r"file\s+not\s+found",
        r"no\s+such\s+file",
        r"cannot\s+open\s+file",
        r"permission\s+denied",
        
        # Network errors
        r"connection\s+error",
        r"timeout\s+error",
        r"network\s+error",
        
        # Framework errors
        r"tensorflow.*error",
        r"pytorch.*error",
        r"keras.*error",
        r"cuda.*error",
    ]
    
    # ==================== TRAINING METRICS PATTERNS ====================
    TRAINING_METRICS = [
        # Epoch/Step
        (r"epoch\s+(\d+)/(\d+)", "epoch"),
        (r"step\s+(\d+)/(\d+)", "step"),
        (r"batch\s+(\d+)/(\d+)", "batch"),
        (r"\[(\d+)/(\d+)\]", "progress"),
        
        # Loss metrics
        (r"loss:\s*(\d+\.\d+)", "loss"),
        (r"train_loss:\s*(\d+\.\d+)", "train_loss"),
        (r"val_loss:\s*(\d+\.\d+)", "val_loss"),
        (r"test_loss:\s*(\d+\.\d+)", "test_loss"),
        
        # Accuracy metrics
        (r"accuracy:\s*(\d+\.\d+)", "accuracy"),
        (r"acc:\s*(\d+\.\d+)", "accuracy"),
        (r"train_acc:\s*(\d+\.\d+)", "train_accuracy"),
        (r"val_acc:\s*(\d+\.\d+)", "val_accuracy"),
        (r"test_acc:\s*(\d+\.\d+)", "test_accuracy"),
        
        # Other metrics
        (r"f1[-_]score:\s*(\d+\.\d+)", "f1_score"),
        (r"precision:\s*(\d+\.\d+)", "precision"),
        (r"recall:\s*(\d+\.\d+)", "recall"),
        (r"auc:\s*(\d+\.\d+)", "auc"),
        (r"mae:\s*(\d+\.\d+)", "mae"),
        (r"mse:\s*(\d+\.\d+)", "mse"),
        (r"rmse:\s*(\d+\.\d+)", "rmse"),
        
        # Learning rate
        (r"lr:\s*(\d+\.\d+e?-?\d*)", "learning_rate"),
        (r"learning_rate:\s*(\d+\.\d+e?-?\d*)", "learning_rate"),
        
        # Time
        (r"time:\s*(\d+\.\d+)s", "time_seconds"),
        (r"eta:\s*(\d+):(\d+)", "eta_minutes"),
    ]
    
    def load_stats(self):
        """Load pattern matching statistics."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            except:
                self.stats = self._init_stats()
        else:
            self.stats = self._init_stats()
    
    def _init_stats(self) -> Dict:
        """Initialize statistics structure."""
        return {
            'total_analyses': 0,
            'pattern_matches': 0,
            'ai_fallbacks': 0,
            'pattern_accuracy': {},
            'last_updated': datetime.now().isoformat()
        }
    
    def save_stats(self):
        """Save pattern matching statistics."""
        try:
            self.stats['last_updated'] = datetime.now().isoformat()
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            pass  # Silent fail for stats
    
    def analyze_text(self, text: str) -> Dict:
        """
        Fast pattern-based analysis of extracted text.
        Returns status and confidence without using AI.
        
        This is the main entry point for knowledge-based detection.
        """
        text_lower = text.lower()
        self.stats['total_analyses'] += 1
        
        # Multi-pattern scoring system
        scores = {
            'EMPTY': 0,
            'RUNNING': 0,
            'COMPLETE': 0,
            'ERROR': 0
        }
        
        matched_patterns = []
        
        # Check EMPTY patterns
        for pattern in self.EMPTY_PATTERNS:
            if re.search(pattern, text_lower):
                scores['EMPTY'] += 1
                matched_patterns.append(('EMPTY', pattern))
        
        # Check ERROR patterns (high priority)
        for pattern in self.ERROR_PATTERNS:
            if re.search(pattern, text_lower):
                scores['ERROR'] += 2  # Errors get double weight
                matched_patterns.append(('ERROR', pattern))
        
        # Check RUNNING patterns
        for pattern in self.RUNNING_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                scores['RUNNING'] += 1
                matched_patterns.append(('RUNNING', pattern))
                
                # Check if progress is incomplete (X < Y)
                if len(match.groups()) >= 2:
                    try:
                        current = int(match.group(1))
                        total = int(match.group(2))
                        if current < total:
                            scores['RUNNING'] += 2  # Strong indicator
                            return self._create_result(
                                'RUNNING', 'high', 
                                f'Training in progress: {match.group(0)}',
                                self._extract_metrics(text),
                                matched_patterns
                            )
                    except:
                        pass
        
        # Check COMPLETE patterns
        for pattern in self.COMPLETE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                scores['COMPLETE'] += 1
                matched_patterns.append(('COMPLETE', pattern))
                
                # Check if progress is complete (X == Y)
                if len(match.groups()) >= 2:
                    try:
                        current = int(match.group(1))
                        total = int(match.group(2))
                        if current == total:
                            scores['COMPLETE'] += 2  # Strong indicator
                    except:
                        pass
        
        # Determine status based on scores
        max_score = max(scores.values())
        
        if max_score == 0:
            # No patterns matched
            if len(text.strip()) < 100:
                return self._create_result('EMPTY', 'medium', 'Very little text found', {}, [])
            else:
                return self._create_result('UNKNOWN', 'low', 'No clear indicators', {}, [], needs_ai=True)
        
        # Find status with highest score
        status = max(scores, key=scores.get)
        
        # Determine confidence
        confidence = 'low'
        if max_score >= 3:
            confidence = 'high'
        elif max_score >= 2:
            confidence = 'medium'
        
        # Special cases for high confidence
        if status == 'EMPTY' and scores['EMPTY'] >= 2:
            confidence = 'high'
        elif status == 'ERROR' and scores['ERROR'] >= 2:
            confidence = 'high'
        
        # Build details
        pattern_summary = ', '.join([p[1][:30] for p in matched_patterns[:3]])
        details = f'{status} indicators found: {pattern_summary}'
        
        # Extract metrics
        metrics = self._extract_metrics(text)
        
        # Update stats
        self.stats['pattern_matches'] += 1
        self._update_pattern_accuracy(status, confidence)
        
        return self._create_result(status, confidence, details, metrics, matched_patterns)
    
    def _create_result(self, status: str, confidence: str, details: str, 
                      metrics: Dict, patterns: List, needs_ai: bool = False) -> Dict:
        """Create standardized result dictionary."""
        return {
            'status': status,
            'confidence': confidence,
            'has_content': status != 'EMPTY',
            'details': details,
            'metrics': metrics,
            'matched_patterns': len(patterns),
            'method': 'pattern_match',
            'needs_ai': needs_ai
        }
    
    def _extract_metrics(self, text: str) -> Dict:
        """Extract training metrics from text using comprehensive patterns."""
        metrics = {}
        
        for pattern, metric_name in self.TRAINING_METRICS:
            match = re.search(pattern, text.lower())
            if match:
                if metric_name in ['epoch', 'step', 'batch', 'progress']:
                    # Format as "X/Y"
                    if len(match.groups()) >= 2:
                        current = match.group(1)
                        total = match.group(2)
                        metrics[metric_name] = f"{current}/{total}"
                        # Calculate percentage
                        try:
                            pct = int(current) / int(total) * 100
                            metrics[f'{metric_name}_percent'] = f"{pct:.0f}%"
                        except:
                            pass
                elif metric_name == 'eta_minutes':
                    # Format as "MM:SS"
                    minutes = match.group(1)
                    seconds = match.group(2)
                    metrics['eta'] = f"{minutes}:{seconds}"
                else:
                    # Single value metrics
                    metrics[metric_name] = match.group(1)
        
        return metrics
    
    def _update_pattern_accuracy(self, status: str, confidence: str):
        """Update pattern accuracy statistics."""
        key = f"{status}_{confidence}"
        if key not in self.stats['pattern_accuracy']:
            self.stats['pattern_accuracy'][key] = 0
        self.stats['pattern_accuracy'][key] += 1
        
        # Save stats periodically (every 10 analyses)
        if self.stats['total_analyses'] % 10 == 0:
            self.save_stats()
    
    def learn_from_ai(self, text: str, ai_status: str, ai_confidence: str):
        """
        Learn from AI analysis to improve pattern matching.
        This can be called after AI analysis to update the knowledge base.
        """
        # For future: Could extract new patterns from AI-analyzed text
        # and add them to the pattern lists dynamically
        self.stats['ai_fallbacks'] += 1
        self.save_stats()
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics."""
        total = self.stats['total_analyses']
        if total == 0:
            return self.stats
        
        pattern_rate = (self.stats['pattern_matches'] / total) * 100
        ai_rate = (self.stats['ai_fallbacks'] / total) * 100
        
        return {
            **self.stats,
            'pattern_match_rate': f"{pattern_rate:.1f}%",
            'ai_fallback_rate': f"{ai_rate:.1f}%"
        }
    
    def add_custom_pattern(self, status: str, pattern: str):
        """
        Add a custom pattern to the knowledge base.
        Useful for learning from specific notebook patterns.
        """
        status = status.upper()
        if status == 'EMPTY':
            self.EMPTY_PATTERNS.append(pattern)
        elif status == 'RUNNING':
            self.RUNNING_PATTERNS.append(pattern)
        elif status == 'COMPLETE':
            self.COMPLETE_PATTERNS.append(pattern)
        elif status == 'ERROR':
            self.ERROR_PATTERNS.append(pattern)
        
        # Save to file for persistence
        self._save_custom_patterns()
    
    def _save_custom_patterns(self):
        """Save custom patterns to file."""
        custom_file = Path(__file__).parent.parent / 'kb_custom_patterns.json'
        try:
            patterns = {
                'EMPTY': self.EMPTY_PATTERNS[-10:],  # Last 10 custom
                'RUNNING': self.RUNNING_PATTERNS[-10:],
                'COMPLETE': self.COMPLETE_PATTERNS[-10:],
                'ERROR': self.ERROR_PATTERNS[-10:]
            }
            with open(custom_file, 'w') as f:
                json.dump(patterns, f, indent=2)
        except:
            pass
