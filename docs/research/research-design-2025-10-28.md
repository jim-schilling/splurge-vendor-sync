# Research Document: One-Way Vendor Synchronization Tool Design
**Date**: October 28, 2025

## Executive Summary

This document outlines the initial design for `splurge-vendor-sync`, a CLI tool that simplifies one-way synchronization of Python libraries and applications using a vendor-approach. The tool automates the process of copying source package code into a target project's vendor directory with selective file filtering and exclusions.

## Problem Statement

When managing Python projects that depend on internal packages, developers often need to "vendor" those dependencies—copying them directly into the project rather than relying on external package management. Currently, this process is manual and error-prone, requiring developers to:

1. Manually identify which files to copy
2. Handle file extensions selectively
3. Remove outdated vendor copies before re-syncing
4. Maintain consistent directory structures across projects

This tool eliminates these manual steps by automating the entire synchronization workflow.

## Solution Overview

### High-Level Concept

The tool implements a two-step process:
1. **Clean Step**: Recursively remove all existing files/directories from the target vendor location
2. **Sync Step**: Recursively copy source package files (filtered by extension) to the target vendor location

This ensures a clean, one-way synchronization without merging complexity or stale file residue.

## CLI Specification

### Command Signature

```bash
splurge-vendor-sync \
  --source <SOURCE-PATH> \
  --target <TARGET-PATH> \
  --package <SOURCE-PACKAGE-SUB-PATH> \
  [--vendor <VENDOR-SUB-PATH>] \
  [--ext <FILE-EXTENSIONS>]
```

### CLI Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--source` | str | Yes | N/A | Root path containing the source package |
| `--target` | str | Yes | N/A | Root path of target project where vendor directory resides |
| `--package` | str | Yes | N/A | Package subdirectory name within source (e.g., `splurge_exceptions`) |
| `--vendor` | str | No | `_vendor` | Subdirectory name within target for vendored packages |
| `--ext` | str | No | `py;json;yml;yaml;ini` | Semicolon-separated file extensions to include (without dots) |
| `--dry-run` | bool | No | False | If set, simulates the sync without making changes |

### Example Usage

```bash
splurge-vendor-sync \
  --source /d/repos/splurge-exceptions \
  --package splurge_exceptions \
  --target /d/repos/splurge-safe-io/splurge_safe_io
```

This command will:
- Source: `/d/repos/splurge-exceptions/splurge_exceptions`
- Target: `/d/repos/splurge-safe-io/splurge_safe_io/_vendor/splurge_exceptions`
- Extensions: `py;json;yml;yaml;ini` (default)

## Architecture

### Module Structure

```
splurge_vendor_sync/
├── cli.py              # CLI interface and argument parsing
├── main.py             # Main entry point wrapping sync.py API
├── exceptions.py       # Custom exception definitions
├── prep.py             # Path normalization and preparation utilities
└── sync.py             # Core synchronization API
```

### Component Responsibilities

#### `sync.py` - Core API
- **Function**: `sync_vendor(source_path, target_path, package, vendor, extensions)`
- Implements core synchronization logic
- Handles all file I/O operations
- Returns status information (files copied, files removed, errors)
- Raises domain-specific exceptions on errors

#### `main.py` - Entry Point Wrapper
- Bridges CLI arguments to prep and sync API
- Handles error reporting and logging
- Returns appropriate exit codes
- Provides user-friendly output formatting

### `prep.py` - Preparation Utilities
- Performs input validation and path normalization
- Prepares file lists for synchronization
- Handles dry-run logic

#### `cli.py` - CLI Interface
- Parses command-line arguments
- Validates argument combinations
- Delegates to main.py for processing
- Handles CLI-specific error formatting

## Synchronization Algorithm

### Step 1: Clean Phase
```
1. Construct target path: [TARGET-PATH]/[VENDOR]/[PACKAGE]
2. If path exists:
   a. Recursively enumerate all files and directories
   b. Remove all files and subdirectories
   c. Log removed items count
3. If path doesn't exist:
   a. Log "clean phase skipped - target path doesn't exist"
```

### Step 2: Sync Phase
```
1. Construct source path: [SOURCE-PATH]/[PACKAGE]
2. Parse extensions from [FILE-EXTENSIONS] (semicolon-separated)
3. Create target base directory if needed
4. Recursively traverse source directory:
   a. For each file:
      - Skip if in __pycache__ directory
      - Skip if extension not in [FILE-EXTENSIONS]
      - Copy to mirrored path under target
      - Preserve relative directory structure
   b. For each directory:
      - Skip if named __pycache__
      - Create corresponding target directory if needed
      - Recurse into directory
5. Log summary (files copied, directories created)
```

### Exclusions

The following are always excluded from synchronization:

- **`__pycache__` directories**: Python's compiled bytecode cache (platform/version-specific)
- **Extension filtering**: Only files matching specified extensions are copied
- **File extension matching**: Case-sensitive matching on file extension (e.g., `.py` vs `.PY`); extensions may be provided without leading dots.

## Data Flow

```
CLI Arguments
    ↓
cli.py (parse & validate)
    ↓
main.py (invoke prep and sync)
    ↓
prep.py (normalize paths, prepare)
    ↓
sync.py (execute sync)
    ├─ Step 1: Clean target vendor path
    └─ Step 2: Copy filtered files
    ↓
Status/Results
    ↓
main.py (format output)
    ↓
CLI (display to user)
```

## Vendor Dependencies & Utilities

The tool leverages two embedded vendor packages for robust file I/O and path validation:

### `_vendor/splurge_exceptions`
Provides a consistent exception hierarchy with domain-based error mapping:
- **`SplurgeVendorSyncError`**: Base exception for all tool errors (domain: `splurge.vendor_sync`)
- **`SplurgeVendorSyncTypeError`**: Type validation failures (domain: `splurge.vendor_sync.type`)
- **`SplurgeVendorSyncValueError`**: Value validation failures (domain: `splurge.vendor_sync.value`)
- **`SplurgeVendorSyncOSError`**: OS and I/O failures (domain: `splurge.vendor_sync.os`)
- **`SplurgeVendorSyncRuntimeError`**: Runtime execution failures (domain: `splurge.vendor_sync.runtime`)
- **`SplurgeVendorSyncUnicodeError`**: Encoding/decoding errors (domain: `splurge.vendor_sync.unicode`)

### `_vendor/splurge_safe_io`
Provides deterministic, safe file I/O operations:

#### **PathValidator.get_validated_path()**
- Validates and resolves file paths securely
- Prevents path traversal attacks
- Returns resolved `pathlib.Path` objects
- Raises `SplurgeSafeIoPathValidationError` for invalid paths

#### **SafeTextFileReader**
- Reads text files with deterministic newline normalization (all newlines → `\n`)
- Methods:
  - `read()`: Full file read as normalized string
  - `readlines()`: Full file read as list of normalized lines
  - `readlines_as_stream()`: Iterator for memory-efficient chunked reads
  - `preview(max_lines)`: Preview first N lines
  - `line_count()`: Count total lines in file
- Raises `SplurgeSafeIoFileNotFoundError`, `SplurgeSafeIoPermissionError`, `SplurgeSafeIoUnicodeError`, etc.

#### **SafeTextFileWriter**
- Writes text files with deterministic newline normalization
- Methods:
  - `write(text)`: Write normalized text
  - `writelines(lines)`: Write multiple normalized lines
  - `flush()`: Flush buffered writes
  - `close()`: Close file handle
- Supports modes: `CREATE_OR_TRUNCATE`, `CREATE_OR_APPEND`, `CREATE_NEW`
- Option: `create_parents=True` to auto-create parent directories
- Raises `SplurgeSafeIoFileExistsError`, `SplurgeSafeIoPermissionError`, `SplurgeSafeIoUnicodeError`, etc.

## Error Handling Strategy

### Exception Mapping

All errors are mapped to the appropriate `SplurgeVendorSync*` exception type:

| Operation | Exception Type | Details |
|-----------|----------------|---------|
| Path validation failure | `SplurgeVendorSyncValueError` | Via `PathValidator.get_validated_path()` |
| Type validation failure | `SplurgeVendorSyncTypeError` | For parameter type validation |
| File read failure | `SplurgeVendorSyncOSError` | Via `SafeTextFileReader` |
| File write failure | `SplurgeVendorSyncOSError` | Via `SafeTextFileWriter` |
| Permission denied | `SplurgeVendorSyncOSError` | From safe I/O utilities |
| Encoding/decoding errors | `SplurgeVendorSyncUnicodeError` | From safe I/O utilities |
| Runtime execution error | `SplurgeVendorSyncRuntimeError` | For unclassified runtime errors |

### Error Scenarios

| Scenario | Handling | Exception Type |
|----------|----------|-----------------|
| Source path doesn't exist | Caught by PathValidator, mapped to domain error | `SplurgeVendorSyncValueError` → exit code 2 |
| Target path doesn't exist | Caught by PathValidator, mapped to domain error | `SplurgeVendorSyncValueError` → exit code 2 |
| Invalid package name | PathValidator validation failure | `SplurgeVendorSyncValueError` → exit code 2 |
| Permission denied (read) | SafeTextFileReader maps to SplurgeSafeIo* | `SplurgeVendorSyncOSError` → exit code 1 |
| Permission denied (write) | SafeTextFileWriter maps to SplurgeSafeIo* | `SplurgeVendorSyncOSError` → exit code 1 |
| Disk space exhausted | OSError caught and mapped | `SplurgeVendorSyncOSError` → exit code 1 |
| Unicode encoding error | SafeTextFile* utilities handle encoding | `SplurgeVendorSyncUnicodeError` → exit code 1 |

## Implementation Considerations

### Path Handling

- Use `PathValidator.get_validated_path()` for all path validation and normalization
- This ensures consistent, secure handling across all path operations
- Validates against path traversal attacks, dangerous characters, and excessive lengths
- Returns resolved `pathlib.Path` objects ready for file operations
- Supports both relative and absolute paths with configurable base directory restrictions

### File I/O Strategy

- **File Reads**: Use `SafeTextFileReader` for all read operations
  - Provides deterministic newline normalization (all variants → `\n`)
  - Handles encoding errors with domain-specific exceptions
  - Supports both full reads and memory-efficient streaming for large files
  - Automatically validates file existence and readability via `PathValidator`
  
- **File Writes**: Use `SafeTextFileWriter` for all write operations
  - Deterministic newline normalization for consistent output
  - Supports multiple write modes (truncate, append, create-new)
  - Option to auto-create parent directories with `create_parents=True`
  - Handles encoding errors with domain-specific exceptions
  - Thread-safe operations with internal locking

### File Extension Parsing

- Parse extensions as semicolon-separated string
- Strip whitespace from each extension
- Case-sensitive matching (e.g., `.py` vs `.PY`)
- Store as lowercase for case-insensitive comparison
- Validate at least one extension is provided
- Default extensions: `py;json;yml;yaml;ini`

### Performance Considerations

- Recursive file operations may be slow on large packages
- Consider progress indicators for large syncs
- Log summary statistics (files/directories affected)
- Future: batch operations, parallel copying (if needed)

### Safety Mechanisms

- **Dry-run mode** (future): Preview changes without executing
- **Backup creation** (future): Optional backup before clean phase
- **Confirmation prompts** (future): Require explicit confirmation for destructive operations
- Validate paths are different (don't allow self-sync)
- Prevent accidental overwrites of system directories

## Success Criteria

A successful synchronization should:

1. ✅ Remove all pre-existing files in target vendor path
2. ✅ Copy all matching extension files from source to target
3. ✅ Preserve directory structure
4. ✅ Exclude `__pycache__` directories entirely
5. ✅ Provide clear summary of operations performed
6. ✅ Handle edge cases gracefully with informative errors
7. ✅ Complete reliably across different Python versions and platforms

## Example Walkthrough

### Scenario
```
Source Structure:
/d/repos/splurge-exceptions/splurge_exceptions/
├── __init__.py
├── __pycache__/          (will be excluded)
│   └── __init__.cpython-311.pyc
├── core/
│   ├── __init__.py
│   ├── base.py
│   └── exceptions.py
├── formatting/
│   ├── __init__.py
│   └── message.py
└── config.yaml

Target Initial State:
/d/repos/splurge-safe-io/splurge_safe_io/_vendor/splurge_exceptions/
├── old_file.py
└── old_config.json
```

### Execution
```bash
splurge-vendor-sync \
  --source-path /d/repos/splurge-exceptions \
  --package splurge_exceptions \
  --target /d/repos/splurge-safe-io/splurge_safe_io
```

### Result

**Step 1 - Clean:**
- Remove `/d/repos/splurge-safe-io/splurge_safe_io/_vendor/splurge_exceptions/old_file.py`
- Remove `/d/repos/splurge-safe-io/splurge_safe_io/_vendor/splurge_exceptions/old_config.json`

**Step 2 - Sync:**
- Create directory structure:
  - `_vendor/splurge_exceptions/`
  - `_vendor/splurge_exceptions/core/`
  - `_vendor/splurge_exceptions/formatting/`

- Copy files (extensions: py, json, yml, yaml, ini):
  - `__init__.py` → `_vendor/splurge_exceptions/__init__.py` ✓
  - `core/__init__.py` → `_vendor/splurge_exceptions/core/__init__.py` ✓
  - `core/base.py` → `_vendor/splurge_exceptions/core/base.py` ✓
  - `core/exceptions.py` → `_vendor/splurge_exceptions/core/exceptions.py` ✓
  - `formatting/__init__.py` → `_vendor/splurge_exceptions/formatting/__init__.py` ✓
  - `formatting/message.py` → `_vendor/splurge_exceptions/formatting/message.py` ✓
  - `config.yaml` → `_vendor/splurge_exceptions/config.yaml` ✓
  - `__pycache__/...` (skipped)

**Summary:**
```
✓ Removed 2 items
✓ Created 3 directories
✓ Copied 7 files
✓ Sync completed successfully
```

## Future Enhancements

1. **Dry-run mode** (`--dry-run`): Preview operations without executing
2. **Backup support** (`--backup`): Create backup of target before cleaning
3. **Confirmation prompts** (`--confirm`): Require explicit confirmation
4. **Verbose logging** (`--verbose`): Detailed operation logs
5. **Exclude patterns** (`--exclude`): Additional glob patterns for exclusion
6. **Include hidden files** (`--hidden`): Option to include dotfiles
7. **Preserve attributes** (`--preserve`): Copy file permissions/timestamps
8. **Watch mode** (`--watch`): Auto-sync on source changes
9. **Config file support** (`--config`): Load settings from config file
10. **Checksum verification**: Verify copied files integrity

## Implementation API Reference

### Module Imports

All implementations should import from the embedded vendor packages:

```python
from splurge_vendor_sync.exceptions import (
    SplurgeVendorSyncError,
    SplurgeVendorSyncTypeError,
    SplurgeVendorSyncValueError,
    SplurgeVendorSyncOSError,
    SplurgeVendorSyncRuntimeError,
    SplurgeVendorSyncUnicodeError,
)

from splurge_vendor_sync._vendor.splurge_safe_io.path_validator import PathValidator
from splurge_vendor_sync._vendor.splurge_safe_io.safe_text_file_reader import SafeTextFileReader
from splurge_vendor_sync._vendor.splurge_safe_io.safe_text_file_writer import (
    SafeTextFileWriter,
    TextFileWriteMode,
)
```

### Key API Usage Patterns

#### Path Validation
```python
# Validate a source path exists and is readable
source_path = PathValidator.get_validated_path(
    user_source_path,
    must_exist=True,
    must_be_readable=True
)

# Validate a target directory path (may not exist yet)
target_path = PathValidator.get_validated_path(
    user_target_path,
    must_exist=False,
    must_be_writable=False
)
```

#### Directory Traversal & Deletion
```python
# Recursively traverse and delete files/directories
# Use pathlib operations on validated paths
# Handle exceptions from os/pathlib as SplurgeVendorSyncOSError
import shutil
try:
    if vendor_target_path.exists():
        shutil.rmtree(vendor_target_path)
except (OSError, PermissionError) as exc:
    raise SplurgeVendorSyncOSError(
        error_code="deletion-failed",
        message=f"Failed to remove target vendor directory: {vendor_target_path}",
    ) from exc
```

#### File Copying with Filter
```python
# Copy filtered files from source to target
# For each file matching the extension filter:
try:
    reader = SafeTextFileReader(source_file)
    content = reader.read()
    
    writer = SafeTextFileWriter(
        target_file,
        file_write_mode=TextFileWriteMode.CREATE_OR_TRUNCATE,
        create_parents=True,
    )
    writer.write(content)
    writer.close()
except Exception as exc:
    # SafeTextFile* raise domain-specific exceptions
    raise SplurgeVendorSyncOSError(
        error_code="copy-failed",
        message=f"Failed to copy file {source_file} to {target_file}",
    ) from exc
```

## Testing Strategy

### Unit Tests
- Path parsing and validation using PathValidator
- Extension filtering logic
- Directory traversal with various structures
- Exception mapping to domain types
- SafeTextFileReader/Writer integration

### Integration Tests
- End-to-end sync operations
- Various directory structures
- Large package scenarios
- Permission and error scenarios

### Manual Testing
- Cross-platform path handling (Windows/Unix)
- Various file extension combinations
- Edge cases (empty packages, single files, deep nesting)
- Performance on large packages

## Deployment & Publishing

1. Package as CLI tool with entry point via `cli.py`
2. Distribute via pip with console script
3. Version management and changelog tracking
4. Documentation and usage examples

---

## References & Related Work

- Python pathlib for cross-platform path handling
- Vendor approach in modern Python projects
- Similar tools: vendoring, vendored dependencies patterns

---

**Author**: Design Team  
**Status**: Initial Research & Specification  
**Last Updated**: October 28, 2025
