"""splurge-vendor-sync: Vendor synchronization tool.

A utility for synchronizing vendor packages into a project's vendor directory
with support for extension filtering, clean/sync phases, and comprehensive error handling.
"""

from splurge_vendor_sync.cli import main as cli_main
from splurge_vendor_sync.exceptions import (
    SplurgeVendorSyncError,
    SplurgeVendorSyncOSError,
    SplurgeVendorSyncRuntimeError,
    SplurgeVendorSyncTypeError,
    SplurgeVendorSyncUnicodeError,
    SplurgeVendorSyncValueError,
)
from splurge_vendor_sync.main import main
from splurge_vendor_sync.sync import sync_vendor

__version__ = "2025.0.1"

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
