# Scan Flag Implementation - November 1, 2025

## Overview
Implemented the `--scan [VERSION-TAG]` CLI flag for scanning vendored packages and extracting version information using Python's AST module.

## Features Implemented

### 1. Version Scanner Module (`splurge_vendor_sync/version_scanner.py`)
A new module that provides utilities for scanning vendored package directories and extracting version information using Python's AST module.

**Key Functions:**
- `extract_version_from_file(file_path, version_tag)`: Extracts version value from a Python file using AST parsing
- `scan_vendor_packages(target_path, vendor_dir, version_tag)`: Scans all packages in a vendor directory and extracts version information
- `format_version_output(versions)`: Formats version information for console output

**Features:**
- Uses Python AST API to safely parse and extract version assignments
- Searches for version tags in `__init__.py` first, falls back to `__main__.py`
- Skips hidden directories (starting with `_`)
- Handles both single and double quoted strings
- Returns `?` for packages where version is not found
- Respects custom vendor directory names

### 2. CLI Flag Update (`splurge_vendor_sync/cli.py`)
Updated the argument parser to accept the `--scan` flag:
- `--scan [VERSION-TAG]`: Optional flag to scan vendor directory
- `VERSION-TAG` defaults to `__version__` when `--scan` is used without arguments
- Source and package parameters are no longer strictly required (but still required for sync mode)

### 3. Main Function Update (`splurge_vendor_sync/main.py`)
- Added `scan` parameter to the main function
- Implemented `_handle_scan()` helper function to handle scan operations
- When scan mode is enabled, other sync parameters are ignored
- Returns sorted list of packages with versions

## Usage Examples

### Basic scan with default `__version__` tag:
```bash
splurge-vendor-sync --target /path/to/project --scan
```

Output format:
```
package_name version
package_name2 2.0.0
package_name3 ?
```

### Scan with custom version tag:
```bash
splurge-vendor-sync --target /path/to/project --scan MY_VERSION
```

### Scan with custom vendor directory:
```bash
splurge-vendor-sync --target /path/to/project --vendor custom_vendor --scan
```

## Testing

### Test Files Created
1. **`tests/unit/test_version_scanner_basic.py`**: Comprehensive unit tests for the version scanner module
   - 28 test cases covering all functionality
   - Tests for AST parsing with different quote styles
   - Tests for fallback from `__init__.py` to `__main__.py`
   - Tests for error handling and edge cases

2. **`tests/unit/test_cli.py`**: Added CLI tests for the scan flag
   - 8 test cases for CLI scan functionality
   - Tests for default and custom version tags
   - Tests for custom vendor directories
   - Tests for error conditions

### Test Results
- All 121 tests pass (14 integration + 107 unit)
- 28 version scanner tests
- 22 CLI tests (14 existing + 8 new)
- 100% success rate

## Implementation Details

### AST-Based Version Extraction
The implementation uses Python's `ast` module to safely parse Python source files and extract version assignments:
- Walks through AST nodes looking for assignments
- Handles both `ast.Constant` (Python 3.8+) and `ast.Str` (older versions) nodes
- Only returns string values assigned to the target version tag
- Gracefully handles syntax errors and file read errors

### Vendor Package Scanning
- Iterates through directories in the vendor folder
- For each package directory:
  1. Attempts to extract version from `__init__.py`
  2. If not found, attempts `__main__.py`
  3. Returns package name and version (or `None`)
- Returns results sorted by package name

## Key Design Decisions

1. **Optional Parameters**: Made `--source` and `--package` optional to avoid requiring dummy values for scan mode
2. **AST-Based Parsing**: Used AST instead of regex for robustness and safety
3. **Fallback Logic**: Checks `__init__.py` first, then `__main__.py` for flexibility
4. **Hidden Directory Skipping**: Automatically skips directories starting with `_` (like `__pycache__`)
5. **Missing Version Handling**: Uses `?` to indicate missing versions for clear output

## Files Modified
- `splurge_vendor_sync/cli.py`: Added --scan flag to argument parser
- `splurge_vendor_sync/main.py`: Added scan mode handling and _handle_scan function
- `tests/unit/test_cli.py`: Added 8 new CLI tests for scan functionality

## Files Created
- `splurge_vendor_sync/version_scanner.py`: New module for version scanning functionality
- `tests/unit/test_version_scanner_basic.py`: Comprehensive unit tests for version scanner

## Backward Compatibility
All existing functionality is preserved. The --scan flag is entirely optional and doesn't affect sync mode operation.
