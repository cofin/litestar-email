"""Utilities for litestar-email.

This package provides utilities for dependency checking and module loading.
"""

from litestar_email.utils.dependencies import (
    OptionalDependencyFlag,
    dependency_flag,
    module_available,
    reset_dependency_cache,
)
from litestar_email.utils.module_loader import (
    ensure_aiohttp,
    ensure_aiosmtplib,
    ensure_httpx,
)

__all__ = (
    "OptionalDependencyFlag",
    "dependency_flag",
    "ensure_aiohttp",
    "ensure_aiosmtplib",
    "ensure_httpx",
    "module_available",
    "reset_dependency_cache",
)
