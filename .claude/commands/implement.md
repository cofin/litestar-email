---
description: Pattern-guided implementation with quality checks
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, WebSearch, mcp__context7__resolve-library-id, mcp__context7__query-docs, mcp__pal__thinkdeep, mcp__pal__debug
---

# Pattern-Guided Implementation Workflow

You are implementing the feature: **$ARGUMENTS**

## Pre-Implementation Intelligence

1. **Load PRD**: Read `specs/active/{slug}/prd.md`
2. **Load Patterns**: Read similar implementations identified in PRD
3. **Load Tasks**: Read `specs/active/{slug}/tasks.md`
4. **Load Recovery**: Check `specs/active/{slug}/recovery.md` for session state

## Critical Rules

1. **FOLLOW PATTERNS** - Match existing code style exactly
2. **NO OVER-ENGINEERING** - Only implement what's in the PRD
3. **TEST AS YOU GO** - Run tests after each significant change
4. **UPDATE PROGRESS** - Mark tasks complete in `tasks.md`
5. **DOCUMENT DEVIATIONS** - If patterns must be broken, document why

---

## Code Standards (MANDATORY)

### Python Style

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from litestar_email.message import EmailMessage

__all__ = ("MyBackend",)


class MyBackend(BaseEmailBackend):
    """Backend description.

    Google-style docstring with description.

    Attributes:
        attr_name: Description of attribute.
    """

    __slots__ = ("attr_name",)

    def __init__(self, fail_silently: bool = False, attr_name: str = "") -> None:
        """Initialize the backend.

        Args:
            fail_silently: If True, suppress exceptions.
            attr_name: Description.
        """
        super().__init__(fail_silently=fail_silently)
        self.attr_name = attr_name

    async def send_messages(self, messages: list["EmailMessage"]) -> int:
        """Send email messages.

        Args:
            messages: List of messages to send.

        Returns:
            Number of messages sent successfully.
        """
        sent_count = 0
        for message in messages:
            # Implementation
            sent_count += 1
        return sent_count
```

### Anti-Patterns (NEVER DO)

```python
# BAD - Don't use Optional
from typing import Optional
def foo(x: Optional[str]) -> None: ...

# GOOD - Use PEP 604
def foo(x: str | None) -> None: ...

# BAD - Don't use future annotations
from __future__ import annotations

# GOOD - Use TYPE_CHECKING and stringified types
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from litestar_email import EmailConfig

def foo(config: "EmailConfig") -> None: ...

# BAD - No relative imports
from ..config import EmailConfig

# GOOD - Absolute imports only
from litestar_email.config import EmailConfig
```

---

## Checkpoint 1: Load Context

1. Read PRD and extract requirements
2. Read similar implementations
3. Identify files to create/modify

**Output**: "✓ Checkpoint 1 - Context loaded, [N] files to modify"

---

## Checkpoint 2: Implement Core Logic

For each file in the implementation plan:

1. **Read existing patterns** in related files
2. **Write code** following exact style
3. **Add `__slots__`** to all classes
4. **Use TYPE_CHECKING** for type-only imports

**Output**: "✓ Checkpoint 2 - Core implementation complete"

---

## Checkpoint 3: Register Backend (if applicable)

```python
# In src/litestar_email/backends/__init__.py
from litestar_email.backends.my_backend import MyBackend

# Add to registry
register_backend("my_backend", MyBackend)

# Add to __all__
__all__ = (
    ...,
    "MyBackend",
)
```

**Output**: "✓ Checkpoint 3 - Backend registered"

---

## Checkpoint 4: Update Exports

```python
# In src/litestar_email/__init__.py
from litestar_email.backends import MyBackend

__all__ = (
    ...,
    "MyBackend",
)
```

**Output**: "✓ Checkpoint 4 - Exports updated"

---

## Checkpoint 5: Run Tests

```bash
# Run existing tests to ensure no regressions
make test

# Run linting
make lint
```

**Fix any failures before proceeding.**

**Output**: "✓ Checkpoint 5 - Tests pass, linting clean"

---

## Checkpoint 6: Update Progress

Update `specs/active/{slug}/tasks.md` with completed items.

**Output**: "✓ Checkpoint 6 - Progress updated"

---

## Checkpoint 7: Auto-Invoke Testing

Invoke the testing agent:

```
Task(subagent_type="testing", prompt="Write tests for {slug} feature following specs/active/{slug}/prd.md")
```

**Output**: "✓ Checkpoint 7 - Testing agent invoked"

---

## Final Summary

```
Implementation Phase Complete ✓

Files Modified:
- src/litestar_email/backends/{file}.py
- src/litestar_email/backends/__init__.py
- src/litestar_email/__init__.py

Quality Checks:
- ✓ Tests passing
- ✓ Linting clean
- ✓ Pattern compliance verified

Next: Tests will run via `/test {slug}` or review via `/review {slug}`
```
