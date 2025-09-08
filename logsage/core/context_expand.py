from typing import List, Set
from logsage.config import WEIGHT_COUNT_THRESHOLD, WEIGHT_THRESHOLD_LOW, WEIGHT_THRESHOLD_HIGH, EXPAND_BEFORE, EXPAND_AFTER


def compute_adaptive_threshold(weights: List[int], gamma: int = WEIGHT_COUNT_THRESHOLD) -> int:
    """
    Compute the adaptive threshold θ from Equation 2 for contextual window expansion.
    
    Equation 2: θ = { 1 if max(W) = 1 or |{wi ≥ 1}| ≤ γ
                    { 3 otherwise
    
    Args:
        weights (List[int]): Weight vector for all log lines
        gamma (int): γ=500, threshold for determining if filtering is sparse
        
    Returns:
        int: Adaptive threshold θ (1 for broad expansion, 3 for selective)
        
    Logic:
        - θ=1: When max weight is 1 OR count of weighted lines ≤ γ (weak filtering)
        - θ=3: When filtering successfully identified high-weight critical entries
    """
    max_weight = max(weights)
    num_nonzero_weights = sum(1 for w in weights if w >= 1)

    if max_weight == 1 or num_nonzero_weights <= gamma:
        return WEIGHT_THRESHOLD_LOW
    return WEIGHT_THRESHOLD_HIGH


def expand_context_around_high_weight_lines(
        log_lines: List[str],
        weights: List[int],
        lines_before: int = EXPAND_BEFORE,
        lines_after: int = EXPAND_AFTER,
        gamma: int = WEIGHT_COUNT_THRESHOLD
) -> Set[int]:
    """
    Contextual Window Expansion: Ensures contextual integrity of high-weight critical log lines.
    
    For log lines with weights above the adaptive threshold θ, expands into log blocks
    in their neighborhood [i - m, i + n] to preserve semantic continuity.
    
    Args:
        log_lines (List[str]): Full list of all log lines
        weights (List[int]): Weight vector for all log lines (from weight enhancement)
        lines_before (int): m=4 lines before high-weight line (same as Log Expansion)
        lines_after (int): n=6 lines after high-weight line (same as Log Expansion) 
        gamma (int): γ=500 threshold for determining sparse vs adequate filtering
    
    Returns:
        Set[int]: Set of line indices to include in candidate pool for block ranking
        
    Adaptive Threshold (Equation 2):
        θ = 1 if max(W) = 1 or |{wi ≥ 1}| ≤ γ  (broad expansion - weak filtering)
        θ = 3 otherwise                        (selective expansion - strong filtering)
    
    Expansion Strategy:
        - When θ=1: Broader contextual expansion (weak filtering detected)
        - When θ=3: Selective expansion around high-weight entries (strong filtering)
        - Uses same m=4, n=6 parameters as Log Expansion stage
    """
    assert len(log_lines) == len(weights), "Mismatch between log lines and weights"

    # Compute adaptive threshold based on weight distribution
    threshold = compute_adaptive_threshold(weights, gamma)
    selected_line_indices = set()

    for idx, weight in enumerate(weights):
        if weight >= threshold:
            # Include surrounding lines in context window [i - m, i + n]
            start = max(0, idx - lines_before)
            end = min(len(log_lines), idx + lines_after + 1)
            selected_line_indices.update(range(start, end))

    return selected_line_indices
