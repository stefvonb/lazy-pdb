"""Variable viewer widget for displaying local and global variables."""

from types import FrameType

from rich.table import Table
from textual.widgets import DataTable


class VariableViewer(DataTable):
    """Widget to display variables in the current scope."""

    DEFAULT_CSS = """
    VariableViewer {
        height: 50%;
        border: solid blue;
        padding: 0;
    }
    """

    BINDINGS = [
        ("g", "toggle_globals", "Toggle Global/Local"),
        ("enter", "inspect_variable", "Inspect Variable"),
    ]

    can_focus = True

    def __init__(self, frame: FrameType, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """Initialize the variable viewer."""
        super().__init__(*args, **kwargs)
        self.frame = frame
        self.show_globals = False
        self.variables_data: dict[str, tuple[str, str]] = {}
        self.cursor_type = "row"
        self.border_title = "Variables (Local)"

    def on_mount(self) -> None:
        """Update the variables view when mounted."""
        self.update_frame(self.frame)

    def update_frame(self, frame: FrameType) -> None:
        """Update the displayed frame."""
        self.frame = frame
        self.render_variables()

    def toggle_scope(self) -> None:
        """Toggle between local and global variables."""
        self.show_globals = not self.show_globals
        self.border_title = "Variables (Global)" if self.show_globals else "Variables (Local)"
        self.render_variables()

    def action_toggle_globals(self) -> None:
        """Action to toggle between global and local variables."""
        self.toggle_scope()

    def action_inspect_variable(self) -> None:
        """Action to inspect the selected variable (handled by RowSelected event)."""
        # This action is handled by the DataTable.RowSelected event
        # Just trigger a row selection if we have a cursor
        if self.cursor_row is not None and self.row_count > 0:
            # Emit the row selected event by simulating selection
            self.action_select_cursor()

    def render_variables(self) -> None:
        """Render the variables table."""
        # Clear existing data
        self.clear(columns=True)

        # Add columns
        self.add_column("Name", width=20)
        self.add_column("Type", width=15)
        self.add_column("Value")

        # Get variables based on current mode
        vars_dict = self.frame.f_globals if self.show_globals else self.frame.f_locals

        # Filter out special variables and sort
        filtered_vars = {
            k: v for k, v in vars_dict.items()
            if not k.startswith("__")
        }

        # Store variable data for inspection
        self.variables_data = {}

        for name in sorted(filtered_vars.keys()):
            value = filtered_vars[name]
            type_name = type(value).__name__

            # Limit value representation length
            # Handle errors in __repr__ (e.g., uninitialized objects)
            try:
                value_str = repr(value)
            except Exception as e:
                value_str = f"<repr error: {type(e).__name__}: {e}>"

            if len(value_str) > 50:
                value_str = value_str[:47] + "..."

            self.add_row(name, type_name, value_str)

            # Store full representation for later inspection
            # Use the same value_str if repr succeeded, otherwise try again
            try:
                full_repr = repr(value)
            except Exception as e:
                full_repr = f"<repr error: {type(e).__name__}: {e}>"

            self.variables_data[name] = (type_name, full_repr)

        if not filtered_vars:
            self.add_row("(no variables)", "", "")
