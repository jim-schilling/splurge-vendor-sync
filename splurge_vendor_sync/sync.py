"""Core synchronization API for vendor package synchronization.

This module implements the main synchronization logic for splurge-vendor-sync.
It handles the two-phase sync process (clean and sync) with proper error handling
and statistics tracking.

DOMAINS: ['vendor_sync', 'sync', 'file_operations']
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import TypedDict

from ._vendor.splurge_safe_io.exceptions import (
    SplurgeSafeIoError,
    SplurgeSafeIoPathValidationError,
    SplurgeSafeIoUnicodeError,
)
from ._vendor.splurge_safe_io.path_validator import PathValidator
from ._vendor.splurge_safe_io.safe_text_file_reader import (
    open_safe_text_reader,
)
from ._vendor.splurge_safe_io.safe_text_file_writer import (
    TextFileWriteMode,
    open_safe_text_writer,
)
from .exceptions import (
    SplurgeVendorSyncError,
    SplurgeVendorSyncOSError,
    SplurgeVendorSyncTypeError,
    SplurgeVendorSyncValueError,
)

logger = logging.getLogger(__name__)


class SyncResult(TypedDict):
    """Type definition for sync_vendor() return value."""

    files_removed: int
    files_copied: int
    directories_created: int
    status: str
    errors: list[str]


class SyncPhaseResult(TypedDict):
    """Type definition for _sync_phase() return value."""

    files_copied: int
    directories_created: int
    errors: list[str]


def sync_vendor(
    source_path: str | Path,
    target_path: str | Path,
    package: str,
    vendor: str = "_vendor",
    extensions: str = "py;json;yml;yaml;ini",
) -> SyncResult:
    """Synchronize a source package to a target project's vendor directory.

    This function implements a two-phase synchronization:
    1. Clean Phase: Removes all existing files in the target vendor location
    2. Sync Phase: Copies all matching files from source to target

    Args:
        source_path: Root directory containing the source package
        target_path: Target project directory where vendor directory will be created
        package: Package subdirectory name to sync (e.g., 'splurge_exceptions')
        vendor: Vendor directory name (default: '_vendor')
        extensions: Semicolon-separated file extensions to include
                   (default: 'py;json;yml;yaml;ini')

    Returns:
        Dictionary with sync results:
            'files_removed': Number of files removed in clean phase
            'files_copied': Number of files copied in sync phase
            'directories_created': Number of directories created
            'status': 'success' | 'partial' | 'failed'
            'errors': List of error messages

    Raises:
        SplurgeVendorSyncTypeError: If parameter types are invalid
        SplurgeVendorSyncValueError: If parameter values are invalid or paths don't exist
        SplurgeVendorSyncOSError: If I/O operations fail
        SplurgeVendorSyncUnicodeError: If file encoding fails
    """
    # Initialize result dictionary
    result: SyncResult = {
        "files_removed": 0,
        "files_copied": 0,
        "directories_created": 0,
        "status": "success",
        "errors": [],
    }

    try:
        # Phase 1: Input Validation
        _validate_inputs(source_path, target_path, package, vendor, extensions)

        # Phase 2: Path Normalization & Validation
        validated_source = _validate_and_get_paths(source_path, target_path, package, vendor)
        source_package_path = validated_source["source_package_path"]
        vendor_target_path = validated_source["vendor_target_path"]

        # Phase 3: Clean Phase
        result["files_removed"] = _clean_phase(vendor_target_path)

        # Phase 4: Sync Phase
        sync_stats = _sync_phase(
            source_package_path,
            vendor_target_path,
            extensions,
        )
        result["files_copied"] = sync_stats["files_copied"]
        result["directories_created"] = sync_stats["directories_created"]
        result["errors"] = sync_stats["errors"]

        # Phase 5: Determine final status
        if result["errors"]:
            result["status"] = "partial" if result["files_copied"] > 0 else "failed"
        else:
            result["status"] = "success"

        logger.info(
            f"Sync completed with status '{result['status']}': "
            f"removed {result['files_removed']} files, "
            f"copied {result['files_copied']} files, "
            f"created {result['directories_created']} directories"
        )

    except SplurgeVendorSyncError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Map unexpected exceptions to our exception types
        result["status"] = "failed"
        result["errors"].append(f"Unexpected error: {str(e)}")
        logger.error(f"Unexpected error during sync: {e}")
        raise SplurgeVendorSyncError(
            message=f"Sync failed with unexpected error: {str(e)}",
            error_code="sync-failed",
        ) from e

    return result


def _validate_inputs(
    source_path: str | Path,
    target_path: str | Path,
    package: str,
    vendor: str,
    extensions: str,
) -> None:
    """Validate input parameters."""
    # Type validation
    if not isinstance(source_path, str | Path):
        raise SplurgeVendorSyncTypeError(
            message=f"source_path must be str or Path, got {type(source_path).__name__}",
            error_code="type-mismatch",
        )

    if not isinstance(target_path, str | Path):
        raise SplurgeVendorSyncTypeError(
            message=f"target_path must be str or Path, got {type(target_path).__name__}",
            error_code="type-mismatch",
        )

    if not isinstance(package, str):
        raise SplurgeVendorSyncTypeError(
            message=f"package must be str, got {type(package).__name__}",
            error_code="type-mismatch",
        )

    if not isinstance(vendor, str):
        raise SplurgeVendorSyncTypeError(
            message=f"vendor must be str, got {type(vendor).__name__}",
            error_code="type-mismatch",
        )

    if not isinstance(extensions, str):
        raise SplurgeVendorSyncTypeError(
            message=f"extensions must be str, got {type(extensions).__name__}",
            error_code="type-mismatch",
        )

    # Value validation
    if not package or package.strip() == "":
        raise SplurgeVendorSyncValueError(
            message="package must be non-empty",
            error_code="invalid-package",
        )

    if not vendor or vendor.strip() == "":
        raise SplurgeVendorSyncValueError(
            message="vendor must be non-empty",
            error_code="invalid-value",
        )

    if not extensions or extensions.strip() == "":
        raise SplurgeVendorSyncValueError(
            message="extensions must be non-empty",
            error_code="invalid-value",
        )


def _validate_and_get_paths(
    source_path: str | Path,
    target_path: str | Path,
    package: str,
    vendor: str = "_vendor",
) -> dict[str, Path]:
    """Validate paths and return normalized versions."""
    source_path = Path(source_path).resolve()
    target_path = Path(target_path).resolve()

    # Validate source path exists
    if not source_path.exists():
        raise SplurgeVendorSyncValueError(
            message=f"source_path does not exist: {source_path}",
            error_code="path-not-found",
        )

    # Validate source package exists
    source_package_path = source_path / package
    if not source_package_path.exists():
        raise SplurgeVendorSyncValueError(
            message=f"package directory not found: {source_package_path}",
            error_code="path-not-found",
        )

    # Validate target path exists
    if not target_path.exists():
        raise SplurgeVendorSyncValueError(
            message=f"target_path does not exist: {target_path}",
            error_code="path-not-found",
        )

    # Use PathValidator for security check on paths
    try:
        validator = PathValidator()
        validator.get_validated_path(source_package_path)
        validator.get_validated_path(target_path)
    except SplurgeSafeIoPathValidationError as e:
        raise SplurgeVendorSyncValueError(
            message=f"Path validation failed: {str(e)}",
            error_code="path-validation-failed",
        ) from e

    return {
        "source_package_path": source_package_path,
        "vendor_target_path": target_path / vendor / package,
    }


def _clean_phase(vendor_target_path: Path) -> int:
    """Remove existing vendor directory if it exists.

    Returns:
        Number of files removed
    """
    if not vendor_target_path.exists():
        return 0

    files_removed = 0
    try:
        # Count files before deletion
        for item in vendor_target_path.rglob("*"):
            if item.is_file():
                files_removed += 1

        # Remove the entire directory
        shutil.rmtree(vendor_target_path, ignore_errors=False)
        logger.info(f"Removed {files_removed} files from {vendor_target_path}")

    except PermissionError as e:
        raise SplurgeVendorSyncOSError(
            message=f"Permission denied removing {vendor_target_path}: {str(e)}",
            error_code="permission-denied",
        ) from e
    except OSError as e:
        raise SplurgeVendorSyncOSError(
            message=f"Failed to remove vendor directory: {str(e)}",
            error_code="deletion-failed",
        ) from e

    return files_removed


def _sync_phase(
    source_package_path: Path,
    vendor_target_path: Path,
    extensions: str,
) -> SyncPhaseResult:
    """Copy files from source to target vendor directory.

    Returns:
        Dictionary with:
            'files_copied': Number of files copied
            'directories_created': Number of directories created
            'errors': List of error messages
    """
    result: SyncPhaseResult = {
        "files_copied": 0,
        "directories_created": 0,
        "errors": [],
    }

    # Parse extensions
    ext_set = {ext.strip().lower() for ext in extensions.split(";")}

    try:
        # Create target directory
        vendor_target_path.parent.mkdir(parents=True, exist_ok=True)
        vendor_target_path.mkdir(parents=True, exist_ok=True)
        result["directories_created"] += 1

        # Recursively copy files
        for source_item in source_package_path.rglob("*"):
            # Skip __pycache__ directories
            if "__pycache__" in source_item.parts:
                continue

            # Calculate relative path
            relative_path = source_item.relative_to(source_package_path)
            target_item = vendor_target_path / relative_path

            try:
                if source_item.is_dir():
                    # Create directory
                    target_item.mkdir(parents=True, exist_ok=True)
                    result["directories_created"] += 1

                elif source_item.is_file():
                    # Check extension
                    file_ext = source_item.suffix.lstrip(".").lower()
                    if file_ext not in ext_set:
                        continue

                    # Create parent directories
                    target_item.parent.mkdir(parents=True, exist_ok=True)

                    # Copy file using SafeTextFileReader/Writer for text files
                    if file_ext in ("py", "json", "yml", "yaml", "ini", "md", "txt"):
                        try:
                            with open_safe_text_reader(source_item) as reader:
                                content = reader.read()

                            with open_safe_text_writer(
                                target_item,
                                file_write_mode=TextFileWriteMode.CREATE_OR_TRUNCATE,
                                create_parents=True,
                            ) as writer:
                                writer.write(content)

                        except SplurgeSafeIoUnicodeError as e:
                            result["errors"].append(f"Unicode error copying {source_item}: {str(e)}")
                            logger.warning(f"Unicode error: {e}")
                            continue
                        except SplurgeSafeIoError as e:
                            result["errors"].append(f"Error copying {source_item}: {str(e)}")
                            logger.warning(f"Safe IO error: {e}")
                            continue
                    else:
                        # Binary copy for other file types
                        shutil.copy2(source_item, target_item)

                    result["files_copied"] += 1
                    logger.debug(f"Copied {source_item} to {target_item}")

            except Exception as e:
                result["errors"].append(f"Error processing {source_item}: {str(e)}")
                logger.warning(f"Error processing {source_item}: {e}")
                continue

    except PermissionError as e:
        raise SplurgeVendorSyncOSError(
            message=f"Permission denied during sync: {str(e)}",
            error_code="permission-denied",
        ) from e
    except OSError as e:
        if "disk" in str(e).lower():
            raise SplurgeVendorSyncOSError(
                message=f"Disk full or I/O error: {str(e)}",
                error_code="disk-full",
            ) from e
        else:
            raise SplurgeVendorSyncOSError(
                message=f"Failed to copy files: {str(e)}",
                error_code="copy-failed",
            ) from e

    logger.info(
        f"Sync phase completed: copied {result['files_copied']} files, "
        f"created {result['directories_created']} directories"
    )

    return result
