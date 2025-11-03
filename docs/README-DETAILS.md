# Comprehensive Features & Error Handling Guide

**splurge-vendor-sync** | Complete Reference for Features, Usage, and Troubleshooting

---

## Table of Contents

1. [Overview](#overview)
2. [Core Features](#core-features)
3. [How It Works](#how-it-works)
4. [File Filtering](#file-filtering)
5. [Directory Structure](#directory-structure)
6. [Error Handling](#error-handling)
7. [Common Scenarios](#common-scenarios)
8. [Troubleshooting](#troubleshooting)
9. [Performance Considerations](#performance-considerations)
10. [Security Considerations](#security-considerations)
11. [Limitations](#limitations)

---

## Overview

**splurge-vendor-sync** is a command-line tool that automates the one-way synchronization of Python packages into a project's vendor directory. It was designed to solve the problem of manually maintaining vendored (embedded) dependencies by fully automating the sync process.

### Use Cases

- **Maintaining internal packages**: Keep copies of company-internal Python packages synchronized in multiple projects
- **Dependency management**: Avoid relying on external package repositories for critical internal libraries
- **Monorepo dependencies**: Share code between multiple sub-projects in a monorepo
- **Isolated environments**: Reduce external dependencies in air-gapped or restricted environments

---

## Core Features

### 1. One-Way Synchronization

The tool implements a **two-step synchronization process**:

#### Step 1: Clean
- Recursively removes all existing files and directories from the target vendor location
- Ensures no stale or outdated files remain
- Starts with a clean slate for every sync

#### Step 2: Sync
- Recursively copies all matching files from source to target
- Preserves the exact directory structure from source
- Filters files based on configured extensions
- Excludes build artifacts like `__pycache__`

### 2. Version Scanning

Scan vendored packages to extract version information:

- **Extract version from Python files** using AST parsing for safety
- **Search for custom version tags** (default: `__version__`)
- **Check `__init__.py` first**, then fallback to `__main__.py`
- **Display missing versions** with `?` marker for clear visibility
- **Supports custom vendor directories** via `--vendor` flag
- **Recursive nested vendor discovery**: Automatically discovers and scans nested vendor directories at any depth
- **Hierarchical output**: Shows parent-child relationships when vendors are nested

#### Nested Vendor Example

If your project structure contains vendors within vendors:

```
my_project/
  _vendor/
    library-a/
      __init__.py  (__version__ = "1.0.0")
      _vendor/
        library-b/
          __init__.py  (__version__ = "2.0.0")
          _vendor/
            library-f/
              __init__.py  (__version__ = "3.0.0")
            library-g/
              __init__.py  (__version__ = "4.0.0")
```

The scan output will show the hierarchy:

```
library-a 1.0.0
  library-b 2.0.0
    library-f 3.0.0
    library-g 4.0.0
```

This clearly shows:
- `library-b` is vendored **under** `library-a`
- `library-f` and `library-g` are vendored **under** `library-b`

### 3. Selective File Filtering

Include only the file types your project needs:

- **Default extensions**: `py`, `json`, `yml`, `yaml`, `ini`
- **Customizable**: Use `--ext` to specify a different set
- **Semicolon-separated**: Format is `ext1;ext2;ext3` (without dots)
- **Case-insensitive**: `.PY` and `.py` are treated identically

### 4. Automatic Cleanup

Before syncing new files, the tool automatically:
- Removes the entire old vendor package directory
- Ensures no accidental file conflicts
- Prevents version mismatches from lingering files

### 5. Build Artifact Exclusion

The tool automatically excludes:
- `__pycache__` directories (Python bytecode cache)
- Any files within `__pycache__` directories

### 6. Safe I/O Operations

Uses embedded vendor utilities for robust file operations:
- **Deterministic newline normalization**: All newline variants (LF, CRLF, CR) are normalized to LF
- **Secure path validation**: Prevents path traversal attacks
- **Proper error handling**: Clear, actionable error messages
- **Thread-safe operations**: Safe for concurrent use

### 7. Cross-Platform Compatibility

Works seamlessly on:
- **Windows**: Handles backslashes and drive letters correctly
- **Linux/Unix**: Handles forward slashes and Unix permissions
- **macOS**: Handles case-insensitive filesystem correctly

---

## How It Works

### High-Level Process

```
1. Parse CLI arguments
2. Validate all paths and parameters
3. Normalize paths for current OS
4. Remove old vendor package (if exists)
5. Traverse source package recursively
6. Copy matching files to target, preserving structure
7. Report results to user
8. Exit with appropriate code
```

### Detailed Algorithm

#### Clean Phase

```
INPUT: target_path, vendor, package
vendor_target = target_path / vendor / package

IF vendor_target exists:
  DELETE vendor_target recursively
  LOG "Removed N files and M directories"
ELSE:
  LOG "Target vendor path doesn't exist, skipping clean phase"
```

#### Sync Phase

```
INPUT: source_path, target_path, vendor, package, extensions

source_package = source_path / package
vendor_target = target_path / vendor / package
parsed_extensions = PARSE_SEMICOLON_SEPARATED(extensions)

FOR EACH item IN source_package (recursive):
  IF item is directory:
    IF item.name == "__pycache__":
      SKIP
    ELSE:
      CREATE corresponding directory in target
  
  IF item is file:
    IF parent is "__pycache__":
      SKIP
    IF file.extension NOT IN parsed_extensions:
      SKIP
    ELSE:
      COPY file to target, preserving relative path

LOG summary: "Copied N files to M directories"
```

---

## File Filtering

### How Extension Matching Works

The tool matches files by extension:

```
File: splurge_exceptions/__init__.py
Extension: .py
Match: YES (if "py" in extensions)

File: config.yaml
Extension: .yaml
Match: YES (if "yaml" in extensions)

File: binary.pyc
Extension: .pyc
Match: NO (only "py" is included by default, not "pyc")

File: settings.INI
Extension: .INI
Match: YES (matching is case-insensitive)
```

### Default Extensions

The default extension set is carefully chosen to include most Python source and configuration files:

- `py`: Python source files (the main target)
- `json`: JSON configuration files
- `yml`: YAML configuration files (short form)
- `yaml`: YAML configuration files (long form)
- `ini`: INI configuration files

### When to Customize Extensions

**Keep defaults for**: Most Python packages with standard configurations  
**Use custom extensions for**:
- Packages that use non-standard file types
- Situations where you want minimal file sync
- Including data files like `.txt` or `.md`

### Extension Format

- Extensions are specified as a **semicolon-separated string**: `ext1;ext2;ext3`
- **No leading dots**: Use `py` not `.py`
- **No spaces**: Use `py;json;yaml` not `py; json; yaml`
- **Case-insensitive**: `py` matches `.py`, `.PY`, `.Py`, etc.
- **Examples**:
  - Default: `py;json;yml;yaml;ini`
  - Minimal: `py;ini`
  - Extended: `py;json;yml;yaml;ini;txt;md;rst`

---

## Directory Structure

### How Directory Structures Are Preserved

The tool maintains the exact directory hierarchy from source to target:

```
Source:
/repo/splurge_exceptions/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── base.py
│   └── exceptions.py
├── formatting/
│   ├── __init__.py
│   └── message.py
└── __pycache__/
    └── __init__.cpython-311.pyc

Target After Sync:
/my-project/my_project/_vendor/splurge_exceptions/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── base.py
│   └── exceptions.py
└── formatting/
    ├── __init__.py
    └── message.py
```

Note that `__pycache__` is not copied.

### Relative Path Structure

- The tool preserves **relative paths** within the package
- The `--package` parameter is the root; everything under it is preserved
- **Example**: If `core/sub/file.py` exists in source, it will be at `core/sub/file.py` in target

---

## Error Handling

### Exception Hierarchy

All errors are mapped to `SplurgeVendorSyncError` (or a subclass) with a domain-based classification:

```
SplurgeVendorSyncError (domain: splurge.vendor_sync)
├── SplurgeVendorSyncTypeError (domain: splurge.vendor_sync.type)
├── SplurgeVendorSyncValueError (domain: splurge.vendor_sync.value)
├── SplurgeVendorSyncOSError (domain: splurge.vendor_sync.os)
├── SplurgeVendorSyncRuntimeError (domain: splurge.vendor_sync.runtime)
└── SplurgeVendorSyncUnicodeError (domain: splurge.vendor_sync.unicode)
```

### Exception Details

| Exception Type | Error Code | When It Occurs | Exit Code |
|---|---|---|---|
| `SplurgeVendorSyncTypeError` | `splurge-vendor-sync.type.type-mismatch` | Parameter type is invalid | 2 |
| `SplurgeVendorSyncValueError` | `splurge-vendor-sync.value.invalid-value` | Parameter value is invalid | 2 |
| `SplurgeVendorSyncValueError` | `splurge-vendor-sync.value.path-not-found` | Source or target path doesn't exist | 2 |
| `SplurgeVendorSyncValueError` | `splurge-vendor-sync.value.invalid-package` | Package name is empty or invalid | 2 |
| `SplurgeVendorSyncValueError` | `splurge-vendor-sync.value.path-validation-failed` | Path failed security validation | 2 |
| `SplurgeVendorSyncOSError` | `splurge-vendor-sync.os.permission-denied` | No permission to read/write | 1 |
| `SplurgeVendorSyncOSError` | `splurge-vendor-sync.os.disk-full` | Disk space exhausted | 1 |
| `SplurgeVendorSyncOSError` | `splurge-vendor-sync.os.deletion-failed` | Failed to remove old vendor files | 1 |
| `SplurgeVendorSyncOSError` | `splurge-vendor-sync.os.copy-failed` | Failed to copy a file | 1 |
| `SplurgeVendorSyncError` | `splurge-vendor-sync.sync-failed` | Unexpected sync error | 1 |

### Exit Codes

- **Exit 0**: Synchronization completed successfully
- **Exit 1**: Runtime error (I/O, permissions, encoding, etc.)
- **Exit 2**: Validation error (invalid arguments, missing paths, type errors)

### Error Messages

Error messages follow a consistent format:

```
ERROR: {domain}: {error_code} - {description}
       {file_or_path}: {additional_context}
       Suggestion: {actionable_remediation}
```

### Error Recovery

Most errors are **fatal** (the tool cannot proceed), but some scenarios are **recoverable**:

| Scenario | Recovery |
|---|---|
| Source path doesn't exist | Fix the path and try again |
| Target parent doesn't exist | Create the parent and try again |
| Old vendor files can't be deleted | Manually delete them and retry |
| A single file copy fails | Check permissions and retry |
| Permission denied on source | Ensure read permission and retry |
| Permission denied on target | Ensure write permission and retry |
| Disk full | Free up space and retry |

---

## Common Scenarios

### Scenario 1: Initial Setup

**Goal**: Set up vendor package for the first time

```bash
splurge-vendor-sync \
  --source /path/to/splurge-exceptions \
  --package splurge_exceptions \
  --target /my-project/my_package
```

**Result**: Creates `_vendor/splurge_exceptions/` with all source files (filtered by extension)

### Scenario 2: Update Existing Vendor Package

**Goal**: Sync latest version of a vendor package

```bash
# Just re-run the same command
splurge-vendor-sync \
  --source /path/to/splurge-exceptions \
  --package splurge_exceptions \
  --target /my-project/my_package
```

**Result**: Removes old `_vendor/splurge_exceptions/` completely and copies new version

### Scenario 3: Sync Multiple Packages

**Goal**: Vendor multiple internal packages in one project

```bash
#!/bin/bash
splurge-vendor-sync --source /repo/splurge-exceptions --package splurge_exceptions --target /my-project/my_package
splurge-vendor-sync --source /repo/splurge-safe-io --package splurge_safe_io --target /my-project/my_package
splurge-vendor-sync --source /repo/splurge-formatting --package splurge_formatting --target /my-project/my_package
```

**Result**: All three packages synced to their respective `_vendor/` subdirectories

### Scenario 4: Different Vendor Directory Name

**Goal**: Use custom vendor directory name (not `_vendor`)

```bash
splurge-vendor-sync \
  --source /path/to/splurge-exceptions \
  --package splurge_exceptions \
  --target /my-project/my_package \
  --vendor "vendored"
```

**Result**: Files synced to `vendored/splurge_exceptions/` instead of `_vendor/splurge_exceptions/`

### Scenario 5: Minimal File Sync

**Goal**: Only sync Python files, skip configuration

```bash
splurge-vendor-sync \
  --source /path/to/splurge-exceptions \
  --package splurge_exceptions \
  --target /my-project/my_package \
  --ext "py"
```

**Result**: Only `.py` files are copied, configuration files skipped

### Scenario 6: Extended File Sync

**Goal**: Include additional file types (e.g., docs, data)

```bash
splurge-vendor-sync \
  --source /path/to/splurge-exceptions \
  --package splurge_exceptions \
  --target /my-project/my_package \
  --ext "py;json;yml;yaml;ini;txt;md;rst"
```

**Result**: All specified file types copied to target

### Scenario 7: Scan Vendored Package Versions

**Goal**: Extract version information from all vendored packages

```bash
# Default: scan for __version__
splurge-vendor-sync \
  --target /my-project/my_package \
  --scan
```

**Output**:
```
splurge_exceptions 2025.3.1
splurge_safe_io 2025.4.3
custom_package ?
```

**Result**: Displays version for each vendored package, or `?` if not found

### Scenario 8: Scan with Custom Version Tag

**Goal**: Extract version information using a custom version variable name

```bash
splurge-vendor-sync \
  --target /my-project/my_package \
  --scan MY_VERSION
```

**Result**: Scans for `MY_VERSION` instead of `__version__` in each package

---

## Troubleshooting

### Problem: "Source path not found"

```
ERROR: splurge.vendor_sync.value: path-not-found - File not found: /invalid/path
```

**Causes**:
- Typo in `--source` path
- Directory doesn't exist
- Permission denied (can't access parent directory)

**Solutions**:
1. Double-check the path: `ls /path/to/source`
2. Verify the directory exists: `test -d /path/to/source && echo "OK"`
3. Check permissions: `ls -ld /path/to/source`
4. Use absolute paths instead of relative paths

### Problem: "Target path not found"

```
ERROR: splurge.vendor_sync.value: path-not-found - File not found: /invalid/target
```

**Causes**:
- Typo in `--target` path
- Parent directory doesn't exist
- Permission denied on parent

**Solutions**:
1. Verify target path exists: `test -d /path/to/target && echo "OK"`
2. Create parent if needed: `mkdir -p /path/to/target`
3. Check permissions: `ls -ld /path/to/target`

### Problem: "Permission denied" (during sync)

```
ERROR: splurge-vendor-sync.os: permission-denied - Permission error reading file
```

**Causes**:
- Source directory not readable
- Target directory not writable
- File locked by another process

**Solutions**:
1. For source: `chmod +r /source/path` (make readable)
2. For target: `chmod +w /target/path` (make writable)
3. Close any files in use and retry
4. Run with appropriate user/role permissions

### Problem: "Files not being copied"

**Causes**:
- File extensions don't match `--ext` parameter
- Files are in `__pycache__` directory
- Extension matching is case-sensitive (unlikely)

**Solutions**:
1. Verify extension: Check the actual file extension: `file myfile`
2. Adjust `--ext`: Use `--ext "py;json;yaml;txt"` to include needed types
3. Check for `__pycache__`: Look for files in `__pycache__` subdirectories (these are always excluded)
4. Debug: Run with `--verbose` (when available) to see which files are being skipped

### Problem: "Disk full" error

```
ERROR: splurge.vendor_sync.os: disk-full - No space left on device
```

**Causes**:
- Target filesystem is full
- Source files are very large

**Solutions**:
1. Free up disk space: `du -sh /* | sort -rh` to identify large directories
2. Delete unnecessary files: `rm -rf /some/unused/directory`
3. Check available space: `df -h`
4. Use a different target filesystem with more space

### Problem: "Encoding error"

```
ERROR: splurge.vendor_sync.unicode: encoding-error - Decoding error
```

**Causes**:
- File has non-UTF-8 encoding
- File has mixed or corrupted encoding

**Solutions**:
1. Check file encoding: `file -i myfile`
2. Convert to UTF-8: `iconv -f ISO-8859-1 -t UTF-8 myfile > myfile_utf8`
3. Exclude the problematic file type from sync
4. Fix the encoding in the source and resync

### Problem: Sync completes but files missing

**Causes**:
- Files filtered out by extension (most common)
- Files in excluded directories (`__pycache__`)
- Source files don't have expected extensions

**Solutions**:
1. Verify expected extensions are in `--ext`
2. List files in source: `find /source -type f | head -20`
3. Check what was actually copied: `find /target/_vendor -type f | wc -l`
4. Re-run with `--ext "py;json;yaml;ini;txt"` if needed (temporarily add more extensions)

---

## Performance Considerations

### Factors Affecting Speed

| Factor | Impact | Mitigation |
|--------|--------|-----------|
| Package size | Larger packages take longer | N/A (inherent to tool) |
| File count | More files = more iterations | Filter extensions to reduce count |
| Disk I/O | Slower disk = slower sync | Use local/fast disk for target |
| Network | Network drives much slower | Copy to local disk first, then move |
| Extension filtering | More types = more checks | Use only needed extensions |
| Newline normalization | Adds processing time | N/A (inherent to tool for safety) |

### Typical Performance

- Small package (< 50 files): < 500ms
- Medium package (50-500 files): 1-5 seconds
- Large package (500+ files): 5-30 seconds
- Very large package (5000+ files): 1-5 minutes

### Optimization Tips

1. **Use local filesystem**: Avoid network-mounted directories when possible
2. **Filter extensions**: Don't include unneeded file types in `--ext`
3. **Pre-create target**: Ensure target directory exists before syncing
4. **Batch operations**: If syncing multiple packages, run sequentially (avoid parallel)
5. **Monitor disk**: Ensure adequate free space to avoid slowdowns

---

## Security Considerations

### Path Traversal Prevention

The tool uses `PathValidator` from `splurge_safe_io` to prevent path traversal attacks:

- Validates paths for dangerous characters (`..`, symlinks, etc.)
- Prevents escaping intended boundaries
- Resolves symlinks safely

**Safe to use with untrusted paths**: Yes, but validate inputs first.

### File Permissions

The tool preserves source file permissions when copying:

- Read-only files remain read-only in target
- Executable scripts remain executable
- No permission elevation occurs

**Risk**: If source has overly-permissive files, target will too. Review after sync.

### Encoding Safety

The tool safely handles file encoding:

- Validates encodings before processing
- Normalizes newlines consistently
- Raises clear errors for encoding problems

**Risk**: None known. Safe to use with any UTF-8 encoded files.

### Exclusions

The tool excludes build artifacts:

- `__pycache__` directories (never synchronized)
- This prevents copying out-of-date bytecode

**Risk**: None known. Bytecode should never be vendored.

---

## Limitations

### Known Limitations

1. **No incremental sync**: Always does full clean + sync (future: dry-run mode)
2. **No backup**: Previous vendor files deleted without backup (future: `--backup` flag)
3. **No filtering by content**: Only extension-based filtering available (future: exclude patterns)
4. **No symlink handling**: Symlinks treated as regular files (potential issue on Unix)
5. **No parallel copying**: Single-threaded, cannot leverage multiple CPUs
6. **No watch mode**: Must manually re-run for updates (future: `--watch` mode)

### When to Use Alternatives

- **If you need git-based version control**: Consider `git submodules` or `git subtree`
- **If you need package management**: Use `pip` or other package managers
- **If you need incremental sync**: Use `rsync` (but loses the clean phase benefit)
- **If you need file-level versioning**: Use version control systems

### Workarounds for Limitations

| Limitation | Workaround |
|---|---|
| No backup | Create backup before sync: `cp -r target _vendor.backup` |
| No dry-run | Test in temporary directory first |
| No symlink support | Convert symlinks to copies before syncing |
| No parallel copy | Not necessary for most packages (< 1 minute for typical sizes) |

---

## Related Documentation

- **[CLI Reference](../cli/CLI-REFERENCE.md)**: Command-line interface details
- **[API Reference](../api/API-REFERENCE.md)**: Python API for programmatic use
- **[Implementation Plan](../plans/plan-implementation-2025-10-28.md)**: Development roadmap

---

**Last Updated**: October 28, 2025  
**For Questions**: See the CLI or API reference, or check README.md for quick-start guide.
