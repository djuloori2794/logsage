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
    Computes density of each block using the formula:
        sum(weights) / number of lines in the block
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
    Ranks blocks by descending density.

    Returns:
        List of (start, end) tuples sorted by density.
    """
    sorted_indices = sorted(set(selected_indices))
    contiguous_blocks = group_contiguous_blocks(sorted_indices)
    densities = compute_block_densities(weights, contiguous_blocks)
    ranked_blocks = sorted(densities, key=lambda x: x[1], reverse=True)
    return [block for block, _ in ranked_blocks]
