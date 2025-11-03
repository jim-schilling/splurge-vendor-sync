# splurge-vendor-sync

[![PyPI version](https://badge.fury.io/py/splurge-vendor-sync.svg)](https://pypi.org/project/splurge-vendor-sync/)
[![Python versions](https://img.shields.io/pypi/pyversions/splurge-vendor-sync.svg)](https://pypi.org/project/splurge-vendor-sync/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

[![CI](https://github.com/jim-schilling/splurge-vendor-sync/actions/workflows/ci-quick-test.yml/badge.svg)](https://github.com/jim-schilling/splurge-vendor-sync/actions/workflows/ci-quick-test.yml)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen.svg)](https://github.com/jim-schilling/splurge-vendor-sync)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-black)](https://mypy-lang.org/)

[![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](https://jim-schilling.github.io/splurge-vendor-sync/)

A powerful CLI tool for one-way vendor synchronization of Python libraries and applications. Automatically synchronize internal package dependencies into your project's vendor directory with selective file filtering and automatic cleanup.

## Features

- **One-way synchronization**: Clean removal and fresh copy of vendor packages
- **Selective file filtering**: Include only the file types you need (default: `.py`, `.json`, `.yml`, `.yaml`, `.ini`)
- **Automatic cleanup**: Removes outdated vendor files before syncing new ones
- **Exclusion support**: Automatically excludes `__pycache__` and other build artifacts
- **Version scanning**: Scan vendored packages to extract version information with `--scan`
  - Recursive nested vendor discovery: Detects transitive vendor dependencies at any depth
  - Hierarchical output: Shows parent-child relationships between vendored packages
  - Custom version tags: Search for `__version__` or custom version variable names
- **Cross-platform**: Works on Windows, Linux, and macOS
- **Safe I/O**: Uses deterministic newline normalization and secure path validation
- **Clear error reporting**: Domain-based exception hierarchy with actionable error messages

## Quick Start

### Installation

```bash
# From source
pip install -e .

# Or after packaging
pip install splurge-vendor-sync
```

### Basic Usage

Synchronize a source package to your project's vendor directory:

```bash
splurge-vendor-sync \
  --source /path/to/splurge-vendor-sync \
  --package splurge_exceptions \
  --target /path/to/my-project/my_project
```

This will:
1. Remove all existing files from `/path/to/my-project/my_project/_vendor/splurge_exceptions/`
2. Copy all `.py`, `.json`, `.yml`, `.yaml`, `.ini` files from the source package
3. Preserve the directory structure
4. Exclude `__pycache__` directories

### With Custom Extensions

```bash
splurge-vendor-sync \
  --source /path/to/splurge-vendor-sync \
  --package splurge_exceptions \
  --target /path/to/my-project/my_project \
  --ext "py;json;yaml"
```

### With Custom Vendor Directory

```bash
splurge-vendor-sync \
  --source /path/to/splurge-vendor-sync \
  --package splurge_exceptions \
  --target /path/to/my-project/my_project \
  --vendor "_vendored"
```

### Scan Vendored Packages

```bash
# Scan for __version__ in all vendored packages (including nested vendors)
splurge-vendor-sync \
  --target /path/to/my-project/my_project \
  --scan

# Scan with custom version tag
splurge-vendor-sync \
  --target /path/to/my-project/my_project \
  --scan MY_VERSION

# Scan with custom vendor directory
splurge-vendor-sync \
  --target /path/to/my-project/my_project \
  --vendor custom_vendor \
  --scan
```

**Scan Output with Nested Vendors:**

The scanner displays hierarchical relationships when vendors are nested:

```
library-a 1.0.0
  library-b 2.0.0
    library-f 3.0.0
    library-g 4.0.0
```

This shows that `library-b` is vendored under `library-a`, and both `library-f` and `library-g` are vendored under `library-b`.

## Documentation

- **[CLI Reference](docs/cli/CLI-REFERENCE.md)**: Complete command-line interface documentation with examples
- **[API Reference](docs/api/API-REFERENCE.md)**: Complete Python API reference for programmatic use
- **[Features & Errors](docs/README-DETAILS.md)**: Comprehensive guide to features, error handling, and troubleshooting

## Exit Codes

- `0`: Synchronization completed successfully
- `1`: Runtime error (I/O failure, permission denied, etc.)
- `2`: Validation error (invalid paths, missing arguments, etc.)

## Common Scenarios

### Sync after updating source package

```bash
# Re-run the same command - old files are automatically removed
splurge-vendor-sync \
  --source /path/to/splurge-vendor-sync \
  --package splurge_exceptions \
  --target /path/to/my-project/my_project
```

### Sync multiple packages

```bash
# Create a script to sync all your vendored dependencies
splurge-vendor-sync --source /path/to/splurge-vendor-sync --package splurge_exceptions --target /path/to/my-project/my_project
splurge-vendor-sync --source /path/to/splurge-safe-io --package splurge_safe_io --target /path/to/my-project/my_project
```

### Troubleshooting

**Q: "File not found" error**  
A: Verify the `--source` and `--target` paths exist and the `--package` directory name is correct.

**Q: "Permission denied" error**  
A: Ensure you have write permissions to the target directory.

**Q: Files not being copied**  
A: Check that the file extensions match your `--ext` parameter (default: `py;json;yml;yaml;ini`)

For more help, see [Features & Errors](docs/README-DETAILS.md).

## Development

### Running Tests

```bash
pytest tests/
pytest --cov=splurge_vendor_sync tests/
```

### Code Quality

```bash
ruff .
mypy .
```

## License

See [LICENSE](LICENSE) for details.

