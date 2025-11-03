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
- `splurge-vendor-sync.type.type-mismatch`: Parameter type doesn't match expected type

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
- `splurge-vendor-sync.value.invalid-value`: Value is invalid or empty
- `splurge-vendor-sync.value.path-not-found`: Source or target path doesn't exist
- `splurge-vendor-sync.value.path-validation-failed`: Path failed security validation
- `splurge-vendor-sync.value.invalid-package`: Package name is invalid or empty

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
- `splurge-vendor-sync.os.permission-denied`: No read/write permission
- `splurge-vendor-sync.os.deletion-failed`: Failed to remove old vendor files
- `splurge-vendor-sync.os.copy-failed`: Failed to copy a file
- `splurge-vendor-sync.os.disk-full`: Disk space exhausted

### SplurgeVendorSyncUnicodeError

Raised when file encoding or decoding fails (currently not raised in implementation, reserved for future use).

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

**Error Codes** (Reserved):
- `splurge-vendor-sync.unicode.encoding-error`: File encoding problem
- `splurge-vendor-sync.unicode.decoding-error`: File decoding problem

**Note**: Unicode errors are not currently raised in sync operations. Encoding/decoding errors are caught as generic exceptions and re-raised as `SplurgeVendorSyncError` with `error_code="sync-failed"`.

### SplurgeVendorSyncRuntimeError

Raised for unexpected runtime errors during sync operations.

```python
try:
    result = sync_vendor(...)
except SplurgeVendorSyncError as e:
    print(f"Unexpected sync error: {e.error_code}")
```

**Error Codes**:
- `splurge-vendor-sync.sync-failed`: Unexpected error during synchronization

**Note**: Unexpected errors caught during sync are raised as the base `SplurgeVendorSyncError` exception with `error_code="sync-failed"`, not as `SplurgeVendorSyncRuntimeError`. The `SplurgeVendorSyncRuntimeError` subclass is reserved for future use with domain `splurge-vendor-sync.runtime`.

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

## Nested Vendor Scanning API

### scan_vendor_packages_nested() Function

```python
def scan_vendor_packages_nested(
    target_path: str | Path,
    vendor_dir: str = "_vendor",
    version_tag: str = "__version__",
    depth: int = 0,
    parent_package: str | None = None
) -> list[NestedVersionInfo]:
```

#### Description

Recursively scans vendor directories (including nested vendors) to extract version information with hierarchical structure. This function discovers transitive vendor dependencies at any nesting depth.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target_path` | `str` or `Path` | Yes | N/A | Absolute or relative path to the target project directory |
| `vendor_dir` | `str` | No | `"_vendor"` | Name of the vendor subdirectory (default: `_vendor`) |
| `version_tag` | `str` | No | `"__version__"` | Version variable name to search for |
| `depth` | `int` | No | `0` | Current nesting depth (internal use for recursion) |
| `parent_package` | `str` | No | `None` | Name of parent package (internal use for recursion) |

#### Return Value - NestedVersionInfo Structure

```python
{
    'package_name': str,                      # Name of the package
    'version': str | None,                    # Version string or None if not found
    'depth': int,                             # Nesting depth (0=top-level, 1+=nested)
    'parent_package': str | None,             # Name of parent package containing this vendor
    'nested_packages': list[NestedVersionInfo]  # Recursively nested packages
}
```

#### Example Result Structure

```python
versions = scan_vendor_packages_nested("/path/to/project")

# Result:
[
    {
        'package_name': 'library_a',
        'version': '1.0.0',
        'depth': 0,
        'parent_package': None,
        'nested_packages': [
            {
                'package_name': 'library_b',
                'version': '2.0.0',
                'depth': 1,
                'parent_package': 'library_a',
                'nested_packages': [
                    {
                        'package_name': 'library_f',
                        'version': '3.0.0',
                        'depth': 2,
                        'parent_package': 'library_b',
                        'nested_packages': []
                    },
                    {
                        'package_name': 'library_g',
                        'version': '4.0.0',
                        'depth': 2,
                        'parent_package': 'library_b',
                        'nested_packages': []
                    }
                ]
            }
        ]
    }
]
```

#### Raises

| Exception | When |
|-----------|------|
| `ValueError` | Target path doesn't exist or vendor directory doesn't exist |

#### Usage Examples

```python
from splurge_vendor_sync.version_scanner import (
    scan_vendor_packages_nested,
    format_nested_version_output
)

# Scan nested vendors
versions = scan_vendor_packages_nested(
    target_path="/path/to/my-project/my_package"
)

# Scan with custom version tag
versions = scan_vendor_packages_nested(
    target_path="/path/to/my-project/my_package",
    version_tag="MY_VERSION"
)

# Scan with custom vendor directory
versions = scan_vendor_packages_nested(
    target_path="/path/to/my-project/my_package",
    vendor_dir="custom_vendor"
)
```

### format_nested_version_output() Function

```python
def format_nested_version_output(versions: list[NestedVersionInfo]) -> str:
```

#### Description

Formats nested version information with hierarchy visualization using indentation. Each nesting level adds 2 spaces of indentation. Missing versions are displayed as `?`.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `versions` | `list[NestedVersionInfo]` | Yes | List of nested version info dicts to format |

#### Return Value

Returns a formatted string with one package per line, indented according to nesting depth:

```
library_a 1.0.0
  library_b 2.0.0
    library_f 3.0.0
    library_g 4.0.0
library_c 1.5.0
  library_d ?
```

#### Usage Examples

```python
from splurge_vendor_sync.version_scanner import (
    scan_vendor_packages_nested,
    format_nested_version_output
)

# Scan and format
versions = scan_vendor_packages_nested("/path/to/project")
output = format_nested_version_output(versions)
print(output)

# Output:
# library_a 1.0.0
#   library_b 2.0.0
#     library_f 3.0.0
#     library_g 4.0.0

# Save to file
with open("vendor_versions.txt", "w") as f:
    f.write(format_nested_version_output(versions))

# Check specific package in output
if "  library_b 2.0.0" in output:
    print("library_b is nested under a parent package")
```

### Example: Complete Nested Scanning Workflow

```python
from splurge_vendor_sync.version_scanner import (
    scan_vendor_packages_nested,
    format_nested_version_output
)

def report_vendor_hierarchy(project_path):
    """Generate a report of all vendored packages with hierarchy."""
    try:
        # Scan nested vendors
        versions = scan_vendor_packages_nested(
            target_path=project_path
        )
        
        # Generate formatted output
        output = format_nested_version_output(versions)
        
        # Display
        print("Vendor Package Hierarchy:")
        print("=" * 50)
        print(output)
        print("=" * 50)
        
        # Optionally, analyze the structure
        def count_packages(items, total=0):
            for item in items:
                total += 1
                if item.get('nested_packages'):
                    total = count_packages(item['nested_packages'], total)
            return total
        
        total = count_packages(versions)
        print(f"\nTotal packages: {total}")
        
    except ValueError as e:
        print(f"Error: {e}")

# Usage
report_vendor_hierarchy("/path/to/project")
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
| `SplurgeVendorSyncTypeError: splurge-vendor-sync.type.type-mismatch` | Verify all parameters are correct types (Path or str) |
| `SplurgeVendorSyncValueError: splurge-vendor-sync.value.path-not-found` | Verify paths exist: `test -d /path` |
| `SplurgeVendorSyncValueError: splurge-vendor-sync.value.invalid-package` | Ensure package name is not empty |
| `SplurgeVendorSyncOSError: splurge-vendor-sync.os.permission-denied` | Check permissions: `ls -ld /path` |
| `SplurgeVendorSyncOSError: splurge-vendor-sync.os.disk-full` | Free disk space and retry |
| `SplurgeVendorSyncError: splurge-vendor-sync.sync-failed` | Check logs for specific error details |
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
