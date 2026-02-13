# xylen/cli.py
import sys
import argparse
import importlib
import os
from pathlib import Path

from .app import Xylen


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def resolve_import_string(import_str: str) -> str:
    if ':' not in import_str:
        eprint(f"Invalid --app format: {import_str!r} (expected 'module:app' or 'file.py:app')")
        sys.exit(1)

    module_part, attr_name = import_str.rsplit(":", 1)
    module_part = module_part.strip()

    if module_part.endswith(".py"):
        file_path = Path(module_part).resolve()
        if not file_path.is_file():
            eprint(f"File not found: {file_path}")
            sys.exit(1)

        parent_dir = str(file_path.parent.absolute())
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        module_name = file_path.stem
    else:
        module_name = module_part

    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        eprint(f"Cannot import module '{module_name}': {exc}")
        if "No module named" in str(exc):
            eprint("Hint: make sure you are in the correct directory or use relative path with .py")
        sys.exit(1)

    try:
        app = getattr(module, attr_name)
    except AttributeError:
        eprint(f"Module '{module_name}' has no attribute '{attr_name}'")
        sys.exit(1)

    if not isinstance(app, Xylen):
        eprint(f"'{import_str}' is not a Xylen instance (got {type(app).__name__})")
        sys.exit(1)

    return import_str


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="xylen",
        description="Xylen Web Framework CLI",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "command",
        choices=["run", "dev"],
        help="run = production-like\n dev = with reload",
    )
    parser.add_argument(
        "--app",
        required=True,
        help="import string to Xylen app\n"
             "examples:\n"
             "  app:app\n"
             "  app.py:app\n"
             "  myproject.main:app\n"
             "  ./src/api.py:app",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--log-level",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        default="info",
    )

    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError:
        eprint("uvicorn not found. Install it with: pip install uvicorn")
        sys.exit(1)

    import_path = resolve_import_string(args.app)

    reload = args.reload or (args.command == "dev")

    if reload and args.workers > 1:
        eprint("Warning: --workers > 1 is ignored when --reload is enabled")
        args.workers = 1

    try:
        uvicorn.run(
            import_path,
            host=args.host,
            port=args.port,
            reload=reload,
            workers=args.workers,
            log_level=args.log_level,
            factory=False,
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as exc:
        eprint(f"Uvicorn failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()