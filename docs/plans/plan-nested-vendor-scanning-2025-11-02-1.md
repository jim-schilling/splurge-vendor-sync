# Plan: Nested Vendor Package Scanning

## Overview
Update the version scanner to support recursive scanning of nested vendor directories, enabling visibility into transitive vendor dependencies.

## Requirements
1. Scan nested `_vendor` directories recursively (e.g., `_vendor/library-b/_vendor/library-f`)
2. Display package hierarchy showing parent-child relationships
3. Show package name, version, and nesting depth
4. Maintain backward compatibility with existing output format when no nested vendors exist

## Data Structure Changes

### Current VersionInfo
```python
class VersionInfo(TypedDict):
    package_name: str
    version: str | None
```

### Proposed NestedVersionInfo
```python
class NestedVersionInfo(TypedDict):
    package_name: str
    version: str | None
    depth: int  # 0 for top-level, 1 for first level nested, etc.
    parent: str | None  # Name of parent package (e.g., "library-b")
    nested_packages: list[NestedVersionInfo]  # Recursively nested packages
```

## Implementation Stages

### Stage 1: Update Data Structures
- Add depth tracking to version info
- Create hierarchical structure for nested packages
- Maintain backward compatibility

### Stage 2: Implement Recursive Scanning
- Modify `scan_vendor_packages()` to recursively traverse nested `_vendor` directories
- Collect hierarchy information
- Return nested structure

### Stage 3: Update Output Formatting
- Modify `format_version_output()` to display hierarchy
- Use indentation to show nesting levels
- Example output:
  ```
  library-a 1.0.0
    library-b 2.0.0
      library-f 3.0.0
      library-g 4.0.0
  ```

### Stage 4: Testing
- Add unit tests for nested vendor scanning
- Add integration tests to verify end-to-end functionality
- Verify existing tests still pass

## Example Structure
```
project/
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

## Acceptance Criteria
1. Nested packages at any depth are discovered and scanned
2. Hierarchy is clearly displayed in output
3. Versions are correctly extracted from nested packages
4. All existing tests pass
5. New functionality covered by unit and integration tests
6. Performance is acceptable (no deep recursion issues)
