# Documentation Updates - November 1, 2025

## Summary

Updated README.md, README-DETAILS.md, and CLI-REFERENCE.md to document the new `--scan [VERSION-TAG]` CLI flag for scanning vendored packages and extracting version information.

## Changes Made

### 1. README.md Updates

**Added to Features Section:**
- New feature highlight: "**Version scanning**: Scan vendored packages to extract version information with `--scan`"

**Added New Section: "Scan Vendored Packages"**
- Three example usage patterns:
  1. Basic scan with default `__version__` tag
  2. Scan with custom version tag
  3. Scan with custom vendor directory

### 2. docs/README-DETAILS.md Updates

**Modified Core Features Section:**
- Renamed "### 2. Selective File Filtering" → "### 3. Selective File Filtering"
- Renamed "### 2. Automatic Cleanup" → "### 4. Automatic Cleanup"
- Added new "### 2. Version Scanning" feature with detailed description:
  - Extract version from Python files using AST parsing
  - Search for custom version tags
  - Check `__init__.py` first with fallback to `__main__.py`
  - Display missing versions with `?` marker
  - Support for custom vendor directories

**Added Common Scenarios:**
- Scenario 7: Scan Vendored Package Versions
- Scenario 8: Scan with Custom Version Tag

### 3. docs/cli/CLI-REFERENCE.md Updates

**Updated Basic Usage Section:**
- Added separate command signatures for Sync Mode and Scan Mode
- Added minimal and full examples for both modes
- Clarified the two operational modes

**Added --scan Flag to Arguments Reference:**
Complete documentation including:
- Type, requirement status, and default value
- Detailed description of behavior
- Usage patterns and examples
- Output format specification
- Error handling information

**Added New CLI Examples:**
- Example 9: Scan for Default Version Tag
- Example 10: Scan with Custom Version Tag
- Example 11: Scan with Custom Vendor Directory
- Example 12: Scan and Save to File
- Example 13: Scan and Parse with Bash
- Example 14: Sync and Then Verify Versions

## Documentation Coverage

The new `--scan` flag is now fully documented with:

✅ Quick-start example in README.md  
✅ Detailed feature description in README-DETAILS.md  
✅ Complete argument reference in CLI-REFERENCE.md  
✅ Multiple usage examples in CLI-REFERENCE.md  
✅ Integration examples showing scan in workflows  
✅ Error handling information  
✅ Output format specification  

## Usage Example

```bash
# Scan for __version__ in all vendored packages
splurge-vendor-sync --target /path/to/project --scan

# Output:
# splurge_exceptions 2025.3.1
# splurge_safe_io 2025.4.3
# custom_package ?
```

## Testing

All documentation updates have been verified:
- CLI help displays `--scan` flag correctly
- README.md includes scan examples
- CLI-REFERENCE.md has complete argument documentation
- README-DETAILS.md describes the feature
- All cross-references are consistent

## Files Updated

1. `README.md` - Quick-start guide
2. `docs/README-DETAILS.md` - Comprehensive features guide
3. `docs/cli/CLI-REFERENCE.md` - Complete CLI reference

## Notes

- All documentation examples have been tested and verified to work
- The scan mode is fully independent of sync mode
- Documentation covers all use cases: default tag, custom tags, custom vendor directories
- Error handling and exit codes are clearly documented
