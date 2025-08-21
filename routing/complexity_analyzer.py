"""
Complexity Analyzer - Advanced analysis of task complexity for model routing.

Analyzes prompts, code content, and context to determine task complexity
and appropriate model requirements.
"""

import re
import os
import json
from typing import Dict, List, Tuple, Set, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Task type categories."""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    GENERAL = "general"

@dataclass
class ComplexityIndicator:
    """Individual complexity indicator."""
    name: str
    weight: float
    score: float
    evidence: List[str]

class ComplexityAnalyzer:
    """
    Advanced complexity analysis for intelligent model routing.
    
    Analyzes various aspects of prompts and context to determine:
    - Task complexity level (simple, moderate, complex, expert)
    - Task type classification
    - Confidence in the assessment
    """
    
    def __init__(self):
        self.complexity_patterns = self._load_complexity_patterns()
        self.task_type_patterns = self._load_task_type_patterns()
        self.file_type_complexity = self._load_file_type_complexity()
        
    def _load_complexity_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load patterns for complexity detection."""
        return {
            "simple_keywords": {
                "patterns": [
                    r'\bhelp\b', r'\bexplain\b', r'\bwhat is\b', r'\bhow to\b',
                    r'\bsimple\b', r'\bbasic\b', r'\bquick\b', r'\beasy\b'
                ],
                "weight": 0.3,
                "complexity_impact": -0.2
            },
            "moderate_keywords": {
                "patterns": [
                    r'\bimplement\b', r'\bcreate\b', r'\bbuild\b', r'\bwrite\b',
                    r'\bfix\b', r'\bupdate\b', r'\bmodify\b', r'\bimprove\b'
                ],
                "weight": 0.4,
                "complexity_impact": 0.1
            },
            "complex_keywords": {
                "patterns": [
                    r'\barchitecture\b', r'\bdesign pattern\b', r'\boptimize\b',
                    r'\bperformance\b', r'\bscale\b', r'\brefactor\b',
                    r'\balgorithm\b', r'\bcomplex\b', r'\badvanced\b'
                ],
                "weight": 0.6,
                "complexity_impact": 0.3
            },
            "expert_keywords": {
                "patterns": [
                    r'\bmachine learning\b', r'\bdeep learning\b', r'\bai\b',
                    r'\bdistributed\b', r'\bmicroservices\b', r'\bconcurrency\b',
                    r'\bsecurity\b', r'\bcryptography\b', r'\bprotocol\b',
                    r'\bsystem design\b', r'\bhigh availability\b'
                ],
                "weight": 0.8,
                "complexity_impact": 0.5
            },
            "technical_indicators": {
                "patterns": [
                    r'\b[A-Z_]{3,}\b',  # Constants/enums
                    r'\b\w+\(\w*\)\s*{',  # Function definitions
                    r'class\s+\w+',  # Class definitions
                    r'import\s+\w+',  # Imports
                    r'\b\w+\.\w+\(',  # Method calls
                ],
                "weight": 0.3,
                "complexity_impact": 0.1
            },
            "length_indicators": {
                "thresholds": {
                    "short": 100,
                    "medium": 500,
                    "long": 2000,
                    "very_long": 5000
                },
                "weight": 0.2,
                "complexity_mapping": {
                    "short": -0.1,
                    "medium": 0.0,
                    "long": 0.2,
                    "very_long": 0.4
                }
            },
            "code_complexity": {
                "patterns": [
                    r'for\s+\w+\s+in',  # Loops
                    r'if\s+.+:',  # Conditionals
                    r'try\s*:',  # Exception handling
                    r'async\s+def',  # Async functions
                    r'yield\s+',  # Generators
                    r'lambda\s+',  # Lambda functions
                ],
                "weight": 0.4,
                "complexity_per_match": 0.05
            }
        }
    
    def _load_task_type_patterns(self) -> Dict[TaskType, Dict[str, Any]]:
        """Load patterns for task type classification."""
        return {
            TaskType.CODE_GENERATION: {
                "keywords": [
                    "write", "create", "generate", "implement", "build",
                    "code", "function", "class", "script", "program"
                ],
                "patterns": [
                    r'\bwrite\s+(?:a\s+)?(?:function|class|script|program)\b',
                    r'\bcreate\s+(?:a\s+)?(?:function|class|method)\b',
                    r'\bimplement\s+(?:a\s+)?(?:algorithm|solution|feature)\b'
                ],
                "weight": 1.0
            },
            TaskType.CODE_REVIEW: {
                "keywords": [
                    "review", "check", "analyze", "improve", "optimize",
                    "feedback", "suggestions", "quality", "best practices"
                ],
                "patterns": [
                    r'\breview\s+(?:this\s+)?code\b',
                    r'\bcheck\s+(?:this\s+)?(?:code|implementation)\b',
                    r'\bimprove\s+(?:this\s+)?code\b'
                ],
                "weight": 1.0
            },
            TaskType.DEBUGGING: {
                "keywords": [
                    "debug", "fix", "error", "bug", "issue", "problem",
                    "not working", "broken", "fails", "exception"
                ],
                "patterns": [
                    r'\bfix\s+(?:this\s+)?(?:bug|error|issue)\b',
                    r'\bdebug\s+(?:this\s+)?code\b',
                    r'\b(?:not\s+working|broken|fails)\b'
                ],
                "weight": 1.0
            },
            TaskType.DOCUMENTATION: {
                "keywords": [
                    "document", "explain", "describe", "comment",
                    "readme", "docs", "documentation", "docstring"
                ],
                "patterns": [
                    r'\bdocument\s+(?:this\s+)?code\b',
                    r'\bwrite\s+(?:a\s+)?(?:readme|documentation)\b',
                    r'\badd\s+(?:comments|docstrings)\b'
                ],
                "weight": 0.8
            },
            TaskType.ANALYSIS: {
                "keywords": [
                    "analyze", "analysis", "understand", "explain",
                    "study", "examine", "investigate", "research"
                ],
                "patterns": [
                    r'\banalyze\s+(?:this\s+)?(?:code|data|system)\b',
                    r'\bunderstand\s+(?:how|what|why)\b',
                    r'\bexplain\s+(?:this\s+)?(?:code|algorithm)\b'
                ],
                "weight": 0.9
            },
            TaskType.PLANNING: {
                "keywords": [
                    "plan", "design", "architect", "structure",
                    "organize", "strategy", "approach", "roadmap"
                ],
                "patterns": [
                    r'\bdesign\s+(?:a\s+)?(?:system|architecture|solution)\b',
                    r'\bplan\s+(?:the\s+)?(?:implementation|approach)\b',
                    r'\barchitect\s+(?:a\s+)?(?:system|solution)\b'
                ],
                "weight": 1.1
            },
            TaskType.GENERAL: {
                "keywords": ["help", "question", "general", "misc"],
                "patterns": [r'\bhelp\s+(?:me\s+)?(?:with|understand)\b'],
                "weight": 0.5
            }
        }
    
    def _load_file_type_complexity(self) -> Dict[str, float]:
        """Load complexity mappings for different file types."""
        return {
            # Programming languages (by typical complexity)
            '.py': 0.2,     # Python - moderate
            '.js': 0.1,     # JavaScript - easy to moderate
            '.ts': 0.3,     # TypeScript - more complex
            '.java': 0.4,   # Java - verbose, complex
            '.cpp': 0.5,    # C++ - high complexity
            '.c': 0.4,      # C - moderate to high
            '.rs': 0.4,     # Rust - memory safety complexity
            '.go': 0.3,     # Go - designed for simplicity
            '.rb': 0.2,     # Ruby - readable
            '.php': 0.2,    # PHP - web-focused
            '.swift': 0.3,  # Swift - modern but Apple-specific
            '.kt': 0.3,     # Kotlin - Java alternative
            '.scala': 0.5,  # Scala - functional complexity
            '.hs': 0.6,     # Haskell - high functional complexity
            
            # Configuration and markup
            '.json': 0.0,   # JSON - simple structure
            '.yaml': 0.1,   # YAML - slightly more complex
            '.yml': 0.1,    # YAML alternative
            '.toml': 0.1,   # TOML - configuration
            '.xml': 0.2,    # XML - verbose
            '.html': 0.1,   # HTML - markup
            '.css': 0.1,    # CSS - styling
            '.scss': 0.2,   # SCSS - more features
            '.sql': 0.3,    # SQL - database queries
            
            # Documentation
            '.md': 0.0,     # Markdown - simple
            '.rst': 0.1,    # reStructuredText - more complex
            '.tex': 0.4,    # LaTeX - complex formatting
            
            # DevOps and infrastructure
            '.dockerfile': 0.3,  # Docker complexity
            '.tf': 0.4,          # Terraform - infrastructure
            '.yml': 0.2,         # CI/CD configs
            '.sh': 0.2,          # Shell scripts
            '.ps1': 0.3,         # PowerShell - Windows complexity
            
            # Default for unknown extensions
            'default': 0.1
        }
    
    def analyze(self, 
               prompt: str, 
               context: Optional[Dict[str, Any]] = None) -> Tuple[str, float, TaskType]:
        """
        Analyze prompt and context to determine complexity and task type.
        
        Args:
            prompt: The input prompt/task description
            context: Additional context (file types, errors, etc.)
            
        Returns:
            tuple: (complexity_level, confidence, task_type)
        """
        indicators = []
        
        # Analyze prompt text
        text_indicators = self._analyze_text_complexity(prompt)
        indicators.extend(text_indicators)
        
        # Analyze context if provided
        if context:
            context_indicators = self._analyze_context_complexity(context)
            indicators.extend(context_indicators)
        
        # Determine task type
        task_type = self._classify_task_type(prompt, context)
        
        # Calculate overall complexity
        complexity_level, confidence = self._calculate_complexity(indicators, task_type)
        
        return complexity_level, confidence, task_type
    
    def _analyze_text_complexity(self, text: str) -> List[ComplexityIndicator]:
        """Analyze text content for complexity indicators."""
        indicators = []
        text_lower = text.lower()
        
        # Keyword-based analysis
        for category, config in self.complexity_patterns.items():
            if category == "length_indicators":
                continue  # Handle separately
            if category == "code_complexity":
                continue  # Handle separately
                
            if "patterns" in config:
                matches = []
                for pattern in config["patterns"]:
                    pattern_matches = re.findall(pattern, text_lower)
                    matches.extend(pattern_matches)
                
                if matches:
                    impact = config.get("complexity_impact", 0.0)
                    score = len(matches) * config["weight"] * abs(impact)
                    
                    indicators.append(ComplexityIndicator(
                        name=category,
                        weight=config["weight"],
                        score=score * (1 if impact >= 0 else -1),
                        evidence=matches[:3]  # First 3 matches as evidence
                    ))
        
        # Length-based analysis
        length_config = self.complexity_patterns["length_indicators"]
        text_length = len(text)
        length_category = "short"
        
        for category, threshold in length_config["thresholds"].items():
            if text_length >= threshold:
                length_category = category
        
        length_impact = length_config["complexity_mapping"][length_category]
        if length_impact != 0:
            indicators.append(ComplexityIndicator(
                name="text_length",
                weight=length_config["weight"],
                score=length_impact * length_config["weight"],
                evidence=[f"Text length: {text_length} chars ({length_category})"]
            ))
        
        # Code complexity analysis
        code_config = self.complexity_patterns["code_complexity"]
        code_matches = []
        for pattern in code_config["patterns"]:
            matches = re.findall(pattern, text)
            code_matches.extend(matches)
        
        if code_matches:
            code_score = len(code_matches) * code_config["complexity_per_match"]
            indicators.append(ComplexityIndicator(
                name="code_complexity",
                weight=code_config["weight"],
                score=code_score,
                evidence=[f"Code patterns found: {len(code_matches)}"]
            ))
        
        return indicators
    
    def _analyze_context_complexity(self, context: Dict[str, Any]) -> List[ComplexityIndicator]:
        """Analyze context information for complexity indicators."""
        indicators = []
        
        # File type analysis
        if "file_types" in context:
            file_types = context["file_types"]
            if isinstance(file_types, str):
                file_types = [file_types]
            
            total_complexity = 0.0
            evidence = []
            
            for file_type in file_types:
                if not file_type.startswith('.'):
                    file_type = '.' + file_type
                
                complexity = self.file_type_complexity.get(
                    file_type, 
                    self.file_type_complexity["default"]
                )
                total_complexity += complexity
                evidence.append(f"{file_type}: {complexity}")
            
            if total_complexity > 0:
                indicators.append(ComplexityIndicator(
                    name="file_type_complexity",
                    weight=0.3,
                    score=total_complexity,
                    evidence=evidence
                ))
        
        # Error context analysis
        if "errors" in context or "error" in context:
            error_info = context.get("errors") or context.get("error")
            if error_info:
                # Errors typically indicate debugging tasks
                indicators.append(ComplexityIndicator(
                    name="error_context",
                    weight=0.4,
                    score=0.2,  # Moderate complexity boost
                    evidence=["Error context present"]
                ))
        
        # Existing code analysis
        if "existing_code" in context:
            existing_code = context["existing_code"]
            if existing_code:
                code_length = len(str(existing_code))
                complexity_boost = min(code_length / 10000, 0.3)  # Cap at 0.3
                
                indicators.append(ComplexityIndicator(
                    name="existing_code",
                    weight=0.3,
                    score=complexity_boost,
                    evidence=[f"Existing code: {code_length} chars"]
                ))
        
        # Multi-file context
        if "files" in context:
            files = context["files"]
            if isinstance(files, (list, tuple)) and len(files) > 1:
                indicators.append(ComplexityIndicator(
                    name="multi_file_context",
                    weight=0.2,
                    score=min(len(files) * 0.05, 0.3),
                    evidence=[f"Multiple files: {len(files)}"]
                ))
        
        return indicators
    
    def _classify_task_type(self, 
                          prompt: str, 
                          context: Optional[Dict[str, Any]] = None) -> TaskType:
        """Classify the task type based on prompt and context."""
        scores = {}
        prompt_lower = prompt.lower()
        
        # Score each task type
        for task_type, config in self.task_type_patterns.items():
            score = 0.0
            
            # Keyword matching
            for keyword in config["keywords"]:
                if keyword.lower() in prompt_lower:
                    score += 1.0
            
            # Pattern matching
            for pattern in config["patterns"]:
                matches = re.findall(pattern, prompt_lower)
                score += len(matches) * 2.0  # Pattern matches are stronger
            
            # Apply weight
            scores[task_type] = score * config["weight"]
        
        # Context-based adjustments
        if context:
            if "errors" in context or "error" in context:
                scores[TaskType.DEBUGGING] += 2.0
            
            if "files" in context and len(context.get("files", [])) > 1:
                scores[TaskType.ANALYSIS] += 1.0
                scores[TaskType.PLANNING] += 1.0
        
        # Return highest scoring task type
        if scores:
            return max(scores, key=scores.get)
        
        return TaskType.GENERAL
    
    def _calculate_complexity(self, 
                            indicators: List[ComplexityIndicator],
                            task_type: TaskType) -> Tuple[str, float]:
        """Calculate overall complexity level and confidence."""
        if not indicators:
            return "simple", 0.5
        
        # Calculate weighted score
        total_weight = sum(ind.weight for ind in indicators)
        if total_weight == 0:
            return "simple", 0.5
        
        weighted_score = sum(ind.score * ind.weight for ind in indicators) / total_weight
        
        # Task type adjustments
        task_type_adjustments = {
            TaskType.CODE_GENERATION: 0.1,
            TaskType.DEBUGGING: 0.2,
            TaskType.ANALYSIS: 0.15,
            TaskType.PLANNING: 0.2,
            TaskType.CODE_REVIEW: 0.1,
            TaskType.DOCUMENTATION: -0.1,
            TaskType.GENERAL: 0.0
        }
        
        adjusted_score = weighted_score + task_type_adjustments.get(task_type, 0.0)
        
        # Determine complexity level
        if adjusted_score < 0:
            complexity = "simple"
        elif adjusted_score < 0.3:
            complexity = "moderate"
        elif adjusted_score < 0.6:
            complexity = "complex"
        else:
            complexity = "expert"
        
        # Calculate confidence based on number and consistency of indicators
        confidence = min(len(indicators) / 10.0, 1.0)  # More indicators = higher confidence
        
        # Adjust confidence based on score magnitude
        if abs(adjusted_score) > 0.5:
            confidence = min(confidence + 0.2, 1.0)
        
        return complexity, confidence
    
    def get_analysis_details(self, 
                           prompt: str, 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get detailed analysis breakdown for debugging/transparency."""
        indicators = []
        
        # Analyze components
        text_indicators = self._analyze_text_complexity(prompt)
        indicators.extend(text_indicators)
        
        if context:
            context_indicators = self._analyze_context_complexity(context)
            indicators.extend(context_indicators)
        
        task_type = self._classify_task_type(prompt, context)
        complexity_level, confidence = self._calculate_complexity(indicators, task_type)
        
        return {
            "complexity_level": complexity_level,
            "confidence": confidence,
            "task_type": task_type.value,
            "indicators": [
                {
                    "name": ind.name,
                    "weight": ind.weight,
                    "score": ind.score,
                    "evidence": ind.evidence
                }
                for ind in indicators
            ],
            "total_indicators": len(indicators),
            "weighted_score": sum(ind.score * ind.weight for ind in indicators) / sum(ind.weight for ind in indicators) if indicators else 0
        }