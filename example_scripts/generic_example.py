#!/usr/bin/env python3
"""Example script for testing the lazy-pdb debugger."""


def calculate_fibonacci(n: int) -> list[int]:
    """Calculate the first n Fibonacci numbers."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]

    fib = [0, 1]
    breakpoint()  # Test debugger inside a function

    for i in range(2, n):
        next_val = fib[i - 1] + fib[i - 2]
        fib.append(next_val)

    return fib


def process_data(items: list[str]) -> dict[str, int]:
    """Process a list of items and count their lengths."""
    result = {}

    for item in items:
        length = len(item)
        result[item] = length

    breakpoint()  # Test debugger with local variables

    return result


class Person:
    """A simple person class for testing object inspection."""

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self) -> str:
        """Return a greeting message."""
        message = f"Hello, I'm {self.name} and I'm {self.age} years old"
        breakpoint()  # Test debugger inside a method
        return message

    def __repr__(self) -> str:
        return f"Person(name={self.name!r}, age={self.age})"


def main() -> None:
    """Main function to demonstrate various debugging scenarios."""
    print("=== Testing lazy-pdb ===\n")

    # Test 1: Simple variables
    x = 42
    y = "hello world"
    z = [1, 2, 3, 4, 5]

    print("Test 1: Simple variables")
    print(f"x = {x}, y = {y}, z = {z}")
    breakpoint()  # Test debugger with simple variables

    # Test 2: Function with loop
    print("\nTest 2: Fibonacci calculation")
    fib_numbers = calculate_fibonacci(10)
    print(f"First 10 Fibonacci numbers: {fib_numbers}")

    # Test 3: Dictionary processing
    print("\nTest 3: Processing data")
    items = ["apple", "banana", "cherry", "date"]
    lengths = process_data(items)
    print(f"Item lengths: {lengths}")

    # Test 4: Object-oriented code
    print("\nTest 4: Object inspection")
    person = Person("Alice", 30)
    greeting = person.greet()
    print(greeting)

    # Test 5: Nested data structures
    print("\nTest 5: Nested structures")
    complex_data = {
        "users": [
            {"name": "Alice", "scores": [85, 90, 88]},
            {"name": "Bob", "scores": [92, 87, 95]},
        ],
        "metadata": {"version": "1.0", "timestamp": "2025-11-22"},
    }
    breakpoint()  # Test debugger with complex nested structures
    print(f"Complex data: {complex_data}")

    print("\n=== All tests completed ===")


if __name__ == "__main__":
    main()
