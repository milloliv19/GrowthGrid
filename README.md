# Monthly Random Matching Algorithm

A Python script that performs monthly random matching for groups of people (e.g., coffee chats) using graph theory to ensure optimal pairings while avoiding previous matches.

## Features

- **No Repeats**: Ensures people are never matched with someone they've matched with before
- **Graph Theory Approach**: Uses NetworkX's maximum cardinality matching algorithm for optimal pairing
- **Automatic Reset**: If matching becomes impossible, archives history and starts fresh
- **Odd Number Handling**: Creates triads (groups of 3) when there's an odd number of participants
- **New User Support**: Seamlessly handles new users added to the CSV

## Installation

1. Install the required dependency:
```bash
pip install -r requirements.txt
```

## Usage

1. Prepare your `users.csv` file with columns: `id`, `name`, `email`
2. Run the script:
```bash
python match_maker.py
```

The script will:
- Read users from `users.csv`
- Load previous match history from `match_history.json` (created automatically if missing)
- Generate new matches avoiding previous pairings
- Save results to `matches_current_month.csv`
- Update `match_history.json` with new matches

## Input Format

`users.csv` supports two formats:

### Format 1: Simple Format
Must contain these columns:
- `id`: Unique identifier for each user
- `name`: User's name
- `email`: User's email address

Example:
```csv
id,name,email
1,Alice Johnson,alice@example.com
2,Bob Smith,bob@example.com
```

### Format 2: Survey Format (Default)
Must contain these columns:
- `Email Address`: User's email address
- `Please provide your preferred first and last name.`: User's name
- Other columns (Timestamp, location, etc.) are ignored

Example:
```csv
Timestamp,Email Address,Please provide your preferred first and last name.,What is your office location?,Superpower,Growth Zone
1/21/2026 14:55:00,olivia.miller@braze.com,Olivia Miller,London,Wine Evaluation,Crochet
1/21/2026 14:56:00,alice.johnson@example.com,Alice Johnson,New York,Problem Solving,Public Speaking
```

**Note:** When using the survey format, user IDs are automatically generated from email addresses (using MD5 hash) to ensure consistency across runs.

## Output Format

`matches_current_month.csv` contains:
- `person1_id`, `person1_name`, `person1_email`
- `person2_id`, `person2_name`, `person2_email`
- `match_type`: Either "pair" or "triad"

## How It Works

1. **Graph Construction**: Creates a graph where nodes are people and edges represent possible matches (only between people who haven't matched before)
2. **Maximum Matching**: Uses NetworkX's maximum cardinality matching algorithm to find the optimal set of pairs
3. **Triad Handling**: If there's an odd number of people, one pair is converted into a triad (group of 3)
4. **History Management**: Tracks all previous matches to prevent repeats

## Customization

You can customize file paths by modifying the `run_matching()` function call:

```python
run_matching(
    users_csv='custom_users.csv',
    history_json='custom_history.json',
    output_csv='custom_output.csv'
)
```
