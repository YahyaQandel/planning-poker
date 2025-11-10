#!/usr/bin/env python3

def get_discussion_suggestion(votes):
    """Generate discussion suggestion when there are wide spreads in votes"""
    if not votes or len(votes) < 2:
        return None
        
    # Convert to integers and find min/max
    vote_values = [int(v) for v in votes if v not in ['?', 'coffee']]
    
    if not vote_values:
        return None
        
    min_vote = min(vote_values)
    max_vote = max(vote_values)
    
    # Find Fibonacci positions
    fibonacci_sequence = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    min_pos = next((i for i, fib in enumerate(fibonacci_sequence) if fib >= min_vote), 0)
    max_pos = next((i for i, fib in enumerate(fibonacci_sequence) if fib >= max_vote), len(fibonacci_sequence) - 1)
    
    # Check for wide spread (more than 2 Fibonacci steps apart)
    spread = max_pos - min_pos
    
    if spread > 2:
        # Mock finding participants with min and max votes
        # In real app, this would come from the database
        participants = [
            {'vote': 1, 'username': 'Alice'},
            {'vote': 2, 'username': 'Bob'},
            {'vote': 21, 'username': 'Charlie'},
        ]
        
        min_voters = [p['username'] for p in participants if p['vote'] == min_vote]
        max_voters = [p['username'] for p in participants if p['vote'] == max_vote]
        
        min_voter = min_voters[0] if min_voters else "someone"
        max_voter = max_voters[0] if max_voters else "someone"
        
        return {
            "message": f"Wide spread detected! {min_voter} (voted {min_vote}) and {max_voter} (voted {max_vote}) should discuss the story complexity.",
            "min_vote": min_vote,
            "max_vote": max_vote,
            "min_voter": min_voter,
            "max_voter": max_voter,
            "spread_level": "high" if spread > 4 else "medium"
        }
    
    return None

# Test cases
test_cases = [
    ([1, 2, 21], "Your original example"),
    ([1, 3, 34], "Very wide spread"),
    ([5, 8, 13], "Normal spread - no message"),
    ([1, 1, 2], "Consensus - no message"),
    ([2, 5, 21], "Medium wide spread"),
]

print("Discussion Message Generator")
print("===========================")

for votes, description in test_cases:
    message = get_discussion_suggestion(votes)
    
    print(f"\nVotes: {votes} ({description})")
    if message:
        print(f"📢 {message['message']}")
        print(f"   Spread Level: {message['spread_level']}")
        print(f"   UI will show: Orange banner suggesting discussion")
    else:
        print("✅ No discussion needed - votes are close enough")

print("\nUI Display:")
print("- Shows orange banner in the Average Calculation modal")
print("- Identifies the two people who should discuss")
print("- Encourages discussion before confirming points")
print("- Re-vote button available for after discussion")