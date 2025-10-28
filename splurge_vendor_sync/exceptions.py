"""Custom exceptions for the vendor synchronization tool."""

from ._vendor.splurge_exceptions.core.exceptions import SplurgeFrameworkError


class SplurgeVendorSyncError(SplurgeFrameworkError):
    """Base exception for the vendor synchronization tool.

    Attributes:
        _domain (str): "splurge.vendor_sync"
    """

    _domain = "splurge.vendor_sync"


class SplurgeVendorSyncTypeError(SplurgeVendorSyncError):
    """Error for type-related issues in vendor synchronization.

    Attributes:
        _domain (str): "splurge.vendor_sync.type"
    """

    _domain = "splurge.vendor_sync.type"


class SplurgeVendorSyncValueError(SplurgeVendorSyncError):
    """Error for value-related issues in vendor synchronization.

    Attributes:
        _domain (str): "splurge.vendor_sync.value"
    """

    _domain = "splurge.vendor_sync.value"


class SplurgeVendorSyncOSError(SplurgeVendorSyncError):
    """Error for OS and I/O issues in vendor synchronization.

    Attributes:
        _domain (str): "splurge.vendor_sync.os"
    """

    _domain = "splurge.vendor_sync.os"


class SplurgeVendorSyncRuntimeError(SplurgeVendorSyncError):
    """Error for runtime issues in vendor synchronization.

    Attributes:
        _domain (str): "splurge.vendor_sync.runtime"
    """

    _domain = "splurge.vendor_sync.runtime"


class SplurgeVendorSyncUnicodeError(SplurgeVendorSyncError):
    """Error for Unicode-related issues in vendor synchronization.

    Attributes:
        _domain (str): "splurge.vendor_sync.unicode"
    """

    _domain = "splurge.vendor_sync.unicode"
