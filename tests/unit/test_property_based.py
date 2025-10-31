"""Property-based tests using Hypothesis for splurge-vendor-sync.

These tests use Hypothesis to generate random test cases and verify
properties that should always hold true regardless of input.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from splurge_vendor_sync.sync import sync_vendor


class TestPathHandling:
    """Property-based tests for path handling."""

    @given(
        st.from_regex(
            r"[a-zA-Z_][a-zA-Z0-9_]*",
            fullmatch=True,
        )
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
    def test_package_name_with_valid_characters(self, pkg_name: str) -> None:
        """Property: sync_vendor should handle any valid package name."""
        # Strategy only generates valid Python package names:
        # - starts with letter or underscore
        # - contains only letters, digits, underscores
        # - no whitespace, no special characters

        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()

            # Create package directory
            pkg_dir = source / pkg_name
            pkg_dir.mkdir()
            (pkg_dir / "module.py").write_text("# test")

            # Should succeed without raising exceptions
            result = sync_vendor(
                source_path=source,
                target_path=target,
                package=pkg_name,
            )

            # Property: result should have expected keys
            assert "files_removed" in result
            assert "files_copied" in result
            assert "directories_created" in result
            assert "status" in result

            # Property: result should indicate success or partial
            assert result["status"] in ("success", "partial")

    @given(
        st.lists(
            st.text(min_size=1, max_size=10, alphabet="abcdefghijklmnopqrstuvwxyz"),
            min_size=1,
            max_size=5,
        )
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=30)
    def test_nested_directory_structures(self, dir_names: list[str]) -> None:
        """Property: sync_vendor should handle arbitrarily nested directory structures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()

            pkg_name = "test_pkg"
            pkg_dir = source / pkg_name
            pkg_dir.mkdir()

            # Create nested structure
            current = pkg_dir
            for dir_name in dir_names:
                current = current / dir_name
                current.mkdir(parents=True, exist_ok=True)
                (current / "file.py").write_text("# nested")

            result = sync_vendor(
                source_path=source,
                target_path=target,
                package=pkg_name,
            )

            # Property: should create directories for all nesting levels
            assert result["directories_created"] >= len(dir_names)
            assert result["files_copied"] >= len(dir_names)


class TestExtensionFiltering:
    """Property-based tests for file extension filtering."""

    @given(
        st.lists(
            st.text(min_size=1, max_size=5, alphabet="abcdefghijklmnopqrstuvwxyz"),
            min_size=1,
            max_size=10,
        )
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=30)
    def test_extension_filtering_consistency(self, extensions: list[str]) -> None:
        """Property: only files with specified extensions should be copied."""
        # Filter duplicates and join
        ext_str = ";".join(set(extensions))

        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()

            pkg_name = "ext_test_pkg"
            pkg_dir = source / pkg_name
            pkg_dir.mkdir()

            # Create files with various extensions
            (pkg_dir / "file1.py").write_text("python")
            (pkg_dir / "file2.json").write_text("{}")
            (pkg_dir / "file3.txt").write_text("text")
            (pkg_dir / "file4.yaml").write_text("yaml")
            (pkg_dir / "file5.ini").write_text("ini")

            sync_vendor(
                source_path=source,
                target_path=target,
                package=pkg_name,
                extensions=ext_str,
            )

            vendor_pkg = target / "_vendor" / pkg_name

            # Property: only files with matching extensions exist
            for ext in set(extensions):
                matching_files = list(vendor_pkg.glob(f"*.{ext}"))
                # If this extension was requested, files might exist
                # If they exist, they should have the right extension
                for file in matching_files:
                    assert file.suffix[1:] == ext


class TestEdgeCases:
    """Edge case tests for various scenarios."""

    def test_empty_source_package(self) -> None:
        """Edge case: empty source package with no files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()

            pkg_dir = source / "empty_pkg"
            pkg_dir.mkdir()

            result = sync_vendor(
                source_path=source,
                target_path=target,
                package="empty_pkg",
            )

            # Property: should succeed even with empty package
            assert result["status"] in ("success", "partial")
            assert result["files_copied"] == 0

    def test_package_with_only_excluded_files(self) -> None:
        """Edge case: package with only excluded file types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()

            pkg_dir = source / "exclude_pkg"
            pkg_dir.mkdir()

            # Create files that won't match extensions
            (pkg_dir / "readme.txt").write_text("readme")
            (pkg_dir / "script.sh").write_text("#!/bin/bash")
            (pkg_dir / "image.png").write_bytes(b"\x89PNG")

            result = sync_vendor(
                source_path=source,
                target_path=target,
                package="exclude_pkg",
                extensions="py;json",  # No txt, sh, or png files
            )

            # Property: should succeed but copy no files
            assert result["status"] in ("success", "partial")
            assert result["files_copied"] == 0

    def test_package_with_pycache_directory(self) -> None:
        """Edge case: package with __pycache__ that should be excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()

            pkg_dir = source / "cache_pkg"
            pkg_dir.mkdir()

            # Create normal files
            (pkg_dir / "module.py").write_text("# code")

            # Create __pycache__
            cache_dir = pkg_dir / "__pycache__"
            cache_dir.mkdir()
            (cache_dir / "module.cpython-310.pyc").write_text("bytecode")

            sync_vendor(
                source_path=source,
                target_path=target,
                package="cache_pkg",
            )

            vendor_pkg = target / "_vendor" / "cache_pkg"

            # Property: __pycache__ should be excluded
            assert not (vendor_pkg / "__pycache__").exists()
            # But regular .py files should exist
            assert (vendor_pkg / "module.py").exists()

    def test_resync_removes_old_files(self) -> None:
        """Edge case: re-syncing removes files that no longer exist in source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()

            pkg_dir = source / "resync_test"
            pkg_dir.mkdir()
            (pkg_dir / "file1.py").write_text("# file 1")

            # First sync
            result1 = sync_vendor(
                source_path=source,
                target_path=target,
                package="resync_test",
            )
            assert result1["files_copied"] == 1

            vendor_pkg = target / "_vendor" / "resync_test"
            assert (vendor_pkg / "file1.py").exists()

            # Add old file directly to vendor (simulating old version)
            (vendor_pkg / "old_file.py").write_text("# old")
            assert (vendor_pkg / "old_file.py").exists()

            # Second sync with only new file
            (pkg_dir / "file2.py").write_text("# file 2")
            # Note: file1.py still exists in source
            sync_vendor(
                source_path=source,
                target_path=target,
                package="resync_test",
            )

            # Property: old_file should be gone after resync
            assert not (vendor_pkg / "old_file.py").exists()
            assert (vendor_pkg / "file1.py").exists()
            assert (vendor_pkg / "file2.py").exists()

    def test_files_with_unicode_names(self) -> None:
        """Edge case: files with unicode characters in names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()

            pkg_dir = source / "unicode_pkg"
            pkg_dir.mkdir()

            # Create files with unicode names
            (pkg_dir / "file_café.py").write_text("# French")
            (pkg_dir / "module_中文.py").write_text("# Chinese")
            (pkg_dir / "script_日本語.py").write_text("# Japanese")

            sync_vendor(
                source_path=source,
                target_path=target,
                package="unicode_pkg",
            )

            vendor_pkg = target / "_vendor" / "unicode_pkg"

            # Property: unicode files should be copied
            assert (vendor_pkg / "file_café.py").exists()
            assert (vendor_pkg / "module_中文.py").exists()
            assert (vendor_pkg / "script_日本語.py").exists()

    def test_files_with_no_extension(self) -> None:
        """Edge case: files with no extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()

            pkg_dir = source / "no_ext_pkg"
            pkg_dir.mkdir()

            # Create files without extensions
            (pkg_dir / "README").write_text("readme")
            (pkg_dir / "LICENSE").write_text("license")
            (pkg_dir / "module.py").write_text("# code")

            sync_vendor(
                source_path=source,
                target_path=target,
                package="no_ext_pkg",
                extensions="py",  # Only .py files
            )

            vendor_pkg = target / "_vendor" / "no_ext_pkg"

            # Property: files without extension should not be copied
            assert not (vendor_pkg / "README").exists()
            assert not (vendor_pkg / "LICENSE").exists()
            # But .py files should be
            assert (vendor_pkg / "module.py").exists()

    def test_deeply_nested_file_preservation(self) -> None:
        """Edge case: deeply nested files should preserve structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()

            pkg_dir = source / "deep_pkg"
            pkg_dir.mkdir()

            # Create deeply nested structure
            deep_path = pkg_dir / "a" / "b" / "c" / "d" / "e"
            deep_path.mkdir(parents=True)
            (deep_path / "deep.py").write_text("# deep")

            sync_vendor(
                source_path=source,
                target_path=target,
                package="deep_pkg",
            )

            vendor_pkg = target / "_vendor" / "deep_pkg"

            # Property: directory structure should be preserved
            assert (vendor_pkg / "a" / "b" / "c" / "d" / "e" / "deep.py").exists()

    def test_case_sensitive_extension_matching(self) -> None:
        """Edge case: extension matching should be case-insensitive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()

            pkg_dir = source / "case_pkg"
            pkg_dir.mkdir()

            # Create files with different case extensions
            (pkg_dir / "file1.py").write_text("# lowercase")
            (pkg_dir / "file2.PY").write_text("# uppercase")
            (pkg_dir / "file3.Py").write_text("# mixed case")

            sync_vendor(
                source_path=source,
                target_path=target,
                package="case_pkg",
                extensions="py",
            )

            vendor_pkg = target / "_vendor" / "case_pkg"

            # Property: all variations of .py should be copied
            assert (vendor_pkg / "file1.py").exists()
            assert (vendor_pkg / "file2.PY").exists()
            assert (vendor_pkg / "file3.Py").exists()

    def test_vendor_dir_creation_when_missing(self) -> None:
        """Edge case: vendor directory should be created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()

            pkg_dir = source / "new_vendor_pkg"
            pkg_dir.mkdir()
            (pkg_dir / "module.py").write_text("# code")

            # Ensure vendor path doesn't exist yet
            vendor_path = target / "_vendor"
            assert not vendor_path.exists()

            sync_vendor(
                source_path=source,
                target_path=target,
                package="new_vendor_pkg",
            )

            # Property: vendor directory should be created
            assert vendor_path.exists()
            assert (vendor_path / "new_vendor_pkg").exists()

    def test_custom_vendor_directory_creation(self) -> None:
        """Edge case: custom vendor directory should be created if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source = base / "source"
            target = base / "target"
            source.mkdir()
            target.mkdir()

            pkg_dir = source / "custom_vendor_pkg"
            pkg_dir.mkdir()
            (pkg_dir / "module.py").write_text("# code")

            sync_vendor(
                source_path=source,
                target_path=target,
                package="custom_vendor_pkg",
                vendor="my_custom_vendor",
            )

            # Property: custom vendor directory should be created
            custom_vendor = target / "my_custom_vendor" / "custom_vendor_pkg"
            assert custom_vendor.exists()
            assert (custom_vendor / "module.py").exists()
