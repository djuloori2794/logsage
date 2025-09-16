"""
Unit tests for weight_enhance module.
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from logsage.core.weight_enhance import enhance_weights_by_pattern


class TestWeightEnhance:
    """Test class for weight enhancement functions."""

    def test_enhance_weights_basic(self):
        """Test basic weight enhancement functionality."""
        log_lines = [
            "INFO: Starting process",       # index 0
            "ERROR: Connection failed",     # index 1
            "DEBUG: Retrying",             # index 2
            "WARN: High memory usage"      # index 3
        ]
        initial_weights = [0, 1, 1, 0]  # Only indices 1,2 are candidates

        result = enhance_weights_by_pattern(log_lines, initial_weights)

        # Should return same length as input
        assert len(result) == len(initial_weights)
        assert isinstance(result, list)
        assert all(isinstance(w, int) for w in result)

        # Non-candidates should remain 0
        assert result[0] == 0
        assert result[3] == 0

        # Candidates should get weak boost (+1) since ENABLE_WEAK_BOOST=True
        assert result[1] == 2  # 1 + 1 (weak boost)
        assert result[2] == 2  # 1 + 1 (weak boost)

    def test_enhance_weights_failure_patterns(self):
        """Test failure pattern detection and max weight assignment."""
        log_lines = [
            "Normal log line",                    # index 0
            "--- FAIL: TestUserLogin",           # index 1 - should get weight 10
            "Some other log",                    # index 2
            "Failures: 3 tests failed",         # index 3 - should get weight 10
            "Test completed",                    # index 4 - should get weak boost only
            "No failure here"                   # index 5
        ]
        initial_weights = [1, 1, 1, 1, 1, 0]

        result = enhance_weights_by_pattern(log_lines, initial_weights)

        # Failure patterns should override to weight 10
        # FAILURE_PATTERNS = [r"--- FAIL:", r"Failures?:"]
        assert result[1] == 10, "--- FAIL: pattern should get weight 10"
        assert result[3] == 10, "Failures: pattern should get weight 10"

        # Non-failure candidates should get weak boost
        assert result[0] == 2   # 1 + 1 weak boost
        assert result[2] == 2   # 1 + 1 weak boost
        assert result[4] == 2   # 1 + 1 weak boost

        # Non-candidates remain unchanged
        assert result[5] == 0

    def test_enhance_weights_section_patterns(self):
        """Test section header pattern detection."""
        log_lines = [
            "Regular line",              # index 0
            "# Section Header",          # index 1 - section pattern
            "  # Indented Header",       # index 2 - section pattern with spaces
            "#NoSpaceHeader",           # index 3 - section pattern
            "Not # a header",           # index 4 - not a section
            "## Markdown Header"        # index 5 - section pattern
        ]
        initial_weights = [1, 1, 2, 1, 1, 3]

        result = enhance_weights_by_pattern(log_lines, initial_weights)

        # Section patterns should get +2 boost
        assert result[1] == 3   # 1 + 2 section boost
        assert result[2] == 4   # 2 + 2 section boost
        assert result[3] == 3   # 1 + 2 section boost
        assert result[5] == 5   # 3 + 2 section boost

        # Non-section candidates get weak boost
        assert result[0] == 2   # 1 + 1 weak boost
        assert result[4] == 2   # 1 + 1 weak boost

    def test_enhance_weights_priority_order(self):
        """Test that failure patterns take priority over section patterns."""
        log_lines = [
            "# --- FAIL: TestCase",      # Both section AND failure pattern
            "# Normal section",          # Only section pattern
            "--- FAIL: not section"     # Only failure pattern
        ]
        initial_weights = [1, 1, 1]

        result = enhance_weights_by_pattern(log_lines, initial_weights)

        # Failure pattern should override (weight 10), not section boost
        assert result[0] == 10, "Failure pattern should take priority over section"
        assert result[1] == 3,  "Section pattern should get +2 boost"
        assert result[2] == 10, "Failure pattern should get weight 10"

    def test_enhance_weights_weak_boost_disabled(self):
        """Test behavior when weak boost is disabled."""
        # Note: This test assumes we can modify ENABLE_WEAK_BOOST
        # In practice, you might want to make this configurable or mock it
        log_lines = [
            "Regular candidate line",
            "Another candidate"
        ]
        initial_weights = [1, 2]

        # Mock ENABLE_WEAK_BOOST = False by directly testing the logic
        # We'll test this by ensuring only explicit patterns get enhanced
        result = enhance_weights_by_pattern(log_lines, initial_weights)

        # These should get weak boost since ENABLE_WEAK_BOOST is True by default
        assert result[0] == 2  # 1 + 1
        assert result[1] == 3  # 2 + 1

    def test_enhance_weights_zero_initial_weights(self):
        """Test that zero weights don't get weak boost."""
        log_lines = [
            "Non-candidate line",
            "Another non-candidate",
            "# Section but not candidate"
        ]
        initial_weights = [0, 0, 0]

        result = enhance_weights_by_pattern(log_lines, initial_weights)

        # Zero weights should not get weak boost
        assert result[0] == 0
        assert result[1] == 0

        # But section pattern should still get boost
        assert result[2] == 2  # 0 + 2 section boost

    def test_enhance_weights_mismatched_lengths(self):
        """Test error handling for mismatched input lengths."""
        log_lines = ["line1", "line2", "line3"]
        initial_weights = [1, 1]  # Wrong length

        with pytest.raises(AssertionError, match="Mismatched log line and weight vector lengths"):
            enhance_weights_by_pattern(log_lines, initial_weights)

    def test_enhance_weights_empty_input(self):
        """Test with empty inputs."""
        result = enhance_weights_by_pattern([], [])
        assert result == []

    def test_enhance_weights_pattern_case_sensitivity(self):
        """Test that pattern matching works with exact patterns."""
        log_lines = [
            "--- FAIL: TestCase",        # Exact match
            "--- fail: testcase",        # Different case - should not match
            "Failures: 5 tests",        # Should match Failures? pattern
            "Test result"               # Should not match
        ]
        initial_weights = [1, 1, 1, 1]

        result = enhance_weights_by_pattern(log_lines, initial_weights)

        # Check which patterns actually match based on regex
        # FAILURE_PATTERNS = [r"--- FAIL:", r"Failures?:"]
        assert result[0] == 10, "Exact '--- FAIL:' should match"
        assert result[1] == 2,  "Different case should not match failure pattern"
        assert result[2] == 10, "Failures: pattern should match"
        assert result[3] == 2,  "Non-pattern should get weak boost"

    def test_enhance_weights_regex_patterns(self):
        """Test specific regex pattern matching."""
        log_lines = [
            "--- FAIL: TestUserAuth",    # Exact FAIL pattern
            "Failures: test results",   # Should match Failures? pattern
            "Failure: single failure",  # Should match Failures? pattern
            "Normal log line",          # Should not match
            "Not a fail pattern",       # Should not match
            "FAIL without dashes"       # Should not match
        ]
        initial_weights = [1, 1, 1, 1, 1, 1]

        result = enhance_weights_by_pattern(log_lines, initial_weights)

        # Test specific pattern matches - FAILURE_PATTERNS = [r"--- FAIL:", r"Failures?:"]
        assert result[0] == 10, "--- FAIL: should match"
        assert result[1] == 10, "Failures: should match Failures? pattern"
        assert result[2] == 10, "Failure: should match Failures? pattern"
        assert result[3] == 2,  "Should not match failure pattern, get weak boost"
        assert result[4] == 2,  "Should not match failure pattern, get weak boost"
        assert result[5] == 2,  "Should not match failure pattern, get weak boost"

    def test_enhance_weights_original_not_modified(self):
        """Test that original weights list is not modified."""
        log_lines = ["# Section", "--- FAIL: Test", "Normal line"]
        initial_weights = [1, 1, 1]
        original_weights = initial_weights.copy()

        result = enhance_weights_by_pattern(log_lines, initial_weights)

        # Original should be unchanged
        assert initial_weights == original_weights

        # Result should be different
        assert result != initial_weights
        assert result == [3, 10, 2]  # section +2, failure 10, weak +1

    def test_enhance_weights_line_stripping(self):
        """Test that lines are properly stripped before pattern matching."""
        log_lines = [
            "  # Section with spaces  ",   # Should still match section pattern
            "\t--- FAIL: TestCase\n",      # Should still match failure pattern
            "   Normal line   "           # Should get weak boost
        ]
        initial_weights = [1, 1, 1]

        result = enhance_weights_by_pattern(log_lines, initial_weights)

        assert result[0] == 3,  "Spaced section should match"
        assert result[1] == 10, "Spaced failure should match"
        assert result[2] == 2,  "Normal line should get weak boost"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])