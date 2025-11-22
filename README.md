# lazy-pdb

A modern Python debugger with a terminal user interface (TUI) built with Textual.

## Features

- Beautiful TUI for debugging Python code
- Integrates with Python's built-in `breakpoint()` function
- Can debug scripts and modules from the command line
- Modern interface with syntax highlighting and interactive controls

## Installation

Using UV (recommended):

```bash
uv pip install -e .
```

Or with pip:

```bash
pip install -e .
```

## Running Without Installation

If you want to run lazy-pdb without installing it, you need to add the `src` directory to your `PYTHONPATH`:

### Command-line usage

```bash
# With UV (recommended)
PYTHONPATH=src uv run python -m lazy_pdb script.py [args...]
PYTHONPATH=src uv run python -m lazy_pdb -m module.name [args...]

# Or with regular Python
PYTHONPATH=src python -m lazy_pdb script.py [args...]
PYTHONPATH=src python -m lazy_pdb -m module.name [args...]
```

### Using with breakpoint()

```bash
# With UV (recommended)
PYTHONPATH=src PYTHONBREAKPOINT=lazy_pdb.set_trace uv run python your_script.py

# Or with regular Python
PYTHONPATH=src PYTHONBREAKPOINT=lazy_pdb.set_trace python your_script.py
```

### Optional: Create a shell alias

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# With UV
alias lazy-pdb='PYTHONPATH=src uv run python -m lazy_pdb'

# Or with regular Python
alias lazy-pdb='PYTHONPATH=src python -m lazy_pdb'
```

Then you can use it like:

```bash
lazy-pdb script.py [args...]
```

## Usage

### Using with breakpoint()

Set the environment variable to use lazy-pdb as your debugger:

```bash
export PYTHONBREAKPOINT=lazy_pdb.set_trace
python your_script.py
```

Then use `breakpoint()` anywhere in your code:

```python
def my_function():
    x = 42
    breakpoint()  # lazy-pdb will start here
    return x
```

### Command-line debugging

Debug a script:

```bash
lazy-pdb script.py [args...]
```

Debug a module:

```bash
lazy-pdb -m module.name [args...]
```

## Development

Install development dependencies:

```bash
uv pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run linter:

```bash
ruff check .
```

Run type checker:

```bash
ty check src/lazy_pdb
```
