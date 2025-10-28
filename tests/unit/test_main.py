"""Unit tests for splurge_vendor_sync.main module."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

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

    def test_main_with_complex_package_structure(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() with complex package structure including subdirectories."""
        source, target = temp_workspace

        # Create a more complex package structure
        package = source / "complex_pkg"
        package.mkdir()
        (package / "module.py").write_text("# Module 1")
        (package / "config.json").write_text('{"key": "value"}')

        sub_dir = package / "submodule"
        sub_dir.mkdir()
        (sub_dir / "utils.py").write_text("# Utils")
        (sub_dir / "settings.json").write_text("{}")

        exit_code = main(
            source_path=source,
            target_path=target,
            package="complex_pkg",
        )

        assert exit_code == 0
        vendor_pkg = target / "_vendor" / "complex_pkg"
        assert vendor_pkg.exists()
        assert (vendor_pkg / "module.py").exists()
        assert (vendor_pkg / "config.json").exists()
        assert (vendor_pkg / "submodule" / "utils.py").exists()

    def test_main_with_multiple_file_types(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() syncs only specified file extensions."""
        source, target = temp_workspace

        package = source / "multi_ext_pkg"
        package.mkdir()
        (package / "main.py").write_text("# Python")
        (package / "config.json").write_text("{}")
        (package / "readme.txt").write_text("# Readme")
        (package / "script.sh").write_text("#!/bin/bash")

        # Only sync py and json files
        exit_code = main(
            source_path=source,
            target_path=target,
            package="multi_ext_pkg",
            extensions="py;json",
        )

        assert exit_code == 0
        vendor_pkg = target / "_vendor" / "multi_ext_pkg"
        assert (vendor_pkg / "main.py").exists()
        assert (vendor_pkg / "config.json").exists()
        assert not (vendor_pkg / "readme.txt").exists()
        assert not (vendor_pkg / "script.sh").exists()

    def test_main_handles_resync_of_existing_vendor(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() handles re-syncing when vendor directory already exists."""
        source, target = temp_workspace

        package = source / "resync_pkg"
        package.mkdir()
        (package / "new.py").write_text("# New file")

        # First sync
        exit_code = main(
            source_path=source,
            target_path=target,
            package="resync_pkg",
        )
        assert exit_code == 0

        vendor_pkg = target / "_vendor" / "resync_pkg"
        assert (vendor_pkg / "new.py").exists()

        # Add an old file to the vendor directory that should be removed
        (vendor_pkg / "old.py").write_text("# Old file")
        assert (vendor_pkg / "old.py").exists()

        # Second sync - old files should be removed
        exit_code = main(
            source_path=source,
            target_path=target,
            package="resync_pkg",
        )
        assert exit_code == 0
        assert (vendor_pkg / "new.py").exists()
        assert not (vendor_pkg / "old.py").exists()

    def test_main_empty_package(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() with empty package (no matching files)."""
        source, target = temp_workspace

        package = source / "empty_pkg"
        package.mkdir()
        (package / "readme.txt").write_text("No Python files here")

        # Only sync py files
        exit_code = main(
            source_path=source,
            target_path=target,
            package="empty_pkg",
            extensions="py",
        )

        assert exit_code == 0
        vendor_pkg = target / "_vendor" / "empty_pkg"
        assert vendor_pkg.exists()  # Directory created but empty
