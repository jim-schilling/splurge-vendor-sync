# API Reference

**splurge-vendor-sync** | Complete Python API Documentation

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core API](#core-api)
3. [Exceptions](#exceptions)
4. [Return Values](#return-values)
5. [Usage Examples](#usage-examples)
6. [Advanced Usage](#advanced-usage)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

---

## Quick Start

### Basic Import

```python
from splurge_vendor_sync.sync import sync_vendor
from splurge_vendor_sync.exceptions import SplurgeVendorSyncError
```

### Minimal Example

```python
result = sync_vendor(
    source_path="/path/to/splurge-exceptions",
    target_path="/path/to/my-project/my_package",
    package="splurge_exceptions"
)

print(f"Copied {result['files_copied']} files")
print(f"Status: {result['status']}")
```

---

## Core API

### sync_vendor() Function

```python
def sync_vendor(
    source_path: str | Path,
    target_path: str | Path,
    package: str,
    vendor: str = "_vendor",
    extensions: str = "py;json;yml;yaml;ini"
) -> dict[str, Any]:
```

#### Description

Synchronizes a source package to a target project's vendor directory in two phases:
1. **Clean Phase**: Removes all existing files in the target vendor location
2. **Sync Phase**: Copies all matching files from source to target

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source_path` | `str` or `Path` | Yes | N/A | Absolute or relative path to the directory containing the source package |
| `target_path` | `str` or `Path` | Yes | N/A | Absolute or relative path to the target project directory (where vendor dir will be created) |
| `package` | `str` | Yes | N/A | Name of the package subdirectory to sync (e.g., `splurge_exceptions`) |
| `vendor` | `str` | No | `"_vendor"` | Name of the vendor directory within target (default: `_vendor`) |
| `extensions` | `str` | No | `"py;json;yml;yaml;ini"` | Semicolon-separated file extensions to include (without leading dots) |

#### Return Value

Returns a dictionary with the following keys:

```python
{
    'files_removed': int,           # Number of files removed in clean phase
    'files_copied': int,            # Number of files copied in sync phase
    'directories_created': int,     # Number of directories created in sync phase
    'status': 'success' | 'partial' | 'failed',  # Overall status
    'errors': list[str],            # List of error messages (if any)
}
```

#### Return Status Values

- **`'success'`**: Sync completed with no errors
- **`'partial'`**: Sync completed but some files were skipped (see `errors` list)
- **`'failed'`**: Sync failed, check `errors` for details

#### Raises

| Exception | When | Details |
|-----------|------|---------|
| `SplurgeVendorSyncTypeError` | Invalid parameter type | Parameter is not str/Path or expected type |
| `SplurgeVendorSyncValueError` | Invalid parameter value | Value is empty, invalid, or path doesn't exist |
| `SplurgeVendorSyncOSError` | I/O failure | Permission denied, disk full, deletion failed, etc. |
| `SplurgeVendorSyncUnicodeError` | Encoding error | File encoding problem |
| `SplurgeVendorSyncRuntimeError` | Unexpected error | Unclassified runtime error |

---

## Exceptions

### Exception Hierarchy

```python
SplurgeVendorSyncError (base)
├── SplurgeVendorSyncTypeError
├── SplurgeVendorSyncValueError
├── SplurgeVendorSyncOSError
├── SplurgeVendorSyncRuntimeError
└── SplurgeVendorSyncUnicodeError
```

### SplurgeVendorSyncError

Base exception for all sync-related errors.

```python
try:
    result = sync_vendor(...)
except SplurgeVendorSyncError as e:
    print(f"Sync error: {e}")
```

**Attributes**:
- `error_code` (str): Machine-readable error classification
- `message` (str): Human-readable error description
- `details` (dict): Additional error context

### SplurgeVendorSyncTypeError

Raised when parameter types are incorrect.

```python
try:
    sync_vendor(
        source_path=123,  # Wrong type!
        target_path="/target",
        package="pkg"
    )
except SplurgeVendorSyncTypeError as e:
    print(f"Type error: {e.error_code}")
```

**Error Codes**:
- `type-mismatch`: Parameter type doesn't match expected type

### SplurgeVendorSyncValueError

Raised when parameter values are invalid.

```python
try:
    sync_vendor(
        source_path="/nonexistent/path",  # Path doesn't exist!
        target_path="/target",
        package="pkg"
    )
except SplurgeVendorSyncValueError as e:
    print(f"Value error: {e.error_code}")
```

**Error Codes**:
- `invalid-value`: Value is invalid or empty
- `path-not-found`: Source or target path doesn't exist
- `path-validation-failed`: Path failed security validation
- `invalid-package`: Package name is invalid or empty

### SplurgeVendorSyncOSError

Raised when I/O or operating system operations fail.

```python
try:
    sync_vendor(
        source_path="/restricted/path",  # Permission denied!
        target_path="/target",
        package="pkg"
    )
except SplurgeVendorSyncOSError as e:
    print(f"OS error: {e.error_code}")
```

**Error Codes**:
- `permission-denied`: No read/write permission
- `deletion-failed`: Failed to remove old vendor files
- `copy-failed`: Failed to copy a file
- `disk-full`: Disk space exhausted

### SplurgeVendorSyncUnicodeError

Raised when file encoding or decoding fails.

```python
try:
    sync_vendor(
        source_path="/path/with/bad/encoding",
        target_path="/target",
        package="pkg"
    )
except SplurgeVendorSyncUnicodeError as e:
    print(f"Encoding error: {e.error_code}")
```

**Error Codes**:
- `encoding-error`: File encoding problem
- `decoding-error`: File decoding problem

### SplurgeVendorSyncRuntimeError

Raised for unexpected runtime errors.

```python
try:
    result = sync_vendor(...)
except SplurgeVendorSyncRuntimeError as e:
    print(f"Unexpected runtime error: {e}")
```

**Error Codes**:
- `general`: Unclassified runtime error

---

## Return Values

### Successful Sync

```python
result = sync_vendor(
    source_path="/repo/splurge-exceptions",
    target_path="/my-project/my_package",
    package="splurge_exceptions"
)

# Result:
{
    'files_removed': 5,
    'files_copied': 42,
    'directories_created': 8,
    'status': 'success',
    'errors': []
}
```

### Partial Sync (Some Errors)

```python
{
    'files_removed': 5,
    'files_copied': 40,        # 2 files failed
    'directories_created': 8,
    'status': 'partial',
    'errors': [
        'Failed to copy file: /source/path/file1.py',
        'Failed to copy file: /source/path/file2.py'
    ]
}
```

### Failed Sync

When an exception is raised, no return value is provided (exception handling required).

---

## Usage Examples

### Example 1: Basic Synchronization

Sync a package with all default settings.

```python
from splurge_vendor_sync.sync import sync_vendor

result = sync_vendor(
    source_path="/repos/splurge-exceptions",
    target_path="/my-project/my_package",
    package="splurge_exceptions"
)

if result['status'] == 'success':
    print(f"✓ Synced {result['files_copied']} files")
else:
    print(f"✗ Sync failed: {result['errors']}")
```

### Example 2: Custom Vendor Directory

Use a different vendor directory name.

```python
result = sync_vendor(
    source_path="/repos/splurge-exceptions",
    target_path="/my-project/my_package",
    package="splurge_exceptions",
    vendor="vendored"  # Uses 'vendored' instead of '_vendor'
)

# Result: /my-project/my_package/vendored/splurge_exceptions/
```

### Example 3: Custom File Extensions

Only sync Python and YAML files, skip JSON and INI.

```python
result = sync_vendor(
    source_path="/repos/splurge-exceptions",
    target_path="/my-project/my_package",
    package="splurge_exceptions",
    extensions="py;yaml"  # Only .py and .yaml files
)

# Result: Only .py and .yaml files are copied
```

### Example 4: Multiple Packages

Sync multiple packages to the same project.

```python
packages = [
    ("splurge-exceptions", "splurge_exceptions"),
    ("splurge-safe-io", "splurge_safe_io"),
    ("splurge-formatting", "splurge_formatting"),
]

for repo_name, pkg_name in packages:
    result = sync_vendor(
        source_path=f"/repos/{repo_name}",
        target_path="/my-project/my_package",
        package=pkg_name
    )
    print(f"{pkg_name}: {result['files_copied']} files")
```

### Example 5: Error Handling

Catch and handle different error types.

```python
from splurge_vendor_sync.sync import sync_vendor
from splurge_vendor_sync.exceptions import (
    SplurgeVendorSyncValueError,
    SplurgeVendorSyncOSError,
    SplurgeVendorSyncError
)

try:
    result = sync_vendor(
        source_path="/repos/splurge-exceptions",
        target_path="/my-project/my_package",
        package="splurge_exceptions"
    )
    print(f"Sync completed: {result['status']}")

except SplurgeVendorSyncValueError as e:
    print(f"Validation error: {e.message}")
    print(f"Error code: {e.error_code}")
    # Handle invalid paths or values

except SplurgeVendorSyncOSError as e:
    print(f"I/O error: {e.message}")
    # Handle permission or disk errors

except SplurgeVendorSyncError as e:
    print(f"Other sync error: {e.message}")
    # Handle other errors
```

### Example 6: Relative Paths

Use relative paths (relative to current working directory).

```python
import os
from pathlib import Path

# Set working directory
os.chdir("/workspace")

result = sync_vendor(
    source_path="../splurge-exceptions",
    target_path="./my-project/my_package",
    package="splurge_exceptions"
)
```

### Example 7: Path Objects

Use `pathlib.Path` objects instead of strings.

```python
from pathlib import Path
from splurge_vendor_sync.sync import sync_vendor

result = sync_vendor(
    source_path=Path("/repos/splurge-exceptions"),
    target_path=Path("/my-project/my_package"),
    package="splurge_exceptions"
)
```

### Example 8: Programmatic Integration

Integrate sync into a build or setup script.

```python
from splurge_vendor_sync.sync import sync_vendor
from splurge_vendor_sync.exceptions import SplurgeVendorSyncError

def sync_vendors():
    """Sync all vendored dependencies."""
    configs = [
        {
            "source": "/repos/splurge-exceptions",
            "package": "splurge_exceptions",
            "extensions": "py;json"
        },
        {
            "source": "/repos/splurge-safe-io",
            "package": "splurge_safe_io",
            "extensions": "py"
        }
    ]
    
    target = "/my-project/my_package"
    
    for config in configs:
        try:
            result = sync_vendor(
                source_path=config["source"],
                target_path=target,
                package=config["package"],
                extensions=config["extensions"]
            )
            
            if result['status'] != 'success':
                print(f"Warning: {config['package']} sync had issues")
                for error in result['errors']:
                    print(f"  - {error}")
            else:
                print(f"✓ {config['package']}: {result['files_copied']} files")
                
        except SplurgeVendorSyncError as e:
            print(f"✗ {config['package']}: {e.message}")
            raise

if __name__ == "__main__":
    sync_vendors()
    print("All vendors synced!")
```

---

## Advanced Usage

### Validation Before Sync

Validate paths before attempting sync:

```python
from pathlib import Path
from splurge_vendor_sync._vendor.splurge_safe_io.path_validator import PathValidator

def validate_paths(source, target, package):
    """Validate paths before sync."""
    try:
        source_path = PathValidator.get_validated_path(
            source, must_exist=True, must_be_readable=True
        )
        target_path = PathValidator.get_validated_path(
            target, must_exist=True, must_be_writable=True
        )
        
        package_path = source_path / package
        if not package_path.exists():
            raise ValueError(f"Package not found: {package_path}")
        
        return source_path, target_path
    except Exception as e:
        print(f"Validation failed: {e}")
        raise

# Usage
try:
    src, tgt = validate_paths(
        "/repos/splurge-exceptions",
        "/my-project/my_package",
        "splurge_exceptions"
    )
    print(f"Valid paths: {src} -> {tgt}")
except Exception:
    # Handle validation error
    pass
```

### Extension Set Management

Create reusable extension configurations:

```python
EXTENSION_SETS = {
    "minimal": "py",
    "standard": "py;json;yml;yaml;ini",
    "extended": "py;json;yml;yaml;ini;txt;md;rst",
    "all_text": "py;json;yml;yaml;ini;txt;md;rst;sh;bash;cfg"
}

def sync_with_preset(source, target, package, preset="standard"):
    """Sync using a preset extension set."""
    extensions = EXTENSION_SETS.get(preset, EXTENSION_SETS["standard"])
    
    return sync_vendor(
        source_path=source,
        target_path=target,
        package=package,
        extensions=extensions
    )

# Usage
result = sync_with_preset(
    "/repos/splurge-exceptions",
    "/my-project/my_package",
    "splurge_exceptions",
    preset="extended"
)
```

### Batch Sync with Progress Tracking

Sync multiple packages with progress reporting:

```python
from splurge_vendor_sync.sync import sync_vendor

packages = [
    ("splurge-exceptions", "splurge_exceptions"),
    ("splurge-safe-io", "splurge_safe_io"),
    ("splurge-formatting", "splurge_formatting"),
]

total_files = 0
total_errors = 0

print(f"Syncing {len(packages)} packages...")

for idx, (repo, pkg) in enumerate(packages, 1):
    try:
        result = sync_vendor(
            source_path=f"/repos/{repo}",
            target_path="/my-project/my_package",
            package=pkg
        )
        
        total_files += result['files_copied']
        total_errors += len(result['errors'])
        
        status_icon = "✓" if result['status'] == 'success' else "⚠"
        print(f"[{idx}/{len(packages)}] {status_icon} {pkg}: {result['files_copied']} files")
        
    except Exception as e:
        print(f"[{idx}/{len(packages)}] ✗ {pkg}: {e}")
        total_errors += 1

print(f"\nSummary: {total_files} files synced, {total_errors} errors")
```

---

## Error Handling

### Best Practices

#### 1. Catch Specific Exceptions

```python
from splurge_vendor_sync.exceptions import (
    SplurgeVendorSyncValueError,
    SplurgeVendorSyncOSError,
)

try:
    result = sync_vendor(...)
except SplurgeVendorSyncValueError:
    # Handle validation errors (exit code 2)
    pass
except SplurgeVendorSyncOSError:
    # Handle I/O errors (exit code 1)
    pass
```

#### 2. Check Return Status

```python
result = sync_vendor(...)

if result['status'] == 'success':
    print("All files synced successfully")
elif result['status'] == 'partial':
    print(f"Some files failed: {result['errors']}")
else:
    print("Sync failed")
```

#### 3. Log Errors for Debugging

```python
import logging

logger = logging.getLogger(__name__)

try:
    result = sync_vendor(...)
    if result['errors']:
        for error in result['errors']:
            logger.warning(f"Sync error: {error}")
except SplurgeVendorSyncError as e:
    logger.error(f"Sync failed: {e.message}", exc_info=True)
```

---

## Best Practices

1. **Always validate input paths** before calling `sync_vendor()`
2. **Check return status** and `errors` list for issues
3. **Use try/except** for exception handling
4. **Use relative paths carefully** (be aware of current working directory)
5. **Test with dry-run first** (when available in future versions)
6. **Handle partial sync** by checking `errors` list
7. **Log all operations** for debugging and auditing
8. **Batch syncs sequentially**, not in parallel
9. **Monitor disk space** before syncing large packages
10. **Document your extension configuration** for reproducibility

---

## Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| `SplurgeVendorSyncValueError: path-not-found` | Verify paths exist: `test -d /path` |
| `SplurgeVendorSyncOSError: permission-denied` | Check permissions: `ls -ld /path` |
| `SplurgeVendorSyncUnicodeError` | Check file encoding: `file -i myfile` |
| Files not copied | Verify extensions in `--ext` parameter |
| Out of memory on large packages | Use streaming reader (not applicable to sync_vendor directly) |

---

## Related Documentation

- **[CLI Reference](../cli/CLI-REFERENCE.md)**: Command-line interface documentation
- **[Features & Errors](../README-DETAILS.md)**: Comprehensive features and troubleshooting guide
- **[README](../README.md)**: Quick-start guide

---

**Last Updated**: October 28, 2025  
**API Version**: 1.0
