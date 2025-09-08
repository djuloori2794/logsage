# logsage/run_pipeline.py

from core import (
    read_log,
    filter_log_lines,
    expand_log_blocks,
    assign_initial_weights,
    enhance_weights_by_pattern,
    expand_context_around_high_weight_lines,
    rank_blocks_by_density,
    select_blocks_within_token_budget
)

from logsage.config import TOKEN_LIMIT
from logsage.rca_template import create_rca_prompt_with_line_numbers

def run_logsage_pipeline(log_path):
    # 1. Read raw log
    raw_log = read_log(log_path)

    # 2. Filter log lines based on heuristics (e.g., tail + keywords)
    filtered_lines = filter_log_lines(raw_log)

    # 3. Extract key line indices from filtered results
    key_line_indices = [line_idx for line_idx, _ in filtered_lines]

    # 4. Expand around key lines to form log blocks (m=4, n=6)
    expanded_lines = expand_log_blocks(raw_log, key_line_indices)

    # 5. Assign initial weights to expanded candidate pool
    weights = assign_initial_weights(raw_log, expanded_lines)

    # 6. Enhance weights based on patterns, keywords
    weights = enhance_weights_by_pattern(raw_log, weights)

    # 7. Expand blocks for high-weight lines to preserve context
    candidate_indices = expand_context_around_high_weight_lines(raw_log, weights)

    # 8. Rank blocks by weight density
    ranked_block_ranges = rank_blocks_by_density(weights, list(candidate_indices))

    # 9. Convert block ranges to actual log content
    ranked_log_blocks = []
    for start, end in ranked_block_ranges:
        block_lines = [raw_log[i].strip() for i in range(start, end + 1)]
        ranked_log_blocks.append(block_lines)

    # 10. Select blocks under token budget using greedy strategy
    final_blocks = select_blocks_within_token_budget(ranked_log_blocks)

    # 11. Extract final lines to return or feed to LLM
    final_log = [line for block in final_blocks for line in block]

    return final_log


def run_logsage_with_rca_prompt(log_path: str) -> str:
    """
    Run the complete LogSage pipeline and generate RCA prompt for LLM analysis.
    
    Processes the log file through all LogSage stages and formats the output
    as a structured RCA prompt template ready for LLM-based root cause analysis.
    
    Args:
        log_path (str): Path to the log file to analyze
        
    Returns:
        str: Complete RCA prompt with filtered logs and analysis instructions
        
    Pipeline Stages:
        1. Log Filtering → Key error lines extraction
        2. Log Expansion → Contextual information around errors  
        3. Weight Assignment → Initial importance scoring
        4. Weight Enhancement → Pattern-based critical error emphasis
        5. Context Expansion → Semantic continuity preservation
        6. Block Ranking → Density-based prioritization
        7. Token Budget → Greedy selection within 22K token limit
        8. RCA Template → Structured prompt for LLM analysis
    """
    # Run the main LogSage pipeline to get filtered logs
    final_log = run_logsage_pipeline(log_path)
    
    # Generate structured RCA prompt with line numbers for LLM analysis
    rca_prompt = create_rca_prompt_with_line_numbers(final_log)
    
    return rca_prompt


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <path_to_log_file> [--rca]")
        print("  <path_to_log_file>: Path to the log file to process")
        print("  --rca: Generate RCA prompt template instead of raw log output")
        sys.exit(1)

    path = sys.argv[1]
    use_rca = len(sys.argv) > 2 and sys.argv[2] == "--rca"

    if use_rca:
        # Generate RCA prompt for LLM analysis
        rca_prompt = run_logsage_with_rca_prompt(path)
        print(rca_prompt)
    else:
        # Output raw pruned log lines
        processed_log = run_logsage_pipeline(path)
        print("\n--- Final Pruned Log ---\n")
        for line in processed_log:
            print(line.strip())
