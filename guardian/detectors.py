import json
import re
import yaml
import os
from typing import List, Tuple, Dict, Any, Optional

ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')
PATTERNS_FILE = os.path.join(ASSETS_DIR, 'regex_patterns.json')
SCORES_FILE = os.path.join(ASSETS_DIR, 'threat_score_rules.yaml')

def load_patterns(default_patterns_path: str, custom_patterns: Optional[Dict[str, List[str]]] = None) -> Dict[str, List[str]]:
    """
    Load default patterns and merge with custom patterns if provided.
    """
    with open(default_patterns_path, 'r') as f:
        patterns = json.load(f)
    if custom_patterns:
        for k, v in custom_patterns.items():
            if k in patterns:
                patterns[k].extend(v)
            else:
                patterns[k] = v
    return patterns

def load_scores(scores_path: str) -> Dict[str, int]:
    with open(scores_path, 'r') as f:
        return yaml.safe_load(f)

def detect_threats(log_line: str, patterns: Dict[str, List[str]], scores: Dict[str, int]) -> List[Tuple[str, int, str]]:
    """
    Checks a log line for all suspicious patterns.
    Returns a list of (threat_type, score, matched_pattern).
    """
    matches = []
    for threat_type, pats in patterns.items():
        for pattern in pats:
            if re.search(pattern, log_line, re.IGNORECASE):
                score = scores.get(threat_type, scores.get('default', 10))
                matches.append((threat_type, score, pattern))
    return matches 