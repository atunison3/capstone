#!/usr/bin/env python3
"""Scan a module's imports and resolve pinned versions for pyproject.toml.

Examples
--------
# Print dependency pins for a package/module path:
python get_dependencies.py capstone

# Only one file:
python get_dependencies.py capstone/visualization/report_fig2_real.py

# Write/merge into pyproject.toml [project].dependencies:
python get_dependencies.py capstone --update

# Prefer versions already installed in the active environment when missing
# from requirements.txt:
python get_dependencies.py capstone --update --use-installed
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
import tomllib
from importlib import metadata
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_REQUIREMENTS = PROJECT_ROOT / "requirements.txt"
DEFAULT_PYPROJECT = PROJECT_ROOT / "pyproject.toml"

# Top-level import name -> PyPI / requirements distribution name.
# Extend as needed when import name != package name on PyPI.
IMPORT_TO_DIST: dict[str, str] = {
    "PIL": "pillow",
    "bs4": "beautifulsoup4",
    "cv2": "opencv-python",
    "dateutil": "python-dateutil",
    "dotenv": "python-dotenv",
    "mpl_toolkits": "matplotlib",
    "skimage": "scikit-image",
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
}

# Local / first-party roots that should never become third-party deps.
LOCAL_TOP_LEVELS = {"capstone"}


def stdlib_module_names() -> set[str]:
    """Return top-level names that belong to the standard library."""
    names = set(sys.stdlib_module_names)
    names.update({"__future__", "builtins", "typing_extensions"})
    return names


def collect_python_files(target: Path) -> list[Path]:
    """Resolve a module path/name to the list of .py files to scan."""
    if target.exists():
        path = target.resolve()
    else:
        # Allow dotted module names like "capstone.visualization"
        candidate = PROJECT_ROOT.joinpath(*target.as_posix().split("."))
        if candidate.with_suffix(".py").exists():
            path = candidate.with_suffix(".py")
        elif candidate.is_dir():
            path = candidate
        else:
            raise FileNotFoundError(f"Module path not found: {target}")

    if path.is_file():
        if path.suffix != ".py":
            raise ValueError(f"Not a Python file: {path}")
        return [path]

    if path.is_dir():
        files = sorted(p for p in path.rglob("*.py") if p.is_file())
        if not files:
            raise FileNotFoundError(f"No Python files under: {path}")
        return files

    raise FileNotFoundError(f"Module path not found: {target}")


def top_level_imports_from_file(path: Path) -> set[str]:
    """Parse a file and return top-level imported module names."""
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        source = path.read_text(encoding="utf-8", errors="replace")

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        print(f"warning: skipping {path} (syntax error: {exc})", file=sys.stderr)
        return set()

    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            # Relative imports (from .x / from ..x) are first-party.
            if node.level and node.level > 0:
                continue
            if node.module:
                names.add(node.module.split(".")[0])
    return names


def scan_imports(module: str | Path) -> set[str]:
    """Scan all Python files for a module and return third-party top-level imports."""
    files = collect_python_files(Path(module))
    stdlib = stdlib_module_names()
    found: set[str] = set()
    for file in files:
        found |= top_level_imports_from_file(file)

    third_party: set[str] = set()
    for name in found:
        if name in stdlib or name in LOCAL_TOP_LEVELS:
            continue
        third_party.add(name)
    return third_party


def parse_requirements(path: Path) -> dict[str, str]:
    """Parse requirements.txt into {normalized_name: pin_string}.

    Values look like 'pandas==3.0.3' or 'package>=1.0' when that is how they
    appear in the file. Editable/VCS lines are skipped.
    """
    if not path.exists():
        raise FileNotFoundError(f"requirements file not found: {path}")

    pins: dict[str, str] = {}
    line_re = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._\-]*)\s*" r"((?:==|>=|<=|~=|!=|>|<)\s*[^;#\s]+)?\s*(?:[;#].*)?$")

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        match = line_re.match(line)
        if not match:
            continue
        name, spec = match.group(1), match.group(2)
        key = normalize_name(name)
        pin = f"{name}{spec.replace(' ', '')}" if spec else name
        # Prefer an existing pin if this name appears more than once.
        pins.setdefault(key, pin)
    return pins


def normalize_name(name: str) -> str:
    """PEP 503-ish normalization for package name comparison."""
    return re.sub(r"[-_.]+", "-", name).lower()


def import_to_distribution(import_name: str) -> str:
    """Map an import top-level name to a distribution / requirements name."""
    if import_name in IMPORT_TO_DIST:
        return IMPORT_TO_DIST[import_name]
    return import_name


def installed_pin(dist_name: str) -> str | None:
    """Return 'name==version' from the active environment, if installed."""
    candidates = {normalize_name(dist_name), normalize_name(dist_name.replace("-", "_"))}
    # Also try the raw name via importlib.
    try:
        version = metadata.version(dist_name)
        return f"{dist_name}=={version}"
    except metadata.PackageNotFoundError:
        pass

    for dist in metadata.distributions():
        meta_name = dist.metadata.get("Name")
        if meta_name and normalize_name(meta_name) in candidates:
            return f"{meta_name}=={dist.version}"
    return None


def resolve_dependencies(
    imports: set[str],
    requirements: dict[str, str],
    *,
    use_installed: bool = False,
) -> tuple[list[str], list[str]]:
    """Resolve imports to requirement pins.

    Returns
    -------
    resolved:
        Sorted list of pin strings suitable for pyproject dependencies.
    missing:
        Import/distribution names that could not be resolved.
    """
    resolved: list[str] = []
    missing: list[str] = []

    for import_name in sorted(imports, key=str.lower):
        dist_name = import_to_distribution(import_name)
        key = normalize_name(dist_name)

        pin = requirements.get(key)
        if pin is None and use_installed:
            pin = installed_pin(dist_name)

        if pin is None:
            missing.append(dist_name)
            continue

        # Keep the package name casing from requirements / installed pin.
        resolved.append(pin)

    # De-dupe while preserving order (different imports can map to one dist).
    deduped: list[str] = []
    seen: set[str] = set()
    for pin in resolved:
        name = normalize_name(re.split(r"[<=>!~]", pin, maxsplit=1)[0])
        if name in seen:
            continue
        seen.add(name)
        deduped.append(pin)

    return deduped, missing


def format_dependencies_block(deps: list[str], *, indent: str = "  ") -> str:
    """Format a dependencies list for pasting into pyproject.toml."""
    if not deps:
        return "dependencies = []"
    lines = ["dependencies = ["]
    for dep in deps:
        lines.append(f'{indent}"{dep}",')
    lines.append("]")
    return "\n".join(lines)


def read_pyproject_dependencies(pyproject_path: Path) -> list[str]:
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = data.get("project", {})
    deps = project.get("dependencies", [])
    if not isinstance(deps, list):
        raise ValueError("[project].dependencies is not a list")
    return [str(d) for d in deps]


def merge_dependencies(existing: list[str], new_pins: list[str]) -> list[str]:
    """Merge pins by normalized package name; new pins win on conflicts."""
    merged: dict[str, str] = {}
    order: list[str] = []

    def upsert(pin: str) -> None:
        name = normalize_name(re.split(r"[<=>!~]", pin, maxsplit=1)[0].strip())
        if name not in merged:
            order.append(name)
        merged[name] = pin

    for pin in existing:
        upsert(pin)
    for pin in new_pins:
        upsert(pin)

    # Stable alphabetical order keeps diffs clean.
    return [merged[name] for name in sorted(order)]


def update_pyproject_dependencies(pyproject_path: Path, deps: list[str]) -> None:
    """Replace the [project] dependencies array in pyproject.toml in-place."""
    text = pyproject_path.read_text(encoding="utf-8")

    # Match the dependencies = [ ... ] block under [project] without being
    # overly clever about full TOML parsing for writes.
    pattern = re.compile(
        r"(?m)^dependencies\s*=\s*\[(?:[^\[\]]|\n)*?\]",
    )
    match = pattern.search(text)
    if not match:
        raise RuntimeError(f"Could not find a dependencies = [...] block in {pyproject_path}")

    block = format_dependencies_block(deps)
    updated = text[: match.start()] + block + text[match.end() :]
    pyproject_path.write_text(updated, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Scan a module's imports, look up pins in requirements.txt, "
            "and print or update pyproject.toml dependencies."
        )
    )
    parser.add_argument(
        "module",
        help="Module path, package dir, file, or dotted name (e.g. capstone)",
    )
    parser.add_argument(
        "-r",
        "--requirements",
        type=Path,
        default=DEFAULT_REQUIREMENTS,
        help=f"requirements file (default: {DEFAULT_REQUIREMENTS.name})",
    )
    parser.add_argument(
        "-p",
        "--pyproject",
        type=Path,
        default=DEFAULT_PYPROJECT,
        help=f"pyproject.toml path (default: {DEFAULT_PYPROJECT.name})",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Merge resolved pins into pyproject.toml [project].dependencies",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="With --update, replace dependencies instead of merging",
    )
    parser.add_argument(
        "--use-installed",
        action="store_true",
        help="Fall back to versions installed in the active environment",
    )
    parser.add_argument(
        "--show-imports",
        action="store_true",
        help="Also print discovered third-party import names",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        imports = scan_imports(args.module)
        requirements = parse_requirements(args.requirements)
        resolved, missing = resolve_dependencies(
            imports,
            requirements,
            use_installed=args.use_installed,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.show_imports:
        print("imports:")
        for name in sorted(imports, key=str.lower):
            dist = import_to_distribution(name)
            note = f" -> {dist}" if dist != name else ""
            print(f"  {name}{note}")
        print()

    if missing:
        print("unresolved (not in requirements.txt):", file=sys.stderr)
        for name in missing:
            print(f"  - {name}", file=sys.stderr)
        print(
            "hint: add them to requirements.txt or pass --use-installed",
            file=sys.stderr,
        )
        print(file=sys.stderr)

    if not resolved and not args.update:
        print("dependencies = []")
        return 0 if not missing else 2

    if args.update:
        pyproject = args.pyproject
        if not pyproject.is_absolute():
            pyproject = (Path.cwd() / pyproject).resolve()
        if not pyproject.exists():
            print(f"error: pyproject not found: {pyproject}", file=sys.stderr)
            return 1

        if args.replace:
            final_deps = sorted(resolved, key=lambda s: normalize_name(s))
        else:
            existing = read_pyproject_dependencies(pyproject)
            final_deps = merge_dependencies(existing, resolved)

        update_pyproject_dependencies(pyproject, final_deps)
        print(f"updated {pyproject}")
        print(format_dependencies_block(final_deps))
        return 0 if not missing else 2

    # Default: paste-ready block for pyproject.toml
    print(format_dependencies_block(resolved))
    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
