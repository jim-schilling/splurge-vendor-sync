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
        """Test CLI with missing required arguments."""
        with pytest.raises(SystemExit):
            import sys

            original_argv = sys.argv
            try:
                sys.argv = ["splurge-vendor-sync"]
                cli_main()
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
