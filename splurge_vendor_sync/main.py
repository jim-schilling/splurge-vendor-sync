"""Main entry point wrapper for splurge-vendor-sync.

This module provides the entry point that bridges CLI arguments to the
sync_vendor() function with proper error handling and exit codes.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from splurge_vendor_sync.exceptions import SplurgeVendorSyncError
from splurge_vendor_sync.sync import SyncResult, sync_vendor

logger = logging.getLogger(__name__)


def main(
    source_path: str | Path | None = None,
    target_path: str | Path | None = None,
    package: str | None = None,
    vendor: str = "_vendor",
    extensions: str | None = None,
    verbose: bool = False,
) -> int:
    """Main entry point for the sync operation.

    Args:
        source_path: Path to the source directory
        target_path: Path to the target directory
        package: Package name to sync
        vendor: Vendor directory name (default: '_vendor')
        extensions: Semicolon-separated file extensions
        verbose: Enable verbose logging (default: False)

    Returns:
        Exit code: 0 (success), 1 (runtime error), 2 (validation error)
    """
    # Set up logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )

    # Validate required parameters
    if source_path is None:
        print("Error: source_path is required", file=sys.stderr)
        return 2
    if target_path is None:
        print("Error: target_path is required", file=sys.stderr)
        return 2
    if package is None:
        print("Error: package is required", file=sys.stderr)
        return 2

    try:
        # Use defaults if not provided
        if extensions is None:
            extensions = "py;json;yml;yaml;ini"

        # Perform the sync
        result = sync_vendor(
            source_path=source_path,
            target_path=target_path,
            package=package,
            vendor=vendor,
            extensions=extensions,
        )

        # Output results
        _format_and_print_result(result)

        # Return success exit code
        return 0

    except SplurgeVendorSyncError as e:
        # Handle expected sync errors
        error_msg = _format_error(e)
        print(error_msg, file=sys.stderr)
        logger.error(f"Sync error: {error_msg}")

        # Determine exit code based on error type
        if "type" in str(type(e).__name__).lower() or "value" in str(type(e).__name__).lower():
            return 2  # Validation error
        else:
            return 1  # Runtime error

    except KeyboardInterrupt:
        print("\nSync cancelled by user", file=sys.stderr)
        return 1

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg, file=sys.stderr)
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


def _format_and_print_result(result: SyncResult) -> None:
    """Format and print the sync result."""
    status = result["status"]
    files_removed = result["files_removed"]
    files_copied = result["files_copied"]
    dirs_created = result["directories_created"]

    # Print summary
    print(f"Status: {status.upper()}")
    print(f"Files removed: {files_removed}")
    print(f"Files copied: {files_copied}")
    print(f"Directories created: {dirs_created}")

    # Print errors if any
    if result["errors"]:
        print(f"\nErrors ({len(result['errors'])}):")
        for error in result["errors"]:
            print(f"  - {error}")


def _format_error(error: SplurgeVendorSyncError) -> str:
    """Format an error for display."""
    error_type = type(error).__name__
    error_code = getattr(error, "error_code", "unknown")
    message = str(error)

    return f"{error_type} ({error_code}): {message}"


if __name__ == "__main__":
    # This would normally be called from CLI, but allow direct invocation for testing
    exit_code = main()
    sys.exit(exit_code)
