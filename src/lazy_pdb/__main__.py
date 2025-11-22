"""Command-line entry point for lazy-pdb."""

import sys
from typing import NoReturn


def main() -> NoReturn:
    """Main entry point for the lazy-pdb CLI."""
    import argparse
    import runpy

    parser = argparse.ArgumentParser(
        prog="lazy-pdb",
        description="A modern TUI debugger for Python",
    )
    parser.add_argument(
        "-m",
        dest="module",
        action="store_true",
        help="Run library module as a script (like python -m)",
    )
    parser.add_argument(
        "target",
        help="Python script or module to debug",
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Arguments to pass to the script/module",
    )

    args = parser.parse_args()

    # Set up sys.argv for the target script/module
    sys.argv = [args.target] + args.args

    # Import and set our debugger as the breakpoint handler
    from lazy_pdb.debugger import set_trace
    from lazy_pdb.output_capture import start_capture

    sys.breakpointhook = set_trace

    # Start capturing stdout/stderr so it can be displayed in the TUI
    start_capture()

    # Run the target
    try:
        if args.module:
            runpy.run_module(args.target, run_name="__main__")
        else:
            # Add the script's directory to sys.path
            import os

            script_dir = os.path.dirname(os.path.abspath(args.target))
            sys.path.insert(0, script_dir)

            runpy.run_path(args.target, run_name="__main__")
    except SystemExit:
        raise
    except Exception:
        # Let the debugger handle uncaught exceptions
        import traceback

        traceback.print_exc()
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
