#!/usr/bin/env python3
"""
Test runner script for the plumbing voice AI agent.
This script runs all tests with proper configuration and environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run all tests with proper configuration."""
    
    # Set up environment variables for testing
    os.environ.setdefault("LIVEKIT_EVALS_VERBOSE", "1")
    os.environ.setdefault("PYTHONPATH", ".")
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Test files to run
    test_files = [
        "tests/test_assistant.py",
        "tests/test_agent_behavior.py", 
        "tests/test_agent_edge_cases.py",
        "tests/test_agent_handoffs.py"
    ]
    
    # Build pytest command
    cmd = [
        "python", "-m", "pytest",
        "-v",  # verbose output
        "-s",  # don't capture stdout (needed for LIVEKIT_EVALS_VERBOSE)
        "--tb=short",  # shorter traceback format
        "--asyncio-mode=auto",  # auto-detect async tests
    ]
    
    # Add test files
    cmd.extend(test_files)
    
    # Add any command line arguments
    cmd.extend(sys.argv[1:])
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print(f"Project root: {project_root}")
    print(f"Working directory: {os.getcwd()}")
    print("-" * 60)
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Run the tests
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"❌ Tests failed with exit code {e.returncode}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("⚠️  Tests interrupted by user")
        return 1

if __name__ == "__main__":
    sys.exit(main())
