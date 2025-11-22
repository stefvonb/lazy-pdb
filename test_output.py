"""Test script to verify output capture in the debugger."""

print("Line 1: Before breakpoint")
print("Line 2: Still before breakpoint")
print("Line 3: Last line before breakpoint")

breakpoint()

print("Line 4: After breakpoint")
print("Line 5: Final line")
