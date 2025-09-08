"""
Unit tests for weight_init module.
"""
import pytest
import sys
from pathlib import Path

# Add project root to path  
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from logsage.core.weight_init import assign_initial_weights


class TestWeightInit:
    """Test class for weight initialization functions."""
    
    def test_assign_initial_weights_basic(self):
        """Test basic weight assignment functionality."""
        log_lines = ["line 0", "line 1", "line 2", "line 3", "line 4"]
        candidate_indices = [1, 3]  # Lines 1 and 3 are candidates
        
        result = assign_initial_weights(log_lines, candidate_indices)
        
        # Should return list of integers with same length as log_lines
        assert isinstance(result, list)
        assert len(result) == len(log_lines)
        assert all(isinstance(w, int) for w in result)
        
        # Candidate lines should have weight > 0, others should be 0
        assert result[1] > 0, "Candidate line should have positive weight"  
        assert result[3] > 0, "Candidate line should have positive weight"
        assert result[0] == 0, "Non-candidate line should have weight 0"
        assert result[2] == 0, "Non-candidate line should have weight 0"
        assert result[4] == 0, "Non-candidate line should have weight 0"
    
    def test_assign_initial_weights_high_confidence(self):
        """Test high confidence weight assignment (Equation 1)."""
        # Create scenario for high confidence: 
        # |I|/|L| ≤ α=0.7 AND |I| ≤ β=500
        log_lines = ["line {}".format(i) for i in range(10)]  # 10 lines total
        candidate_indices = [2, 5]  # 2 candidates
        
        # Density = 2/10 = 0.2 ≤ 0.7 ✓ AND 2 ≤ 500 ✓ -> high confidence
        result = assign_initial_weights(log_lines, candidate_indices)
        
        # High confidence should assign weight 3
        assert result[2] == 3, "High confidence should assign weight 3"
        assert result[5] == 3, "High confidence should assign weight 3"
        assert result[0] == 0, "Non-candidate should have weight 0"
    
    def test_assign_initial_weights_low_confidence_high_density(self):
        """Test low confidence due to high candidate density."""
        # Create scenario: |I|/|L| > α=0.7 -> low confidence
        log_lines = ["line {}".format(i) for i in range(10)]  # 10 lines
        candidate_indices = list(range(8))  # 8 candidates (80% > 70%)
        
        # Density = 8/10 = 0.8 > 0.7 -> low confidence  
        result = assign_initial_weights(log_lines, candidate_indices)
        
        # Low confidence should assign weight 1
        for i in candidate_indices:
            assert result[i] == 1, f"Low confidence should assign weight 1, got {result[i]} for index {i}"
        
        # Non-candidates should still be 0
        assert result[8] == 0
        assert result[9] == 0
    
    def test_assign_initial_weights_low_confidence_high_count(self):
        """Test low confidence due to high candidate count."""
        # Create scenario: |I| > β=500 -> low confidence
        log_lines = ["line {}".format(i) for i in range(1000)]  # 1000 lines
        candidate_indices = list(range(600))  # 600 candidates > β=500
        
        # Even though density = 600/1000 = 0.6 ≤ 0.7, count 600 > 500 -> low confidence
        result = assign_initial_weights(log_lines, candidate_indices)
        
        # Should assign weight 1 (low confidence)
        for i in range(10):  # Check first 10 candidates
            assert result[i] == 1, f"Should assign weight 1 for high count scenario"
        
        # Non-candidates should be 0
        for i in range(600, 610):  # Check some non-candidates
            assert result[i] == 0
    
    def test_assign_initial_weights_empty_candidates(self):
        """Test with no candidate lines."""
        log_lines = ["line 0", "line 1", "line 2"]
        candidate_indices = []
        
        result = assign_initial_weights(log_lines, candidate_indices)
        
        # All weights should be 0
        assert result == [0, 0, 0]
    
    def test_assign_initial_weights_empty_log(self):
        """Test with empty log."""
        log_lines = []
        candidate_indices = []
        
        result = assign_initial_weights(log_lines, candidate_indices)
        
        # Should return empty list
        assert result == []
    
    def test_assign_initial_weights_all_candidates(self):
        """Test when all lines are candidates."""
        log_lines = ["line 0", "line 1", "line 2"]
        candidate_indices = [0, 1, 2]
        
        result = assign_initial_weights(log_lines, candidate_indices)
        
        # Density = 3/3 = 1.0 > 0.7 -> low confidence -> weight 1
        assert result == [1, 1, 1]
    
    def test_assign_initial_weights_invalid_indices(self):
        """Test handling of invalid candidate indices."""
        log_lines = ["line 0", "line 1", "line 2"]
        candidate_indices = [1, 5, -1]  # Index 5 and -1 are out of bounds
        
        result = assign_initial_weights(log_lines, candidate_indices)
        
        # Should handle gracefully - only valid index 1 should get weight
        assert len(result) == 3
        assert result[1] > 0, "Valid candidate should get weight"
        assert result[0] == 0, "Non-candidate should be 0"  
        assert result[2] == 0, "Non-candidate should be 0"
        
        # Invalid indices should be ignored (no crash)
        assert isinstance(result, list)
    
    def test_assign_initial_weights_equation_1_boundary(self):
        """Test boundary conditions for Equation 1 thresholds."""
        # Test exactly at α=0.7 threshold
        log_lines = ["line {}".format(i) for i in range(10)]
        candidate_indices = list(range(7))  # Exactly 7/10 = 0.7
        
        result = assign_initial_weights(log_lines, candidate_indices)
        
        # At boundary: 7/10 = 0.7 ≤ 0.7 AND 7 ≤ 500 -> should be high confidence (weight 3)
        for i in range(7):
            assert result[i] == 3, f"Boundary condition should give high confidence weight 3"
        
        # Test exactly at β=500 threshold
        log_lines_large = ["line {}".format(i) for i in range(1000)]
        candidate_indices_large = list(range(500))  # Exactly 500 candidates
        
        result_large = assign_initial_weights(log_lines_large, candidate_indices_large)
        
        # Density = 500/1000 = 0.5 ≤ 0.7 AND 500 ≤ 500 -> high confidence (weight 3)
        for i in range(10):  # Check first 10
            assert result_large[i] == 3, "Boundary β=500 should give high confidence"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])