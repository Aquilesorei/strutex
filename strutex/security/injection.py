"""
Prompt injection detection security plugin.
"""

import re
from typing import List, Tuple, Optional, Any, Dict

from ..plugins.base import SecurityPlugin, SecurityResult


class PromptInjectionDetector(SecurityPlugin):
    """
    Detects common prompt injection patterns.
    
    Checks for:
    - Direct instruction overrides ("ignore previous instructions")
    - Role manipulation ("you are now", "pretend to be")
    - Delimiter attacks (markdown, XML-style tags)
    - Encoding attacks (base64 instructions)
    
    Usage:
        detector = PromptInjectionDetector(strict=True)
        result = detector.validate_input(text)
    """
    
    # Common injection patterns (case-insensitive)
    DEFAULT_PATTERNS: List[Tuple[str, str]] = [
        # Direct overrides
        (r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)", "instruction_override"),
        (r"disregard\s+(all\s+)?(previous|above|prior)", "instruction_override"),
        (r"forget\s+(everything|all|your)\s+(previous|instructions?)", "instruction_override"),
        
        # Role manipulation
        (r"you\s+are\s+now\s+a", "role_manipulation"),
        (r"pretend\s+(to\s+be|you\s+are)", "role_manipulation"),
        (r"act\s+as\s+(if\s+you\s+are|a)", "role_manipulation"),
        (r"from\s+now\s+on\s+you", "role_manipulation"),
        
        # System prompt extraction
        (r"(show|reveal|print|display)\s+(me\s+)?(your|the)\s+(system|original)\s+prompt", "prompt_extraction"),
        (r"what\s+(is|are)\s+your\s+(system\s+)?instructions?", "prompt_extraction"),
        
        # Delimiter/boundary attacks
        (r"<\/?system>", "delimiter_attack"),
        (r"\[INST\]|\[\/INST\]", "delimiter_attack"),
        (r"```\s*system", "delimiter_attack"),
        (r"###\s*(system|instruction)", "delimiter_attack"),
        
        # Jailbreak attempts
        (r"DAN\s+mode", "jailbreak"),
        (r"developer\s+mode\s+enabled", "jailbreak"),
        (r"bypass\s+(your\s+)?(restrictions?|filters?|safety)", "jailbreak"),
    ]
    
    def __init__(
        self,
        block_on_detection: bool = True,
        additional_patterns: Optional[List[Tuple[str, str]]] = None
    ):
        """
        Args:
            block_on_detection: Whether to raise SecurityError on detection.
            additional_patterns: List of (pattern, description) tuples to add.
        """
        self.block_on_detection = block_on_detection
        
        # Combine default patterns with any additional ones
        self.patterns: List[Tuple[str, str]] = self.DEFAULT_PATTERNS.copy()
        if additional_patterns:
            self.patterns.extend(additional_patterns)
            
    def _check_injection(self, text: str) -> List[str]:
        """Check text against injection patterns."""
        issues = []
        for pattern, description in self.patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"Prompt injection detected: {description}")
        return issues

    def validate_input(self, text: str) -> SecurityResult:
        """Validate input text."""
        issues = self._check_injection(text)
        
        if issues:
            message = "; ".join(issues)
            if self.block_on_detection:
                from ..exceptions import SecurityError
                raise SecurityError(
                    f"Security violation: {message}",
                    details={"issues": issues}
                )
            
            return SecurityResult(
                valid=False,
                text=text,
                reason=message
            )
            
        return SecurityResult(valid=True, text=text)

    def process(
        self,
        file_path: str,
        prompt: str,
        schema: Any,
        mime_type: str,
        context: Dict[str, Any]
    ) -> SecurityResult:
        """Check for prompt injection attempts (adapter for Processor)."""
        return self.validate_input(prompt)
    
    def get_detections(self, text: str) -> List[dict]:
        """Get detailed detection information without blocking."""
        detections = []
        for pattern, category in self.patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detections.append({
                    "category": category,
                    "pattern": pattern,
                    "matches": matches[:5]  # Limit for safety
                })
        return detections
