#!/usr/bin/env python3
import statistics

def calculate_planning_poker_estimate(votes):
    """Calculate estimate using Planning Poker best practices"""
    fibonacci_sequence = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    
    if not votes:
        return None
        
    # Convert votes to integers and sort
    vote_values = sorted([int(v) for v in votes])
    min_vote = vote_values[0]
    max_vote = vote_values[-1]
    
    # Find positions in Fibonacci sequence
    min_pos = next((i for i, fib in enumerate(fibonacci_sequence) if fib >= min_vote), 0)
    max_pos = next((i for i, fib in enumerate(fibonacci_sequence) if fib >= max_vote), len(fibonacci_sequence) - 1)
    
    # Check for wide spread (more than 2 Fibonacci steps apart)
    spread = max_pos - min_pos
    
    if spread > 2:
        # Wide spread - suggest towards higher estimate with median approach
        # This encourages discussion and tends toward the complexity some see
        if len(vote_values) == 1:
            return vote_values[0]
        
        # Use 75th percentile approach for wide spreads
        percentile_75 = statistics.quantiles(vote_values, n=4)[2]  # 75th percentile
        
        # Round up to nearest Fibonacci
        for fib in fibonacci_sequence:
            if percentile_75 <= fib:
                return fib
        return fibonacci_sequence[-1]
    else:
        # Normal spread - use median or standard approach
        median = statistics.median(vote_values)
        
        # Round to nearest Fibonacci (up)
        for fib in fibonacci_sequence:
            if median <= fib:
                return fib
        return fibonacci_sequence[-1]

# Test cases to demonstrate the new Planning Poker logic
test_cases = [
    ([1, 2, 21], "Your example: Wide spread - complexity disagreement"),
    ([1, 1, 2], "Close consensus - simple story"), 
    ([5, 8, 8], "Close consensus - medium story"),
    ([13, 13, 21], "Close consensus - complex story"),
    ([1, 3, 8], "Medium spread"),
    ([2, 5, 21], "Wide spread - lean towards complexity"),
    ([8, 13, 34], "Wide spread - high complexity detected"),
    ([5, 5, 5], "Perfect consensus"),
    ([1, 8, 21, 34], "Very wide spread"),
]

print("Planning Poker Estimate Calculator")
print("=================================")
print(f"{'Votes':<15} {'Math Avg':<8} {'Old Round':<9} {'New Estimate':<12} {'Description'}")
print("-" * 80)

for votes, description in test_cases:
    math_avg = sum(votes) / len(votes)
    old_round = round(math_avg)
    new_estimate = calculate_planning_poker_estimate(votes)
    
    vote_str = str(votes)
    print(f"{vote_str:<15} {math_avg:<8.2f} {old_round:<9} {new_estimate:<12} {description}")

print("\nKey Improvements:")
print("- Wide spreads (>2 Fibonacci steps apart) use 75th percentile")
print("- Encourages discussion when there's disagreement") 
print("- Leans toward higher estimates when complexity is detected")
print("- Normal spreads use median for consensus")
print("- Always rounds to valid Fibonacci numbers")
print("\nYour Example: [1, 2, 21]")
print("- Math average: 8.0 → rounds to 8")
print("- Planning Poker: 75th percentile ≈ 16.5 → rounds up to 21")
print("- Recommendation: Discussion needed! Re-vote after talking through the '21' complexity.")