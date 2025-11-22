#!/usr/bin/env python3
"""Example script to test debugger with long-running functions."""

import time


def slow_calculation(n: int) -> int:
    """Simulate a slow calculation that takes several seconds."""
    print(f"Starting slow calculation with n={n}")
    breakpoint()  # Debug before the slow operation

    print("Processing... this will take 5 seconds")
    time.sleep(5)  # Simulate long-running operation

    result = n * 2
    print(f"Calculation complete! Result: {result}")
    breakpoint()  # Debug after the slow operation

    return result


def process_with_delay(items: list[str]) -> list[str]:
    """Process items with a delay between each."""
    print(f"\nProcessing {len(items)} items with delays...")
    results = []

    for i, item in enumerate(items, 1):
        print(f"  Processing item {i}/{len(items)}: {item}")
        time.sleep(2)  # 2 second delay per item
        results.append(item.upper())

    breakpoint()  # Debug after processing all items
    return results


def main() -> None:
    """Main function to test long-running operations."""
    print("=== Testing lazy-pdb with long-running functions ===\n")

    # Test 1: Single slow calculation
    print("Test 1: Slow calculation")
    result = slow_calculation(42)
    print(f"Result: {result}\n")

    # Test 2: Processing multiple items with delays
    print("Test 2: Processing with delays")
    items = ["apple", "banana", "cherry"]
    processed = process_with_delay(items)
    print(f"Processed: {processed}\n")

    print("=== All tests completed ===")


if __name__ == "__main__":
    main()
