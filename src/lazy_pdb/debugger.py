"""Core debugger implementation."""

import sys
from typing import Any

from lazy_pdb.output_capture import get_capture, get_captured_output
from lazy_pdb.tui import DebuggerApp


def set_trace(*args: Any, **kwargs: Any) -> None:
    """
    Entry point for the debugger, compatible with sys.breakpointhook.

    This function is called when breakpoint() is invoked in user code,
    or when PYTHONBREAKPOINT=lazy_pdb.set_trace is set.
    """
    # Ensure output capture is running
    capture = get_capture()
    if not capture.is_capturing:
        capture.start()

    # Get the caller's frame (the frame that called breakpoint())
    frame = sys._getframe(1)

    # Get captured output
    stdout_output, stderr_output = get_captured_output()

    # Launch the TUI debugger
    app = DebuggerApp(frame, stdout_output, stderr_output)
    app.run()

    # Handle step modes after TUI exits
    if app.step_mode == "quit":
        sys.exit(0)
