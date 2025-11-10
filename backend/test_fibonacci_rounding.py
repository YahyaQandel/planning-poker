#!/usr/bin/env python3

def round_to_fibonacci(value):
    """Round to nearest Fibonacci number, always rounding up"""
    fibonacci_sequence = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    
    # Find the closest Fibonacci numbers
    for fib in fibonacci_sequence:
        if value <= fib:
            return fib
    
    # If value is larger than our sequence, return the largest
    return fibonacci_sequence[-1]

# Test cases to demonstrate the new rounding behavior
test_cases = [
    (1.0, "Should round to 1"),
    (1.5, "Should round up to 2"),
    (2.0, "Should round to 2"),
    (2.5, "Should round up to 3"),
    (4.0, "Should round up to 5"),
    (4.9, "Should round up to 5"),
    (5.0, "Should round to 5"),
    (5.1, "Should round up to 8"),
    (7.25, "Should round up to 8 (your example)"),
    (12.0, "Should round up to 13"),
    (12.9, "Should round up to 13"),
    (13.0, "Should round to 13"),
    (13.1, "Should round up to 21"),
    (25.0, "Should round up to 34"),
    (100.0, "Should cap at 89"),
]

print("Testing Fibonacci Rounding Logic")
print("=" * 50)
print(f"{'Average':<8} {'Old Round':<10} {'New Fibonacci':<15} {'Description'}")
print("-" * 70)

for average, description in test_cases:
    old_round = round(average)
    new_round = round_to_fibonacci(average)
    print(f"{average:<8} {old_round:<10} {new_round:<15} {description}")

print("\nKey Changes:")
print("- Always rounds UP to the nearest Fibonacci number")
print("- No more inconsistent rounding (e.g., 7.25 → 8 instead of 7)")
print("- Follows Planning Poker best practices")
print("- Valid Fibonacci sequence: 1, 2, 3, 5, 8, 13, 21, 34, 55, 89")