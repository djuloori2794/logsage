from typing import List, Set
from logsage.config import WEIGHT_COUNT_THRESHOLD, WEIGHT_THRESHOLD_LOW, WEIGHT_THRESHOLD_HIGH, NUM_LINES_BEFORE, NUM_LINES_AFTER


def compute_adaptive_threshold(weights: List[int], gamma: int = WEIGHT_COUNT_THRESHOLD) -> int:
    """
    Compute the threshold (θ) that determines which log lines are important enough
    to expand context around.

    θ = 1 if:
        - All weights are 1 (max = 1), OR
        - The number of weights ≥ 1 is small (≤ γ)
    Otherwise:
        - θ = 3
    """
    max_weight = max(weights)
    num_nonzero_weights = sum(1 for w in weights if w >= 1)

    if max_weight == 1 or num_nonzero_weights <= gamma:
        return WEIGHT_THRESHOLD_LOW
    return WEIGHT_THRESHOLD_HIGH


def expand_context_around_high_weight_lines(
        log_lines: List[str],
        weights: List[int],
        lines_before: int = NUM_LINES_BEFORE,
        lines_after: int = NUM_LINES_AFTER,
        gamma: int = WEIGHT_COUNT_THRESHOLD
) -> Set[int]:
    """
    For each log line with weight ≥ θ, include its neighboring lines to preserve context.

    Returns:
        A set of line indices to keep.
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
