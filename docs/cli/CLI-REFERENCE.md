# CLI Reference

**splurge-vendor-sync** | Complete Command-Line Interface Documentation

---

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Arguments Reference](#arguments-reference)
4. [Common Examples](#common-examples)
5. [Exit Codes](#exit-codes)
6. [Output Format](#output-format)
7. [Troubleshooting](#troubleshooting)
8. [Tips & Tricks](#tips--tricks)

---

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/jim-schilling/splurge-vendor-sync.git
cd splurge-vendor-sync

# Install in development mode
pip install -e .

# Verify installation
splurge-vendor-sync --help
```

### From Package (When Published)

```bash
pip install splurge-vendor-sync

# Verify installation
splurge-vendor-sync --help
```

### Verify Installation

```bash
$ splurge-vendor-sync --help
usage: splurge-vendor-sync [-h] --source SOURCE --target TARGET 
                           --package PACKAGE [--vendor VENDOR] 
                           [--ext EXT]

One-way vendor synchronization for Python packages...
```

---

## Basic Usage

### Command Signature

```bash
splurge-vendor-sync \
  --source <SOURCE-PATH> \
  --target <TARGET-PATH> \
  --package <PACKAGE-NAME> \
  [--vendor <VENDOR-DIR>] \
  [--ext <EXTENSIONS>]
```

### Minimal Example

```bash
splurge-vendor-sync \
  --source /path/to/splurge-exceptions \
  --target /path/to/my-project/my_package \
  --package splurge_exceptions
```

### Full Example

```bash
splurge-vendor-sync \
  --source /d/repos/splurge-exceptions \
  --target /d/repos/my-project/my_package \
  --package splurge_exceptions \
  --vendor _vendor \
  --ext "py;json;yaml"
```

---

## Arguments Reference

### Required Arguments

#### --source <SOURCE-PATH>

**Type**: Path (string)  
**Required**: Yes  
**Default**: None

The root directory path containing the source package to sync.

**Description**:
- Must be an absolute or relative path to an existing directory
- Should contain the package subdirectory specified by `--package`
- Example: `/repos/splurge-exceptions` or `./packages/splurge-exceptions`

**Examples**:
```bash
# Absolute path
splurge-vendor-sync --source /d/repos/splurge-exceptions ...

# Relative path
splurge-vendor-sync --source ../splurge-exceptions ...

# Current directory package
splurge-vendor-sync --source . ...
```

**Error Handling**:
- ❌ Path doesn't exist → `SplurgeVendorSyncValueError` (exit code 2)
- ❌ No read permission → `SplurgeVendorSyncOSError` (exit code 1)

---

#### --target <TARGET-PATH>

**Type**: Path (string)  
**Required**: Yes  
**Default**: None

The root directory path of the target project where the vendor directory will be created.

**Description**:
- Must be an absolute or relative path to an existing directory
- Vendor directory will be created within this path if it doesn't exist
- Example: `/projects/my-project/my_package` or `./my-package`

**Examples**:
```bash
# Absolute path to project root
splurge-vendor-sync --target /d/projects/my-project/my_package ...

# Relative path
splurge-vendor-sync --target ./my-package ...

# Home directory relative
splurge-vendor-sync --target ~/projects/my-package ...
```

**Error Handling**:
- ❌ Path doesn't exist → `SplurgeVendorSyncValueError` (exit code 2)
- ❌ No write permission → `SplurgeVendorSyncOSError` (exit code 1)

---

#### --package <PACKAGE-NAME>

**Type**: String  
**Required**: Yes  
**Default**: None

The name of the package subdirectory within the source to synchronize.

**Description**:
- Must match a subdirectory name in `--source`
- Example: `splurge_exceptions`, `my_package`, `utils`
- Cannot be empty or contain path separators (no `/` or `\`)
- Used to construct: `[SOURCE]/[PACKAGE]`

**Examples**:
```bash
# Simple package name
splurge-vendor-sync --package splurge_exceptions ...

# Package with underscores
splurge-vendor-sync --package splurge_safe_io ...

# Package with numbers
splurge-vendor-sync --package package_v2 ...
```

**Error Handling**:
- ❌ Empty string → `SplurgeVendorSyncValueError` (exit code 2)
- ❌ Directory doesn't exist → `SplurgeVendorSyncValueError` (exit code 2)
- ❌ Contains invalid characters → `SplurgeVendorSyncValueError` (exit code 2)

---

### Optional Arguments

#### --vendor <VENDOR-DIR>

**Type**: String  
**Required**: No  
**Default**: `_vendor`

The name of the vendor directory within the target project.

**Description**:
- Specifies the subdirectory name for vendored packages
- Default `_vendor` is a common convention (Python import-style)
- Can be any valid directory name
- Used to construct: `[TARGET]/[VENDOR]/[PACKAGE]`

**Examples**:
```bash
# Default (recommended)
splurge-vendor-sync --vendor _vendor ...

# Alternative name
splurge-vendor-sync --vendor vendored ...

# No underscore prefix
splurge-vendor-sync --vendor vendor ...

# Namespaced vendor
splurge-vendor-sync --vendor third_party ...
```

**Error Handling**:
- ❌ Invalid directory name → `SplurgeVendorSyncValueError` (exit code 2)

---

#### --ext <FILE-EXTENSIONS>

**Type**: String (semicolon-separated)  
**Required**: No  
**Default**: `py;json;yml;yaml;ini`

Semicolon-separated list of file extensions to include in the sync.

**Description**:
- Extensions should be specified **without leading dots** (e.g., `py` not `.py`)
- Multiple extensions separated by semicolons (no spaces)
- Matching is **case-insensitive** (`.PY` and `.py` both match)
- Only files with these extensions will be copied
- **Default extensions** include most Python source and config files

**Format**:
```
--ext "ext1;ext2;ext3;..."
```

**Common Extension Sets**:

| Set | Extensions | Use Case |
|-----|------------|----------|
| Minimal | `py` | Only Python source files |
| Standard | `py;json;yml;yaml;ini` | Python + common configs (default) |
| Extended | `py;json;yml;yaml;ini;txt;md;rst` | Includes documentation |
| Full | `py;json;yml;yaml;ini;txt;md;rst;sh;bash;cfg` | Everything except binaries |

**Examples**:
```bash
# Default (standard Python + config)
splurge-vendor-sync --ext "py;json;yml;yaml;ini" ...

# Only Python source
splurge-vendor-sync --ext "py" ...

# Python + YAML only
splurge-vendor-sync --ext "py;yaml" ...

# Extended with docs
splurge-vendor-sync --ext "py;json;yml;yaml;ini;txt;md;rst" ...

# Custom set for specific needs
splurge-vendor-sync --ext "py;ini" ...
```

**Error Handling**:
- ❌ Empty string → `SplurgeVendorSyncValueError` (exit code 2)
- ❌ No valid extensions → `SplurgeVendorSyncValueError` (exit code 2)

---

#### --help, -h

**Type**: Flag (boolean)  
**Required**: No  
**Default**: False (help not shown)

Display help message and exit.

**Examples**:
```bash
splurge-vendor-sync --help
splurge-vendor-sync -h
```

**Output**: Shows usage, all arguments, defaults, and examples.

---

## Common Examples

### Example 1: Basic Sync

Sync a package with all default settings.

```bash
splurge-vendor-sync \
  --source /d/repos/splurge-exceptions \
  --target /d/repos/my-project/my_package \
  --package splurge_exceptions
```

**What happens**:
- Removes `/d/repos/my-project/my_package/_vendor/splurge_exceptions/` (if exists)
- Copies all `.py`, `.json`, `.yml`, `.yaml`, `.ini` files from source
- Result: `/d/repos/my-project/my_package/_vendor/splurge_exceptions/...`

**Expected output**:
```
✓ Sync completed successfully
  Files removed: 5
  Files copied: 42
  Directories created: 8
Exit code: 0
```

---

### Example 2: Relative Paths

Using relative paths from current directory.

```bash
cd /d/repos

splurge-vendor-sync \
  --source ./splurge-exceptions \
  --target ./my-project/my_package \
  --package splurge_exceptions
```

---

### Example 3: Custom Vendor Directory

Use a different vendor directory name.

```bash
splurge-vendor-sync \
  --source /d/repos/splurge-exceptions \
  --target /d/repos/my-project/my_package \
  --package splurge_exceptions \
  --vendor "vendored"
```

**Result**: Files synced to `/d/repos/my-project/my_package/vendored/splurge_exceptions/`

---

### Example 4: Minimal Extensions

Only sync Python files, skip configuration files.

```bash
splurge-vendor-sync \
  --source /d/repos/splurge-exceptions \
  --target /d/repos/my-project/my_package \
  --package splurge_exceptions \
  --ext "py"
```

**Result**: Only `.py` files copied; `.json`, `.yaml`, etc. skipped

---

### Example 5: Extended Extensions

Include Python, configs, and documentation.

```bash
splurge-vendor-sync \
  --source /d/repos/splurge-exceptions \
  --target /d/repos/my-project/my_package \
  --package splurge_exceptions \
  --ext "py;json;yml;yaml;ini;txt;md;rst"
```

**Result**: All specified file types copied

---

### Example 6: Multiple Packages (Bash Script)

Sync multiple packages in one script.

```bash
#!/bin/bash

TARGET="/d/repos/my-project/my_package"

splurge-vendor-sync --source /d/repos/splurge-exceptions --package splurge_exceptions --target "$TARGET"
splurge-vendor-sync --source /d/repos/splurge-safe-io --package splurge_safe_io --target "$TARGET"
splurge-vendor-sync --source /d/repos/splurge-formatting --package splurge_formatting --target "$TARGET"

echo "All packages synced!"
```

---

### Example 7: Verify Before Sync

Check that everything is set up correctly before syncing.

```bash
#!/bin/bash

SOURCE="/d/repos/splurge-exceptions"
TARGET="/d/repos/my-project/my_package"
PACKAGE="splurge_exceptions"

# Verify source
if [ ! -d "$SOURCE/$PACKAGE" ]; then
    echo "Error: Source package not found: $SOURCE/$PACKAGE"
    exit 1
fi

# Verify target
if [ ! -d "$TARGET" ]; then
    echo "Error: Target directory not found: $TARGET"
    exit 1
fi

# Proceed with sync
splurge-vendor-sync \
    --source "$SOURCE" \
    --target "$TARGET" \
    --package "$PACKAGE"
```

---

### Example 8: Error Handling (Bash Script)

Handle errors in a bash script.

```bash
#!/bin/bash

splurge-vendor-sync \
    --source /d/repos/splurge-exceptions \
    --target /d/repos/my-project/my_package \
    --package splurge_exceptions

exit_code=$?

case $exit_code in
    0)
        echo "✓ Sync successful"
        ;;
    1)
        echo "✗ Runtime error (I/O, permissions, etc.)"
        exit 1
        ;;
    2)
        echo "✗ Validation error (invalid arguments, missing paths)"
        exit 1
        ;;
    *)
        echo "✗ Unknown error code: $exit_code"
        exit 1
        ;;
esac
```

---

## Exit Codes

### Exit Code 0: Success

Synchronization completed successfully. All files were copied.

```bash
$ splurge-vendor-sync --source /source --target /target --package pkg
$ echo $?
0
```

**What it means**:
- Sync operation completed
- All matching files copied successfully
- No errors occurred

---

### Exit Code 1: Runtime Error

A runtime error occurred (I/O failure, permission issue, etc.).

```bash
$ splurge-vendor-sync --source /restricted --target /target --package pkg
✗ Permission denied: cannot read from /restricted
$ echo $?
1
```

**Common causes**:
- Permission denied (read or write)
- Disk full
- File locked by another process
- Encoding error
- Network timeout (if network drive)

**What to do**:
1. Check the error message for specific problem
2. Fix the underlying issue (permissions, disk space, etc.)
3. Re-run the command

---

### Exit Code 2: Validation Error

An argument validation error occurred (invalid paths, missing arguments, etc.).

```bash
$ splurge-vendor-sync --source /nonexistent --target /target --package pkg
✗ Source path not found: /nonexistent
$ echo $?
2
```

**Common causes**:
- Required argument missing (`--source`, `--target`, `--package`)
- Path doesn't exist
- Invalid argument value
- Type mismatch

**What to do**:
1. Check command-line arguments
2. Verify all required arguments are present
3. Verify paths exist and are correct
4. Re-run the command with correct arguments

---

## Output Format

### Successful Sync

```
✓ Sync completed successfully
  Files removed: 5
  Files copied: 42
  Directories created: 8
```

**Fields**:
- **Files removed**: Number of files deleted in clean phase (from old vendor directory)
- **Files copied**: Number of files copied in sync phase
- **Directories created**: Number of directories created to match source structure

### Partial Sync (Warnings)

```
⚠ Sync completed with issues
  Files removed: 5
  Files copied: 40 (2 failed)
  Directories created: 8
  Errors:
    - Failed to copy: path/to/file1.py
    - Failed to copy: path/to/file2.py
```

### Error Output

```
ERROR: splurge.vendor_sync.value - path-not-found
  Cannot find source path: /invalid/path
  Suggestion: Verify the path exists and is accessible
```

**Error message format**:
```
ERROR: {domain}.{error_code} - {description}
  {file/path}: {details}
  Suggestion: {remediation}
```

---

## Troubleshooting

### Problem: "Source path not found"

```
ERROR: splurge.vendor_sync.value - path-not-found
```

**Solutions**:
1. Verify source path exists: `test -d /path && echo "OK"`
2. Check for typos in path
3. Use absolute paths instead of relative
4. Check file permissions: `ls -ld /path`

---

### Problem: "Target path not found"

```
ERROR: splurge.vendor_sync.value - path-not-found
```

**Solutions**:
1. Verify target path exists: `test -d /path && echo "OK"`
2. Create target if needed: `mkdir -p /path`
3. Check parent permissions: `ls -ld /path/..`

---

### Problem: "Permission denied"

```
ERROR: splurge.vendor_sync.os - permission-denied
```

**Solutions**:
1. Check read permission on source: `test -r /path && echo "OK"`
2. Check write permission on target: `test -w /path && echo "OK"`
3. Fix permissions: `chmod +r /path` (read) or `chmod +w /path` (write)
4. Check file locks: `lsof | grep filename`
5. Run with appropriate user/elevated privileges if needed

---

### Problem: "Files not being copied"

**Solutions**:
1. Verify file extensions: `find /source -type f | head -10`
2. Check extension filter: Ensure `--ext` includes needed types
3. Look for `__pycache__`: These directories are always excluded
4. Check with verbose (when available): `--verbose`

---

### Problem: "Disk full" error

```
ERROR: splurge.vendor_sync.os - disk-full
```

**Solutions**:
1. Check disk space: `df -h`
2. Free up space: `rm -rf /unused/directory`
3. Use a different target with more space

---

## Tips & Tricks

### Tip 1: Create a Shell Function

Create a reusable function in your shell profile:

```bash
# Add to ~/.bashrc or ~/.zshrc
vendor-sync() {
    splurge-vendor-sync \
        --source "$1" \
        --target "$2" \
        --package "$3" \
        --vendor "${4:-_vendor}"
}

# Usage
vendor-sync /repos/splurge-exceptions /my-project/my_package splurge_exceptions
```

---

### Tip 2: Dry-Run Alternative (Current)

Since dry-run isn't available yet, test in a temporary directory:

```bash
#!/bin/bash

SOURCE="/d/repos/splurge-exceptions"
PACKAGE="splurge_exceptions"
TEMP_TARGET="/tmp/vendor-test"

# Create temporary test directory
mkdir -p "$TEMP_TARGET"

# Test sync
splurge-vendor-sync \
    --source "$SOURCE" \
    --target "$TEMP_TARGET" \
    --package "$PACKAGE"

if [ $? -eq 0 ]; then
    echo "✓ Test sync successful, proceeding with real sync..."
    splurge-vendor-sync \
        --source "$SOURCE" \
        --target /d/repos/my-project/my_package \
        --package "$PACKAGE"
else
    echo "✗ Test sync failed, aborting"
fi

# Cleanup
rm -rf "$TEMP_TARGET"
```

---

### Tip 3: Backup Before Sync (Current)

Since backup flag isn't available yet, create manual backup:

```bash
#!/bin/bash

TARGET="/d/repos/my-project/my_package"
VENDOR_DIR="$TARGET/_vendor"
BACKUP_DIR="$VENDOR_DIR.backup.$(date +%Y%m%d_%H%M%S)"

# Backup existing vendor if it exists
if [ -d "$VENDOR_DIR" ]; then
    echo "Backing up existing vendor to: $BACKUP_DIR"
    cp -r "$VENDOR_DIR" "$BACKUP_DIR"
fi

# Perform sync
splurge-vendor-sync \
    --source /d/repos/splurge-exceptions \
    --target "$TARGET" \
    --package splurge_exceptions

if [ $? -ne 0 ]; then
    echo "Sync failed! Restoring from backup..."
    rm -rf "$VENDOR_DIR"
    mv "$BACKUP_DIR" "$VENDOR_DIR"
fi
```

---

### Tip 4: Logging Sync Operations

Capture output to log file:

```bash
#!/bin/bash

LOGFILE="/var/log/vendor-sync.log"

splurge-vendor-sync \
    --source /d/repos/splurge-exceptions \
    --target /d/repos/my-project/my_package \
    --package splurge_exceptions \
    2>&1 | tee -a "$LOGFILE"

echo "Sync exit code: $?" >> "$LOGFILE"
```

---

### Tip 5: Scheduled Syncing (Cron)

Sync packages on a schedule:

```bash
# Add to crontab: crontab -e

# Daily sync at 2 AM
0 2 * * * /path/to/vendor-sync-script.sh >> /var/log/vendor-sync.log 2>&1

# Weekly sync on Monday at 6 AM
0 6 * * 1 /path/to/vendor-sync-script.sh >> /var/log/vendor-sync.log 2>&1
```

Script content:
```bash
#!/bin/bash
set -e

echo "[$(date)] Starting vendor sync..."

splurge-vendor-sync \
    --source /d/repos/splurge-exceptions \
    --target /d/repos/my-project/my_package \
    --package splurge_exceptions

splurge-vendor-sync \
    --source /d/repos/splurge-safe-io \
    --target /d/repos/my-project/my_package \
    --package splurge_safe_io

echo "[$(date)] Vendor sync complete"
```

---

### Tip 6: Integration with Build Systems

#### Make

```makefile
.PHONY: vendor-sync

vendor-sync:
    splurge-vendor-sync \
        --source /d/repos/splurge-exceptions \
        --target $(PWD)/my_package \
        --package splurge_exceptions

.PHONY: build
build: vendor-sync
    python setup.py build
```

#### Python setup.py

```python
from setuptools import setup
import subprocess

# Sync vendors before building
subprocess.run([
    "splurge-vendor-sync",
    "--source", "/d/repos/splurge-exceptions",
    "--target", "./my_package",
    "--package", "splurge_exceptions"
], check=True)

setup(
    name="my-package",
    # ...
)
```

---

## Related Documentation

- **[API Reference](../api/API-REFERENCE.md)**: Python API for programmatic use
- **[Features & Errors](../README-DETAILS.md)**: Comprehensive features guide and troubleshooting
- **[README](../README.md)**: Quick-start guide

---

**Last Updated**: October 28, 2025  
**CLI Version**: 1.0
