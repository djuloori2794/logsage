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
    Greedy Token Budget Selection: Selects high-density blocks within token limit.
    
    Applies greedy selection algorithm to include as many high-density blocks as 
    possible while ensuring total token count ≤ TOKEN_LIMIT (22,000 tokens).
    
    Token Constraint: Token Limit ≥ Σ(Token(Bi) from i=1 to k-1) + Token(Bk)
    
    Args:
        ranked_blocks (List[List[str]]): Log blocks ranked by density (B1, B2, ..., BK)
        
    Returns:
        List[List[str]]: Selected blocks that fit within token budget
        
    Strategy:
        - High-density blocks retained with priority
        - Low-density blocks exceeding limit are discarded  
        - Stops when adding next block would exceed TOKEN_LIMIT=22,000
        - Achieves effective pruning while maintaining critical information
        
    Example:
        Input: [Block1(5000 tokens), Block2(8000 tokens), Block3(12000 tokens)]
        TOKEN_LIMIT: 22000
        Output: [Block1, Block2] (total: 13000 ≤ 22000, Block3 would exceed limit)
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
