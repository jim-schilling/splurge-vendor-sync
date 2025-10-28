"""Integration tests for splurge_vendor_sync."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from splurge_vendor_sync.main import main
from splurge_vendor_sync.sync import sync_vendor


@pytest.fixture
def temp_workspace() -> Generator[tuple[Path, Path], None, None]:
    """Create temporary workspace for integration tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        source = base / "source"
        target = base / "target"

        source.mkdir(exist_ok=True)
        target.mkdir(exist_ok=True)

        yield source, target


class TestE2EBasicSync:
    """End-to-end tests for basic sync operations."""

    def test_e2e_single_package_sync(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test syncing a single package."""
        source, target = temp_workspace

        # Create a package with multiple file types
        pkg = source / "mylib"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("__version__ = '1.0.0'")
        (pkg / "core.py").write_text("def hello(): pass")
        (pkg / "utils.py").write_text("def util(): pass")
        (pkg / "config.json").write_text('{"setting": "value"}')
        (pkg / "readme.md").write_text("# MyLib")
        (pkg / "ignore.txt").write_text("ignore me")

        result = sync_vendor(source, target, "mylib")

        assert result["status"] == "success"
        assert result["files_copied"] >= 3
        assert (target / "_vendor" / "mylib" / "__init__.py").exists()
        assert (target / "_vendor" / "mylib" / "core.py").exists()
        assert not (target / "_vendor" / "mylib" / "readme.md").exists()
        assert not (target / "_vendor" / "mylib" / "ignore.txt").exists()

    def test_e2e_multiple_package_sync(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test syncing multiple packages from same source."""
        source, target = temp_workspace

        # Create multiple packages
        for pkg_name in ["lib1", "lib2", "lib3"]:
            pkg = source / pkg_name
            pkg.mkdir()
            (pkg / "__init__.py").write_text("")
            (pkg / "module.py").write_text("pass")

        # Sync each package
        results = []
        for pkg_name in ["lib1", "lib2", "lib3"]:
            result = sync_vendor(source, target, pkg_name)
            results.append(result)
            assert result["status"] == "success"

        # Verify all packages synced
        for pkg_name in ["lib1", "lib2", "lib3"]:
            assert (target / "_vendor" / pkg_name / "__init__.py").exists()

    def test_e2e_nested_directory_sync(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test syncing packages with nested directories."""
        source, target = temp_workspace

        # Create nested structure
        pkg = source / "complex_lib"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "core").mkdir()
        (pkg / "core" / "__init__.py").write_text("")
        (pkg / "core" / "base.py").write_text("class Base: pass")
        (pkg / "utils").mkdir()
        (pkg / "utils" / "__init__.py").write_text("")
        (pkg / "utils" / "helpers.py").write_text("def help(): pass")

        result = sync_vendor(source, target, "complex_lib")

        assert result["status"] == "success"
        assert result["directories_created"] >= 2
        assert (target / "_vendor" / "complex_lib" / "core" / "base.py").exists()
        assert (target / "_vendor" / "complex_lib" / "utils" / "helpers.py").exists()

    def test_e2e_extension_filtering(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test extension filtering in sync."""
        source, target = temp_workspace

        pkg = source / "mixedlib"
        pkg.mkdir()
        (pkg / "module.py").write_text("")
        (pkg / "config.json").write_text("")
        (pkg / "settings.yaml").write_text("")
        (pkg / "readme.txt").write_text("")
        (pkg / "data.xml").write_text("")

        result = sync_vendor(source, target, "mixedlib", extensions="py;json;yaml;yml")

        assert result["status"] == "success"
        assert (target / "_vendor" / "mixedlib" / "module.py").exists()
        assert (target / "_vendor" / "mixedlib" / "config.json").exists()
        assert (target / "_vendor" / "mixedlib" / "settings.yaml").exists()
        assert not (target / "_vendor" / "mixedlib" / "readme.txt").exists()
        assert not (target / "_vendor" / "mixedlib" / "data.xml").exists()

    def test_e2e_pycache_exclusion(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test that __pycache__ directories are excluded."""
        source, target = temp_workspace

        pkg = source / "cachedlib"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "module.py").write_text("")

        # Create __pycache__ directories
        pycache = pkg / "__pycache__"
        pycache.mkdir()
        (pycache / "module.cpython-310.pyc").write_text("")

        result = sync_vendor(source, target, "cachedlib")

        assert result["status"] == "success"
        assert not (target / "_vendor" / "cachedlib" / "__pycache__").exists()

    def test_e2e_custom_vendor_directory(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test using custom vendor directory."""
        source, target = temp_workspace

        pkg = source / "mylib"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "module.py").write_text("")

        result = sync_vendor(source, target, "mylib", vendor="third_party")

        assert result["status"] == "success"
        assert (target / "third_party" / "mylib" / "__init__.py").exists()
        assert not (target / "_vendor" / "mylib").exists()

    def test_e2e_resync_updates_files(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test that resyncing updates existing files."""
        source, target = temp_workspace

        pkg = source / "evolving"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("VERSION = '1'")
        (pkg / "module.py").write_text("def func1(): pass")

        # First sync
        result1 = sync_vendor(source, target, "evolving")
        assert result1["status"] == "success"

        # Modify source
        (pkg / "__init__.py").write_text("VERSION = '2'")
        (pkg / "module.py").write_text("def func1(): pass\ndef func2(): pass")
        (pkg / "newmodule.py").write_text("def newfunc(): pass")

        # Resync
        result2 = sync_vendor(source, target, "evolving")
        assert result2["status"] == "success"

        # Verify updates
        content = (target / "_vendor" / "evolving" / "__init__.py").read_text()
        assert "VERSION = '2'" in content

    def test_e2e_resync_removes_old_files(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test that resyncing removes files no longer in source."""
        source, target = temp_workspace

        pkg = source / "changing"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "oldmodule.py").write_text("")

        # First sync
        result1 = sync_vendor(source, target, "changing")
        assert result1["status"] == "success"
        assert (target / "_vendor" / "changing" / "oldmodule.py").exists()

        # Remove file from source
        (pkg / "oldmodule.py").unlink()

        # Resync
        result2 = sync_vendor(source, target, "changing")
        assert result2["status"] == "success"

        # Verify old file removed
        assert not (target / "_vendor" / "changing" / "oldmodule.py").exists()


class TestE2EErrorHandling:
    """End-to-end tests for error handling."""

    def test_e2e_missing_source_directory(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test handling of missing source directory."""
        from splurge_vendor_sync.exceptions import SplurgeVendorSyncError

        _, target = temp_workspace

        with pytest.raises(SplurgeVendorSyncError):
            sync_vendor("/nonexistent/source", target, "mylib")

    def test_e2e_missing_package(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test handling of missing package in source."""
        from splurge_vendor_sync.exceptions import SplurgeVendorSyncError

        source, target = temp_workspace

        with pytest.raises(SplurgeVendorSyncError):
            sync_vendor(source, target, "nonexistent")

    def test_e2e_invalid_target_path(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test handling of invalid target path."""
        from splurge_vendor_sync.exceptions import SplurgeVendorSyncError

        source, _ = temp_workspace

        pkg = source / "mylib"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")

        # Use invalid target path
        with pytest.raises(SplurgeVendorSyncError):
            sync_vendor(source, "/sys/root/invalid", "mylib")


class TestE2EMainWrapper:
    """End-to-end tests for main() wrapper."""

    def test_e2e_main_success(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() successful execution."""
        source, target = temp_workspace

        pkg = source / "wrapped"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "module.py").write_text("")

        exit_code = main(source, target, "wrapped")

        assert exit_code == 0
        assert (target / "_vendor" / "wrapped" / "__init__.py").exists()

    def test_e2e_main_with_options(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() with all options."""
        source, target = temp_workspace

        pkg = source / "optioned"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "module.py").write_text("")
        (pkg / "config.json").write_text("")

        exit_code = main(
            source,
            target,
            "optioned",
            vendor="libs",
            extensions="py;json",
            verbose=True,
        )

        assert exit_code == 0
        assert (target / "libs" / "optioned" / "__init__.py").exists()

    def test_e2e_main_validation_error(self, temp_workspace: tuple[Path, Path]) -> None:
        """Test main() with validation error."""
        _, target = temp_workspace

        # Missing source path
        exit_code = main(None, target, "test")

        assert exit_code == 2  # Validation error
