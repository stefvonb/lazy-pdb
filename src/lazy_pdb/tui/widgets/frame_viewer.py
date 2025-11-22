"""Frame viewer widget for displaying the call stack."""

import traceback
from types import FrameType

from rich.table import Table
from textual.widgets import Static


class FrameViewer(Static):
    """Widget to display the call stack and allow frame navigation."""

    DEFAULT_CSS = """
    FrameViewer {
        height: 50%;
        border: solid magenta;
        padding: 1;
    }
    """

    def __init__(self, frame: FrameType, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """Initialize the frame viewer."""
        super().__init__(*args, **kwargs)
        self.frame = frame
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
        table = Table(title="Call Stack", expand=True)
        table.add_column("#", style="cyan", no_wrap=True, width=4)
        table.add_column("Function", style="yellow")
        table.add_column("Location", style="green")

        # Build the stack from current frame
        stack = []
        current = self.frame
        while current is not None:
            stack.append(current)
            current = current.f_back

        # Display stack in reverse order (oldest first)
        for i, frame in enumerate(reversed(stack)):
            func_name = frame.f_code.co_name
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno

            # Shorten filename if too long
            if len(filename) > 40:
                filename = "..." + filename[-37:]

            location = f"{filename}:{lineno}"

            # Highlight the current frame
            if frame is self.frame:
                table.add_row(
                    f"→{i}",
                    f"[bold]{func_name}[/bold]",
                    f"[bold]{location}[/bold]",
                )
            else:
                table.add_row(str(i), func_name, location)

        self.update(table)
