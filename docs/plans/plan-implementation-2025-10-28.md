# Implementation Plan: splurge-vendor-sync
**Date**: October 28, 2025  
**Status**: Planning Phase  
**Version**: 1.0

## Overview

This document provides a comprehensive, phased implementation plan for `splurge-vendor-sync`, derived from the research design document. The plan includes all development phases, testing milestones, and documentation deliverables.

---

## Phase 1: Core Infrastructure & Foundation

### 1.1 Exception Handling Setup
- [ ] Review `splurge_vendor_sync/exceptions.py` for all required exception types
- [ ] Verify all `SplurgeVendorSync*` exceptions inherit from `SplurgeVendorSyncError`
- [ ] Document exception domains in code comments
- [ ] Add docstrings with usage examples for each exception type
- [ ] **Test**: Unit tests for exception instantiation and domain mapping

### 1.2 Module Structure & Imports
- [ ] Create `splurge_vendor_sync/__init__.py` with public API exports
- [ ] Set up proper import paths for vendor dependencies:
  - [ ] `_vendor.splurge_exceptions`
  - [ ] `_vendor.splurge_safe_io`
- [ ] Verify circular dependency avoidance
- [ ] Add version string and package metadata
- [ ] **Test**: Integration test to verify all imports work correctly

### 1.3 Package Initialization
- [ ] Configure `pyproject.toml` with:
  - [ ] Entry point for CLI: `splurge-vendor-sync = splurge_vendor_sync.cli:main`
  - [ ] Required dependencies (if any external)
  - [ ] Package version and metadata
- [ ] Set up logging configuration defaults
- [ ] **Test**: Verify CLI entry point is registered

---

## Phase 2: Core Synchronization API (sync.py)

### 2.1 Core Function: sync_vendor()
- [ ] Implement `sync_vendor(source_path, target_path, package, vendor, extensions)` function signature
- [ ] Add comprehensive docstring with:
  - [ ] Parameter descriptions and types
  - [ ] Return value documentation
  - [ ] Exception documentation
  - [ ] Usage examples
- [ ] Implement function body:
  - [ ] **2.1a: Input Validation Phase**
    - [ ] Validate all parameters are strings or Path objects
    - [ ] Raise `SplurgeVendorSyncTypeError` for type violations
    - [ ] Raise `SplurgeVendorSyncValueError` for invalid values (empty strings, etc.)
    - [ ] Validate extensions list is not empty
  - [ ] **2.1b: Path Normalization & Validation Phase**
    - [ ] Use `PathValidator.get_validated_path()` for source path (must exist, readable)
    - [ ] Use `PathValidator.get_validated_path()` for target path (must exist or parent writable)
    - [ ] Construct vendor target path: `[target]/[vendor]/[package]`
    - [ ] Validate source and target are different paths
    - [ ] Catch `SplurgeSafeIoPathValidationError` and map to `SplurgeVendorSyncValueError`
  - [ ] **2.1c: Clean Phase Implementation**
    - [ ] Check if vendor target path exists
    - [ ] If exists: recursively delete all contents using `shutil.rmtree()`
    - [ ] Catch OS errors and map to `SplurgeVendorSyncOSError`
    - [ ] Track deletion statistics (files/dirs removed)
  - [ ] **2.1d: Sync Phase Implementation**
    - [ ] Parse extensions from semicolon-separated string
    - [ ] Normalize extensions to lowercase
    - [ ] Recursively traverse source package directory:
      - [ ] Skip `__pycache__` directories
      - [ ] For directories: create in target, recurse
      - [ ] For files: check extension filter, copy if match
      - [ ] Use `SafeTextFileReader` for reads
      - [ ] Use `SafeTextFileWriter` for writes (with `create_parents=True`)
      - [ ] Preserve relative path structure
    - [ ] Track sync statistics (files copied, dirs created)
  - [ ] **2.1e: Return Value**
    - [ ] Return dictionary with sync results:
      ```python
      {
          'files_removed': int,
          'files_copied': int,
          'directories_created': int,
          'status': 'success' | 'partial' | 'failed',
          'errors': list[str],
      }
      ```

### 2.2 Error Handling & Resilience
- [ ] Catch and map all `SplurgeSafeIoFileNotFoundError` → `SplurgeVendorSyncValueError`
- [ ] Catch and map all `SplurgeSafeIoPermissionError` → `SplurgeVendorSyncOSError`
- [ ] Catch and map all `SplurgeSafeIoUnicodeError` → `SplurgeVendorSyncUnicodeError`
- [ ] Catch and map all other `SplurgeSafeIoOSError` → `SplurgeVendorSyncOSError`
- [ ] Log all operations with appropriate detail levels
- [ ] Provide context in error messages (file paths, operation type)

### 2.3 Unit Tests for sync.py
- [ ] Test 1: Valid sync operation with all parameters
  - [ ] Verify clean phase removes existing files
  - [ ] Verify sync phase copies matching files
  - [ ] Verify `__pycache__` excluded
  - [ ] Verify directory structure preserved
  - [ ] Verify return statistics accurate
- [ ] Test 2: Source path doesn't exist → `SplurgeVendorSyncValueError`
- [ ] Test 3: Target path doesn't exist → `SplurgeVendorSyncValueError`
- [ ] Test 4: Permission denied on read → `SplurgeVendorSyncOSError`
- [ ] Test 5: Permission denied on write → `SplurgeVendorSyncOSError`
- [ ] Test 6: Empty package directory (no matching files) → success, 0 files copied
- [ ] Test 7: Extension filtering works correctly
- [ ] Test 8: Mixed extension cases handled consistently
- [ ] Test 9: Nested directory structures preserved
- [ ] Test 10: Unicode filename handling (if applicable)
- [ ] **Coverage Target**: > 90% code coverage for sync.py

---

## Phase 3: Main Entry Point (main.py)

### 3.1 Main Function Implementation
- [ ] Implement `main()` function (accepts parsed CLI arguments)
- [ ] Add comprehensive docstring with:
  - [ ] Parameter descriptions
  - [ ] Return value (exit code)
  - [ ] Exception documentation
- [ ] Implement function body:
  - [ ] **3.1a: Argument Preparation Phase**
    - [ ] Extract arguments from namespace/dict
    - [ ] Apply argument transformations if needed
    - [ ] Prepare for API call
  - [ ] **3.1b: Validation Phase**
    - [ ] Quick sanity checks before API call
    - [ ] Validate argument combinations
  - [ ] **3.1c: API Call Phase**
    - [ ] Call `sync_vendor()` with prepared arguments
    - [ ] Catch all `SplurgeVendorSyncError` exceptions
    - [ ] Catch unexpected exceptions, wrap as `SplurgeVendorSyncRuntimeError`
  - [ ] **3.1d: Output Formatting**
    - [ ] Format results for user display:
      - [ ] Success summary with statistics
      - [ ] Error messages with actionable guidance
      - [ ] Log level appropriate messages
    - [ ] Handle verbose flag if present (future enhancement)
  - [ ] **3.1e: Exit Code Mapping**
    - [ ] Return 0 for success
    - [ ] Return 1 for runtime errors (`SplurgeVendorSyncOSError`, etc.)
    - [ ] Return 2 for validation errors (`SplurgeVendorSyncValueError`)
    - [ ] Return 1 for unexpected errors

### 3.2 Error Reporting
- [ ] Implement consistent error message formatting
- [ ] Include exception domain in error output
- [ ] Provide actionable remediation suggestions where possible
- [ ] Log full exception traceback at DEBUG level
- [ ] Log user-friendly message at ERROR/INFO level

### 3.3 Unit Tests for main.py
- [ ] Test 1: Success path with valid arguments → exit code 0
- [ ] Test 2: Validation error from sync_vendor() → exit code 2
- [ ] Test 3: OS error from sync_vendor() → exit code 1
- [ ] Test 4: Unexpected exception → exit code 1, logged as runtime error
- [ ] Test 5: Output formatting includes statistics
- [ ] Test 6: Error messages are helpful and actionable
- [ ] **Coverage Target**: > 85% code coverage for main.py

---

## Phase 4: CLI Interface (cli.py)

### 4.1 Argument Parser Setup
- [ ] Use `argparse` module for CLI parsing
- [ ] Configure parser with description and epilog
- [ ] Add required arguments:
  - [ ] `--source` (str): Source package root path
  - [ ] `--target` (str): Target project path
  - [ ] `--package` (str): Package subdirectory name
- [ ] Add optional arguments:
  - [ ] `--vendor` (str, default=`_vendor`): Vendor directory name
  - [ ] `--ext` (str, default=`py;json;yml;yaml;ini`): File extensions
  - [ ] `--dry-run` (bool, future): Preview without executing
  - [ ] `--verbose` (bool, future): Verbose logging
  - [ ] `--help` (bool): Show help message

### 4.2 Help Text & Documentation
- [ ] Write clear, concise help text for each argument
- [ ] Include examples in epilog
- [ ] Document default values
- [ ] Document error codes and their meanings (future: in help)

### 4.3 Main Entry Point
- [ ] Implement `main()` function for CLI entry point
- [ ] Parse command-line arguments
- [ ] Call `main.main()` with parsed arguments
- [ ] Handle parse errors gracefully (argparse does this)
- [ ] Return appropriate exit codes

### 4.4 CLI Output Formatting
- [ ] Format output messages for terminal readability
- [ ] Use clear, easy-to-scan format:
  - [ ] Success messages with checkmarks
  - [ ] Error messages with clear context
  - [ ] Statistics in key=value or tabular format
- [ ] Support future: color output (optional)
- [ ] Support future: structured output (JSON, etc.)

### 4.5 Unit Tests for cli.py
- [ ] Test 1: Valid CLI invocation with all arguments → calls main() correctly
- [ ] Test 2: Missing required argument → argparse error
- [ ] Test 3: Invalid argument value → argparse error or validation error
- [ ] Test 4: Help text displays correctly (`--help` flag)
- [ ] Test 5: Exit code propagates correctly from main()
- [ ] Test 6: Long/short argument names work
- [ ] **Coverage Target**: > 80% code coverage for cli.py

---

## Phase 5: Integration Testing

### 5.1 End-to-End Scenario Tests
- [ ] **Scenario 1: Basic sync**
  - [ ] Setup: source package with mixed file types
  - [ ] Action: Run sync
  - [ ] Verify: files copied, structure preserved, exit code 0
  
- [ ] **Scenario 2: Re-sync (clean phase)**
  - [ ] Setup: previous target with old files
  - [ ] Action: Run sync again
  - [ ] Verify: old files removed, new files copied, exit code 0

- [ ] **Scenario 3: Extension filtering**
  - [ ] Setup: source with .py, .json, .txt, .pyc files
  - [ ] Action: Run sync with default extensions
  - [ ] Verify: only .py, .json, .yml, .yaml, .ini copied

- [ ] **Scenario 4: __pycache__ exclusion**
  - [ ] Setup: source with __pycache__ directories
  - [ ] Action: Run sync
  - [ ] Verify: __pycache__ not in target, exit code 0

- [ ] **Scenario 5: Error handling - source not found**
  - [ ] Setup: invalid source path
  - [ ] Action: Run sync
  - [ ] Verify: exit code 2, clear error message

- [ ] **Scenario 6: Error handling - permission denied**
  - [ ] Setup: target directory with restricted permissions
  - [ ] Action: Run sync (if runnable)
  - [ ] Verify: exit code 1, clear error message

- [ ] **Scenario 7: Large package sync**
  - [ ] Setup: source with many nested directories and files
  - [ ] Action: Run sync, measure performance
  - [ ] Verify: all files copied, exit code 0, reasonable performance

- [ ] **Scenario 8: Unicode handling**
  - [ ] Setup: source with unicode filenames (if applicable)
  - [ ] Action: Run sync
  - [ ] Verify: files copied correctly, exit code 0

### 5.2 Cross-Platform Tests
- [ ] **Windows**: Verify path handling with backslashes
- [ ] **Unix/Linux**: Verify path handling with forward slashes
- [ ] **macOS**: Verify case-insensitive filesystem handling (if applicable)

### 5.3 Regression Tests
- [ ] Ensure all Phase 1-4 tests still pass
- [ ] Verify no new errors introduced
- [ ] Check performance hasn't degraded

---

## Phase 6: Documentation

### 6.1 API Reference (docs/api/API-REFERENCE.md)
- [ ] Document `sync_vendor()` function signature
- [ ] Document all parameters and types
- [ ] Document return value structure
- [ ] Document all exceptions that can be raised
- [ ] Provide multiple usage examples:
  - [ ] Basic synchronization
  - [ ] With custom extensions
  - [ ] With custom vendor directory
  - [ ] Error handling examples
- [ ] Document best practices

### 6.2 CLI Reference (docs/cli/CLI-REFERENCE.md)
- [ ] Document command syntax
- [ ] Document each argument:
  - [ ] `--source`: description, type, required, examples
  - [ ] `--target`: description, type, required, examples
  - [ ] `--package`: description, type, required, examples
  - [ ] `--vendor`: description, type, optional, default, examples
  - [ ] `--ext`: description, type, optional, default, examples
- [ ] Provide usage examples:
  - [ ] Basic command
  - [ ] With custom extensions
  - [ ] With custom vendor directory
  - [ ] Multiple common scenarios
- [ ] Document exit codes and their meanings:
  - [ ] 0: Success
  - [ ] 1: Runtime error
  - [ ] 2: Validation error
- [ ] Document common errors and solutions

### 6.3 Comprehensive Features & Errors (docs/README-DETAILS.md)
- [ ] Overview of tool features
- [ ] Detailed explanation of each feature:
  - [ ] Clean phase
  - [ ] Sync phase
  - [ ] Extension filtering
  - [ ] Directory structure preservation
  - [ ] Exclusions (__pycache__)
- [ ] Error handling guide:
  - [ ] Exception types and domains
  - [ ] Common error scenarios
  - [ ] Troubleshooting tips
  - [ ] Debug techniques
- [ ] Performance considerations
- [ ] Security considerations
- [ ] Limitations and known issues

### 6.4 README Quick-Start (README.md updates)
- [ ] Feature summary (2-3 sentences)
- [ ] Quick-start guide:
  - [ ] Installation instructions
  - [ ] Basic usage example
  - [ ] Expected output
- [ ] Link to detailed documentation
- [ ] Link to API reference
- [ ] Link to CLI reference

### 6.5 Code Documentation
- [ ] Docstrings on all public functions
- [ ] Module-level docstrings
- [ ] Type hints on all functions
- [ ] Inline comments for complex logic
- [ ] Document exception mapping strategy

---

## Phase 7: Testing & Quality Assurance

### 7.1 Unit Test Coverage
- [ ] exceptions.py: > 80% coverage (simple module)
- [ ] sync.py: > 90% coverage (core logic)
- [ ] main.py: > 85% coverage (entry point wrapper)
- [ ] cli.py: > 80% coverage (argument parsing)
- [ ] **Overall Target**: > 85% project coverage

### 7.2 Code Quality
- [ ] Run `pylint` on all Python files
- [ ] Run `black` for code formatting
- [ ] Run `mypy` for type checking
- [ ] Fix all issues and warnings
- [ ] Set up pre-commit hooks (future)

### 7.3 Performance Testing
- [ ] Benchmark sync on various package sizes:
  - [ ] Small: < 50 files
  - [ ] Medium: 50-500 files
  - [ ] Large: 500+ files
- [ ] Document performance baseline
- [ ] Identify and document any bottlenecks

### 7.4 Security Testing
- [ ] Verify path traversal attacks are prevented by PathValidator
- [ ] Test with malicious path inputs
- [ ] Verify no arbitrary file execution
- [ ] Test with unusual character filenames

### 7.5 Manual Testing Checklist
- [ ] Install package from source
- [ ] Run basic sync operation
- [ ] Run with custom vendor directory
- [ ] Run with custom extensions
- [ ] Trigger each error scenario manually
- [ ] Verify help text displays correctly
- [ ] Test on both Windows and Unix (if possible)

---

## Phase 8: Release Preparation

### 8.1 Versioning & Changelog
- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with all changes
- [ ] Tag release in git

### 8.2 Package Distribution
- [ ] Build distribution packages:
  - [ ] Source distribution (sdist)
  - [ ] Wheel distribution
- [ ] Verify packages contain all necessary files
- [ ] Test installation from distribution

### 8.3 Final Documentation Review
- [ ] Verify all docs are up-to-date
- [ ] Check for broken links
- [ ] Verify examples work (if testable)
- [ ] Proofread for clarity and accuracy

### 8.4 Release Announcement
- [ ] Write release notes
- [ ] Update documentation index if needed
- [ ] Prepare any announcements

---

## Phase 9: Future Enhancements (Post-Release)

### 9.1 Dry-Run Mode
- [ ] Add `--dry-run` flag to CLI
- [ ] Implement dry-run logic in sync_vendor()
- [ ] Output preview of changes without executing
- [ ] Tests for dry-run mode

### 9.2 Backup Support
- [ ] Add `--backup` flag to CLI
- [ ] Create backup of target before clean phase
- [ ] Document backup location and format
- [ ] Tests for backup creation and restoration

### 9.3 Confirmation Prompts
- [ ] Add `--confirm` flag to CLI
- [ ] Require user confirmation before destructive operations
- [ ] Tests for confirmation prompts

### 9.4 Verbose Logging
- [ ] Add `--verbose` flag to CLI
- [ ] Implement detailed logging
- [ ] Document logging output
- [ ] Tests for verbose mode

### 9.5 Exclude Patterns
- [ ] Add `--exclude` flag to CLI
- [ ] Implement glob pattern exclusion
- [ ] Document exclude syntax
- [ ] Tests for exclusion patterns

### 9.6 Additional Features
- [ ] Watch mode for auto-sync on changes
- [ ] Config file support
- [ ] Checksum verification
- [ ] Parallel copying for performance
- [ ] Structured output (JSON, etc.)

---

## Timeline & Milestones

| Phase | Duration | Target Completion |
|-------|----------|------------------|
| Phase 1-2 | 1-2 weeks | Core API complete |
| Phase 3-4 | 1-2 weeks | CLI complete |
| Phase 5 | 1 week | Integration tests pass |
| Phase 6 | 1 week | Documentation complete |
| Phase 7 | 1 week | QA testing complete |
| Phase 8 | 1 week | Release ready |
| **Total** | **6-8 weeks** | **Ready for release** |

---

## Dependencies & Prerequisites

- Python 3.8+
- `splurge_exceptions` (vendored)
- `splurge_safe_io` (vendored)
- Testing: `pytest`, `pytest-cov`
- Code quality: `black`, `pylint`, `mypy`
- Documentation: Markdown

---

## Success Criteria for Release

- [ ] All Phase 1-5 tasks completed
- [ ] All tests passing (unit, integration, manual)
- [ ] Code coverage > 85%
- [ ] All code quality checks passing
- [ ] All documentation complete and reviewed
- [ ] Performance acceptable (< 1s for typical 100-file package)
- [ ] No known bugs or limitations
- [ ] Package successfully installable via pip

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Complex error handling | Comprehensive error mapping tests |
| Path traversal vulnerabilities | Rely on PathValidator, test with malicious inputs |
| Large package performance | Benchmark early, optimize if needed |
| Cross-platform issues | Test on Windows and Unix during Phase 5 |
| Documentation gaps | Comprehensive doc review in Phase 6 |
| Missed requirements | Regular alignment with research doc |

---

## Notes & Assumptions

- Assumes `splurge_exceptions` and `splurge_safe_io` are stable and tested
- Assumes Python 3.8+ is available
- Assumes file extension matching is case-insensitive for implementation
- Assumes typical packages < 10,000 files (performance not critical for larger packages)
- Dry-run mode deferred to Phase 9 for MVP release

---

**Plan Status**: Ready for Implementation  
**Next Steps**: Begin Phase 1 tasks  
**Contact**: @jim-schilling for clarifications
