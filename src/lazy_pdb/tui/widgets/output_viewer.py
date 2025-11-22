"""Output viewer widget for displaying STDOUT and STDERR."""

from textual.widgets import RichLog


class OutputViewer(RichLog):
    """Widget to display program output (STDOUT/STDERR)."""

    DEFAULT_CSS = """
    OutputViewer {
        height: 40%;
        border: solid yellow;
        padding: 1;
    }
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """Initialize the output viewer."""
        super().__init__(*args, **kwargs)
        self.border_title = "Output (STDOUT/STDERR)"
        self.can_focus = False

    def on_mount(self) -> None:
        """Initialize the output viewer when mounted."""
        self.write("[dim]Program output will appear here...[/dim]")

    def add_output(self, text: str, stream: str = "stdout") -> None:
        """Add output to the viewer."""
        if stream == "stderr":
            self.write(f"[red]{text}[/red]")
        else:
            self.write(text)
