#!/usr/bin/env python3
"""
Monthly Random Matching Algorithm
Matches individuals into pairs (1:1) while avoiding previous matches.
Uses NetworkX for graph-based maximum cardinality matching.
"""

import csv
import json
import os
import random
import hashlib
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
import networkx as nx


def load_users(csv_path: str) -> List[Dict[str, str]]:
    """
    Load users from CSV file.
    
    Supports two CSV formats:
    1. Simple format: id, name, email
    2. Survey format: Timestamp, Email Address, Please provide your preferred first and last name., ...
    
    Args:
        csv_path: Path to the users CSV file
        
    Returns:
        List of user dictionaries with id, name, email
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If required columns are missing
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Users file not found: {csv_path}")
    
    users = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        if not fieldnames:
            raise ValueError("CSV file appears to be empty or invalid")
        
        # Check which format we're using
        has_simple_format = all(field in fieldnames for field in ['id', 'name', 'email'])
        has_survey_format = all(field in fieldnames for field in ['Email Address', 'Please provide your preferred first and last name.'])
        
        if not has_simple_format and not has_survey_format:
            raise ValueError(
                "CSV must contain either:\n"
                "  - Simple format: 'id', 'name', 'email'\n"
                "  - Survey format: 'Email Address', 'Please provide your preferred first and last name.'"
            )
        
        seen_emails = set()  # Track duplicates
        
        for row in reader:
            if has_simple_format:
                # Simple format
                user_id = row['id'].strip()
                name = row['name'].strip()
                email = row['email'].strip()
            else:
                # Survey format
                email = row['Email Address'].strip()
                name = row['Please provide your preferred first and last name.'].strip()
                
                # Generate ID from email (using hash for consistency)
                # Use first 8 characters of MD5 hash for shorter IDs
                email_lower = email.lower()
                user_id = hashlib.md5(email_lower.encode('utf-8')).hexdigest()[:8]
            
            # Skip empty rows
            if not email or not name:
                continue
            
            # Check for duplicate emails
            if email.lower() in seen_emails:
                print(f"Warning: Duplicate email found: {email}. Skipping.")
                continue
            seen_emails.add(email.lower())
            
            users.append({
                'id': user_id,
                'name': name,
                'email': email
            })
    
    return users


def load_match_history(json_path: str) -> Dict[str, Set[str]]:
    """
    Load match history from JSON file.
    
    Args:
        json_path: Path to the match history JSON file
        
    Returns:
        Dictionary mapping user_id -> set of user_ids they've matched with
    """
    if not os.path.exists(json_path):
        return {}
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
            # Convert lists back to sets for efficient lookup
            return {user_id: set(matched_ids) for user_id, matched_ids in history.items()}
    except (json.JSONDecodeError, IOError):
        # If file is corrupted or empty, return empty history
        return {}


def save_match_history(history: Dict[str, Set[str]], json_path: str) -> None:
    """
    Save match history to JSON file.
    
    Args:
        history: Dictionary mapping user_id -> set of user_ids they've matched with
        json_path: Path to save the JSON file
    """
    # Convert sets to lists for JSON serialization
    serializable_history = {
        user_id: list(matched_ids) 
        for user_id, matched_ids in history.items()
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_history, f, indent=2, sort_keys=True)


def archive_match_history(json_path: str) -> None:
    """
    Archive the current match history before resetting.
    
    Args:
        json_path: Path to the match history JSON file
    """
    if not os.path.exists(json_path):
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = json_path.replace('.json', f'_archive_{timestamp}.json')
    
    try:
        os.rename(json_path, archive_path)
        print(f"Archived match history to: {archive_path}")
    except OSError as e:
        print(f"Warning: Could not archive history: {e}")


def build_compatibility_graph(users: List[Dict[str, str]], 
                              history: Dict[str, Set[str]]) -> nx.Graph:
    """
    Build a graph where:
    - Nodes = People
    - Edges = Possible matches (only if they haven't matched before)
    
    Args:
        users: List of user dictionaries
        history: Match history dictionary
        
    Returns:
        NetworkX graph with edges only between compatible (unmatched) pairs
    """
    G = nx.Graph()
    
    # Add all users as nodes
    for user in users:
        G.add_node(user['id'], name=user['name'], email=user['email'])
    
    # Add edges only between users who haven't matched before
    user_ids = [user['id'] for user in users]
    for i, user1 in enumerate(user_ids):
        for user2 in user_ids[i+1:]:
            # Check if they've matched before
            user1_matches = history.get(user1, set())
            user2_matches = history.get(user2, set())
            
            # Add edge only if they haven't matched
            if user2 not in user1_matches and user1 not in user2_matches:
                G.add_edge(user1, user2)
    
    return G


def find_maximum_matching(G: nx.Graph) -> Set[Tuple[str, str]]:
    """
    Find maximum cardinality matching using NetworkX.
    
    This ensures optimal pairing and prevents greedy errors where
    early matches leave others with no valid options.
    
    Args:
        G: NetworkX graph with compatible pairs as edges
        
    Returns:
        Set of tuples representing matched pairs (user_id1, user_id2)
        Tuples are sorted for consistency.
    """
    # NetworkX's max_weight_matching with maxcardinality=True returns a set
    # Format: {(node1, node2), (node3, node4), ...}
    matching_set = nx.max_weight_matching(G, maxcardinality=True)
    
    # Convert to set of sorted tuples for consistency
    # Sorting ensures (A, B) and (B, A) are treated the same
    final_matching = set()
    for node1, node2 in matching_set:
        # Sort to ensure consistent tuple ordering
        pair = tuple(sorted([node1, node2]))
        final_matching.add(pair)
    
    return final_matching


def is_matching_possible(users: List[Dict[str, str]], 
                        history: Dict[str, Set[str]]) -> bool:
    """
    Check if it's mathematically possible to create valid matches.
    
    Args:
        users: List of user dictionaries
        history: Match history dictionary
        
    Returns:
        True if matching is possible, False otherwise
    """
    if len(users) < 2:
        return False
    
    # Build graph and check if maximum matching covers all or all-but-one users
    G = build_compatibility_graph(users, history)
    matching = find_maximum_matching(G)
    
    matched_users = set()
    for pair in matching:
        matched_users.update(pair)
    
    # For even number: all must be matched
    # For odd number: all but one must be matched
    unmatched_count = len(users) - len(matched_users)
    
    return unmatched_count <= 1


def create_triad(matches: Set[Tuple[str, str]], 
                all_users: List[Dict[str, str]], 
                matched_users: Set[str],
                history: Dict[str, Set[str]]) -> Optional[Tuple[str, str, str]]:
    """
    Create a triad (group of 3) from the remaining unmatched person.
    Selects a pair where the unmatched person is compatible with both members.
    
    Args:
        matches: Set of matched pairs
        all_users: List of all users
        matched_users: Set of user IDs that are already matched
        history: Match history dictionary to check compatibility
        
    Returns:
        Tuple of (user1_id, user2_id, user3_id) or None if no triad needed
    """
    # Find the unmatched user
    all_user_ids = {user['id'] for user in all_users}
    unmatched = all_user_ids - matched_users
    
    if not unmatched:
        return None
    
    unmatched_id = unmatched.pop()
    unmatched_history = history.get(unmatched_id, set())
    
    # Find a compatible pair (where unmatched person hasn't matched with both)
    compatible_pairs = []
    for pair in matches:
        user1, user2 = pair
        # Check if unmatched person is compatible with both members
        if user1 not in unmatched_history and user2 not in unmatched_history:
            compatible_pairs.append(pair)
    
    # If no compatible pair found, use any pair (triad will be created anyway)
    # This handles edge cases where reset might be needed next time
    if compatible_pairs:
        pair = random.choice(compatible_pairs)
    elif matches:
        pair = random.choice(list(matches))
    else:
        return None
    
    return (pair[0], pair[1], unmatched_id)


def update_match_history(history: Dict[str, Set[str]], 
                        matches: Set[Tuple[str, str]], 
                        triad: Optional[Tuple[str, str, str]] = None) -> None:
    """
    Update match history with new matches.
    
    Args:
        history: Match history dictionary (modified in place)
        matches: Set of matched pairs
        triad: Optional triad tuple (user1, user2, user3)
    """
    # Update history for regular pairs
    for user1, user2 in matches:
        if user1 not in history:
            history[user1] = set()
        if user2 not in history:
            history[user2] = set()
        
        history[user1].add(user2)
        history[user2].add(user1)
    
    # Update history for triad (each person matches with the other two)
    if triad:
        user1, user2, user3 = triad
        for user in [user1, user2, user3]:
            if user not in history:
                history[user] = set()
        
        # Each person in triad matches with the other two
        history[user1].add(user2)
        history[user1].add(user3)
        history[user2].add(user1)
        history[user2].add(user3)
        history[user3].add(user1)
        history[user3].add(user2)


def save_matches_to_csv(matches: Set[Tuple[str, str]], 
                        triad: Optional[Tuple[str, str, str]], 
                        users: List[Dict[str, str]], 
                        output_path: str) -> None:
    """
    Save matches to CSV file.
    
    Args:
        matches: Set of matched pairs
        triad: Optional triad tuple
        users: List of all users (for name/email lookup)
        output_path: Path to save the CSV file
    """
    # Create lookup dictionary for user info
    user_lookup = {user['id']: user for user in users}
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['person1_id', 'person1_name', 'person1_email', 
                        'person2_id', 'person2_name', 'person2_email', 
                        'match_type'])
        
        # Write regular pairs
        for user1_id, user2_id in sorted(matches):
            user1 = user_lookup[user1_id]
            user2 = user_lookup[user2_id]
            writer.writerow([
                user1_id, user1['name'], user1['email'],
                user2_id, user2['name'], user2['email'],
                'pair'
            ])
        
        # Write triad if exists
        if triad:
            user1_id, user2_id, user3_id = triad
            user1 = user_lookup[user1_id]
            user2 = user_lookup[user2_id]
            user3 = user_lookup[user3_id]
            
            # Write triad as three rows (each person with the other two)
            writer.writerow([
                user1_id, user1['name'], user1['email'],
                user2_id, user2['name'], user2['email'],
                'triad'
            ])
            writer.writerow([
                user1_id, user1['name'], user1['email'],
                user3_id, user3['name'], user3['email'],
                'triad'
            ])
            writer.writerow([
                user2_id, user2['name'], user2['email'],
                user3_id, user3['name'], user3['email'],
                'triad'
            ])


def run_matching(users_csv: str = 'users.csv',
                history_json: str = 'match_history.json',
                output_csv: str = 'matches_current_month.csv') -> None:
    """
    Main function to run the matching algorithm.
    
    This function:
    1. Loads users from CSV
    2. Loads match history from JSON
    3. Checks if matching is possible
    4. If not possible, archives history and resets
    5. Builds compatibility graph using NetworkX
    6. Finds maximum cardinality matching
    7. Handles odd numbers by creating a triad
    8. Updates history and saves results
    
    Args:
        users_csv: Path to input CSV file
        history_json: Path to match history JSON file
        output_csv: Path to output CSV file
    """
    print("Starting matching algorithm...")
    
    # Load users
    try:
        users = load_users(users_csv)
        print(f"Loaded {len(users)} users from {users_csv}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    if len(users) < 2:
        print("Error: Need at least 2 users to create matches")
        return
    
    # Load match history
    history = load_match_history(history_json)
    print(f"Loaded match history for {len(history)} users")
    
    # Check if matching is possible
    if not is_matching_possible(users, history):
        print("Warning: Matching is impossible with current history.")
        print("Archiving history and resetting for fresh start...")
        archive_match_history(history_json)
        history = {}  # Reset history
    
    # Build compatibility graph
    # Graph Theory Approach: Nodes = People, Edges = Possible matches
    G = build_compatibility_graph(users, history)
    print(f"Built compatibility graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} possible edges")
    
    # Find maximum cardinality matching
    # This prevents "greedy" errors by finding optimal pairing
    matches = find_maximum_matching(G)
    print(f"Found {len(matches)} pairs")
    
    # Handle odd number case (create triad)
    matched_users = set()
    for pair in matches:
        matched_users.update(pair)
    
    triad = None
    if len(users) % 2 == 1:  # Odd number
        triad = create_triad(matches, users, matched_users, history)
        if triad:
            print(f"Created triad: {triad}")
            # Remove the pair that became part of the triad
            pair_to_remove = tuple(sorted([triad[0], triad[1]]))
            if pair_to_remove in matches:
                matches.remove(pair_to_remove)
    
    # Update match history
    update_match_history(history, matches, triad)
    save_match_history(history, history_json)
    print(f"Updated match history")
    
    # Save matches to CSV
    save_matches_to_csv(matches, triad, users, output_csv)
    print(f"Saved matches to {output_csv}")
    
    print("Matching complete!")


if __name__ == '__main__':
    # Set random seed for reproducibility (optional)
    # random.seed(42)
    
    run_matching()
