"""Output capture for redirecting stdout/stderr to the debugger TUI."""

import sys
from io import StringIO
from typing import TextIO


class OutputCapture:
    """Captures stdout and stderr for display in the debugger."""

    def __init__(self) -> None:
        """Initialize the output capture."""
        self.stdout_capture = StringIO()
        self.stderr_capture = StringIO()
        self.original_stdout: TextIO = sys.stdout
        self.original_stderr: TextIO = sys.stderr
        self.is_capturing = False

    def start(self) -> None:
        """Start capturing stdout and stderr."""
        if not self.is_capturing:
            sys.stdout = _TeeStream(self.original_stdout, self.stdout_capture)
            sys.stderr = _TeeStream(self.original_stderr, self.stderr_capture)
            self.is_capturing = True

    def stop(self) -> None:
        """Stop capturing and restore original stdout/stderr."""
        if self.is_capturing:
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr
            self.is_capturing = False

    def get_stdout(self) -> str:
        """Get captured stdout content."""
        return self.stdout_capture.getvalue()

    def get_stderr(self) -> str:
        """Get captured stderr content."""
        return self.stderr_capture.getvalue()

    def clear(self) -> None:
        """Clear captured output."""
        self.stdout_capture = StringIO()
        self.stderr_capture = StringIO()
        if self.is_capturing:
            # Reinstall with new buffers
            sys.stdout = _TeeStream(self.original_stdout, self.stdout_capture)
            sys.stderr = _TeeStream(self.original_stderr, self.stderr_capture)


class _TeeStream:
    """Stream that writes to both original stream and capture buffer."""

    def __init__(self, original: TextIO, capture: StringIO) -> None:
        """Initialize the tee stream."""
        self.original = original
        self.capture = capture

    def write(self, text: str) -> int:
        """Write to both streams."""
        self.original.write(text)
        self.capture.write(text)
        return len(text)

    def flush(self) -> None:
        """Flush both streams."""
        self.original.flush()
        self.capture.flush()

    def __getattr__(self, name: str):
        """Delegate other attributes to original stream."""
        return getattr(self.original, name)


# Global output capture instance
_global_capture: OutputCapture | None = None


def get_capture() -> OutputCapture:
    """Get or create the global output capture instance."""
    global _global_capture
    if _global_capture is None:
        _global_capture = OutputCapture()
    return _global_capture


def start_capture() -> None:
    """Start capturing output globally."""
    get_capture().start()


def stop_capture() -> None:
    """Stop capturing output globally."""
    capture = get_capture()
    capture.stop()


def get_captured_output() -> tuple[str, str]:
    """Get captured stdout and stderr as a tuple."""
    capture = get_capture()
    return capture.get_stdout(), capture.get_stderr()
