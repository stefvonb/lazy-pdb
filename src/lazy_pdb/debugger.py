"""Core debugger implementation."""

import sys
from typing import Any

from lazy_pdb.tui import DebuggerApp


def set_trace(*args: Any, **kwargs: Any) -> None:
    """
    Entry point for the debugger, compatible with sys.breakpointhook.

    This function is called when breakpoint() is invoked in user code,
    or when PYTHONBREAKPOINT=lazy_pdb.set_trace is set.
    """
    # Get the caller's frame (the frame that called breakpoint())
    frame = sys._getframe(1)

    # Launch the TUI debugger
    app = DebuggerApp(frame)
    app.run()

    # Handle step modes after TUI exits
    if app.step_mode == "quit":
        sys.exit(0)
