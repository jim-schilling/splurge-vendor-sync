"""Core exception types used by the splurge-exceptions framework.

This module re-exports the central exception classes that downstream
libraries and applications should import. Each exception class provides a
predefined `_domain` that is used to construct full, hierarchical error codes.

Examples:

    from splurge_exceptions.core import SplurgeValueError

    raise SplurgeValueError("Invalid input", error_code="invalid")

"""

from splurge_exceptions.core.base import SplurgeError
from splurge_exceptions.core.exceptions import (
    SplurgeFrameworkError,
    SplurgeLookupError,
    SplurgeOSError,
    SplurgeRuntimeError,
    SplurgeTypeError,
    SplurgeValueError,
)

__all__ = [
    "SplurgeError",
    "SplurgeValueError",
    "SplurgeOSError",
    "SplurgeLookupError",
    "SplurgeRuntimeError",
    "SplurgeTypeError",
    "SplurgeFrameworkError",
]
