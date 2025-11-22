"""Core debugger implementation."""

import sys
from types import FrameType
from typing import Any

from lazy_pdb.output_capture import get_capture, get_captured_output
from lazy_pdb.tui import DebuggerApp


# Global debugger state
_debugger_state = {
    "mode": None,  # "step", "next", or None
    "start_frame": None,  # Frame where next/step was initiated
    "old_trace": None,  # Previous trace function
}


def _is_debugger_code(frame: FrameType) -> bool:
    """Check if the frame is from the debugger's own code."""
    filename = frame.f_code.co_filename
    # Check if it's in the lazy_pdb package source directories
    if "/src/lazy_pdb/" in filename or "\\src\\lazy_pdb\\" in filename:
        return True
    if "/site-packages/lazy_pdb/" in filename or "\\site-packages\\lazy_pdb\\" in filename:
        return True
    return False


def _trace_dispatch(frame: FrameType, event: str, arg: Any) -> Any:
    """
    Trace function for stepping through code.

    This is called by Python's tracing mechanism on each line of code.
    """
    # Skip debugger's own code - but keep tracing active
    if _is_debugger_code(frame):
        return _trace_dispatch

    mode = _debugger_state["mode"]
    start_frame = _debugger_state["start_frame"]

    if mode == "step":
        # Step mode: stop at any line in any frame
        if event == "line":
            # Stop here and show debugger
            _debugger_state["mode"] = None
            set_trace_internal(frame)
            # Check if we should continue tracing after debugger exits
            # If mode was set again (step/next), keep tracing; otherwise stop
            if _debugger_state["mode"] in ("step", "next"):
                return _trace_dispatch
            else:
                return None

    elif mode == "next":
        # Next mode: stop at the next line in the same frame or when returning
        if event == "line" and frame is start_frame:
            # We're back at the same frame level, stop here
            _debugger_state["mode"] = None
            set_trace_internal(frame)
            # Check if we should continue tracing after debugger exits
            if _debugger_state["mode"] in ("step", "next"):
                return _trace_dispatch
            else:
                return None
        elif event == "return" and frame is start_frame:
            # The frame is returning - we want to stop at the next line in the caller
            parent_frame = frame.f_back
            if parent_frame is not None and not _is_debugger_code(parent_frame):
                # Stay in "next" mode but switch to the parent frame
                # This will make us stop at the next line event in the parent
                _debugger_state["mode"] = "next"
                _debugger_state["start_frame"] = parent_frame

                # IMPORTANT: Set the parent frame's trace to ensure we get the line event
                parent_frame.f_trace = _trace_dispatch
            else:
                # No parent frame or parent is debugger code, stop tracing
                _debugger_state["mode"] = None

    # Continue tracing
    return _trace_dispatch


def set_trace_internal(frame: FrameType) -> None:
    """
    Internal set_trace that works with an explicit frame.

    This is called both from the public set_trace() and from the trace function.
    """
    # CRITICAL: Disable tracing while in the debugger to avoid tracing our own code
    old_trace = sys.gettrace()
    sys.settrace(None)

    try:
        # Get captured output
        stdout_output, stderr_output = get_captured_output()

        # Launch the TUI debugger
        app = DebuggerApp(frame, stdout_output, stderr_output)
        app.run()

        # Handle step modes after TUI exits
        if app.step_mode == "quit":
            # Restore old trace function and quit
            sys.settrace(_debugger_state["old_trace"])
            sys.exit(0)
        elif app.step_mode in ("next", "step"):
            # Set up tracing for stepping
            _debugger_state["mode"] = app.step_mode
            _debugger_state["start_frame"] = frame

            # Save old trace if this is the first time setting up tracing
            if old_trace != _trace_dispatch:
                _debugger_state["old_trace"] = old_trace

            # Re-enable global tracing
            sys.settrace(_trace_dispatch)

            # IMPORTANT: Set trace for the current frame
            # sys.settrace() only affects future frames, not the current one
            # We need to set f_trace for the frame where we want to start stepping
            if not _is_debugger_code(frame):
                frame.f_trace = _trace_dispatch
        else:
            # Continue mode or None - remove trace function
            sys.settrace(_debugger_state["old_trace"])
            _debugger_state["mode"] = None
    finally:
        # If we didn't set up new tracing and we're not in step/next mode,
        # this finally block ensures we don't accidentally leave tracing disabled
        # But actually, we handle trace restoration above, so this is just a safety net
        pass


def set_trace(*args: Any, **kwargs: Any) -> None:
    """
    Entry point for the debugger, compatible with sys.breakpointhook.

    This function is called when breakpoint() is invoked in user code,
    or when PYTHONBREAKPOINT=lazy_pdb.set_trace is set.
    """
    # If we're already in stepping mode and hit a breakpoint,
    # the trace function has already stopped here, so don't show debugger again
    if _debugger_state["mode"] in ("step", "next"):
        # We're stepping and hit an explicit breakpoint() call
        # The trace function already showed the debugger when we hit this line
        # Just return without clearing mode so stepping continues
        return

    # Ensure output capture is running
    capture = get_capture()
    if not capture.is_capturing:
        capture.start()

    # Get the caller's frame (the frame that called breakpoint())
    frame = sys._getframe(1)

    # Use internal function to show debugger
    set_trace_internal(frame)
