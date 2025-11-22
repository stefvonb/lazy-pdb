"""Test script to verify interactive features in the debugger."""

def outer_function(x, y):
    """Outer function for testing call stack."""
    print(f"Outer function called with x={x}, y={y}")
    result = inner_function(x * 2, y * 2)
    return result + 10

def inner_function(a, b):
    """Inner function for testing call stack and variables."""
    print(f"Inner function called with a={a}, b={b}")

    # Local variables to test
    local_var1 = "Hello, World!"
    local_var2 = [1, 2, 3, 4, 5]
    local_dict = {"key1": "value1", "key2": "value2", "nested": {"inner": "data"}}

    # Global variables are also available
    print("About to hit breakpoint...")
    breakpoint()

    return a + b

# Global variables to test
GLOBAL_CONSTANT = "This is a global constant"
global_list = [10, 20, 30, 40, 50]

print("Starting test...")
result = outer_function(5, 10)
print(f"Final result: {result}")
