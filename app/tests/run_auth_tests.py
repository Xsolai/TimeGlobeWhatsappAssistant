#!/usr/bin/env python
"""
CLI runner for authentication tests
Usage:
    python run_auth_tests.py [options]
Options:
    --unit       Run pytest unit tests
    --verify     Run verification script
    --all        Run both (default if no options provided)
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the parent directory to sys.path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

def run_unit_tests():
    """Run the pytest unit tests"""
    print("\n" + "="*50)
    print(" RUNNING UNIT TESTS ".center(50, "="))
    print("="*50 + "\n")
    
    test_file = current_file.parent / "test_auth.py"
    subprocess.run([sys.executable, str(test_file)])

def run_verification():
    """Run the verification script"""
    print("\n" + "="*50)
    print(" RUNNING VERIFICATION SCRIPT ".center(50, "="))
    print("="*50 + "\n")
    
    verify_file = current_file.parent / "verify_auth_endpoints.py"
    subprocess.run([sys.executable, str(verify_file)])

if __name__ == "__main__":
    # Parse command line arguments
    args = sys.argv[1:]
    run_unit = "--unit" in args or "--all" in args or not args
    run_verify = "--verify" in args or "--all" in args or not args
    
    # Display help if requested
    if "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)
    
    # Run the selected tests
    if run_unit:
        run_unit_tests()
    
    if run_verify:
        run_verification()
    
    print("\nTest execution complete.") 