"""Runtime optional dependency detection utilities.

This module provides utilities for checking whether optional dependencies
are installed without actually importing them. Uses importlib.util.find_spec
for lightweight, cached availability checks.
"""

from importlib.util import find_spec

__all__ = (
    "OptionalDependencyFlag",
    "dependency_flag",
    "module_available",
    "reset_dependency_cache",
)

_dependency_cache: dict[str, bool] = {}


def module_available(module_name: str) -> bool:
    """Return True if the given module can be resolved.

    The result is cached per interpreter session. Call
    :func:`reset_dependency_cache` to invalidate cached entries when
    tests manipulate ``sys.path``.

    Args:
        module_name: Dotted module path to check (e.g., "httpx", "aiohttp").

    Returns:
        True if importlib can find the module, False otherwise.

    Example:
        Check if httpx is available::

            if module_available("httpx"):
                import httpx
                # use httpx
            else:
                # fallback or raise error
    """
    cached = _dependency_cache.get(module_name)
    if cached is not None:
        return cached

    try:
        is_available = find_spec(module_name) is not None
    except ModuleNotFoundError:
        is_available = False

    _dependency_cache[module_name] = is_available
    return is_available


def reset_dependency_cache(module_name: str | None = None) -> None:
    """Clear cached availability for one module or the entire cache.

    This is primarily useful in tests when manipulating sys.path
    or mocking imports.

    Args:
        module_name: Specific dotted module path to drop from the cache.
            Clears the full cache when ``None``.

    Example:
        Reset cache for testing::

            reset_dependency_cache()  # Clear all
            reset_dependency_cache("httpx")  # Clear specific module
    """
    if module_name is None:
        _dependency_cache.clear()
        return

    _dependency_cache.pop(module_name, None)


class OptionalDependencyFlag:
    """Boolean-like wrapper that evaluates module availability lazily.

    This class provides a convenient way to create module-level flags
    that evaluate lazily when used in boolean contexts.

    Example:
        Create a lazy dependency flag::

            HAS_HTTPX = OptionalDependencyFlag("httpx")

            if HAS_HTTPX:
                import httpx
                # use httpx
    """

    __slots__ = ("module_name",)

    def __init__(self, module_name: str) -> None:
        """Initialize the dependency flag.

        Args:
            module_name: The module name to check availability for.
        """
        self.module_name = module_name

    def __bool__(self) -> bool:
        """Return True if the module is available."""
        return module_available(self.module_name)

    def __repr__(self) -> str:
        """Return a string representation of the flag."""
        status = "available" if module_available(self.module_name) else "missing"
        return f"OptionalDependencyFlag(module={self.module_name!r}, status={status!r})"


def dependency_flag(module_name: str) -> OptionalDependencyFlag:
    """Return a lazily evaluated flag for the supplied module name.

    This is a convenience factory function for creating OptionalDependencyFlag
    instances.

    Args:
        module_name: Dotted module path to guard.

    Returns:
        OptionalDependencyFlag tracking the module.

    Example:
        Create dependency flags::

            HAS_AIOHTTP = dependency_flag("aiohttp")
            HAS_HTTPX = dependency_flag("httpx")
    """
    return OptionalDependencyFlag(module_name)
