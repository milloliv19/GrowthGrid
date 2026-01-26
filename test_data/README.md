# Test Data for Monthly Matching Algorithm

This directory contains test datasets for validating the matching algorithm.

## Directory Structure

- `users_*.csv` - Various user CSV files for different scenarios
- `history_*.json` - Various match history files for different test states

## Test Files

### User Files

- **users_base_6.csv** - 6 users (even number, base test set)
- **users_base_8.csv** - 8 users (even number, larger set)
- **users_odd_7.csv** - 7 users (odd number, tests triad creation)
- **users_min_2.csv** - 2 users (minimum valid)
- **users_min_3.csv** - 3 users (minimum odd, tests triad)
- **users_single.csv** - 1 user (should fail)
- **users_empty.csv** - Empty CSV (should fail)
- **users_large_20.csv** - 20 users (performance/scalability test)
- **users_new_added.csv** - 8 users (for testing new user addition)
- **users_special_chars.csv** - Users with special characters in names/emails

### History Files

- **history_empty.json** - Empty history (first run scenario)
- **history_partial.json** - Some users have previous matches
- **history_asymmetric.json** - Asymmetric history (A has B, but B doesn't have A)
- **history_near_exhaustion.json** - Most pairs exhausted, few remaining
- **history_complete_exhaustion_4.json** - All pairs exhausted for 4 users
- **history_complete_exhaustion_6.json** - All pairs exhausted for 6 users
- **history_orphaned.json** - History contains users not in current CSV
- **history_chain.json** - Chain pattern (A-B-C-D-E-F)
- **history_star.json** - Star pattern (1 connected to 2,3,4,5; 6 isolated)
- **history_bipartite.json** - Bipartite graph (group 1: 1,2,3; group 2: 4,5,6)
- **history_with_triad.json** - History includes previous triad
- **history_corrupted.json** - Invalid JSON (tests error handling)

## Running Tests

Use the `test_runner.py` script in the parent directory:

```bash
python test_runner.py
```

This will:
1. Run all test scenarios
2. Create test output directories
3. Verify results match expectations
4. Generate a summary report

## Manual Testing

To manually test a specific scenario:

1. Copy the desired `users_*.csv` to `users.csv`
2. Copy the desired `history_*.json` to `match_history.json` (or delete it for no history)
3. Run: `python match_maker.py`
4. Check `matches_current_month.csv` and `match_history.json` for results

## Test Scenarios Covered

### Basic Functionality
- First run (no history)
- Normal matching (even/odd numbers)
- Minimum valid cases

### Edge Cases
- Single user (should fail)
- Empty CSV (should fail)
- Small numbers (2, 3 users)

### History Scenarios
- New users added
- Users removed
- Asymmetric history
- Orphaned users in history
- Partial history

### Reset Scenarios
- Complete exhaustion
- Near exhaustion
- Impossible matching

### Graph Theory Patterns
- Complete graph
- Star pattern
- Chain pattern
- Bipartite graph

### Data Integrity
- Special characters
- Large datasets
- Corrupted files
