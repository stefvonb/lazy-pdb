"""Main Textual application for the debugger."""

from types import FrameType
from typing import Any

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Header, Input, Static

from lazy_pdb.tui.widgets.code_viewer import CodeViewer
from lazy_pdb.tui.widgets.frame_viewer import FrameViewer
from lazy_pdb.tui.widgets.output_viewer import OutputViewer
from lazy_pdb.tui.widgets.variable_viewer import VariableViewer

# Global state to persist focus across breakpoints
_last_focused_id: str | None = None


class VariableInspectScreen(ModalScreen[None]):
    """Modal screen for inspecting a variable in detail."""

    DEFAULT_CSS = """
    VariableInspectScreen {
        align: center middle;
    }
    """

    BINDINGS = [
        ("escape", "dismiss_screen", ""),
        ("enter", "dismiss_screen", ""),
    ]

    def __init__(self, name: str, type_name: str, value: str, *args: Any, **kwargs: Any) -> None:
        """Initialize the variable inspect screen."""
        super().__init__(*args, **kwargs)
        self.var_name = name
        self.var_type = type_name
        self.var_value = value

    def compose(self) -> ComposeResult:
        """Compose the inspection screen."""
        content = f"[bold cyan]{self.var_name}[/bold cyan]\n\n"
        content += f"[yellow]Type:[/yellow] {self.var_type}\n\n"
        content += f"[yellow]Value:[/yellow]\n{self.var_value}\n\n"
        content += "[dim italic]<ESC> or <Enter> to go back[/dim italic]"

        yield Container(
            Static(content, id="inspect-content"),
            id="inspect-dialog",
        )

    def action_dismiss_screen(self) -> None:
        """Dismiss the modal screen."""
        self.dismiss()


class DebuggerApp(App[None]):
    """A TUI debugger application built with Textual."""

    CSS_PATH = "debugger.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "continue_execution", "Continue"),
        ("n", "next_line", "Next"),
        ("s", "step_into", "Step"),
        # Vim-style navigation keys
        ("j", "cursor_down", ""),
        ("k", "cursor_up", ""),
        ("h", "cursor_left", ""),
        ("l", "cursor_right", ""),
    ]

    def __init__(
        self,
        frame: FrameType,
        stdout_output: str = "",
        stderr_output: str = "",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the debugger app with a frame."""
        super().__init__(*args, **kwargs)
        self.current_frame = frame
        self.stdout_output = stdout_output
        self.stderr_output = stderr_output
        self.should_continue = False
        self.step_mode: str | None = None

    def compose(self) -> ComposeResult:
        """Compose the debugger UI."""
        yield Header()

        with Horizontal(id="main-container"):
            # Left side: Code and output
            with Vertical(id="left-panel"):
                yield CodeViewer(self.current_frame, id="code-viewer")
                yield OutputViewer(id="output-viewer")

            # Right side: Variables and frames
            with Vertical(id="right-panel"):
                yield VariableViewer(self.current_frame, id="variable-viewer")
                yield FrameViewer(self.current_frame, id="frame-viewer")

        yield Input(placeholder="Enter debugger command (h for help)", id="command-input")
        yield Footer()

    def on_mount(self) -> None:
        """Handle app mount."""
        global _last_focused_id

        # Display captured output
        output_viewer = self.query_one("#output-viewer", OutputViewer)
        if self.stdout_output:
            output_viewer.add_output(self.stdout_output, "stdout")
        if self.stderr_output:
            output_viewer.add_output(self.stderr_output, "stderr")

        # Restore focus to last focused widget, or default to command input
        if _last_focused_id:
            try:
                widget = self.query_one(f"#{_last_focused_id}")
                widget.focus()
            except Exception:
                # If the widget doesn't exist, fall back to command input
                self.query_one("#command-input", Input).focus()
        else:
            self.query_one("#command-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command input."""
        command = event.value.strip()
        event.input.value = ""

        if not command:
            return

        self.handle_command(command)

    def handle_command(self, command: str) -> None:
        """Handle debugger commands."""
        cmd = command.split()[0] if command else ""

        match cmd:
            case "c" | "continue":
                self.action_continue_execution()
            case "n" | "next":
                self.action_next_line()
            case "s" | "step":
                self.action_step_into()
            case "q" | "quit":
                self.action_quit()
            case "h" | "help":
                self.show_help()
            case "p" | "print":
                self.print_expression(command[len(cmd):].strip())
            case "l" | "list":
                self.refresh_code_view()
            case _:
                self.log(f"Unknown command: {command}")
                self.notify(f"Unknown command: {command}. Type 'h' for help.", severity="warning")

    def show_help(self) -> None:
        """Show help message."""
        help_text = """
Available commands:
  c, continue  - Continue execution
  n, next      - Execute next line (step over)
  s, step      - Step into function
  p, print <expr> - Print expression
  l, list      - Refresh code view
  h, help      - Show this help
  q, quit      - Quit debugger

Navigation:
  Tab/Shift+Tab - Focus next/previous window
  Arrow keys    - Navigate within focused window
  g             - Toggle global/local variables
  Enter         - Inspect selected variable (when focused on variables)
        """
        self.notify(help_text.strip())

    def print_expression(self, expr: str) -> None:
        """Evaluate and print an expression."""
        if not expr:
            self.notify("Usage: p <expression>", severity="warning")
            return

        try:
            result = eval(expr, self.current_frame.f_globals, self.current_frame.f_locals)
            self.notify(f"{expr} = {result!r}")
            self.log(f"Evaluated: {expr} = {result!r}")
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")
            self.log(f"Error evaluating '{expr}': {e}")

    def refresh_code_view(self) -> None:
        """Refresh the code viewer."""
        code_viewer = self.query_one("#code-viewer", CodeViewer)
        code_viewer.update_frame(self.current_frame)

    def _save_focus(self) -> None:
        """Save the currently focused widget ID."""
        global _last_focused_id
        focused = self.focused
        if focused and hasattr(focused, 'id') and focused.id:
            _last_focused_id = focused.id

    def action_cursor_down(self) -> None:
        """Vim-style down navigation."""
        focused = self.focused
        if focused:
            # Try to call the widget's cursor_down action
            if hasattr(focused, 'action_cursor_down'):
                focused.action_cursor_down()
            # Fallback to scroll_down for scrollable widgets
            elif hasattr(focused, 'action_scroll_down'):
                focused.action_scroll_down()

    def action_cursor_up(self) -> None:
        """Vim-style up navigation."""
        focused = self.focused
        if focused:
            if hasattr(focused, 'action_cursor_up'):
                focused.action_cursor_up()
            elif hasattr(focused, 'action_scroll_up'):
                focused.action_scroll_up()

    def action_cursor_left(self) -> None:
        """Vim-style left navigation."""
        focused = self.focused
        if focused:
            if hasattr(focused, 'action_cursor_left'):
                focused.action_cursor_left()
            elif hasattr(focused, 'action_scroll_left'):
                focused.action_scroll_left()

    def action_cursor_right(self) -> None:
        """Vim-style right navigation."""
        focused = self.focused
        if focused:
            if hasattr(focused, 'action_cursor_right'):
                focused.action_cursor_right()
            elif hasattr(focused, 'action_scroll_right'):
                focused.action_scroll_right()

    def action_continue_execution(self) -> None:
        """Continue execution."""
        self._save_focus()
        self.should_continue = True
        self.step_mode = "continue"
        self.exit()

    def action_next_line(self) -> None:
        """Execute next line."""
        self._save_focus()
        self.should_continue = True
        self.step_mode = "next"
        self.exit()

    def action_step_into(self) -> None:
        """Step into function."""
        self._save_focus()
        self.should_continue = True
        self.step_mode = "step"
        self.exit()

    def action_quit(self) -> None:
        """Quit the debugger."""
        self._save_focus()
        self.should_continue = False
        self.step_mode = "quit"
        self.exit()

    def action_toggle_globals(self) -> None:
        """Toggle between global and local variables."""
        var_viewer = self.query_one("#variable-viewer", VariableViewer)
        var_viewer.toggle_scope()

    def action_inspect_variable(self) -> None:
        """Inspect the selected variable in a popup (fallback for non-DataTable focus)."""
        var_viewer = self.query_one("#variable-viewer", VariableViewer)

        # Check if variable viewer is focused
        if not var_viewer.has_focus:
            return

        # Get the selected row
        if var_viewer.cursor_row is None or var_viewer.row_count == 0:
            return

        # Get the variable name from the selected row
        row = var_viewer.get_row_at(var_viewer.cursor_row)
        var_name = str(row[0])

        if var_name == "(no variables)":
            return

        # Get variable details
        if var_name in var_viewer.variables_data:
            type_name, value = var_viewer.variables_data[var_name]
            self.push_screen(VariableInspectScreen(var_name, type_name, value))

    @on(DataTable.RowSelected, "#variable-viewer")
    def on_variable_selected(self, event: DataTable.RowSelected) -> None:
        """Handle variable selection to show inspection popup."""
        var_viewer = self.query_one("#variable-viewer", VariableViewer)

        # Get the variable name from the selected row
        row = var_viewer.get_row_at(event.cursor_row)
        var_name = str(row[0])

        if var_name == "(no variables)":
            return

        # Get variable details and show popup
        if var_name in var_viewer.variables_data:
            type_name, value = var_viewer.variables_data[var_name]
            self.push_screen(VariableInspectScreen(var_name, type_name, value))

    @on(DataTable.RowSelected, "#frame-viewer")
    def on_frame_selected(self, event: DataTable.RowSelected) -> None:
        """Handle frame selection in the call stack."""
        frame_viewer = self.query_one("#frame-viewer", FrameViewer)

        # Get the selected frame index
        row_index = event.cursor_row

        if row_index < len(frame_viewer.frames_list):
            selected_frame = frame_viewer.frames_list[row_index]

            # Update current frame
            self.current_frame = selected_frame
            frame_viewer.frame = selected_frame

            # Update all views
            code_viewer = self.query_one("#code-viewer", CodeViewer)
            code_viewer.update_frame(selected_frame)

            var_viewer = self.query_one("#variable-viewer", VariableViewer)
            var_viewer.update_frame(selected_frame)

            # Re-render frame viewer to update the arrow
            frame_viewer.render_frames()
