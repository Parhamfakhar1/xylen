# zephyr/cli.py
import sys
import argparse
import importlib
from .app import Zephyr

def main():
    parser = argparse.ArgumentParser(prog="zephyr", description="Zephyr Web Framework CLI")
    parser.add_argument("command", choices=["run", "dev"], help="Command to run")
    parser.add_argument("--app", required=True, help="Import path to the Zephyr app (e.g., 'module:app')")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    try:
        module_str, app_str = args.app.split(":")
        module = importlib.import_module(module_str)
        app = getattr(module, app_str)
        if not isinstance(app, Zephyr):
            print(f"Error: '{args.app}' is not a Zephyr application.", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error loading app '{args.app}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn not installed. Run: pip install uvicorn", file=sys.stderr)
        sys.exit(1)

    uvicorn.run(
        args.app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        factory=False
    )

if __name__ == "__main__":
    main()