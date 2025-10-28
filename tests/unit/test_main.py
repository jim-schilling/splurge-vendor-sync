"""Unit tests for splurge_vendor_sync.main module."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest

from splurge_vendor_sync.exceptions import (
    SplurgeVendorSyncValueError,
)
from splurge_vendor_sync.main import main


@pytest.fixture
def temp_workspace() -> Generator[tuple[Path, Path], None, None]:
    """Create temporary workspace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        source = base / "source"
        target = base / "target"

        source.mkdir(exist_ok=True)
        target.mkdir(exist_ok=True)

        # Create a sample package
        package = source / "test_pkg"
        package.mkdir()
        (package / "module.py").write_text("print('test')")

        yield source, target


class TestMainBasic:
    """Test main() entry point."""

    def test_main_success(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test successful main() execution."""
        source, target = temp_workspace

        exit_code = main(
            source_path=str(source),
            target_path=str(target),
            package="test_pkg",
            verbose=False,
        )

        assert exit_code == 0

    def test_main_with_path_objects(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() with Path objects."""
        source, target = temp_workspace

        exit_code = main(
            source_path=source,
            target_path=target,
            package="test_pkg",
            verbose=False,
        )

        assert exit_code == 0

    def test_main_missing_source_path(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() with missing source_path."""
        _, target = temp_workspace

        exit_code = main(
            source_path=None,
            target_path=target,
            package="test_pkg",
        )

        assert exit_code == 2  # Validation error

    def test_main_missing_target_path(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() with missing target_path."""
        source, _ = temp_workspace

        exit_code = main(
            source_path=source,
            target_path=None,
            package="test_pkg",
        )

        assert exit_code == 2  # Validation error

    def test_main_missing_package(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() with missing package."""
        source, target = temp_workspace

        exit_code = main(
            source_path=source,
            target_path=target,
            package=None,
        )

        assert exit_code == 2  # Validation error

    def test_main_custom_vendor_dir(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() with custom vendor directory."""
        source, target = temp_workspace

        exit_code = main(
            source_path=source,
            target_path=target,
            package="test_pkg",
            vendor="my_vendor",
        )

        assert exit_code == 0
        assert (target / "my_vendor" / "test_pkg").exists()

    def test_main_custom_extensions(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() with custom extensions."""
        source, target = temp_workspace

        exit_code = main(
            source_path=source,
            target_path=target,
            package="test_pkg",
            extensions="py;txt",
        )

        assert exit_code == 0

    def test_main_uses_default_extensions(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test that main() uses default extensions when not provided."""
        source, target = temp_workspace

        exit_code = main(
            source_path=source,
            target_path=target,
            package="test_pkg",
            extensions=None,
        )

        assert exit_code == 0

    def test_main_nonexistent_package(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() with nonexistent package."""
        source, target = temp_workspace

        exit_code = main(
            source_path=source,
            target_path=target,
            package="nonexistent",
        )

        assert exit_code == 2  # Validation error

    def test_main_sync_error(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() handles sync errors properly."""
        source, _ = temp_workspace

        exit_code = main(
            source_path=source,
            target_path="/invalid/target/path",
            package="test_pkg",
        )

        assert exit_code == 2  # Validation error for invalid target

    def test_main_verbose_mode(self, temp_workspace: tuple[Path, Path], capsys) -> None:
        """Test main() verbose logging."""
        source, target = temp_workspace

        exit_code = main(
            source_path=source,
            target_path=target,
            package="test_pkg",
            verbose=True,
        )

        assert exit_code == 0

    def test_main_keyboard_interrupt(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() handles KeyboardInterrupt."""
        source, target = temp_workspace

        with patch("splurge_vendor_sync.main.sync_vendor") as mock_sync:
            mock_sync.side_effect = KeyboardInterrupt()

            exit_code = main(
                source_path=source,
                target_path=target,
                package="test_pkg",
            )

            assert exit_code == 1  # Runtime error for interrupt

    def test_main_unexpected_exception(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() handles unexpected exceptions."""
        source, target = temp_workspace

        with patch("splurge_vendor_sync.main.sync_vendor") as mock_sync:
            mock_sync.side_effect = RuntimeError("Unexpected error")

            exit_code = main(
                source_path=source,
                target_path=target,
                package="test_pkg",
            )

            assert exit_code == 1  # Runtime error

    def test_main_type_error_from_sync(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() handles SplurgeVendorSyncTypeError."""
        from splurge_vendor_sync.exceptions import SplurgeVendorSyncTypeError

        source, target = temp_workspace

        with patch("splurge_vendor_sync.main.sync_vendor") as mock_sync:
            mock_sync.side_effect = SplurgeVendorSyncTypeError(message="Invalid type", error_code="type-error")

            exit_code = main(
                source_path=source,
                target_path=target,
                package="test_pkg",
            )

            assert exit_code == 2  # Validation error

    def test_main_value_error_from_sync(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() handles SplurgeVendorSyncValueError."""
        source, target = temp_workspace

        with patch("splurge_vendor_sync.main.sync_vendor") as mock_sync:
            mock_sync.side_effect = SplurgeVendorSyncValueError(message="Invalid value", error_code="value-error")

            exit_code = main(
                source_path=source,
                target_path=target,
                package="test_pkg",
            )

            assert exit_code == 2  # Validation error

    def test_main_os_error_from_sync(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() handles SplurgeVendorSyncOSError."""
        from splurge_vendor_sync.exceptions import SplurgeVendorSyncOSError

        source, target = temp_workspace

        with patch("splurge_vendor_sync.main.sync_vendor") as mock_sync:
            mock_sync.side_effect = SplurgeVendorSyncOSError(message="OS error", error_code="os-error")

            exit_code = main(
                source_path=source,
                target_path=target,
                package="test_pkg",
            )

            assert exit_code == 1  # Runtime error

    def test_main_result_with_errors(self, temp_workspace: tuple[Path, Path], capsys) -> None:
        """Test main() output with errors in result."""
        source, target = temp_workspace

        with patch("splurge_vendor_sync.main.sync_vendor") as mock_sync:
            mock_sync.return_value = {
                "files_removed": 0,
                "files_copied": 1,
                "directories_created": 1,
                "status": "partial",
                "errors": ["Error 1", "Error 2"],
            }

            exit_code = main(
                source_path=source,
                target_path=target,
                package="test_pkg",
            )

            assert exit_code == 0
            captured = capsys.readouterr()
            assert "Status: PARTIAL" in captured.out
            assert "Errors (2):" in captured.out
