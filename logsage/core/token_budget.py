from logsage.config import TOKEN_LIMIT
from typing import List

def estimate_tokens(block: List[str]) -> int:
    """
    Estimate the token count of a block based on word count.
    Replace this with a tokenizer like tiktoken for accuracy.
    """
    return sum(len(line.split()) for line in block)

def select_blocks_within_token_budget(ranked_blocks: List[List[str]]) -> List[List[str]]:
    """
    Selects top log blocks while staying within the token budget.
    Uses a greedy selection strategy.
    """
    selected_blocks = []
    current_token_count = 0

    for block in ranked_blocks:
        block_tokens = estimate_tokens(block)

        if current_token_count + block_tokens <= TOKEN_LIMIT:
            selected_blocks.append(block)
            current_token_count += block_tokens
        else:
            break  # Stop when the next block exceeds the token budget

    return selected_blocks
