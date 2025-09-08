# Testing Guide for LogSage

This document provides comprehensive information about testing LogSage components.

## Overview

LogSage uses **pytest** as the testing framework with comprehensive unit tests covering all core modules. The test suite ensures code quality, algorithm correctness, and handles edge cases.

## Prerequisites

### Install Testing Dependencies

```bash
# Install pytest and coverage tools
pip install pytest pytest-cov

# Or install from requirements.txt
pip install -r requirements.txt
```

### Project Structure

```
tests/
├── __init__.py
├── test_data/           # Sample log files for testing
│   ├── sample_build.log
│   └── small_test.log
├── unit/                # Unit tests for individual modules
│   ├── __init__.py
│   ├── test_log_filter.py
│   ├── test_log_expand.py
│   ├── test_weight_init.py
│   └── test_block_ranker.py
└── integration/         # Integration tests (future)
    └── __init__.py
```

## Running Tests

### Quick Start

```bash
# Run all unit tests (recommended)
python run_tests.py

# Run with coverage report
python run_tests.py --cov

# Run only unit tests
python run_tests.py unit

# Get help
python run_tests.py --help
```

### Using pytest Directly

```bash
# Run all tests with verbose output
python -m pytest tests/unit/ -v

# Run specific test file
python -m pytest tests/unit/test_log_filter.py -v

# Run with coverage
python -m pytest tests/unit/ --cov=logsage --cov-report=term-missing

# Run specific test method
python -m pytest tests/unit/test_log_filter.py::TestLogFilter::test_keyword_match_basic -v
```

## Test Coverage

### Current Unit Test Coverage

| Module | Test File | Coverage |
|--------|-----------|----------|
| `log_filter.py` | `test_log_filter.py` | ✅ Complete |
| `log_expand.py` | `test_log_expand.py` | ✅ Complete |  
| `weight_init.py` | `test_weight_init.py` | ✅ Complete |
| `block_ranker.py` | `test_block_ranker.py` | ✅ Complete |
| `weight_enhance.py` | - | ⏳ Pending |
| `context_expand.py` | - | ⏳ Pending |
| `token_budget.py` | - | ⏳ Pending |

### Test Categories

#### 1. **Algorithm Correctness**
- **Equation 1** (Weight Assignment): High/low confidence thresholds
- **Equation 2** (Adaptive Threshold): Context expansion logic
- **Equation 3** (Block Density): Density computation and ranking

#### 2. **Edge Cases**  
- Empty inputs, boundary conditions, invalid indices
- File not found, malformed data, zero weights
- Single elements, duplicate handling

#### 3. **Data Flow**
- Input/output type validation
- Deduplication, sorting, contiguous grouping
- Asymmetric expansion (m=4, n=6)

## Writing New Tests

### Test Structure

```python
"""
Unit tests for [module_name] module.
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from logsage.core.[module_name] import function_to_test


class Test[ModuleName]:
    """Test class for [module_name] functions."""
    
    def test_function_basic(self):
        """Test basic functionality."""
        # Arrange
        input_data = "test input"
        expected = "expected output"
        
        # Act  
        result = function_to_test(input_data)
        
        # Assert
        assert result == expected
    
    def test_function_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test empty input
        assert function_to_test([]) == []
        
        # Test invalid input
        with pytest.raises(ValueError):
            function_to_test(None)
```

### Best Practices

1. **Descriptive Names**: Use clear test method names describing what is being tested
2. **Arrange-Act-Assert**: Structure tests with clear sections
3. **Multiple Test Cases**: Test various input scenarios in one method when related
4. **Edge Cases**: Always test boundaries, empty inputs, and error conditions
5. **Documentation**: Add docstrings explaining the test purpose

## Sample Test Data

The `tests/test_data/` directory contains sample log files:

### `small_test.log`
```
INFO: Starting process
DEBUG: Loading config  
ERROR: Connection failed
INFO: Retrying connection
FATAL: Process crashed
INFO: Cleanup complete
```

### `sample_build.log`  
A realistic build log with 19 lines containing various log levels, TypeScript errors, and build failure scenarios.

## Integration Testing (Future)

Integration tests will verify:
- End-to-end pipeline execution
- RCA template generation  
- File I/O operations
- Error handling and recovery

## Continuous Integration

For CI/CD integration, use:

```bash
# CI command with coverage and XML output
python -m pytest tests/unit/ --cov=logsage --cov-report=xml --cov-report=term --junit-xml=test-results.xml
```

## Debugging Tests

```bash
# Run with detailed output and no capture
python -m pytest tests/unit/test_log_filter.py -v -s --tb=long

# Run single test with debugging
python -m pytest tests/unit/test_log_filter.py::TestLogFilter::test_keyword_match_basic -v -s --pdb
```

## Performance Testing

```bash
# Show test durations
python -m pytest tests/unit/ --durations=10

# Profile slow tests
python -m pytest tests/unit/ --profile
```

## Contributing Tests

When contributing new features:

1. **Write tests first** (TDD approach recommended)
2. **Maintain >90% coverage** for new code  
3. **Test both happy path and edge cases**
4. **Update this documentation** if adding new test categories
5. **Run full test suite** before submitting PRs

## Troubleshooting

### Common Issues

**ModuleNotFoundError**: Ensure you're running tests from project root:
```bash
cd /path/to/logsage
python -m pytest tests/unit/ -v
```

**Import Errors**: Check Python path setup in test files

**File Not Found**: Verify test data files exist in `tests/test_data/`

### Getting Help

- Run `python run_tests.py --help` for test runner options
- Check `pytest.ini` for configuration
- Review existing tests for examples