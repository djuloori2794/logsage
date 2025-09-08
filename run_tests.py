#!/usr/bin/env python3
"""
Test runner for LogSage project.

Usage:
    python run_tests.py           # Run all tests
    python run_tests.py unit      # Run only unit tests  
    python run_tests.py -v        # Run with verbose output
    python run_tests.py --cov     # Run with coverage report
"""

import sys
import subprocess
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests with specified options."""
    
    # Base command
    cmd = ["python3", "-m", "pytest"]
    
    # Select test directory
    if test_type == "unit":
        cmd.append("tests/unit/")
    elif test_type == "integration": 
        cmd.append("tests/integration/")
    else:
        cmd.append("tests/")
    
    # Add options
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-v")  # Always use verbose for better output
        
    if coverage:
        cmd.extend(["--cov=logsage", "--cov-report=term-missing", "--cov-report=html"])
    
    # Add other useful options
    cmd.extend(["--tb=short", "--durations=5"])
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run tests
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("❌ Error: pytest not found. Install it with: pip install pytest")
        return 1


def main():
    """Main test runner entry point."""
    args = sys.argv[1:]
    
    # Parse arguments
    test_type = "all"
    verbose = False
    coverage = False
    
    for arg in args:
        if arg in ["unit", "integration"]:
            test_type = arg
        elif arg in ["-v", "--verbose"]:
            verbose = True
        elif arg in ["--cov", "--coverage"]:
            coverage = True
        elif arg in ["-h", "--help"]:
            print(__doc__)
            return 0
    
    # Check if we're in the right directory
    if not Path("logsage").exists():
        print("❌ Error: Please run this script from the project root directory")
        return 1
    
    return run_tests(test_type, verbose, coverage)


if __name__ == "__main__":
    sys.exit(main())