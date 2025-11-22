"""Code viewer widget for displaying source code."""

import linecache
from types import FrameType

from rich.syntax import Syntax
from textual.containers import VerticalScroll
from textual.widgets import Static


class CodeViewer(VerticalScroll):
    """Widget to display source code around the current line."""

    DEFAULT_CSS = """
    CodeViewer {
        height: 60%;
        border: solid green;
        padding: 1;
    }
    """

    can_focus = True

    def __init__(self, frame: FrameType, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """Initialize the code viewer."""
        super().__init__(*args, **kwargs)
        self.frame = frame
        self.border_title = "Code"

    def on_mount(self) -> None:
        """Update the code view when mounted."""
        self.code_static = Static(id="code-content")
        self.mount(self.code_static)
        self.update_frame(self.frame)

    def update_frame(self, frame: FrameType) -> None:
        """Update the displayed frame."""
        self.frame = frame
        self.render_code()

    def render_code(self) -> None:
        """Render the source code with syntax highlighting."""
        filename = self.frame.f_code.co_filename
        current_line = self.frame.f_lineno

        # Read lines around the current line
        context = 20
        start_line = max(1, current_line - context)
        end_line = current_line + context

        lines = []
        for line_num in range(start_line, end_line + 1):
            line = linecache.getline(filename, line_num)
            if line:
                lines.append(line.rstrip())

        code = "\n".join(lines)

        # Create syntax-highlighted code
        syntax = Syntax(
            code,
            "python",
            theme="monokai",
            line_numbers=True,
            start_line=start_line,
            highlight_lines={current_line},
        )

        self.code_static.update(syntax)
        self.border_title = f"Code: {filename}:{current_line}"
