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

### Command Signature (Sync Mode)

```bash
splurge-vendor-sync \
  --source <SOURCE-PATH> \
  --target <TARGET-PATH> \
  --package <PACKAGE-NAME> \
  [--vendor <VENDOR-DIR>] \
  [--ext <EXTENSIONS>]
```

### Command Signature (Scan Mode)

```bash
splurge-vendor-sync \
  --target <TARGET-PATH> \
  --scan [VERSION-TAG] \
  [--vendor <VENDOR-DIR>]
```

### Minimal Example (Sync Mode)

```bash
splurge-vendor-sync \
  --source /path/to/splurge-exceptions \
  --target /path/to/my-project/my_package \
  --package splurge_exceptions
```

### Minimal Example (Scan Mode)

```bash
splurge-vendor-sync \
  --target /path/to/my-project/my_package \
  --scan
```

### Full Example (Sync Mode)

```bash
splurge-vendor-sync \
  --source /d/repos/splurge-exceptions \
  --target /d/repos/my-project/my_package \
  --package splurge_exceptions \
  --vendor _vendor \
  --ext "py;json;yaml"
```

### Full Example (Scan Mode)

```bash
splurge-vendor-sync \
  --target /d/repos/my-project/my_package \
  --vendor _vendor \
  --scan __version__
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

#### --scan [VERSION-TAG]

**Type**: Optional flag with optional argument  
**Required**: No  
**Default**: None (scan mode disabled)

Scan vendor directory for version information instead of syncing packages. Recursively discovers nested vendors and displays results with hierarchical indentation.

**Description**:
- Enables scan mode instead of sync mode
- **Recursively scans nested vendor directories** to discover transitive dependencies
- Searches for version assignments in all vendored packages at any depth
- Default version tag is `__version__` when flag is used without argument
- Checks `__init__.py` first, then fallback to `__main__.py`
- Returns `?` for packages where version is not found
- **Displays hierarchical structure** with indentation showing vendor relationships
- Ignores `--source` and `--package` parameters when enabled
- Respects custom vendor directory specified by `--vendor`

**Hierarchical Output**:

When packages are nested (vendors within vendors), indentation shows the relationship:
- No indentation: Top-level packages
- 2 spaces: Vendors under a top-level package
- 4 spaces: Vendors under a nested package
- And so on...

**Usage Patterns**:

```bash
# Scan with default __version__ tag
splurge-vendor-sync --target /path/to/project --scan

# Scan with custom version tag
splurge-vendor-sync --target /path/to/project --scan MY_VERSION

# Scan with custom vendor directory
splurge-vendor-sync --target /path/to/project --vendor custom_vendor --scan MY_VERSION
```

**Examples**:
```bash
# Default scan (discovers nested vendors automatically)
splurge-vendor-sync --target /d/projects/my-project/my_package --scan

# Custom version tag
splurge-vendor-sync --target /d/projects/my-project/my_package --scan VERSION

# With custom vendor dir
splurge-vendor-sync --target /d/projects/my-project/my_package --vendor _vendored --scan

# Scan and capture output
splurge-vendor-sync --target /d/projects/my-project/my_package --scan > versions.txt
```

**Output Format**:

Flat structure (no nesting):
```
splurge_exceptions 2025.3.1
splurge_safe_io 2025.4.3
custom_package ?
```

Hierarchical structure (with nesting):
```
library_a 1.0.0
  library_b 2.0.0
    library_f 3.0.0
    library_g 4.0.0
library_c 1.5.0
  library_d ?
```

**Error Handling**:
- ❌ Target path doesn't exist → `SplurgeVendorSyncValueError` (exit code 2)
- ❌ Vendor directory doesn't exist → `SplurgeVendorSyncValueError` (exit code 2)
- ⚠️ Version not found → Returns `?` (not an error)

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

### Example 9: Scan for Default Version Tag

Scan vendored packages for `__version__` (including nested vendors).

```bash
splurge-vendor-sync \
  --target /d/repos/my-project/my_package \
  --scan
```

**What happens**:
- Searches all packages in `_vendor/` directory
- **Recursively scans nested `_vendor` directories** within each package
- Looks for `__version__` assignment in each package's `__init__.py`
- Falls back to `__main__.py` if not found in `__init__.py`
- Displays hierarchical structure showing parent-child relationships
- Prints package name and version, or `?` if not found

**Expected output**:
```
splurge_exceptions 2025.3.1
splurge_safe_io 2025.4.3
library_a 1.0.0
  library_b 2.0.0
    library_f 3.0.0
    library_g 4.0.0
```

This shows:
- `splurge_exceptions` and `splurge_safe_io` are top-level vendors
- `library_b` is nested under `library_a`
- `library_f` and `library_g` are nested under `library_b`

---

### Example 10: Scan with Custom Version Tag

Scan for a custom version variable name.

```bash
splurge-vendor-sync \
  --target /d/repos/my-project/my_package \
  --scan MY_VERSION
```

**What happens**:
- Searches for `MY_VERSION` instead of `__version__`
- Same fallback logic and output format

---

### Example 11: Scan with Custom Vendor Directory

Scan packages in a custom vendor directory.

```bash
splurge-vendor-sync \
  --target /d/repos/my-project/my_package \
  --vendor "custom_vendor" \
  --scan
```

**What happens**:
- Scans `custom_vendor/` instead of `_vendor/`
- Same version extraction logic

---

### Example 12: Scan and Save to File

Capture scan results to a file for logging.

```bash
splurge-vendor-sync \
  --target /d/repos/my-project/my_package \
  --scan > vendor_versions.txt

cat vendor_versions.txt
# Output:
# splurge_exceptions 2025.3.1
# splurge_safe_io 2025.4.3
```

---

### Example 13: Scan and Parse with Bash

Use scan results in a bash script.

```bash
#!/bin/bash

# Scan and parse versions
splurge-vendor-sync --target ./my_package --scan | while read package version; do
    echo "Package: $package, Version: $version"
    if [ "$version" = "?" ]; then
        echo "  ⚠ Warning: Version not found"
    fi
done
```

Expected output:
```
Package: splurge_exceptions, Version: 2025.3.1
Package: splurge_safe_io, Version: 2025.4.3
Package: my_package, Version: ?
  ⚠ Warning: Version not found
```

---

### Example 14: Analyze Nested Vendor Hierarchy (NEW)

Scan and analyze nested vendor relationships.

```bash
#!/bin/bash

echo "Scanning vendor hierarchy..."
splurge-vendor-sync --target /d/repos/my-project/my_package --scan > vendor_structure.txt

echo ""
echo "=== Vendor Structure ==="
cat vendor_structure.txt

echo ""
echo "=== Analysis ==="
top_level=$(grep -v "^  " vendor_structure.txt | grep -v "^    " | wc -l)
nested_level_1=$(grep "^  " vendor_structure.txt | grep -v "^    " | wc -l)
nested_level_2=$(grep "^    " vendor_structure.txt | wc -l)

echo "Top-level packages: $top_level"
echo "Nested level 1: $nested_level_1"
echo "Nested level 2+: $nested_level_2"
```

Example output:
```
Scanning vendor hierarchy...

=== Vendor Structure ===
library_a 1.0.0
  library_b 2.0.0
    library_f 3.0.0
    library_g 4.0.0
library_c 1.5.0

=== Analysis ===
Top-level packages: 2
Nested level 1: 1
Nested level 2+: 2
```

---

### Example 15: Scan and Sync Workflow (NEW)

Scan before syncing to understand vendor structure, then perform sync.

```bash
#!/bin/bash

PROJECT="/d/repos/my-project/my_package"

echo "Step 1: Scan current vendor structure..."
echo "========================================="
splurge-vendor-sync --target "$PROJECT" --scan

echo ""
echo "Step 2: Sync new packages..."
echo "============================"
splurge-vendor-sync \
    --source /d/repos/splurge-exceptions \
    --target "$PROJECT" \
    --package splurge_exceptions

echo ""
echo "Step 3: Verify new vendor structure..."
echo "======================================"
splurge-vendor-sync --target "$PROJECT" --scan

echo ""
echo "Done!"
```

---

### Example 13: Scan and Parse with Bash

Use scan results in a bash script to check for nested vendors.

```bash
#!/bin/bash

# Check for nested vendors (indented lines indicate nesting)
echo "Checking for nested vendors..."
splurge-vendor-sync --target ./my_package --scan | grep "^  " | while read package version; do
    # Remove leading spaces for display
    pkg_name=$(echo "$package" | sed 's/^  *//')
    echo "  Found nested vendor: $pkg_name (version: $version)"
done

# Count nesting levels
echo ""
echo "Nesting level analysis:"
echo "Top-level vendors:"
splurge-vendor-sync --target ./my_package --scan | grep -v "^  "

echo "Nested vendors:"
splurge-vendor-sync --target ./my_package --scan | grep "^  "
```

Expected output:
```
Checking for nested vendors...
  Found nested vendor: library_b 2.0.0
    Found nested vendor: library_f 3.0.0
    Found nested vendor: library_g 4.0.0

Nesting level analysis:
Top-level vendors:
library_a 1.0.0
library_c 1.5.0
Nested vendors:
  library_b 2.0.0
    library_f 3.0.0
    library_g 4.0.0
```

---

### Example 14: Sync and Then Verify Versions

Sync packages and verify they were synced with correct versions.

```bash
#!/bin/bash

echo "Syncing packages..."
splurge-vendor-sync \
    --source /d/repos/splurge-exceptions \
    --target /d/repos/my-project/my_package \
    --package splurge_exceptions

if [ $? -eq 0 ]; then
    echo "✓ Sync successful"
    echo ""
    echo "Verifying versions..."
    splurge-vendor-sync \
        --target /d/repos/my-project/my_package \
        --scan
else
    echo "✗ Sync failed"
    exit 1
fi
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
ERROR: splurge-vendor-sync.os - permission-denied
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
