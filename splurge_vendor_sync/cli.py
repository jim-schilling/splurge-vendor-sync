"""CLI interface for splurge-vendor-sync.

Provides command-line argument parsing and entry point for the application.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from splurge_vendor_sync.main import main as main_func


def main() -> int:
    """Parse CLI arguments and invoke the main sync function.

    Returns:
        Exit code: 0 (success), 1 (runtime error), 2 (validation error)
    """
    parser = _create_parser()
    args = parser.parse_args()

    # Call the main function with parsed arguments
    return main_func(
        source_path=args.source_path,
        target_path=args.target_path,
        package=args.package,
        vendor=args.vendor,
        extensions=args.extensions,
        verbose=args.verbose,
    )


def _create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="splurge-vendor-sync",
        description="Synchronize vendor packages into a project's vendor directory",
        epilog="For more information, see: https://github.com/jim-schilling/splurge-vendor-sync",
    )

    # Required arguments
    parser.add_argument(
        "--source-path",
        type=str,
        required=True,
        help="Path to the source directory containing the package to sync",
        metavar="PATH",
    )

    parser.add_argument(
        "--target-path",
        type=str,
        required=True,
        help="Path to the target project directory",
        metavar="PATH",
    )

    parser.add_argument(
        "--package",
        type=str,
        required=True,
        help="Name of the package subdirectory to sync (e.g., splurge_exceptions)",
        metavar="PACKAGE",
    )

    # Optional arguments
    parser.add_argument(
        "--vendor",
        type=str,
        default="_vendor",
        help="Name of the vendor directory (default: _vendor)",
        metavar="DIR",
    )

    parser.add_argument(
        "--extensions",
        "-e",
        type=str,
        default="py;json;yml;yaml;ini",
        help="Semicolon-separated file extensions to include (default: py;json;yml;yaml;ini)",
        metavar="EXT",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    return parser


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
