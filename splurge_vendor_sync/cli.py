"""CLI interface for splurge-vendor-sync.

Provides command-line argument parsing and entry point for the application.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    """Parse CLI arguments and invoke the main sync function.

    Returns:
        Exit code: 0 (success), 1 (runtime error), 2 (validation error)
    """
    from .main import main as main_func

    parser = _create_parser()
    args = parser.parse_args()

    # Call the main function with parsed arguments
    return main_func(
        source_path=args.source,
        target_path=args.target,
        package=args.package,
        vendor=args.vendor,
        extensions=args.extensions,
        verbose=args.verbose,
        scan=args.scan,
    )


def _create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    from . import __version__

    parser = argparse.ArgumentParser(
        prog="splurge-vendor-sync",
        description="Synchronize vendor packages into a project's vendor directory",
        epilog="For more information, see: https://github.com/jim-schilling/splurge-vendor-sync",
    )

    # Arguments
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Path to the source directory containing the package to sync (not required for --scan)",
        metavar="PATH",
    )

    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Path to the target project directory",
        metavar="PATH",
    )

    parser.add_argument(
        "--package",
        type=str,
        default=None,
        help="Name of the package subdirectory to sync (not required for --scan)",
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
        "--scan",
        type=str,
        nargs="?",
        const="__version__",
        default=None,
        help="Scan vendor directory for version tags (default tag: __version__). Can specify custom version tag.",
        metavar="VERSION-TAG",
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
        version=f"%(prog)s {__version__}",
    )

    return parser


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
