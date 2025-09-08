from typing import List, Tuple


def group_contiguous_blocks(indices: List[int]) -> List[Tuple[int, int]]:
    """
    Groups sorted line indices into contiguous blocks.

    Example: [3,4,5,10,11] -> [(3,5), (10,11)]
    """
    if not indices:
        return []

    blocks = []
    start = prev = indices[0]

    for idx in indices[1:]:
        if idx == prev + 1:
            prev = idx
        else:
            blocks.append((start, prev))
            start = prev = idx

    blocks.append((start, prev))
    return blocks


def compute_block_densities(
        weights: List[int],
        blocks: List[Tuple[int, int]]
) -> List[Tuple[Tuple[int, int], float]]:
    """
    Computes weight density for each log block using Equation 3 from the paper.
    
    Equation 3: density(Bj) = Σ(wi from sj to ej) / (ej - sj + 1)
    
    Args:
        weights (List[int]): Weight vector for all log lines
        blocks (List[Tuple[int, int]]): List of contiguous blocks as (start, end) tuples
        
    Returns:
        List[Tuple[Tuple[int, int], float]]: List of ((start, end), density) tuples
        
    Example:
        Block [10, 15] with weights [3, 1, 5, 2, 4, 1]:
        density = (3+1+5+2+4+1) / (15-10+1) = 16/6 = 2.67
    """
    block_densities = []
    for start, end in blocks:
        total_weight = sum(weights[i] for i in range(start, end + 1))
        num_lines = end - start + 1
        density = total_weight / num_lines if num_lines > 0 else 0
        block_densities.append(((start, end), density))
    return block_densities


def rank_blocks_by_density(
        weights: List[int],
        selected_indices: List[int]
) -> List[Tuple[int, int]]:
    """
    Density-Based Block Ranking: Ranks contiguous log blocks by weight density.
    
    Groups candidate lines into contiguous blocks Bj = [sj, ej], computes their 
    weight density using Equation 3, and ranks them in descending order as 
    B1, B2, ..., BK where B1 has the highest density.
    
    Args:
        weights (List[int]): Weight vector for all log lines 
        selected_indices (List[int]): Candidate line indices from context expansion
        
    Returns:
        List[Tuple[int, int]]: Ranked list of (start, end) block ranges sorted by density
        
    Process:
        1. Groups contiguous indices into blocks Bj = [sj, ej]
        2. Computes density(Bj) = Σwi / (ej - sj + 1) for each block
        3. Ranks blocks in descending density order (highest priority first)
        
    Example:
        Input indices: [1, 2, 3, 7, 8, 10] 
        Grouped blocks: [(1,3), (7,8), (10,10)]
        Ranked by density: [(7,8), (1,3), (10,10)] (assuming decreasing densities)
    """
    sorted_indices = sorted(set(selected_indices))
    contiguous_blocks = group_contiguous_blocks(sorted_indices)
    densities = compute_block_densities(weights, contiguous_blocks)
    ranked_blocks = sorted(densities, key=lambda x: x[1], reverse=True)
    return [block for block, _ in ranked_blocks]
