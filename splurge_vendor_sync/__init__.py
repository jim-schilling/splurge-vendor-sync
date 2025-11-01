"""splurge-vendor-sync: Vendor synchronization tool.

A utility for synchronizing vendor packages into a project's vendor directory
with support for extension filtering, clean/sync phases, and comprehensive error handling.
"""

from .cli import main as cli_main
from .exceptions import (
    SplurgeVendorSyncError,
    SplurgeVendorSyncOSError,
    SplurgeVendorSyncRuntimeError,
    SplurgeVendorSyncTypeError,
    SplurgeVendorSyncUnicodeError,
    SplurgeVendorSyncValueError,
)
from .main import main
from .sync import sync_vendor

__version__ = "2025.1.2"

__all__ = [
    "__version__",
    "cli_main",
    "main",
    "sync_vendor",
    "SplurgeVendorSyncError",
    "SplurgeVendorSyncOSError",
    "SplurgeVendorSyncRuntimeError",
    "SplurgeVendorSyncTypeError",
    "SplurgeVendorSyncUnicodeError",
    "SplurgeVendorSyncValueError",
]
