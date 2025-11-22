"""Core debugger implementation."""

import sys
from typing import Any


def set_trace(*args: Any, **kwargs: Any) -> None:
    """
    Entry point for the debugger, compatible with sys.breakpointhook.

    This function is called when breakpoint() is invoked in user code,
    or when PYTHONBREAKPOINT=lazy_pdb.set_trace is set.
    """
    # Get the caller's frame (the frame that called breakpoint())
    frame = sys._getframe(1)

    # TODO: Launch the TUI debugger here
    print(f"lazy-pdb breakpoint hit at {frame.f_code.co_filename}:{frame.f_lineno}")
    print("TUI debugger not yet implemented")

    # For now, fall back to pdb
    import pdb

    # Use Pdb().set_trace() with the caller's frame
    debugger = pdb.Pdb()
    debugger.set_trace(frame)
