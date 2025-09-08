from logsage.config import EXPAND_BEFORE, EXPAND_AFTER

def expand_log_blocks(log_lines: list[str], key_line_nums: list[int]) -> list[int]:
    """
    Expand around key log lines to preserve context using asymmetric expansion.
    
    This implements the Key Log Expansion module from the paper, which provides
    additional contextual information around error lines to support LLM-based
    root cause analysis and mitigate hallucinations caused by missing context.
    
    Args:
        log_lines (list[str]): Full list of all log lines from the file
            Example: ["INFO: Starting process", "ERROR: Failed to connect", "DEBUG: Retrying..."]
        
        key_line_nums (list[int]): Indices of key error lines from filtering stage
            Example: [1, 5, 12] (represents lines at positions 1, 5, and 12)
    
    Returns:
        list[int]: Sorted list of unique expanded line indices to include in candidate pool
            Example: If key_line_nums=[5, 10] with m=4, n=6:
            - Line 5 expands to [1,2,3,4,5,6,7,8,9,10,11] (5-4 to 5+6)
            - Line 10 expands to [6,7,8,9,10,11,12,13,14,15,16] (10-4 to 10+6)  
            - Merged result: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    
    Expansion Strategy:
        - m=4 lines before each key line (captures operations leading to error)
        - n=6 lines after each key line (captures stack traces, error scope - more critical)
        - Overlapping blocks from multiple key lines are automatically merged
        - Maintains log order by returning sorted indices
    """
    expanded_indices = set()

    for idx in key_line_nums:
        start = max(0, idx - EXPAND_BEFORE)  # m=4 lines before
        end = min(len(log_lines), idx + EXPAND_AFTER + 1)  # n=6 lines after

        # Add all indices in the expansion window
        expanded_indices.update(range(start, end))

    # Return sorted list to maintain log order
    return sorted(expanded_indices)
