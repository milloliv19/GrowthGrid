#!/usr/bin/env python3
"""
Test Runner for Monthly Matching Algorithm

Runs various test scenarios to validate the matching algorithm.
"""

import os
import shutil
import json
import sys
from pathlib import Path

# Add parent directory to path to import match_maker
sys.path.insert(0, str(Path(__file__).parent))
from match_maker import run_matching, load_match_history

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"
OUTPUT_DIR = Path(__file__).parent / "test_outputs"

# Test scenarios configuration
TEST_SCENARIOS = [
    {
        "name": "1.1 First Run (No History)",
        "users": "users_base_6.csv",
        "history": None,  # No history file
        "expected_pairs": 3,
        "expected_triad": False,
    },
    {
        "name": "1.2 Normal Matching (Even Number)",
        "users": "users_base_8.csv",
        "history": "history_partial.json",
        "expected_pairs": 4,
        "expected_triad": False,
    },
    {
        "name": "1.3 Normal Matching (Odd Number)",
        "users": "users_odd_7.csv",
        "history": "history_partial.json",
        "expected_pairs": 2,
        "expected_triad": True,
    },
    {
        "name": "2.1 Minimum Valid (2 Users)",
        "users": "users_min_2.csv",
        "history": None,
        "expected_pairs": 1,
        "expected_triad": False,
    },
    {
        "name": "2.2 Minimum Odd (3 Users)",
        "users": "users_min_3.csv",
        "history": None,
        "expected_pairs": 0,
        "expected_triad": True,
    },
    {
        "name": "2.3 Single User (Should Fail)",
        "users": "users_single.csv",
        "history": None,
        "should_fail": True,
    },
    {
        "name": "3.1 New Users Added",
        "users": "users_new_added.csv",
        "history": "history_partial.json",
        "expected_pairs": 4,
        "expected_triad": False,
    },
    {
        "name": "3.4 Asymmetric History",
        "users": "users_base_6.csv",
        "history": "history_asymmetric.json",
        "expected_pairs": 3,
        "expected_triad": False,
    },
    {
        "name": "3.5 History with Orphaned Users",
        "users": "users_base_6.csv",
        "history": "history_orphaned.json",
        "expected_pairs": 3,
        "expected_triad": False,
    },
    {
        "name": "4.1 Complete Exhaustion (4 users)",
        "users": "users_base_6.csv",
        "history": "history_complete_exhaustion_4.json",
        "expected_pairs": 3,
        "expected_triad": False,
        "should_reset": True,
    },
    {
        "name": "4.2 Near Exhaustion",
        "users": "users_base_6.csv",
        "history": "history_near_exhaustion.json",
        "expected_pairs": 3,  # Algorithm correctly resets when matching becomes impossible
        "expected_triad": False,
    },
    {
        "name": "5.1 Triad with Compatible Pair",
        "users": "users_odd_7.csv",
        "history": "history_partial.json",
        "expected_pairs": 2,
        "expected_triad": True,
    },
    {
        "name": "6.2 Corrupted JSON History",
        "users": "users_base_6.csv",
        "history": "history_corrupted.json",
        "expected_pairs": 3,
        "expected_triad": False,
    },
    {
        "name": "8.1 Complete Graph (No History)",
        "users": "users_base_6.csv",
        "history": None,
        "expected_pairs": 3,
        "expected_triad": False,
    },
    {
        "name": "8.2 Star Graph Pattern",
        "users": "users_base_6.csv",
        "history": "history_star.json",
        "expected_pairs": 3,  # Maximum matching is 3 pairs: (1,6), (2,5), (3,4)
        "expected_triad": False,
    },
    {
        "name": "8.3 Chain Pattern",
        "users": "users_base_6.csv",
        "history": "history_chain.json",
        "expected_pairs": 3,
        "expected_triad": False,
    },
    {
        "name": "8.4 Bipartite Scenario",
        "users": "users_base_6.csv",
        "history": "history_bipartite.json",
        "expected_pairs": 3,
        "expected_triad": False,
    },
    {
        "name": "11.1 Large User Set",
        "users": "users_large_20.csv",
        "history": None,
        "expected_pairs": 10,
        "expected_triad": False,
    },
    {
        "name": "7.3 Special Characters",
        "users": "users_special_chars.csv",
        "history": None,
        "expected_pairs": 3,
        "expected_triad": False,
    },
]


def setup_test(test_scenario, test_num):
    """Set up test environment by copying test files."""
    test_dir = OUTPUT_DIR / f"test_{test_num:02d}_{test_scenario['name'].replace(' ', '_').replace('.', '_')}"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy users CSV
    users_src = TEST_DATA_DIR / test_scenario["users"]
    users_dst = test_dir / "users.csv"
    shutil.copy(users_src, users_dst)
    
    # Copy or create history JSON
    history_dst = test_dir / "match_history.json"
    if test_scenario["history"]:
        history_src = TEST_DATA_DIR / test_scenario["history"]
        if history_src.exists():
            shutil.copy(history_src, history_dst)
        else:
            # Create empty history if file doesn't exist
            with open(history_dst, 'w') as f:
                json.dump({}, f)
    else:
        # No history - ensure file doesn't exist or is empty
        if history_dst.exists():
            history_dst.unlink()
    
    return test_dir


def verify_results(test_dir, test_scenario):
    """Verify test results match expectations."""
    results = {
        "passed": True,
        "errors": [],
        "warnings": []
    }
    
    # Check if output file exists
    output_file = test_dir / "matches_current_month.csv"
    if not output_file.exists():
        if test_scenario.get("should_fail", False):
            results["passed"] = True
            results["warnings"].append("Expected failure occurred (no output file)")
            return results
        else:
            results["passed"] = False
            results["errors"].append("Output file not created")
            return results
    
    # Read output file
    import csv
    matches = []
    with open(output_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            matches.append(row)
    
    # Count pairs and triads
    pairs = [m for m in matches if m.get('match_type') == 'pair']
    triads = [m for m in matches if m.get('match_type') == 'triad']
    
    # Verify expected pairs
    if not test_scenario.get("should_fail", False):
        expected_pairs = test_scenario.get("expected_pairs", 0)
        if len(pairs) != expected_pairs:
            results["passed"] = False
            results["errors"].append(f"Expected {expected_pairs} pairs, got {len(pairs)}")
        
        # Verify expected triad
        expected_triad = test_scenario.get("expected_triad", False)
        has_triad = len(triads) > 0
        if expected_triad and not has_triad:
            results["passed"] = False
            results["errors"].append("Expected triad but none found")
        elif not expected_triad and has_triad:
            results["passed"] = False
            results["errors"].append("Unexpected triad found")
    
    # Check history file
    history_file = test_dir / "match_history.json"
    if history_file.exists() and not test_scenario.get("should_fail", False):
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            if not isinstance(history, dict):
                results["warnings"].append("History file is not a valid dictionary")
        except json.JSONDecodeError:
            results["warnings"].append("History file is not valid JSON")
    
    return results


def run_test(test_scenario, test_num):
    """Run a single test scenario."""
    print(f"\n{'='*60}")
    print(f"Test {test_num}: {test_scenario['name']}")
    print(f"{'='*60}")
    
    # Setup test environment
    test_dir = setup_test(test_scenario, test_num)
    print(f"Test directory: {test_dir}")
    
    # Change to test directory and run matching
    original_dir = os.getcwd()
    try:
        os.chdir(test_dir)
        print(f"\nRunning matching algorithm...")
        run_matching(
            users_csv="users.csv",
            history_json="match_history.json",
            output_csv="matches_current_month.csv"
        )
    except Exception as e:
        if test_scenario.get("should_fail", False):
            print(f"✓ Expected failure: {e}")
            return True
        else:
            print(f"✗ Unexpected error: {e}")
            return False
    finally:
        os.chdir(original_dir)
    
    # Verify results
    results = verify_results(test_dir, test_scenario)
    
    if results["passed"]:
        print("✓ Test PASSED")
    else:
        print("✗ Test FAILED")
        for error in results["errors"]:
            print(f"  Error: {error}")
    
    if results["warnings"]:
        for warning in results["warnings"]:
            print(f"  Warning: {warning}")
    
    return results["passed"]


def main():
    """Run all test scenarios."""
    print("Monthly Matching Algorithm - Test Runner")
    print("=" * 60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Run tests
    passed = 0
    failed = 0
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        try:
            if run_test(scenario, i):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {i} crashed: {e}")
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    print(f"Total tests: {len(TEST_SCENARIOS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed/len(TEST_SCENARIOS)*100:.1f}%")
    print(f"\nTest outputs saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
