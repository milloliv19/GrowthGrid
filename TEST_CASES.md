# Test Cases for Monthly Matching Algorithm

## 1. Basic Functionality Tests

### 1.1 First Run (No History)
- **Setup**: Empty `match_history.json` or missing file
- **Users**: 6 users (even number)
- **Expected**: All users matched into 3 pairs, no repeats
- **Verify**: History file created, all users appear in output

### 1.2 Normal Matching (Even Number)
- **Setup**: Existing history with some previous matches
- **Users**: 8 users
- **Expected**: 4 pairs, no previous matches repeated
- **Verify**: Each pair is new, history updated correctly

### 1.3 Normal Matching (Odd Number)
- **Setup**: Existing history
- **Users**: 7 users
- **Expected**: 2 pairs + 1 triad (3 people)
- **Verify**: Triad properly recorded in history (all 3 matched with each other)

## 2. Small Number Edge Cases

### 2.1 Minimum Valid (2 Users)
- **Setup**: No history
- **Users**: 2 users
- **Expected**: 1 pair created
- **Verify**: Both users matched, history updated

### 2.2 Minimum Odd (3 Users)
- **Setup**: No history
- **Users**: 3 users
- **Expected**: 1 triad (all 3 together)
- **Verify**: All 3 users matched with each other in history

### 2.3 Single User (Should Fail)
- **Setup**: Any history
- **Users**: 1 user
- **Expected**: Error message, no matching performed
- **Verify**: Script exits gracefully with error

### 2.4 Empty CSV (Should Fail)
- **Setup**: Any history
- **Users**: 0 users (empty CSV or header only)
- **Expected**: Error message
- **Verify**: Script handles gracefully

## 3. History Edge Cases

### 3.1 New Users Added
- **Setup**: History with 4 existing users, add 2 new users
- **Users**: 6 total (4 old + 2 new)
- **Expected**: New users can match with anyone, old users respect history
- **Verify**: New users appear in matches, no old matches repeated

### 3.2 Users Removed from CSV
- **Setup**: History with 6 users, remove 2 from CSV
- **Users**: 4 users (2 removed)
- **Expected**: Matching works with remaining users, removed users' history ignored
- **Verify**: No errors, valid matches created

### 3.3 Partial History
- **Setup**: Some users have history, others don't
- **Users**: 6 users (3 with history, 3 without)
- **Expected**: Users with history respect it, new users can match freely
- **Verify**: No previous matches repeated

### 3.4 Asymmetric History
- **Setup**: User A has B in history, but B doesn't have A
- **Users**: 4+ users including A and B
- **Expected**: A and B should NOT match (check both directions)
- **Verify**: Algorithm checks both `A in B's history` and `B in A's history`

### 3.5 History with Orphaned Users
- **Setup**: History contains user IDs not in current CSV
- **Users**: 4 users (but history has 6 users)
- **Expected**: Orphaned history ignored, matching proceeds normally
- **Verify**: No errors, valid matches created

## 4. Reset Scenarios

### 4.1 Complete Exhaustion (Everyone Matched Everyone)
- **Setup**: History where every user has matched with every other user
- **Users**: 4 users (6 possible pairs, all exhausted)
- **Expected**: History archived, reset triggered, fresh matches created
- **Verify**: Archive file created, new matches generated, history reset

### 4.2 Near Exhaustion (Almost Everyone Matched)
- **Setup**: History where most pairs exhausted, but 1-2 valid pairs remain
- **Users**: 6 users
- **Expected**: Valid matches found, no reset needed
- **Verify**: Remaining valid pairs used, no unnecessary reset

### 4.3 Impossible Matching (Disconnected Graph)
- **Setup**: Users split into two groups where everyone in group A has matched everyone in group B, but groups internally haven't matched
- **Users**: 6 users (3 in each group)
- **Expected**: Should still find matches within groups, or reset if truly impossible
- **Verify**: Algorithm handles disconnected components correctly

### 4.4 Reset with Odd Number
- **Setup**: Complete exhaustion with odd number of users
- **Users**: 5 users (all pairs exhausted)
- **Expected**: Reset triggered, new matches + triad created
- **Verify**: Archive created, triad properly formed after reset

## 5. Triad Edge Cases

### 5.1 Triad with Compatible Pair
- **Setup**: 5 users, unmatched person hasn't matched with any pair members
- **Users**: 5 users
- **Expected**: Triad created with compatible pair
- **Verify**: All 3 triad members matched with each other in history

### 5.2 Triad with History Conflicts
- **Setup**: 5 users, unmatched person has matched with all possible pairs
- **Users**: 5 users
- **Expected**: Triad still created (as per requirement), but may need reset next time
- **Verify**: Triad formed even with conflicts, history updated

### 5.3 Triad After Reset
- **Setup**: Reset triggered, odd number of users
- **Users**: 7 users (after reset)
- **Expected**: Fresh matches + triad created
- **Verify**: Triad properly formed with fresh history

## 6. File Handling Edge Cases

### 6.1 Missing users.csv
- **Setup**: No `users.csv` file
- **Expected**: Clear error message, script exits gracefully
- **Verify**: FileNotFoundError handled properly

### 6.2 Corrupted JSON History
- **Setup**: `match_history.json` contains invalid JSON
- **Expected**: History treated as empty, matching proceeds
- **Verify**: No crash, empty history used

### 6.3 Empty JSON History
- **Setup**: `match_history.json` exists but is empty `{}`
- **Expected**: Treated as no history, matching proceeds
- **Verify**: All users can match with anyone

### 6.4 Missing CSV Columns
- **Setup**: CSV missing `id`, `name`, or `email` column
- **Expected**: Clear error message about missing columns
- **Verify**: ValueError raised with helpful message

### 6.5 Duplicate IDs in CSV
- **Setup**: CSV has duplicate `id` values
- **Expected**: Algorithm may create duplicate nodes or fail
- **Verify**: Behavior documented (may need to add validation)

### 6.6 Empty CSV Rows
- **Setup**: CSV has header but empty rows or rows with missing data
- **Expected**: Empty rows skipped or error raised
- **Verify**: Only valid rows processed

## 7. Data Integrity Tests

### 7.1 Duplicate Matches in History
- **Setup**: History has same match recorded multiple times
- **Users**: 4+ users
- **Expected**: Algorithm should still work (sets handle duplicates)
- **Verify**: No errors, matches still valid

### 7.2 Self-Matches in History
- **Setup**: History has user matching with themselves
- **Users**: 4+ users
- **Expected**: Self-matches ignored (graph won't have self-loops)
- **Verify**: No self-matches in output

### 7.3 Special Characters in Names/Emails
- **Setup**: Users with special characters: commas, quotes, newlines, unicode
- **Users**: 4+ users with special chars
- **Expected**: CSV properly escaped, no parsing errors
- **Verify**: Output CSV readable, special chars preserved

### 7.4 Very Long Names/Emails
- **Setup**: Users with extremely long names or emails
- **Users**: 4+ users
- **Expected**: No truncation, all data preserved
- **Verify**: Full data in output CSV

### 7.5 Whitespace in CSV
- **Setup**: CSV with leading/trailing whitespace in fields
- **Users**: 4+ users
- **Expected**: Whitespace stripped (code uses `.strip()`)
- **Verify**: Clean data in output

## 8. Graph Theory Edge Cases

### 8.1 Complete Graph (No History)
- **Setup**: No history, all users can match
- **Users**: 6 users
- **Expected**: Maximum matching finds 3 pairs
- **Verify**: All users matched

### 8.2 Star Graph Pattern
- **Setup**: One user (center) has matched with everyone except one person
- **Users**: 5 users
- **Expected**: Center matched with the one remaining, others matched among themselves
- **Verify**: Optimal matching found

### 8.3 Chain Pattern
- **Setup**: A matched B, B matched C, C matched D, etc. (chain)
- **Users**: 6 users in chain
- **Expected**: Matches found avoiding chain (e.g., A-C, B-D, E-F)
- **Verify**: No adjacent chain matches

### 8.4 Bipartite Scenario
- **Setup**: Two groups where everyone in group 1 has matched everyone in group 2
- **Users**: 6 users (3 in each group)
- **Expected**: Matches within groups, or reset if impossible
- **Verify**: Algorithm handles bipartite structure

## 9. Multiple Run Scenarios

### 9.1 Sequential Runs (Building History)
- **Setup**: Run 1: 6 users, no history → Run 2: Same 6 users → Run 3: Same 6 users
- **Users**: 6 users (same set)
- **Expected**: Each run creates new matches, history accumulates
- **Verify**: No repeats across 3 runs, history grows correctly

### 9.2 Adding Users Mid-Process
- **Setup**: Run 1: 4 users → Run 2: Add 2 users (6 total)
- **Users**: Growing user set
- **Expected**: New users integrated seamlessly
- **Verify**: All users matched, no errors

### 9.3 Removing Users Mid-Process
- **Setup**: Run 1: 6 users → Run 2: Remove 2 users (4 total)
- **Users**: Shrinking user set
- **Expected**: Remaining users matched, removed users' history ignored
- **Verify**: No errors, valid matches

### 9.4 Multiple Runs Until Exhaustion
- **Setup**: Run matching repeatedly with same user set
- **Users**: 4 users (6 possible pairs)
- **Expected**: After 6 runs, reset triggered
- **Verify**: Reset happens at right time, archive created

## 10. Output Validation Tests

### 10.1 CSV Output Format
- **Setup**: Any valid matching
- **Expected**: CSV has correct columns, proper formatting
- **Verify**: All required columns present, data valid

### 10.2 Triad Output Format
- **Setup**: Odd number of users
- **Expected**: Triad represented as 3 rows in CSV
- **Verify**: All 3 pairs of triad present, marked as 'triad'

### 10.3 History Persistence
- **Setup**: Run matching, check history file
- **Expected**: History JSON properly formatted, bidirectional
- **Verify**: If A matched B, both A→B and B→A in history

### 10.4 Archive File Creation
- **Setup**: Trigger reset scenario
- **Expected**: Archive file created with timestamp
- **Verify**: Archive contains previous history, original file cleared

## 11. Performance & Scalability

### 11.1 Large User Set
- **Setup**: 50+ users
- **Expected**: Algorithm completes in reasonable time
- **Verify**: No performance issues, all users matched

### 11.2 Large History
- **Setup**: 20 users with extensive history (many previous matches)
- **Expected**: Graph building and matching still efficient
- **Verify**: Completes quickly, correct results

## 12. Randomness & Determinism

### 12.1 Random Seed Test
- **Setup**: Same users, same history, different random seeds
- **Expected**: Different matchings (if multiple valid solutions exist)
- **Verify**: Randomness works, but no repeats

### 12.2 Deterministic with Seed
- **Setup**: Set random seed, run twice
- **Expected**: Same matches if seed set
- **Verify**: Reproducible results with seed

## 13. Type & Data Type Edge Cases

### 13.1 String IDs vs Numeric IDs
- **Setup**: Mix of string and numeric IDs in CSV
- **Expected**: All treated as strings, matching works
- **Verify**: No type errors, matches created

### 13.2 Numeric IDs as Strings
- **Setup**: IDs are numbers but stored as strings "1", "2", etc.
- **Expected**: Matching works correctly
- **Verify**: String comparison works, no numeric comparison issues

## 14. Concurrent/File Lock Scenarios

### 14.1 File in Use
- **Setup**: History file locked by another process
- **Expected**: Error handled gracefully
- **Verify**: Appropriate error message (may need file locking)

---

## Test Execution Priority

**Critical (Must Pass):**
- 1.1, 1.2, 1.3 (Basic functionality)
- 2.1, 2.2, 2.3, 2.4 (Small numbers)
- 3.1, 3.4 (History basics)
- 4.1 (Reset scenario)
- 5.1 (Triad basics)
- 6.1, 6.2, 6.4 (File errors)

**Important (Should Pass):**
- 3.2, 3.3, 3.5 (History edge cases)
- 4.2, 4.3 (Reset variations)
- 5.2, 5.3 (Triad edge cases)
- 7.1, 7.3 (Data integrity)
- 9.1, 9.2 (Multiple runs)

**Nice to Have:**
- 8.1-8.4 (Graph theory)
- 11.1, 11.2 (Performance)
- 12.1, 12.2 (Randomness)
