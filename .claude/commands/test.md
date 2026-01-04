---
description: Testing with 90%+ coverage and pattern compliance
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, mcp__context7__query-docs
---

# Testing Workflow

You are writing tests for: **$ARGUMENTS**

## Pre-Testing Intelligence

1. **Load PRD**: Read `specs/active/{slug}/prd.md` for acceptance criteria
2. **Load Existing Tests**: Study `src/tests/` for patterns
3. **Load Implementation**: Read the new code to test

## Critical Rules

1. **90%+ COVERAGE** - Target for modified modules
2. **FUNCTION-BASED** - No class-based tests
3. **ASYNC TESTS** - Use `pytest.mark.anyio`
4. **ISOLATION** - Tests must work in parallel
5. **FOLLOW PATTERNS** - Match existing test style

---

## Test File Template

```python
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from litestar import Litestar

    from litestar_email import EmailConfig, EmailPlugin

pytestmark = pytest.mark.anyio


async def test_feature_basic_functionality(email_config: "EmailConfig") -> None:
    """Test that feature works with default configuration."""
    from litestar_email import EmailMessage, MyBackend

    backend = MyBackend()
    message = EmailMessage(
        subject="Test",
        body="Test body",
        to=["test@example.com"],
    )

    async with backend:
        sent = await backend.send_messages([message])

    assert sent == 1


async def test_feature_edge_case() -> None:
    """Test edge case handling."""
    from litestar_email import MyBackend

    backend = MyBackend()

    async with backend:
        sent = await backend.send_messages([])

    assert sent == 0


async def test_feature_error_handling() -> None:
    """Test error handling when fail_silently is False."""
    from litestar_email import MyBackend

    backend = MyBackend(fail_silently=False)
    # Test that appropriate errors are raised


async def test_feature_with_app(app: "Litestar") -> None:
    """Test feature integration with Litestar app."""
    # Integration test using app fixture
    pass
```

---

## Checkpoint 1: Analyze Coverage Requirements

1. Identify all code paths in new implementation
2. List edge cases from PRD acceptance criteria
3. Plan test cases for 90%+ coverage

**Output**: "✓ Checkpoint 1 - [N] test cases planned"

---

## Checkpoint 2: Write Unit Tests

Write tests in `src/tests/test_{module}.py`:

1. Happy path tests
2. Edge case tests
3. Error handling tests
4. Configuration variation tests

**Output**: "✓ Checkpoint 2 - Unit tests written"

---

## Checkpoint 3: Write Integration Tests

If applicable, write integration tests:

1. Plugin integration with Litestar app
2. Backend registration tests
3. Full message flow tests

**Output**: "✓ Checkpoint 3 - Integration tests written"

---

## Checkpoint 4: Run Tests with Coverage

```bash
# Run tests with coverage
make coverage

# Check coverage percentage
uv run coverage report --include="src/litestar_email/{module}.py"
```

**Target**: 90%+ coverage for modified modules

**Output**: "✓ Checkpoint 4 - Coverage: [X]%"

---

## Checkpoint 5: Fix Coverage Gaps

If coverage < 90%:

1. Identify uncovered lines
2. Add tests for uncovered code paths
3. Re-run coverage check

**Output**: "✓ Checkpoint 5 - Coverage gaps addressed"

---

## Checkpoint 6: Verify All Tests Pass

```bash
# Final test run
make test

# Verify no regressions
make lint
```

**Output**: "✓ Checkpoint 6 - All tests passing"

---

## Final Summary

```
Testing Phase Complete ✓

Test Files:
- src/tests/test_{module}.py

Coverage:
- Modified modules: [X]%
- Overall: [Y]%

Test Count:
- Unit tests: [N]
- Integration tests: [M]

Next: Run `/review {slug}` for quality gate
```
