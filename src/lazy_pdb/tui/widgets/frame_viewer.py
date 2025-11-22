"""Frame viewer widget for displaying the call stack."""

import traceback
from types import FrameType

from rich.table import Table
from textual.widgets import DataTable


class FrameViewer(DataTable):
    """Widget to display the call stack and allow frame navigation."""

    DEFAULT_CSS = """
    FrameViewer {
        height: 50%;
        border: solid magenta;
        padding: 0;
    }
    """

    can_focus = True

    def __init__(self, frame: FrameType, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """Initialize the frame viewer."""
        super().__init__(*args, **kwargs)
        self.original_frame = frame  # The frame where breakpoint was hit
        self.frame = frame  # Currently selected frame for display
        self.frames_list: list[FrameType] = []
        self.cursor_type = "row"
        self.border_title = "Call Stack"

    def on_mount(self) -> None:
        """Update the frames view when mounted."""
        self.update_frame(self.frame)

    def update_frame(self, frame: FrameType) -> None:
        """Update the displayed frame."""
        self.frame = frame
        self.render_frames()

    def render_frames(self) -> None:
        """Render the call stack."""
        # Clear existing data
        self.clear(columns=True)

        # Add columns
        self.add_column("#", width=4)
        self.add_column("Function", width=20)
        self.add_column("Location")

        # Build the stack from original breakpoint frame (preserves full stack)
        stack = []
        current = self.original_frame
        while current is not None:
            stack.append(current)
            current = current.f_back

        # Store frames list for selection
        self.frames_list = list(reversed(stack))

        # Display stack in reverse order (oldest first)
        for i, frame in enumerate(self.frames_list):
            func_name = frame.f_code.co_name
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno

            # Shorten filename if too long
            if len(filename) > 40:
                filename = "..." + filename[-37:]

            location = f"{filename}:{lineno}"

            # Mark the current frame
            if frame is self.frame:
                self.add_row(f"→{i}", func_name, location)
                # Move cursor to this row
                self.move_cursor(row=i)
            else:
                self.add_row(str(i), func_name, location)
