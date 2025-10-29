## Changelog

### [2025.1.0] - 2024-10-29

### Updated
- Bumped version to `2025.1.0` in `__init__.py` and `pyproject.toml`.
- Updated vendored `splurge_exceptions` to version `2025.3.0`.
- Updated vendored `splurge_safe_io` to version `2025.4.0`.

### [2025.0.2] - 2024-10-29

### Updated
- Updated `splurge_safe_io` to version `2025.4.0` in the vendored package.
- Bumped version to `2025.0.2` in `__init__.py` and `pyproject.toml`.

### Added
- Test cases for hypothesis strategies covering various sync scenarios.
- Test cases for edge cases in vendor synchronization logic.

## [2025.0.1] - 2024-10-28

### Changed
- Updated `splurge_exceptions` to version `2025.2.2` in the vendored package.

### Fixed
- Corrected case of SplurgeSafeIoOSError in exception handling within the vendored `splurge_safe_io` package.
- Fixed relative import paths in vendored packages to ensure proper module resolution.

## [2025.0.0] - 2024-10-28
- **Initial release** of the splurge-vendor-sync package.