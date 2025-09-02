import re
from typing import List
from logsage.config import FAILURE_PATTERNS, SECTION_PATTERN, ENABLE_WEAK_BOOST

def enhance_weights_by_pattern(log_lines: List[str], initial_weights: List[int]) -> List[int]:
    """
    Enhance weights based on pattern-based matching from the paper:
    - Lines with failure patterns get max weight
    - Lines with section markers get moderate boost
    - Other candidate lines get a small bonus
    """
    assert len(log_lines) == len(initial_weights), "Mismatched log line and weight vector lengths."
    weights = initial_weights.copy()

    for idx, line in enumerate(log_lines):
        line = line.strip()

        # Strong failure signals (override weight to 10)
        if any(re.search(pattern, line) for pattern in FAILURE_PATTERNS):
            weights[idx] = 10

        # Section headers or curated signal (boost by +2)
        elif re.match(SECTION_PATTERN, line):
            weights[idx] += 2

        # Weak candidate boost (if part of recall pool)
        elif weights[idx] > 0 and ENABLE_WEAK_BOOST:
            weights[idx] += 1

    return weights
