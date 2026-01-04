# Pattern: Optional Dependency Import Guard

## When to Use

When implementing features that depend on optional packages (installed via extras like `pip install pkg[extra]`), use this pattern to:

1. Check if the dependency is available at import time
2. Provide clear error messages when missing
3. Allow type hints to work without the package installed

## Implementation

```python
from typing import TYPE_CHECKING

from litestar_email.backends.base import BaseEmailBackend
from litestar_email.exceptions import EmailBackendError

if TYPE_CHECKING:
    import optional_package

    from litestar_email.config import SomeConfig

# Import guard for optional dependency
try:
    import optional_package as optional_package_module
except ImportError:
    optional_package_module = None  # type: ignore[assignment]

HAS_OPTIONAL_PACKAGE = optional_package_module is not None


class SomeBackend(BaseEmailBackend):
    __slots__ = ("_config", "_client")

    def __init__(self, config: "SomeConfig | None" = None) -> None:
        if not HAS_OPTIONAL_PACKAGE:
            msg = (
                "optional_package is required for this backend. "
                "Install with: pip install litestar-email[extra]"
            )
            raise EmailBackendError(msg)

        super().__init__()
        # ... rest of init
```

## Key Points

1. **TYPE_CHECKING block**: Import the package for type hints without runtime import
2. **Try/except with alias**: Import as `module_name_module` to avoid mypy name conflict
3. **HAS_* constant**: Set based on import success using `is not None`
4. **Clear error message**: Tell users exactly which extra to install
5. **type: ignore[assignment]**: Silence mypy warning for None assignment

## Example Files

- `src/litestar_email/backends/smtp.py` - aiosmtplib dependency
- `src/litestar_email/backends/resend.py` - httpx dependency
- `src/litestar_email/backends/sendgrid.py` - httpx dependency

## Notes

- The `# type: ignore[assignment]` is necessary because mypy sees the import as a module type, not `None`
- Using `module_module` naming convention avoids the "name already defined" mypy error
- Always check `HAS_*` at the top of `__init__()` to fail fast with a good error message
- pyright may still show warnings about optional member access - configure with `reportOptionalMemberAccess = "warning"`
