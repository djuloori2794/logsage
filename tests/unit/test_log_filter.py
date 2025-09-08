"""
Unit tests for log_filter module.
"""
import pytest
import sys
from pathlib import Path

# Add the project root to Python path so we can import logsage modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from logsage.core.log_filter import read_log, keyword_match, filter_log_lines


class TestLogFilter:
    """Test class for log filtering functions."""
    
    def test_keyword_match_basic(self):
        """Test basic keyword matching functionality."""
        # Test cases: (input, expected_result)
        test_cases = [
            ("ERROR: Something went wrong", True),      # Contains 'error'
            ("FATAL: Critical failure", True),         # Contains 'fatal'  
            ("INFO: Process started", False),          # No error keywords
            ("failed to connect", True),               # Contains 'fail'
            ("DEBUG: All good", False),                # No error keywords
            ("Exception occurred", True),              # Contains 'exception'
            ("Cannot find file", True),                # Contains 'cannot'
        ]
        
        for log_line, expected in test_cases:
            result = keyword_match(log_line)
            assert result == expected, f"Failed for '{log_line}': got {result}, expected {expected}"
    
    def test_keyword_match_case_insensitive(self):
        """Test that keyword matching is case-insensitive."""
        test_cases = [
            "error: lowercase",
            "ERROR: uppercase", 
            "Error: mixed case",
            "eRrOr: weird case"
        ]
        
        for log_line in test_cases:
            assert keyword_match(log_line) == True, f"Should match '{log_line}'"
    
    def test_filter_log_lines_basic(self):
        """Test basic log line filtering."""
        sample_lines = [
            "INFO: Starting process",      # index 0
            "ERROR: Connection failed",    # index 1 - should match (keyword)
            "DEBUG: Loading config",       # index 2  
            "FATAL: Process crashed",      # index 3 - should match (keyword)
            "INFO: Cleanup done"           # index 4 - should match (tail if LOG_TAIL_LINES=200)
        ]
        
        result = filter_log_lines(sample_lines)
        
        # Check that result is a list of tuples
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], int)    # line index
            assert isinstance(item[1], str)    # line content
        
        # Should contain lines with keywords: index 1 (ERROR), index 3 (FATAL)
        filtered_indices = [item[0] for item in result]
        assert 1 in filtered_indices, "Should contain ERROR line"
        assert 3 in filtered_indices, "Should contain FATAL line"
    
    def test_filter_log_lines_deduplication(self):
        """Test that deduplication works correctly."""
        # Create a scenario where a line matches both keyword AND tail criteria
        sample_lines = ["INFO: Start"] + ["DEBUG: process"] * 190 + ["ERROR: Failed"]
        # The ERROR line is both: keyword match + in tail (last 200 lines)
        
        result = filter_log_lines(sample_lines)
        
        # Count occurrences of the ERROR line (index 191)
        error_line_count = sum(1 for idx, _ in result if idx == 191)
        assert error_line_count == 1, f"ERROR line should appear exactly once, got {error_line_count}"
    
    def test_filter_log_lines_empty_input(self):
        """Test filtering with empty input."""
        result = filter_log_lines([])
        assert result == []
    
    def test_read_log_functionality(self):
        """Test reading log file (using test data)."""
        # Use the sample log file we created
        test_file = project_root / "tests" / "test_data" / "small_test.log"
        
        if test_file.exists():
            lines = read_log(str(test_file))
            
            # Check basic properties
            assert isinstance(lines, list)
            assert len(lines) > 0
            assert all(isinstance(line, str) for line in lines)
            
            # Should contain our test content
            content = "".join(lines)
            assert "ERROR: Connection failed" in content
            assert "FATAL: Process crashed" in content
    
    def test_read_log_file_not_found(self):
        """Test reading non-existent file raises appropriate error."""
        with pytest.raises(FileNotFoundError):
            read_log("/path/that/does/not/exist.log")


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])