"""
Unit tests for block_ranker module.
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from logsage.core.block_ranker import group_contiguous_blocks, compute_block_densities, rank_blocks_by_density


class TestBlockRanker:
    """Test class for block ranking functions."""
    
    def test_group_contiguous_blocks_basic(self):
        """Test basic contiguous block grouping."""
        # Test simple contiguous sequence
        indices = [1, 2, 3, 4]
        result = group_contiguous_blocks(indices)
        assert result == [(1, 4)], "Should group contiguous indices into single block"
        
        # Test non-contiguous sequences  
        indices = [1, 2, 3, 7, 8, 12]
        result = group_contiguous_blocks(indices)
        expected = [(1, 3), (7, 8), (12, 12)]
        assert result == expected, f"Expected {expected}, got {result}"
    
    def test_group_contiguous_blocks_edge_cases(self):
        """Test edge cases for block grouping."""
        # Empty input
        assert group_contiguous_blocks([]) == []
        
        # Single element
        assert group_contiguous_blocks([5]) == [(5, 5)]
        
        # All separate elements
        indices = [1, 3, 5, 7]
        result = group_contiguous_blocks(indices)
        expected = [(1, 1), (3, 3), (5, 5), (7, 7)]
        assert result == expected
    
    def test_compute_block_densities_basic(self):
        """Test density computation using Equation 3."""
        weights = [0, 2, 3, 1, 0, 4, 2, 0, 0, 1]  # weights for indices 0-9
        blocks = [(1, 3), (5, 6)]  # Two blocks: [1-3] and [5-6]
        
        result = compute_block_densities(weights, blocks)
        
        # Should return list of ((start, end), density) tuples
        assert isinstance(result, list)
        assert len(result) == 2
        
        # Block (1, 3): weights[1:4] = [2, 3, 1], sum=6, length=3, density=6/3=2.0
        block1_data = result[0]
        assert block1_data[0] == (1, 3)
        assert abs(block1_data[1] - 2.0) < 0.001, f"Expected density 2.0, got {block1_data[1]}"
        
        # Block (5, 6): weights[5:7] = [4, 2], sum=6, length=2, density=6/2=3.0  
        block2_data = result[1]
        assert block2_data[0] == (5, 6)
        assert abs(block2_data[1] - 3.0) < 0.001, f"Expected density 3.0, got {block2_data[1]}"
    
    def test_compute_block_densities_zero_weights(self):
        """Test density computation with zero weights."""
        weights = [0, 0, 0, 1, 0]
        blocks = [(0, 2), (3, 3)]  # Block with all zeros, block with weight 1
        
        result = compute_block_densities(weights, blocks)
        
        # Block (0, 2): sum=0, length=3, density=0.0
        assert result[0][1] == 0.0
        
        # Block (3, 3): sum=1, length=1, density=1.0
        assert abs(result[1][1] - 1.0) < 0.001
    
    def test_rank_blocks_by_density_basic(self):
        """Test basic block ranking functionality."""
        weights = [1, 5, 3, 2, 0, 8, 4, 1]  # Index: 0,1,2,3,4,5,6,7
        selected_indices = [1, 2, 3, 5, 6, 7]  # Two groups: [1-3] and [5-7]
        
        result = rank_blocks_by_density(weights, selected_indices)
        
        # Should return list of (start, end) tuples ranked by density
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
        
        # Calculate expected densities:
        # Block [1-3]: weights=[5,3,2], sum=10, length=3, density=10/3≈3.33
        # Block [5-7]: weights=[8,4,1], sum=13, length=3, density=13/3≈4.33
        
        # Should be ranked by density (highest first)
        # Block [5-7] (density 4.33) should come before [1-3] (density 3.33)
        assert result[0] == (5, 7), f"Highest density block should be first, got {result[0]}"
        assert result[1] == (1, 3), f"Lower density block should be second, got {result[1]}"
    
    def test_rank_blocks_by_density_single_elements(self):
        """Test ranking with single-element blocks."""
        weights = [0, 10, 0, 5, 0, 1]  # High weights at scattered positions
        selected_indices = [1, 3, 5]   # Three separate single-element blocks
        
        result = rank_blocks_by_density(weights, selected_indices)
        
        # Each forms its own block with density = weight/1 = weight
        # Should be ranked: (1,1) density=10, (3,3) density=5, (5,5) density=1
        expected = [(1, 1), (3, 3), (5, 5)]
        assert result == expected, f"Expected {expected}, got {result}"
    
    def test_rank_blocks_by_density_empty_input(self):
        """Test ranking with empty input."""
        weights = [1, 2, 3]
        result = rank_blocks_by_density(weights, [])
        assert result == []
    
    def test_rank_blocks_by_density_deduplication(self):
        """Test that duplicate indices are handled correctly.""" 
        weights = [1, 5, 3, 2]
        selected_indices = [1, 2, 1, 2, 3]  # Duplicates should be removed
        
        result = rank_blocks_by_density(weights, selected_indices)
        
        # Should deduplicate to [1, 2, 3] -> single block (1, 3)
        assert len(result) == 1
        assert result[0] == (1, 3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])