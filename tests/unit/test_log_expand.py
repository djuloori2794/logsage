"""
Unit tests for log_expand module.
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from logsage.core.log_expand import expand_log_blocks


class TestLogExpand:
    """Test class for log expansion functions."""
    
    def test_expand_log_blocks_basic(self):
        """Test basic log expansion functionality."""
        log_lines = [
            "line 0",  # index 0
            "line 1",  # index 1  
            "line 2",  # index 2
            "line 3",  # index 3
            "line 4",  # index 4 - key line
            "line 5",  # index 5
            "line 6",  # index 6
            "line 7",  # index 7
            "line 8",  # index 8
            "line 9",  # index 9
            "line 10"  # index 10
        ]
        
        key_line_indices = [4]  # Expand around index 4
        result = expand_log_blocks(log_lines, key_line_indices)
        
        # Should return sorted list of indices
        assert isinstance(result, list)
        assert all(isinstance(idx, int) for idx in result)
        assert result == sorted(result), "Result should be sorted"
        
        # With EXPAND_BEFORE=4, EXPAND_AFTER=6:
        # Index 4 should expand to [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # (4-4=0 to 4+6=10, clamped by list bounds)
        expected_indices = list(range(0, 11))  # 0 to 10 inclusive
        assert result == expected_indices
    
    def test_expand_log_blocks_multiple_keys(self):
        """Test expansion with multiple key lines."""
        log_lines = ["line {}".format(i) for i in range(20)]  # 0 to 19
        key_line_indices = [5, 15]  # Two key lines
        
        result = expand_log_blocks(log_lines, key_line_indices)
        
        # Line 5: expand [1-11] (5-4 to 5+6)
        # Line 15: expand [11-21] -> clamped to [11-19] 
        # Combined and deduped: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
        expected_start = max(0, 5-4)  # 1
        expected_end_1 = min(len(log_lines), 5+6+1)  # 12 (exclusive) -> 11 inclusive
        expected_end_2 = min(len(log_lines), 15+6+1)  # 20 -> 19 inclusive
        
        expected_indices = list(range(expected_start, expected_end_2))
        assert result == expected_indices
    
    def test_expand_log_blocks_overlapping(self):
        """Test that overlapping expansions are merged correctly."""
        log_lines = ["line {}".format(i) for i in range(15)]
        key_line_indices = [3, 5]  # Close together, should overlap
        
        result = expand_log_blocks(log_lines, key_line_indices)
        
        # Line 3: expand [0-9] (max(0, 3-4) to 3+6 = 0 to 9)
        # Line 5: expand [1-11] (5-4 to 5+6 = 1 to 11)  
        # Merged: [0,1,2,3,4,5,6,7,8,9,10,11]
        expected_indices = list(range(0, 12))  # 0 to 11
        assert result == expected_indices
        
        # Check no duplicates
        assert len(result) == len(set(result)), "Should not contain duplicates"
    
    def test_expand_log_blocks_boundary_conditions(self):
        """Test expansion at log boundaries."""
        log_lines = ["line {}".format(i) for i in range(5)]  # Very short log
        
        # Test expansion at start
        result_start = expand_log_blocks(log_lines, [0])
        assert 0 in result_start
        assert min(result_start) == 0, "Should not go below 0"
        
        # Test expansion at end  
        result_end = expand_log_blocks(log_lines, [4])
        assert 4 in result_end
        assert max(result_end) == 4, "Should not exceed log length"
    
    def test_expand_log_blocks_empty_input(self):
        """Test with empty inputs."""
        log_lines = ["line 1", "line 2", "line 3"]
        
        # Empty key lines
        result = expand_log_blocks(log_lines, [])
        assert result == []
        
        # Empty log lines  
        result = expand_log_blocks([], [0])
        assert result == []
    
    def test_expand_log_blocks_invalid_indices(self):
        """Test with invalid key line indices."""
        log_lines = ["line 0", "line 1", "line 2"]
        
        # Index out of range should be handled gracefully
        result = expand_log_blocks(log_lines, [10])  # Index 10 doesn't exist
        
        # Should expand around non-existent index 10:
        # start = max(0, 10-4) = 6, end = min(3, 10+6+1) = 3
        # Since start >= end, should result in empty range
        assert result == []
        
        # Negative index
        result = expand_log_blocks(log_lines, [-1])
        # start = max(0, -1-4) = 0, end = min(3, -1+6+1) = 3  
        # Should expand [0, 1, 2]
        expected = list(range(0, 3))
        assert result == expected
    
    def test_expand_log_blocks_asymmetric_expansion(self):
        """Test that expansion is actually asymmetric (4 before, 6 after)."""
        log_lines = ["line {}".format(i) for i in range(20)]
        key_line_index = 10
        
        result = expand_log_blocks(log_lines, [key_line_index])
        
        # Should expand from (10-4=6) to (10+6=16)
        expected_start = 10 - 4  # 6
        expected_end = 10 + 6    # 16
        expected_indices = list(range(expected_start, expected_end + 1))  # 6 to 16 inclusive
        
        assert result == expected_indices
        
        # Verify asymmetry: 4 lines before + key line + 6 lines after = 11 total
        lines_before_key = sum(1 for i in result if i < key_line_index)  
        lines_after_key = sum(1 for i in result if i > key_line_index)
        
        assert lines_before_key == 4, f"Should have 4 lines before, got {lines_before_key}"
        assert lines_after_key == 6, f"Should have 6 lines after, got {lines_after_key}"
        assert key_line_index in result, "Should include the key line itself"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])