"""Variable viewer widget for displaying local and global variables."""

from types import FrameType

from rich.table import Table
from textual.widgets import Static


class VariableViewer(Static):
    """Widget to display variables in the current scope."""

    DEFAULT_CSS = """
    VariableViewer {
        height: 50%;
        border: solid blue;
        padding: 1;
    }
    """

    def __init__(self, frame: FrameType, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """Initialize the variable viewer."""
        super().__init__(*args, **kwargs)
        self.frame = frame
        self.border_title = "Variables"

    def on_mount(self) -> None:
        """Update the variables view when mounted."""
        self.update_frame(self.frame)

    def update_frame(self, frame: FrameType) -> None:
        """Update the displayed frame."""
        self.frame = frame
        self.render_variables()

    def render_variables(self) -> None:
        """Render the variables table."""
        table = Table(title="Local Variables", expand=True)
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Value", style="green")

        # Get local variables
        local_vars = self.frame.f_locals

        # Filter out special variables and sort
        filtered_vars = {
            k: v for k, v in local_vars.items()
            if not k.startswith("__")
        }

        for name in sorted(filtered_vars.keys()):
            value = filtered_vars[name]
            type_name = type(value).__name__

            # Limit value representation length
            value_str = repr(value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."

            table.add_row(name, type_name, value_str)

        if not filtered_vars:
            table.add_row("(no variables)", "", "")

        self.update(table)
