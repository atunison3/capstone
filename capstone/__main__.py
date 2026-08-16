"""Allow ``python -m capstone`` to run the CLI entry point.

Prefer this over a bare ``capstone`` command when multiple Python installs
have console scripts on PATH (avoids accidentally running a global install).
"""

from capstone.analysis import main

if __name__ == "__main__":
    main()
