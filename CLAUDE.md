# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

lazy-pdb is a Python TUI (Terminal User Interface) debugger built with the Textual library. It provides a modern, visual debugging experience that integrates with Python's built-in `breakpoint()` mechanism.

## Development Commands

### Package Management
This project uses **UV** for dependency management. Always use UV commands:

```bash
# Install package in development mode
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"

# Add a new dependency
uv pip install <package>
# Then manually add to pyproject.toml dependencies
```

### Running Without Installation

To run the project without installing it (useful during development):

```bash
# Run the CLI with UV (recommended)
PYTHONPATH=src uv run python -m lazy_pdb script.py [args...]

# Or with regular Python
PYTHONPATH=src python -m lazy_pdb script.py [args...]

# Use with breakpoint() with UV
PYTHONPATH=src PYTHONBREAKPOINT=lazy_pdb.set_trace uv run python script.py

# Or with regular Python
PYTHONPATH=src PYTHONBREAKPOINT=lazy_pdb.set_trace python script.py

# Run tests with UV
PYTHONPATH=src uv run pytest

# Or with regular pytest
PYTHONPATH=src pytest
```

Note: Due to the src layout, you must set `PYTHONPATH=src` to make the `lazy_pdb` package importable. Using `uv run` ensures dependencies are available. However, installing in editable mode with `uv pip install -e .` is recommended for regular development.

### Testing
```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_debugger.py

# Run a specific test
pytest tests/test_debugger.py::test_function_name

# Run with verbose output
pytest -v
```

### Linting and Type Checking
```bash
# Run linter (check only)
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code
ruff format .

# Type check with ty
ty check src/lazy_pdb
```

## Architecture

### Entry Points

The debugger has two main entry points:

1. **`breakpoint()` integration** (via `PYTHONBREAKPOINT` environment variable):
   - Users set `PYTHONBREAKPOINT=lazy_pdb.set_trace`
   - When `breakpoint()` is called, Python invokes `lazy_pdb.set_trace()`
   - The debugger receives the caller's frame via `sys._getframe(1)`

2. **CLI invocation** (via `lazy-pdb` command):
   - Entry point: `src/lazy_pdb/__main__.py:main()`
   - Supports: `lazy-pdb script.py` and `lazy-pdb -m module.name`
   - Sets `sys.breakpointhook` before running the target code
   - Uses `runpy.run_path()` for scripts and `runpy.run_module()` for modules

### Core Components

- **`src/lazy_pdb/__init__.py`**: Package initialization, exports `set_trace`
- **`src/lazy_pdb/__main__.py`**: CLI argument parsing and script/module execution
- **`src/lazy_pdb/debugger.py`**: Core debugger logic, `set_trace()` implementation
- **Future TUI components**: Will be added to handle the Textual-based interface

### Key Design Considerations

1. **Frame Handling**: When `breakpoint()` is called, we must use `sys._getframe(1)` to get the caller's frame (not our own frame). This is critical for showing the correct source location.

2. **sys.argv Management**: When debugging scripts via CLI, we must set `sys.argv` to match what the script expects (script name + its arguments).

3. **Module Path**: When debugging scripts (not modules), add the script's directory to `sys.path[0]` so relative imports work correctly.

4. **Textual Integration**: The TUI will need to:
   - Run in the main thread (Textual requirement)
   - Capture and display the program state (locals, globals, stack frames)
   - Provide step/continue/breakpoint controls
   - Handle source code display with syntax highlighting

5. **Async Compatibility**: Textual is async-based, so the debugger's event loop must coexist with the debugged program's execution model.

## Textual Framework Best Practices

### Application Structure

**App Pattern**: Every Textual app should subclass `App` and implement a `compose()` method:

```python
from textual.app import App
from textual.widgets import Header, Footer, Static

class DebuggerApp(App):
    def compose(self):
        yield Header()
        yield Static("Content here")
        yield Footer()
```

**Widget Composition**: Widgets are self-contained components. Most apps contain multiple widgets that together form the UI. Create custom widgets by subclassing existing ones.

**CSS Styling**: Use external `.tcss` files for styling (Textual CSS). Assign the CSS file path to the `CSS_PATH` class variable. Each widget has default styles that can be overridden.

**DOM Structure**: Textual uses a tree-like DOM structure similar to web development. Widgets contain other widgets, forming a hierarchy.

### Development Tools

**Textual Console** (Essential for debugging):
```bash
# Terminal 1: Start the console
textual console

# Terminal 2: Run your app
textual run --dev your_app.py
```
The console shows:
- Log messages from `self.log()` calls
- Output from `print()` statements
- Errors and system messages
- Rich-formatted data structures

**Development Mode**:
```bash
textual run --dev script.py
```
Benefits:
- Live CSS editing (changes apply without restart)
- Enhanced debugging output
- Better error messages

**Logging**: Use `self.log()` instead of `print()` for debugging output. Supports Rich formatting for pretty-printing data structures.

**Filter Console Output**:
```bash
textual console -x EVENT -x SYSTEM  # Exclude verbose groups
```
Available groups: EVENT, DEBUG, INFO, WARNING, ERROR, PRINT, SYSTEM, LOGGING, WORKER

**Screenshots**:
```bash
textual run --screenshot 5 app.py  # Takes screenshot after 5 seconds
```

### Debugging a Textual Debugger

**Challenge**: Building a debugger with Textual is meta - you're debugging a debugger. Special considerations:

1. **Use `debugpy` for breakpoints**: Integrate `debugpy.listen()` and `debugpy.wait_for_client()` to attach VS Code debugger. Add a `--debug` flag to enable this.

2. **Separate terminals**: Always run `textual console` in a separate terminal to see debug output without interfering with the debugger TUI.

3. **Async operations**: Textual is async under the hood. Be careful with blocking operations that could freeze the UI. Use `run_worker()` for long-running tasks.

4. **Event handling**: Two ways to handle events:
   - Naming convention: `on_<event_name>()` methods
   - Decorator: `@on(EventType)` on methods

### Best Practices for This Project

1. **Immutability**: Prefer immutable objects - easier to reason about, cache, and test.

2. **Component separation**: Keep debugger logic separate from TUI components. The TUI should be a view layer over the core debugger.

3. **Testing**: Textual has an advanced testing framework. Write tests for widgets and app behavior.

4. **CSS organization**: Keep layout and styling in `.tcss` files, not Python code.

5. **Live editing**: Use `--dev` mode extensively during development for rapid CSS iteration.

## File Structure

```
lazy-pdb/
├── src/lazy_pdb/          # Main package (src layout)
│   ├── __init__.py        # Package exports
│   ├── __main__.py        # CLI entry point
│   └── debugger.py        # Core debugger logic
├── tests/                 # Test files
├── pyproject.toml         # Project config (dependencies, build, tools)
├── README.md              # User documentation
└── CLAUDE.md              # This file
```

## Python Version

Requires Python 3.10+ (specified in pyproject.toml). Use modern Python features (match statements, type hints with `|`, etc.).
