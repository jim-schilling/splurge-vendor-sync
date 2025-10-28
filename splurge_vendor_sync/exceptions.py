"""Custom exceptions for the vendor synchronization tool."""

from ._vendor.splurge_exceptions.core.exceptions import SplurgeFrameworkError


class SplurgeVendorSyncError(SplurgeFrameworkError):
    """Base exception for the vendor synchronization tool.

    Attributes:
        _domain (str): "splurge.vendor-sync"
    """

    _domain = "splurge.vendor-sync"


class SplurgeVendorSyncTypeError(SplurgeVendorSyncError):
    """Error for type-related issues in vendor synchronization.

    Attributes:
        _domain (str): "splurge.vendor-sync.type"
    """

    _domain = "splurge.vendor-sync.type"


class SplurgeVendorSyncValueError(SplurgeVendorSyncError):
    """Error for value-related issues in vendor synchronization.

    Attributes:
        _domain (str): "splurge.vendor-sync.value"
    """

    _domain = "splurge.vendor-sync.value"


class SplurgeVendorSyncOSError(SplurgeVendorSyncError):
    """Error for OS and I/O issues in vendor synchronization.

    Attributes:
        _domain (str): "splurge.vendor-sync.os"
    """

    _domain = "splurge.vendor-sync.os"


class SplurgeVendorSyncRuntimeError(SplurgeVendorSyncError):
    """Error for runtime issues in vendor synchronization.

    Attributes:
        _domain (str): "splurge.vendor-sync.runtime"
    """

    _domain = "splurge.vendor-sync.runtime"


class SplurgeVendorSyncUnicodeError(SplurgeVendorSyncError):
    """Error for Unicode-related issues in vendor synchronization.

    Attributes:
        _domain (str): "splurge.vendor-sync.unicode"
    """

    _domain = "splurge.vendor-sync.unicode"
