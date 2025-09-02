# logsage/run_pipeline.py

from preprocess import (
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

def run_logsage_pipeline(log_path):
    # 1. Read raw log
    raw_log = read_log(log_path)

    # 2. Filter log lines based on heuristics (e.g., tail + keywords)
    filtered_lines = filter_log_lines(raw_log)

    # 3. Assign initial weights to all lines
    weights = assign_initial_weights(raw_log, filtered_lines)

    # 4. Enhance weights based on patterns, keywords
    weights = enhance_weights_by_pattern(raw_log, weights)

    # 5. Expand blocks for high-weight lines to preserve context
    candidate_blocks = expand_context_around_high_weight_lines(raw_log, weights)

    # 6. Rank blocks by weight density
    ranked_blocks = rank_blocks_by_density(raw_log, candidate_blocks, weights)

    # 7. Select blocks under token budget using greedy strategy
    final_blocks = select_blocks_within_token_budget(ranked_blocks, token_limit=TOKEN_LIMIT)

    # 8. Extract final lines to return or feed to LLM
    final_log = [line for block in final_blocks for line in block]

    return final_log


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <path_to_log_file>")
        sys.exit(1)

    path = sys.argv[1]
    processed_log = run_logsage_pipeline(path)

    print("\n--- Final Pruned Log ---\n")
    for line in processed_log:
        print(line.strip())
