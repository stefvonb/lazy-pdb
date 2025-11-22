"""Main Textual application for the debugger."""

from types import FrameType
from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Header, Input

from lazy_pdb.tui.widgets.code_viewer import CodeViewer
from lazy_pdb.tui.widgets.frame_viewer import FrameViewer
from lazy_pdb.tui.widgets.output_viewer import OutputViewer
from lazy_pdb.tui.widgets.variable_viewer import VariableViewer


class DebuggerApp(App[None]):
    """A TUI debugger application built with Textual."""

    CSS_PATH = "debugger.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "continue_execution", "Continue"),
        ("n", "next_line", "Next"),
        ("s", "step_into", "Step"),
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
        self.query_one("#command-input", Input).focus()

        # Display captured output
        output_viewer = self.query_one("#output-viewer", OutputViewer)
        if self.stdout_output:
            output_viewer.add_output(self.stdout_output, "stdout")
        if self.stderr_output:
            output_viewer.add_output(self.stderr_output, "stderr")

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

    def action_continue_execution(self) -> None:
        """Continue execution."""
        self.should_continue = True
        self.step_mode = "continue"
        self.exit()

    def action_next_line(self) -> None:
        """Execute next line."""
        self.should_continue = True
        self.step_mode = "next"
        self.exit()

    def action_step_into(self) -> None:
        """Step into function."""
        self.should_continue = True
        self.step_mode = "step"
        self.exit()

    def action_quit(self) -> None:
        """Quit the debugger."""
        self.should_continue = False
        self.step_mode = "quit"
        self.exit()
