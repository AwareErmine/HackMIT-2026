"""UNO Q entry point for the local audio backend and browser control API."""

import os
import socket
import sys
from pathlib import Path


def _add_backend_to_path() -> None:
    script_path = Path(__file__).resolve()
    configured = os.environ.get("HACKMIT_BACKEND_SRC")
    candidates = [
        Path(configured).expanduser() if configured else None,
        script_path.parent,  # Self-contained App Lab bundle: python/backend/.
        script_path.parents[2] / "backend" / "src",  # Repository checkout.
        Path.cwd() / "backend" / "src",
        Path.home() / "project" / "backend" / "src",  # Existing SSH layout.
    ]

    for candidate in candidates:
        if candidate and (candidate / "backend" / "__init__.py").is_file():
            sys.path.insert(0, str(candidate))
            return


_add_backend_to_path()

try:
    from backend import main
except ModuleNotFoundError as exc:
    if exc.name != "backend":
        raise
    raise RuntimeError(
        "Backend package not found. Build the App Lab bundle with "
        "arduino/build_app.ps1 or set HACKMIT_BACKEND_SRC to backend/src."
    ) from exc

if __name__ == "__main__":
    hostname = socket.gethostname()
    print("Starting HackMIT backend on the UNO Q")
    print(f"Control API: http://{hostname}.local:5005")
    print("Mode: audio")
    main()
