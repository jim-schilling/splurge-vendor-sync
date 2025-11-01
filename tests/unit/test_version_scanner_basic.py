"""Unit tests for splurge_vendor_sync.version_scanner module."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from splurge_vendor_sync.version_scanner import (
    extract_version_from_file,
    format_version_output,
    scan_vendor_packages,
)


@pytest.fixture
def temp_vendor_structure() -> Generator[tuple[Path, Path], None, None]:
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

        # Package 2: splurge_exceptions with __version__ in __init__.py (double quotes)
        pkg2 = vendor / "splurge_exceptions"
        pkg2.mkdir()
        (pkg2 / "__init__.py").write_text('__version__ = "2025.3.1"\n')

        # Package 3: splurge_zippy with no __version__
        pkg3 = vendor / "splurge_zippy"
        pkg3.mkdir()
        (pkg3 / "__init__.py").write_text("# No version here\n")

        # Package 4: splurge_foo with __version__ in __main__.py (single quotes)
        pkg4 = vendor / "splurge_foo"
        pkg4.mkdir()
        (pkg4 / "__main__.py").write_text("__version__ = '1.0.0'\n")

        # Package 5: splurge_bar with __version__ in __init__.py but also another var
        pkg5 = vendor / "splurge_bar"
        pkg5.mkdir()
        init_content = """
MY_CONSTANT = "not_a_version"
__version__ = "3.0.0"
OTHER_VAR = "also_not_a_version"
"""
        (pkg5 / "__init__.py").write_text(init_content)

        yield target, vendor


class TestExtractVersionFromFile:
    """Test version extraction from individual Python files."""

    def test_extract_version_with_double_quotes(self, tmp_path: Path) -> None:
        """Test extraction of __version__ with double quotes."""
        file = tmp_path / "test.py"
        file.write_text('__version__ = "1.2.3"\n')

        version = extract_version_from_file(file)
        assert version == "1.2.3"

    def test_extract_version_with_single_quotes(self, tmp_path: Path) -> None:
        """Test extraction of __version__ with single quotes."""
        file = tmp_path / "test.py"
        file.write_text("__version__ = '1.2.3'\n")

        version = extract_version_from_file(file)
        assert version == "1.2.3"

    def test_extract_version_custom_tag(self, tmp_path: Path) -> None:
        """Test extraction with custom version tag."""
        file = tmp_path / "test.py"
        file.write_text('VERSION = "2.0.0"\n')

        version = extract_version_from_file(file, version_tag="VERSION")
        assert version == "2.0.0"

    def test_extract_version_not_found(self, tmp_path: Path) -> None:
        """Test when version tag is not found."""
        file = tmp_path / "test.py"
        file.write_text("# No version here\nx = 1\n")

        version = extract_version_from_file(file)
        assert version is None

    def test_extract_version_nonexistent_file(self, tmp_path: Path) -> None:
        """Test with nonexistent file."""
        file = tmp_path / "nonexistent.py"

        version = extract_version_from_file(file)
        assert version is None

    def test_extract_version_invalid_syntax(self, tmp_path: Path) -> None:
        """Test with file containing invalid Python syntax."""
        file = tmp_path / "test.py"
        file.write_text("this is not valid python !!!\n")

        version = extract_version_from_file(file)
        assert version is None

    def test_extract_version_multiple_assignments(self, tmp_path: Path) -> None:
        """Test extraction when multiple assignments exist."""
        file = tmp_path / "test.py"
        content = """
x = "not_version"
__version__ = "1.5.0"
y = "also_not_version"
"""
        file.write_text(content)

        version = extract_version_from_file(file)
        assert version == "1.5.0"

    def test_extract_version_non_string_value(self, tmp_path: Path) -> None:
        """Test when version is assigned non-string value."""
        file = tmp_path / "test.py"
        file.write_text("__version__ = 123\n")

        version = extract_version_from_file(file)
        assert version is None

    def test_extract_version_with_whitespace(self, tmp_path: Path) -> None:
        """Test extraction with various whitespace patterns."""
        file = tmp_path / "test.py"
        file.write_text("__version__   =   '1.0.0'   \n")

        version = extract_version_from_file(file)
        assert version == "1.0.0"

    def test_extract_version_utf8_encoding(self, tmp_path: Path) -> None:
        """Test extraction with UTF-8 encoded file."""
        file = tmp_path / "test.py"
        file.write_text('# -*- coding: utf-8 -*-\n__version__ = "1.0.0"\n', encoding="utf-8")

        version = extract_version_from_file(file)
        assert version == "1.0.0"


class TestScanVendorPackages:
    """Test scanning vendor directory for packages."""

    def test_scan_vendor_packages_basic(self, temp_vendor_structure: tuple[Path, Path]) -> None:
        """Test basic vendor package scanning."""
        target, _ = temp_vendor_structure

        versions = scan_vendor_packages(target)

        # Should find all 5 packages
        assert len(versions) == 5
        package_names = [v["package_name"] for v in versions]
        assert "splurge_safe_io" in package_names
        assert "splurge_exceptions" in package_names
        assert "splurge_zippy" in package_names
        assert "splurge_foo" in package_names
        assert "splurge_bar" in package_names

    def test_scan_vendor_packages_versions(self, temp_vendor_structure: tuple[Path, Path]) -> None:
        """Test that correct versions are found."""
        target, _ = temp_vendor_structure

        versions = scan_vendor_packages(target)
        version_dict = {v["package_name"]: v["version"] for v in versions}

        assert version_dict["splurge_safe_io"] == "2025.4.3"
        assert version_dict["splurge_exceptions"] == "2025.3.1"
        assert version_dict["splurge_zippy"] is None
        assert version_dict["splurge_foo"] == "1.0.0"
        assert version_dict["splurge_bar"] == "3.0.0"

    def test_scan_vendor_packages_sorted(self, temp_vendor_structure: tuple[Path, Path]) -> None:
        """Test that packages are returned in sorted order."""
        target, _ = temp_vendor_structure

        versions = scan_vendor_packages(target)
        package_names = [v["package_name"] for v in versions]

        assert package_names == sorted(package_names)

    def test_scan_vendor_packages_custom_tag(self, tmp_path: Path) -> None:
        """Test scanning with custom version tag."""
        target = tmp_path / "project"
        target.mkdir()

        vendor = target / "_vendor"
        vendor.mkdir()

        pkg = vendor / "test_pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text('MY_VERSION = "5.0.0"\n')

        versions = scan_vendor_packages(target, version_tag="MY_VERSION")
        assert len(versions) == 1
        assert versions[0]["version"] == "5.0.0"

    def test_scan_vendor_packages_custom_vendor_dir(self, tmp_path: Path) -> None:
        """Test scanning with custom vendor directory."""
        target = tmp_path / "project"
        target.mkdir()

        vendor = target / "custom_vendor"
        vendor.mkdir()

        pkg = vendor / "my_pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text('__version__ = "1.0.0"\n')

        versions = scan_vendor_packages(target, vendor_dir="custom_vendor")
        assert len(versions) == 1
        assert versions[0]["package_name"] == "my_pkg"

    def test_scan_vendor_packages_skips_hidden_dirs(self, tmp_path: Path) -> None:
        """Test that hidden directories (starting with _) are skipped."""
        target = tmp_path / "project"
        target.mkdir()

        vendor = target / "_vendor"
        vendor.mkdir()

        # Create a normal package
        pkg1 = vendor / "normal_pkg"
        pkg1.mkdir()
        (pkg1 / "__init__.py").write_text('__version__ = "1.0.0"\n')

        # Create a hidden package (should be skipped)
        pkg2 = vendor / "_hidden_pkg"
        pkg2.mkdir()
        (pkg2 / "__init__.py").write_text('__version__ = "2.0.0"\n')

        versions = scan_vendor_packages(target)
        assert len(versions) == 1
        assert versions[0]["package_name"] == "normal_pkg"

    def test_scan_vendor_packages_no_init_falls_back_to_main(self, tmp_path: Path) -> None:
        """Test that __main__.py is checked if __init__.py doesn't have version."""
        target = tmp_path / "project"
        target.mkdir()

        vendor = target / "_vendor"
        vendor.mkdir()

        pkg = vendor / "fallback_pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("# No version\n")
        (pkg / "__main__.py").write_text('__version__ = "3.5.0"\n')

        versions = scan_vendor_packages(target)
        assert len(versions) == 1
        assert versions[0]["version"] == "3.5.0"

    def test_scan_vendor_packages_prefers_init_over_main(self, tmp_path: Path) -> None:
        """Test that __init__.py version takes precedence over __main__.py."""
        target = tmp_path / "project"
        target.mkdir()

        vendor = target / "_vendor"
        vendor.mkdir()

        pkg = vendor / "priority_pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text('__version__ = "1.0.0"\n')
        (pkg / "__main__.py").write_text('__version__ = "2.0.0"\n')

        versions = scan_vendor_packages(target)
        assert len(versions) == 1
        assert versions[0]["version"] == "1.0.0"

    def test_scan_vendor_nonexistent_target(self, tmp_path: Path) -> None:
        """Test error when target path doesn't exist."""
        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(ValueError, match="Target path does not exist"):
            scan_vendor_packages(nonexistent)

    def test_scan_vendor_nonexistent_vendor_dir(self, tmp_path: Path) -> None:
        """Test error when vendor directory doesn't exist."""
        target = tmp_path / "project"
        target.mkdir()

        with pytest.raises(ValueError, match="Vendor directory does not exist"):
            scan_vendor_packages(target)

    def test_scan_vendor_packages_empty_vendor(self, tmp_path: Path) -> None:
        """Test scanning empty vendor directory."""
        target = tmp_path / "project"
        target.mkdir()

        vendor = target / "_vendor"
        vendor.mkdir()

        versions = scan_vendor_packages(target)
        assert len(versions) == 0


class TestFormatVersionOutput:
    """Test formatting of version output."""

    def test_format_version_output_single_package(self) -> None:
        """Test formatting with single package."""
        versions = [{"package_name": "my_pkg", "version": "1.0.0"}]

        output = format_version_output(versions)
        assert output == "my_pkg 1.0.0"

    def test_format_version_output_multiple_packages(self) -> None:
        """Test formatting with multiple packages."""
        versions = [
            {"package_name": "pkg1", "version": "1.0.0"},
            {"package_name": "pkg2", "version": "2.0.0"},
            {"package_name": "pkg3", "version": None},
        ]

        output = format_version_output(versions)
        expected = "pkg1 1.0.0\npkg2 2.0.0\npkg3 ?"
        assert output == expected

    def test_format_version_output_missing_versions(self) -> None:
        """Test formatting when all versions are missing."""
        versions = [
            {"package_name": "pkg1", "version": None},
            {"package_name": "pkg2", "version": None},
        ]

        output = format_version_output(versions)
        expected = "pkg1 ?\npkg2 ?"
        assert output == expected

    def test_format_version_output_empty_list(self) -> None:
        """Test formatting with empty list."""
        versions: list = []

        output = format_version_output(versions)
        assert output == ""

    def test_format_version_output_preserves_order(self) -> None:
        """Test that formatting preserves order of packages."""
        versions = [
            {"package_name": "zebra", "version": "1.0.0"},
            {"package_name": "apple", "version": "2.0.0"},
            {"package_name": "banana", "version": None},
        ]

        output = format_version_output(versions)
        lines = output.split("\n")
        assert lines[0] == "zebra 1.0.0"
        assert lines[1] == "apple 2.0.0"
        assert lines[2] == "banana ?"


class TestIntegration:
    """Integration tests for version scanner functionality."""

    def test_full_scan_workflow(self, temp_vendor_structure: tuple[Path, Path]) -> None:
        """Test complete scan workflow from directory to formatted output."""
        target, _ = temp_vendor_structure

        versions = scan_vendor_packages(target)
        output = format_version_output(versions)

        # Verify output format and content
        lines = output.split("\n")
        assert len(lines) == 5

        # Verify each line follows "package version" format
        for line in lines:
            parts = line.split(" ")
            assert len(parts) == 2
            assert parts[0]  # package name exists
            assert parts[1]  # version or ? exists

    def test_scan_with_real_vendored_packages(self) -> None:
        """Test scanning with actual splurge packages if available."""
        # This test would only work if run from the actual project
        # We'll create a temporary realistic structure
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            target = base / "project"
            target.mkdir()

            vendor = target / "_vendor"
            vendor.mkdir()

            # Create realistic package structures
            pkg1 = vendor / "splurge_safe_io"
            pkg1.mkdir()
            (pkg1 / "__init__.py").write_text('''"""Module."""\n__version__ = "2025.4.3"\n''')

            pkg2 = vendor / "splurge_exceptions"
            pkg2.mkdir()
            (pkg2 / "__init__.py").write_text('''"""Module."""\n__version__ = "2025.3.1"\n''')

            versions = scan_vendor_packages(target)
            output = format_version_output(versions)

            assert "splurge_safe_io 2025.4.3" in output
            assert "splurge_exceptions 2025.3.1" in output
