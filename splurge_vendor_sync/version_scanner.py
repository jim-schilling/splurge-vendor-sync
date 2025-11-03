"""Scanner for extracting version information from vendored packages using AST.

This module provides utilities for scanning vendored package directories and extracting
version information using Python's AST module. It searches for version tags in __init__.py
and __main__.py files within each package. Supports recursive scanning of nested vendor
directories to track transitive dependencies.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import TypedDict


class VersionInfo(TypedDict):
    """Type definition for version information."""

    package_name: str
    version: str | None


class NestedVersionInfo(TypedDict, total=False):
    """Type definition for nested version information with hierarchy.

    Attributes:
        package_name: Name of the package
        version: Version string if found, None otherwise
        depth: Nesting depth (0 for top-level, 1+ for nested)
        parent_package: Name of parent package containing this vendor
        nested_packages: List of packages in nested _vendor directory
    """

    package_name: str
    version: str | None
    depth: int
    parent_package: str | None
    nested_packages: list[NestedVersionInfo]


def extract_version_from_file(file_path: Path, version_tag: str = "__version__") -> str | None:
    """Extract version value from a Python file using AST.

    Searches for an assignment statement matching the version_tag (e.g., __version__ = "1.0.0")
    and returns the assigned string value.

    Args:
        file_path: Path to the Python file to scan
        version_tag: The variable name to search for (default: '__version__')

    Returns:
        The version string if found, None otherwise

    Raises:
        ValueError: If file cannot be parsed as valid Python
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None

    # Walk through the AST looking for assignments
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # Check if this is an assignment to our target variable
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == version_tag:
                    # Extract the value if it's a string constant
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        return node.value.value

    return None


def scan_vendor_packages(
    target_path: Path | str,
    vendor_dir: str = "_vendor",
    version_tag: str = "__version__",
) -> list[VersionInfo]:
    """Scan all packages in a vendor directory and extract version information.

    For each package found in the vendor directory, searches for the version_tag in:
    1. package/__init__.py (first)
    2. package/__main__.py (if __init__.py not found)

    Args:
        target_path: Path to the target project directory
        vendor_dir: Name of the vendor subdirectory (default: '_vendor')
        version_tag: The variable name to search for (default: '__version__')

    Returns:
        List of VersionInfo dicts with package_name and version (None if not found)

    Raises:
        ValueError: If target_path or vendor directory doesn't exist
    """
    target_path = Path(target_path)
    vendor_path = target_path / vendor_dir

    if not target_path.exists():
        raise ValueError(f"Target path does not exist: {target_path}")

    if not vendor_path.exists():
        raise ValueError(f"Vendor directory does not exist: {vendor_path}")

    versions: list[VersionInfo] = []

    # Iterate through all subdirectories in the vendor directory
    for package_dir in sorted(vendor_path.iterdir()):
        if not package_dir.is_dir() or package_dir.name.startswith("_"):
            # Skip hidden directories and files
            continue

        package_name = package_dir.name
        version: str | None = None

        # Try __init__.py first
        init_file = package_dir / "__init__.py"
        if init_file.exists():
            version = extract_version_from_file(init_file, version_tag)

        # If not found, try __main__.py
        if version is None:
            main_file = package_dir / "__main__.py"
            if main_file.exists():
                version = extract_version_from_file(main_file, version_tag)

        versions.append({"package_name": package_name, "version": version})

    return versions


def scan_vendor_packages_nested(
    target_path: Path | str,
    vendor_dir: str = "_vendor",
    version_tag: str = "__version__",
    depth: int = 0,
    parent_package: str | None = None,
) -> list[NestedVersionInfo]:
    """Recursively scan vendor directories including nested packages.

    Scans the top-level vendor directory and recursively scans nested _vendor
    directories within packages, creating a hierarchical structure that shows
    parent-child relationships between vendored packages.

    Args:
        target_path: Path to the target project directory
        vendor_dir: Name of the vendor subdirectory (default: '_vendor')
        version_tag: The variable name to search for (default: '__version__')
        depth: Current nesting depth (default: 0, internal use for recursion)
        parent_package: Name of parent package (default: None, internal use)

    Returns:
        List of NestedVersionInfo dicts with hierarchical structure

    Raises:
        ValueError: If target_path or vendor directory doesn't exist
    """
    target_path = Path(target_path)
    vendor_path = target_path / vendor_dir

    if depth == 0:  # Only validate at top level
        if not target_path.exists():
            raise ValueError(f"Target path does not exist: {target_path}")

        if not vendor_path.exists():
            raise ValueError(f"Vendor directory does not exist: {vendor_path}")

    versions: list[NestedVersionInfo] = []

    # Iterate through all subdirectories in the vendor directory
    for package_dir in sorted(vendor_path.iterdir()):
        if not package_dir.is_dir() or package_dir.name.startswith("_"):
            # Skip hidden directories and files
            continue

        package_name = package_dir.name
        version: str | None = None

        # Try __init__.py first
        init_file = package_dir / "__init__.py"
        if init_file.exists():
            version = extract_version_from_file(init_file, version_tag)

        # If not found, try __main__.py
        if version is None:
            main_file = package_dir / "__main__.py"
            if main_file.exists():
                version = extract_version_from_file(main_file, version_tag)

        # Create the version info entry
        version_info: NestedVersionInfo = {
            "package_name": package_name,
            "version": version,
            "depth": depth,
            "parent_package": parent_package,
        }

        # Check for nested vendor directory
        nested_vendor_path = package_dir / vendor_dir
        if nested_vendor_path.exists() and nested_vendor_path.is_dir():
            # Recursively scan nested vendors
            nested_packages = scan_vendor_packages_nested(
                target_path=package_dir,
                vendor_dir=vendor_dir,
                version_tag=version_tag,
                depth=depth + 1,
                parent_package=package_name,
            )
            version_info["nested_packages"] = nested_packages
        else:
            version_info["nested_packages"] = []

        versions.append(version_info)

    return versions


def format_version_output(versions: list[VersionInfo]) -> str:
    """Format version information for console output.

    Formats as 'package-name version' with '?' for missing versions.

    Args:
        versions: List of VersionInfo dicts to format

    Returns:
        Formatted output string with one package per line
    """
    lines = []
    for info in versions:
        version = info["version"] if info["version"] is not None else "?"
        lines.append(f"{info['package_name']} {version}")

    return "\n".join(lines)


def format_nested_version_output(versions: list[NestedVersionInfo]) -> str:
    """Format nested version information with hierarchy visualization.

    Uses indentation to show nesting levels and parent-child relationships.
    Format: indentation + 'package-name version [parent: parent-name]'

    Args:
        versions: List of NestedVersionInfo dicts with hierarchical structure

    Returns:
        Formatted output string with hierarchy indentation

    Example:
        library-a 1.0.0
          library-b 2.0.0
            library-f 3.0.0
            library-g 4.0.0
    """

    def format_recursive(
        items: list[NestedVersionInfo],
        indent: int = 0,
    ) -> list[str]:
        """Recursively format nested version info with indentation.

        Args:
            items: List of NestedVersionInfo items to format
            indent: Current indentation level (number of spaces)

        Returns:
            List of formatted lines
        """
        lines = []
        indent_str = "  " * indent

        for info in items:
            version = info["version"] if info["version"] is not None else "?"
            line = f"{indent_str}{info['package_name']} {version}"
            lines.append(line)

            # Recursively format nested packages
            if info.get("nested_packages"):
                nested_lines = format_recursive(info["nested_packages"], indent + 1)
                lines.extend(nested_lines)

        return lines

    lines = format_recursive(versions)
    return "\n".join(lines)
