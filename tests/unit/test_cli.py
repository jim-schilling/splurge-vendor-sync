"""Unit tests for splurge_vendor_sync.cli module."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from splurge_vendor_sync import __version__
from splurge_vendor_sync.cli import main as cli_main


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
        (package / "config.json").write_text('{"key": "value"}')

        yield source, target


class TestCLIBasic:
    """Test CLI argument parsing and execution."""

    def test_cli_help(self, capsys) -> None:
        """Test CLI help output."""
        with pytest.raises(SystemExit) as exc_info:
            import sys

            original_argv = sys.argv
            try:
                sys.argv = ["splurge-vendor-sync", "--help"]
                cli_main()
            finally:
                sys.argv = original_argv

        # Help should exit with code 0
        assert exc_info.value.code == 0

    def test_cli_version(self, capsys) -> None:
        """Test CLI version output."""
        with pytest.raises(SystemExit) as exc_info:
            import sys

            original_argv = sys.argv
            try:
                sys.argv = ["splurge-vendor-sync", "--version"]
                cli_main()
            finally:
                sys.argv = original_argv

        # Version should exit with code 0
        assert exc_info.value.code == 0

    def test_cli_missing_required_args(self) -> None:
        """Test CLI with missing required arguments for sync mode."""
        import sys

        original_argv = sys.argv
        try:
            sys.argv = ["splurge-vendor-sync"]
            exit_code = cli_main()
            # Should fail due to missing required sync mode arguments
            assert exit_code == 2
        finally:
            sys.argv = original_argv

    def test_cli_success(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test successful CLI execution."""
        source, target = temp_workspace

        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                str(source),
                "--target",
                str(target),
                "--package",
                "test_pkg",
            ]
            exit_code = cli_main()
            assert exit_code == 0
        finally:
            sys.argv = original_argv

    def test_cli_with_vendor_option(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test CLI with custom vendor directory."""
        source, target = temp_workspace

        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                str(source),
                "--target",
                str(target),
                "--package",
                "test_pkg",
                "--vendor",
                "custom_vendor",
            ]
            exit_code = cli_main()
            assert exit_code == 0
            assert (target / "custom_vendor" / "test_pkg").exists()
        finally:
            sys.argv = original_argv

    def test_cli_with_extensions_option(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test CLI with custom extensions."""
        source, target = temp_workspace

        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                str(source),
                "--target",
                str(target),
                "--package",
                "test_pkg",
                "--extensions",
                "py;json",
            ]
            exit_code = cli_main()
            assert exit_code == 0
        finally:
            sys.argv = original_argv

    def test_cli_with_short_extensions_option(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test CLI with short -e option for extensions."""
        source, target = temp_workspace

        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                str(source),
                "--target",
                str(target),
                "--package",
                "test_pkg",
                "-e",
                "py",
            ]
            exit_code = cli_main()
            assert exit_code == 0
        finally:
            sys.argv = original_argv

    def test_cli_with_verbose_option(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test CLI with verbose option."""
        source, target = temp_workspace

        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                str(source),
                "--target",
                str(target),
                "--package",
                "test_pkg",
                "--verbose",
            ]
            exit_code = cli_main()
            assert exit_code == 0
        finally:
            sys.argv = original_argv

    def test_cli_with_short_verbose_option(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test CLI with short -v option for verbose."""
        source, target = temp_workspace

        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                str(source),
                "--target",
                str(target),
                "--package",
                "test_pkg",
                "-v",
            ]
            exit_code = cli_main()
            assert exit_code == 0
        finally:
            sys.argv = original_argv

    def test_cli_invalid_source_path(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test CLI with invalid source path."""
        _, target = temp_workspace

        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                "/invalid/source",
                "--target",
                str(target),
                "--package",
                "test_pkg",
            ]
            exit_code = cli_main()
            assert exit_code == 2  # Validation error
        finally:
            sys.argv = original_argv

    def test_cli_invalid_package(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test CLI with nonexistent package."""
        source, target = temp_workspace

        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                str(source),
                "--target",
                str(target),
                "--package",
                "nonexistent",
            ]
            exit_code = cli_main()
            assert exit_code == 2  # Validation error
        finally:
            sys.argv = original_argv

    def test_cli_with_verbose_and_ext_flags(self, temp_workspace: tuple[Path, Path], capsys) -> None:
        """Test CLI with combined --verbose and --ext flags."""
        source, target = temp_workspace

        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                str(source),
                "--target",
                str(target),
                "--package",
                "test_pkg",
                "--verbose",
                "--ext",
                "py;json",
            ]
            exit_code = cli_main()
            assert exit_code == 0
            # Verify the sync completed successfully
            assert (target / "_vendor" / "test_pkg").exists()
            assert (target / "_vendor" / "test_pkg" / "module.py").exists()
            assert (target / "_vendor" / "test_pkg" / "config.json").exists()
        finally:
            sys.argv = original_argv

    def test_cli_version_output(self, capsys) -> None:
        """Test CLI version output contains expected version string."""
        import sys

        original_argv = sys.argv
        try:
            sys.argv = ["splurge-vendor-sync", "--version"]
            with pytest.raises(SystemExit) as exc_info:
                cli_main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            # Verify version output contains the program name and version
            assert "splurge-vendor-sync" in captured.out
            assert __version__ in captured.out
        finally:
            sys.argv = original_argv

    def test_cli_all_flags_combined(self, temp_workspace: tuple[Path, Path], capsys) -> None:
        """Test CLI with all optional flags combined."""
        source, target = temp_workspace

        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                str(source),
                "--target",
                str(target),
                "--package",
                "test_pkg",
                "--vendor",
                "my_vendor",
                "--ext",
                "py;json;ini",
                "--verbose",
            ]
            exit_code = cli_main()
            assert exit_code == 0
            # Verify custom vendor directory was used
            assert (target / "my_vendor" / "test_pkg").exists()
            assert (target / "my_vendor" / "test_pkg" / "module.py").exists()
            assert (target / "my_vendor" / "test_pkg" / "config.json").exists()
        finally:
            sys.argv = original_argv


@pytest.fixture
def temp_vendor_structure() -> Generator[Path, None, None]:
    """Create a temporary vendor directory structure with test packages."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        target = base / "project"
        target.mkdir()

        vendor = target / "_vendor"
        vendor.mkdir()

        # Package 1: splurge_safe_io with __version__ in __init__.py
        pkg1 = vendor / "splurge_safe_io"
        pkg1.mkdir()
        (pkg1 / "__init__.py").write_text('__version__ = "2025.4.3"\n')

        # Package 2: splurge_exceptions with __version__ in __init__.py
        pkg2 = vendor / "splurge_exceptions"
        pkg2.mkdir()
        (pkg2 / "__init__.py").write_text('__version__ = "2025.3.1"\n')

        # Package 3: splurge_zippy with no __version__
        pkg3 = vendor / "splurge_zippy"
        pkg3.mkdir()
        (pkg3 / "__init__.py").write_text("# No version here\n")

        yield target


class TestCLIScan:
    """Test CLI scan functionality."""

    def test_cli_scan_default_version_tag(self, temp_vendor_structure: Path, capsys) -> None:
        """Test scan with default __version__ tag."""
        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                "/dummy",
                "--target",
                str(temp_vendor_structure),
                "--package",
                "dummy",
                "--scan",
            ]
            exit_code = cli_main()
            assert exit_code == 0

            captured = capsys.readouterr()
            # Verify output contains package versions
            assert "splurge_safe_io 2025.4.3" in captured.out
            assert "splurge_exceptions 2025.3.1" in captured.out
            assert "splurge_zippy ?" in captured.out
        finally:
            sys.argv = original_argv

    def test_cli_scan_custom_version_tag(self, temp_vendor_structure: Path, capsys) -> None:
        """Test scan with custom version tag."""
        # Add a package with custom version tag
        vendor = temp_vendor_structure / "_vendor"
        pkg = vendor / "custom_pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text('MY_VERSION = "5.0.0"\n')

        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                "/dummy",
                "--target",
                str(temp_vendor_structure),
                "--package",
                "dummy",
                "--scan",
                "MY_VERSION",
            ]
            exit_code = cli_main()
            assert exit_code == 0

            captured = capsys.readouterr()
            # Should find the custom version
            assert "custom_pkg 5.0.0" in captured.out
        finally:
            sys.argv = original_argv

    def test_cli_scan_with_custom_vendor_dir(self, capsys) -> None:
        """Test scan with custom vendor directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            target = base / "project"
            target.mkdir()

            vendor = target / "my_vendor"
            vendor.mkdir()

            pkg = vendor / "test_pkg"
            pkg.mkdir()
            (pkg / "__init__.py").write_text('__version__ = "1.5.0"\n')

            import sys

            original_argv = sys.argv
            try:
                sys.argv = [
                    "splurge-vendor-sync",
                    "--source",
                    "/dummy",
                    "--target",
                    str(target),
                    "--package",
                    "dummy",
                    "--scan",
                    "--vendor",
                    "my_vendor",
                ]
                exit_code = cli_main()
                assert exit_code == 0

                captured = capsys.readouterr()
                assert "test_pkg 1.5.0" in captured.out
            finally:
                sys.argv = original_argv

    def test_cli_scan_missing_target_path(self) -> None:
        """Test scan fails without target path."""
        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                "/dummy",
                "--package",
                "dummy",
                "--scan",
            ]
            exit_code = cli_main()
            # Should fail due to missing target
            assert exit_code == 2
        finally:
            sys.argv = original_argv

    def test_cli_scan_invalid_target_path(self) -> None:
        """Test scan fails with invalid target path."""
        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                "/dummy",
                "--target",
                "/nonexistent/path",
                "--package",
                "dummy",
                "--scan",
            ]
            exit_code = cli_main()
            # Should fail due to invalid target
            assert exit_code == 2
        finally:
            sys.argv = original_argv

    def test_cli_scan_ignores_sync_parameters(self, temp_vendor_structure: Path, capsys) -> None:
        """Test that scan mode ignores source and package parameters."""
        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                "/invalid/source",
                "--target",
                str(temp_vendor_structure),
                "--package",
                "invalid_package",
                "--scan",
            ]
            exit_code = cli_main()
            # Should succeed even with invalid source/package since scan mode ignores them
            assert exit_code == 0

            captured = capsys.readouterr()
            # Verify scan completed
            assert "splurge_safe_io 2025.4.3" in captured.out
        finally:
            sys.argv = original_argv

    def test_cli_scan_empty_vendor_dir(self, capsys) -> None:
        """Test scan with empty vendor directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            target = base / "project"
            target.mkdir()

            vendor = target / "_vendor"
            vendor.mkdir()

            import sys

            original_argv = sys.argv
            try:
                sys.argv = [
                    "splurge-vendor-sync",
                    "--source",
                    "/dummy",
                    "--target",
                    str(target),
                    "--package",
                    "dummy",
                    "--scan",
                ]
                exit_code = cli_main()
                assert exit_code == 0

                captured = capsys.readouterr()
                # Empty vendor dir should produce no output
                assert captured.out.strip() == ""
            finally:
                sys.argv = original_argv

    def test_cli_scan_with_verbose_flag(self, temp_vendor_structure: Path, capsys) -> None:
        """Test scan with verbose flag."""
        import sys

        original_argv = sys.argv
        try:
            sys.argv = [
                "splurge-vendor-sync",
                "--source",
                "/dummy",
                "--target",
                str(temp_vendor_structure),
                "--package",
                "dummy",
                "--scan",
                "--verbose",
            ]
            exit_code = cli_main()
            assert exit_code == 0

            captured = capsys.readouterr()
            # Verbose flag should not affect scan output
            assert "splurge_safe_io 2025.4.3" in captured.out
        finally:
            sys.argv = original_argv
