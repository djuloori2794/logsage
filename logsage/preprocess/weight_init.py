from typing import List
from logsage.config import ALPHA, BETA


def assign_initial_weights(log_lines: List[str], candidate_indices: List[int]) -> List[int]:
    """
    Assign initial weights to log lines based on their presence in the candidate pool.

    Args:
        log_lines (List[str]): Full list of all log lines (L).
        candidate_indices (List[int]): Indices of candidate lines (I) from filtering/expansion.

    Returns:
        List[int]: A weight vector W of same length as log_lines.
    """
    num_logs = len(log_lines)
    num_candidates = len(candidate_indices)
    weight_vector = [0] * num_logs  # Initialize all weights to 0

    # Calculate candidate density
    candidate_density = num_candidates / num_logs if num_logs > 0 else 0

    # Determine whether to assign high-confidence weight
    high_confidence = (candidate_density <= ALPHA) and (num_candidates <= BETA)

    for idx in candidate_indices:
        if 0 <= idx < num_logs:
            if high_confidence:
                weight_vector[idx] = 3
            else:
                weight_vector[idx] = 1
        else:
            # Skip invalid indices (safety check)
            continue

    return weight_vector
