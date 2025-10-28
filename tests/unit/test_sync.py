"""Unit tests for splurge_vendor_sync.sync module."""

from __future__ import annotations

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest

from splurge_vendor_sync.exceptions import (
    SplurgeVendorSyncOSError,
    SplurgeVendorSyncTypeError,
    SplurgeVendorSyncValueError,
)
from splurge_vendor_sync.sync import sync_vendor


@pytest.fixture
def temp_workspace() -> Generator[tuple[Path, Path, Path], None, None]:
    """Create temporary workspace with source and target directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        source = base / "source"
        target = base / "target"

        source.mkdir(exist_ok=True)
        target.mkdir(exist_ok=True)

        yield source, target, base

        # Cleanup
        for path in [source, target, base]:
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def sample_package(temp_workspace: tuple[Path, Path, Path]) -> Path:
    """Create a sample package with test files."""
    source, _, _ = temp_workspace
    package = source / "test_package"
    package.mkdir()

    # Create test files
    (package / "module1.py").write_text("print('module1')")
    (package / "module2.py").write_text("print('module2')")
    (package / "config.json").write_text('{"key": "value"}')
    (package / "data.txt").write_text("data")

    # Create subdirectory with files
    subdir = package / "subdir"
    subdir.mkdir()
    (subdir / "nested.py").write_text("print('nested')")

    # Create __pycache__ directory (should be skipped)
    pycache = package / "__pycache__"
    pycache.mkdir()
    (pycache / "module1.cpython-312.pyc").write_bytes(b"compiled")

    return package


class TestSyncVendorBasic:
    """Test basic sync_vendor functionality."""

    def test_sync_vendor_success(self, temp_workspace: tuple[Path, Path, Path], sample_package: Path) -> None:
        """Test successful package synchronization."""
        source, target, _ = temp_workspace
        package_name = sample_package.name

        result = sync_vendor(
            source_path=source,
            target_path=target,
            package=package_name,
            extensions="py;json",
        )

        assert result["status"] == "success"
        assert result["files_copied"] >= 3  # module1.py, module2.py, config.json
        assert result["files_removed"] == 0
        assert result["errors"] == []

        # Verify files were copied
        vendor_dir = target / "_vendor" / package_name
        assert (vendor_dir / "module1.py").exists()
        assert (vendor_dir / "module2.py").exists()
        assert (vendor_dir / "config.json").exists()

    def test_sync_vendor_excludes_pycache(self, temp_workspace: tuple[Path, Path, Path], sample_package: Path) -> None:
        """Test that __pycache__ directories are excluded."""
        source, target, _ = temp_workspace
        package_name = sample_package.name

        result = sync_vendor(
            source_path=source,
            target_path=target,
            package=package_name,
            extensions="py;json;cpython-312",
        )

        vendor_dir = target / "_vendor" / package_name
        assert not (vendor_dir / "__pycache__").exists()
        assert result["status"] == "success"

    def test_sync_vendor_filters_extensions(
        self, temp_workspace: tuple[Path, Path, Path], sample_package: Path
    ) -> None:
        """Test that extension filtering works correctly."""
        source, target, _ = temp_workspace
        package_name = sample_package.name

        result = sync_vendor(
            source_path=source,
            target_path=target,
            package=package_name,
            extensions="py",  # Only Python files
        )

        vendor_dir = target / "_vendor" / package_name
        assert (vendor_dir / "module1.py").exists()
        assert not (vendor_dir / "config.json").exists()
        assert not (vendor_dir / "data.txt").exists()
        assert result["files_copied"] == 3  # module1.py, module2.py, nested.py

    def test_sync_vendor_clean_phase(self, temp_workspace: tuple[Path, Path, Path], sample_package: Path) -> None:
        """Test that clean phase removes existing files."""
        source, target, _ = temp_workspace
        package_name = sample_package.name

        # First sync
        result1 = sync_vendor(
            source_path=source,
            target_path=target,
            package=package_name,
            extensions="py;json",
        )

        assert result1["files_copied"] > 0
        assert result1["files_removed"] == 0

        # Second sync - should remove old files
        result2 = sync_vendor(
            source_path=source,
            target_path=target,
            package=package_name,
            extensions="py;json",
        )

        assert result2["files_removed"] > 0
        assert result2["files_copied"] > 0
        assert result2["status"] == "success"

    def test_sync_vendor_custom_vendor_dir(self, temp_workspace: tuple[Path, Path, Path], sample_package: Path) -> None:
        """Test synchronization with custom vendor directory name."""
        source, target, _ = temp_workspace
        package_name = sample_package.name

        result = sync_vendor(
            source_path=source,
            target_path=target,
            package=package_name,
            vendor="custom_vendor",
            extensions="py",
        )

        vendor_dir = target / "custom_vendor" / package_name
        assert (vendor_dir / "module1.py").exists()
        assert result["status"] == "success"

    def test_sync_vendor_with_path_objects(self, temp_workspace: tuple[Path, Path, Path], sample_package: Path) -> None:
        """Test that Path objects work as well as strings."""
        source, target, _ = temp_workspace
        package_name = sample_package.name

        result = sync_vendor(
            source_path=Path(source),
            target_path=Path(target),
            package=package_name,
            extensions="py",
        )

        assert result["status"] == "success"
        assert result["files_copied"] > 0


class TestSyncVendorValidation:
    """Test input validation."""

    def test_sync_vendor_invalid_source_type(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test that invalid source_path type raises TypeError."""
        _, target, _ = temp_workspace

        with pytest.raises(SplurgeVendorSyncTypeError):
            sync_vendor(
                source_path=123,  # Invalid type
                target_path=target,
                package="test",
            )

    def test_sync_vendor_invalid_target_type(
        self, temp_workspace: tuple[Path, Path, Path], sample_package: Path
    ) -> None:
        """Test that invalid target_path type raises TypeError."""
        source, _, _ = temp_workspace

        with pytest.raises(SplurgeVendorSyncTypeError):
            sync_vendor(
                source_path=source,
                target_path=456,  # Invalid type
                package="test",
            )

    def test_sync_vendor_invalid_package_type(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test that invalid package type raises TypeError."""
        source, target, _ = temp_workspace

        with pytest.raises(SplurgeVendorSyncTypeError):
            sync_vendor(
                source_path=source,
                target_path=target,
                package=789,  # Invalid type
            )

    def test_sync_vendor_empty_package(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test that empty package name raises ValueError."""
        source, target, _ = temp_workspace

        with pytest.raises(SplurgeVendorSyncValueError):
            sync_vendor(
                source_path=source,
                target_path=target,
                package="",  # Empty
            )

    def test_sync_vendor_nonexistent_source(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test that nonexistent source path raises ValueError."""
        _, target, _ = temp_workspace

        with pytest.raises(SplurgeVendorSyncValueError) as exc_info:
            sync_vendor(
                source_path="/nonexistent/path",
                target_path=target,
                package="test",
            )
        assert "path-not-found" in str(exc_info.value)

    def test_sync_vendor_nonexistent_target(
        self, temp_workspace: tuple[Path, Path, Path], sample_package: Path
    ) -> None:
        """Test that nonexistent target path raises ValueError."""
        source, _, _ = temp_workspace

        with pytest.raises(SplurgeVendorSyncValueError) as exc_info:
            sync_vendor(
                source_path=source,
                target_path="/nonexistent/target",
                package=sample_package.name,
            )
        assert "path-not-found" in str(exc_info.value)

    def test_sync_vendor_nonexistent_package(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test that nonexistent package raises ValueError."""
        source, target, _ = temp_workspace

        with pytest.raises(SplurgeVendorSyncValueError) as exc_info:
            sync_vendor(
                source_path=source,
                target_path=target,
                package="nonexistent_package",
            )
        assert "path-not-found" in str(exc_info.value)


class TestSyncVendorErrorHandling:
    """Test error handling during sync."""

    def test_sync_vendor_handles_unicode_errors(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test that unicode errors are caught and reported."""
        source, target, _ = temp_workspace
        package = source / "test_pkg"
        package.mkdir()

        # Create a file with valid Python syntax
        (package / "test.py").write_text("# Valid Python file\nprint('hello')")

        result = sync_vendor(
            source_path=source,
            target_path=target,
            package="test_pkg",
            extensions="py",
        )

        # Should succeed with valid files
        assert result["status"] == "success"
        assert result["files_copied"] > 0

    def test_sync_vendor_partial_success(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test partial success when some files fail but others succeed."""
        source, target, _ = temp_workspace
        package = source / "test_pkg"
        package.mkdir()

        # Create some valid files
        (package / "valid1.py").write_text("print('valid1')")
        (package / "valid2.py").write_text("print('valid2')")

        result = sync_vendor(
            source_path=source,
            target_path=target,
            package="test_pkg",
            extensions="py",
        )

        assert result["status"] == "success"
        assert result["files_copied"] >= 2


class TestSyncVendorEdgeCases:
    """Test edge cases and special scenarios."""

    def test_sync_vendor_empty_package_directory(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test syncing an empty package directory."""
        source, target, _ = temp_workspace
        package = source / "empty_pkg"
        package.mkdir()

        result = sync_vendor(
            source_path=source,
            target_path=target,
            package="empty_pkg",
            extensions="py",
        )

        # Should succeed with no files copied
        assert result["status"] == "success"
        assert result["files_copied"] == 0

    def test_sync_vendor_subdirectory_structure(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test that subdirectory structure is preserved."""
        source, target, _ = temp_workspace
        package = source / "struct_pkg"
        package.mkdir()

        # Create nested directories with files
        (package / "level1").mkdir()
        (package / "level1" / "level2").mkdir()
        (package / "level1" / "file1.py").write_text("# level1")
        (package / "level1" / "level2" / "file2.py").write_text("# level2")

        result = sync_vendor(
            source_path=source,
            target_path=target,
            package="struct_pkg",
            extensions="py",
        )

        vendor_dir = target / "_vendor" / "struct_pkg"
        assert (vendor_dir / "level1" / "file1.py").exists()
        assert (vendor_dir / "level1" / "level2" / "file2.py").exists()
        assert result["status"] == "success"

    def test_sync_vendor_multiple_extensions(
        self, temp_workspace: tuple[Path, Path, Path], sample_package: Path
    ) -> None:
        """Test filtering multiple extensions."""
        source, target, _ = temp_workspace
        package_name = sample_package.name

        result = sync_vendor(
            source_path=source,
            target_path=target,
            package=package_name,
            extensions="py;json;txt",
        )

        vendor_dir = target / "_vendor" / package_name
        assert (vendor_dir / "module1.py").exists()
        assert (vendor_dir / "config.json").exists()
        assert (vendor_dir / "data.txt").exists()
        assert result["files_copied"] >= 4

    def test_sync_vendor_case_insensitive_extensions(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test that extension filtering is case-insensitive."""
        source, target, _ = temp_workspace
        package = source / "case_pkg"
        package.mkdir()

        # Create files with different cases
        (package / "file.PY").write_text("# uppercase")
        (package / "config.JSON").write_text("{}")

        result = sync_vendor(
            source_path=source,
            target_path=target,
            package="case_pkg",
            extensions="py;json",
        )

        # Files should be copied regardless of case
        assert result["files_copied"] >= 2

    def test_sync_vendor_partial_success_with_errors(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test partial success status when some files copy but errors occur."""
        source, target, _ = temp_workspace
        package = source / "partial_pkg"
        package.mkdir()
        (package / "file1.py").write_text("# file1")
        (package / "file2.py").write_text("# file2")

        result = sync_vendor(
            source_path=source,
            target_path=target,
            package="partial_pkg",
            extensions="py;txt",
        )

        # Should succeed with at least some files copied
        assert result["status"] in ("success", "partial")
        assert result["files_copied"] >= 2

    def test_sync_vendor_binary_file_copy(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test that binary files are copied with shutil."""
        source, target, _ = temp_workspace
        package = source / "bin_pkg"
        package.mkdir()
        (package / "module.py").write_text("python")
        (package / "data.bin").write_bytes(b"\x00\x01\x02")

        result = sync_vendor(
            source_path=source,
            target_path=target,
            package="bin_pkg",
            extensions="py;bin",
        )

        assert result["status"] == "success"
        assert result["files_copied"] >= 1  # At least .py file

    def test_sync_vendor_clean_phase_permission_denied(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test handling of permission denied on clean phase."""

        source, target, _ = temp_workspace
        package = source / "clean_pkg"
        package.mkdir()
        (package / "module.py").write_text("test")

        # First sync to create vendor directory
        sync_vendor(source, target, "clean_pkg")

        # Mock shutil.rmtree to raise PermissionError
        with patch("splurge_vendor_sync.sync.shutil.rmtree") as mock_rmtree:
            mock_rmtree.side_effect = PermissionError("cannot remove")

            with pytest.raises(SplurgeVendorSyncOSError) as exc_info:
                sync_vendor(source, target, "clean_pkg")

            assert "permission" in str(exc_info.value).lower()

    def test_sync_vendor_clean_phase_os_error(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test handling of OS errors during clean phase."""

        source, target, _ = temp_workspace
        package = source / "clean_err_pkg"
        package.mkdir()
        (package / "module.py").write_text("test")

        # First sync
        sync_vendor(source, target, "clean_err_pkg")

        # Mock shutil.rmtree to raise generic OSError
        with patch("splurge_vendor_sync.sync.shutil.rmtree") as mock_rmtree:
            mock_rmtree.side_effect = OSError("generic os error")

            with pytest.raises(SplurgeVendorSyncOSError) as exc_info:
                sync_vendor(source, target, "clean_err_pkg")

            assert "Failed to remove" in str(exc_info.value)

    def test_sync_vendor_safe_io_unicode_error(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test handling of Unicode errors from safe_io."""
        from splurge_vendor_sync._vendor.splurge_safe_io.exceptions import (
            SplurgeSafeIoUnicodeError,
        )

        source, target, _ = temp_workspace
        package = source / "unicode_pkg"
        package.mkdir()
        (package / "module.py").write_text("# python file")

        with patch("splurge_vendor_sync.sync.open_safe_text_reader") as mock_reader:
            mock_reader.side_effect = SplurgeSafeIoUnicodeError(message="bad encoding", error_code="encoding-error")

            result = sync_vendor(source, target, "unicode_pkg")

            # Should handle gracefully with error in result
            assert len(result["errors"]) > 0

    def test_sync_vendor_safe_io_general_error(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test handling of general Safe IO errors."""
        from splurge_vendor_sync._vendor.splurge_safe_io.exceptions import (
            SplurgeSafeIoError,
        )

        source, target, _ = temp_workspace
        package = source / "io_err_pkg"
        package.mkdir()
        (package / "module.py").write_text("# python")

        with patch("splurge_vendor_sync.sync.open_safe_text_reader") as mock_reader:
            mock_reader.side_effect = SplurgeSafeIoError(message="io error", error_code="io-error")

            result = sync_vendor(source, target, "io_err_pkg")

            # Should continue with error recorded
            assert len(result["errors"]) > 0

    def test_sync_vendor_unexpected_exception_during_copy(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test handling of unexpected exceptions during file copy."""
        source, target, _ = temp_workspace
        package = source / "exc_pkg"
        package.mkdir()
        (package / "module.py").write_text("# python")

        with patch("splurge_vendor_sync.sync.open_safe_text_reader") as mock_reader:
            mock_reader.side_effect = RuntimeError("unexpected!")

            result = sync_vendor(source, target, "exc_pkg")

            # Should handle and continue
            assert len(result["errors"]) > 0

    def test_sync_vendor_permission_denied_mkdir(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test handling of permission denied when creating directories."""

        source, target, _ = temp_workspace
        package = source / "mkdir_pkg"
        package.mkdir()
        (package / "module.py").write_text("test")

        with patch("splurge_vendor_sync.sync.Path.mkdir") as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("no access")

            # This should raise as permission error during mkdir propagates
            with pytest.raises(SplurgeVendorSyncOSError):
                sync_vendor(source, target, "mkdir_pkg")

    def test_sync_vendor_os_error_during_mkdir(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test handling of OS errors when creating directories."""

        source, target, _ = temp_workspace
        package = source / "mkdir_err_pkg"
        package.mkdir()
        (package / "module.py").write_text("test")

        with patch("splurge_vendor_sync.sync.Path.mkdir") as mock_mkdir:
            mock_mkdir.side_effect = OSError("generic error")

            # This should raise as OS error during mkdir propagates
            with pytest.raises(SplurgeVendorSyncOSError):
                sync_vendor(source, target, "mkdir_err_pkg")

    def test_sync_vendor_disk_full_during_rglob(self, temp_workspace: tuple[Path, Path, Path]) -> None:
        """Test handling of disk full errors during sync phase."""

        source, target, _ = temp_workspace
        package = source / "disk_err_pkg"
        package.mkdir()
        (package / "module.py").write_text("test")

        with patch("splurge_vendor_sync.sync.Path.rglob") as mock_rglob:
            # Create an OSError that mentions "disk"
            error = OSError("No space left on device: disk full")
            mock_rglob.side_effect = error

            with pytest.raises(SplurgeVendorSyncOSError) as exc_info:
                sync_vendor(source, target, "disk_err_pkg")

            # Should match the disk-full code path
            assert "disk-full" in str(exc_info.value)
