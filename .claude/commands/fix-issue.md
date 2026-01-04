---
description: Fix a GitHub issue with pattern-aware implementation
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, WebFetch, mcp__pal__debug, mcp__pal__thinkdeep
---

# Fix GitHub Issue Workflow

You are fixing issue: **$ARGUMENTS**

## Pre-Fix Intelligence

1. **Fetch Issue Details**: Get issue from GitHub
2. **Understand Context**: Read related code
3. **Identify Root Cause**: Use debugging tools
4. **Plan Fix**: Minimal changes following patterns

## Critical Rules

1. **MINIMAL CHANGES** - Fix only what's needed
2. **FOLLOW PATTERNS** - Match existing code style
3. **ADD TESTS** - Test the fix
4. **NO OVER-ENGINEERING** - Don't add features

---

## Checkpoint 1: Fetch Issue

```bash
# If issue number provided
gh issue view {number} --repo litestar-org/litestar-email

# Or if URL provided
# Extract details from the issue
```

**Document:**
- Issue title
- Issue description
- Labels (bug, enhancement, etc.)
- Reproduction steps (if bug)

**Output**: "✓ Checkpoint 1 - Issue fetched"

---

## Checkpoint 2: Reproduce/Understand

For bugs:
```bash
# Try to reproduce
uv run python -c "
from litestar_email import ...
# Reproduction code
"
```

For enhancements:
- Understand the requested change
- Check if similar patterns exist

**Output**: "✓ Checkpoint 2 - Issue understood"

---

## Checkpoint 3: Root Cause Analysis

Use debugging tools:

```python
mcp__pal__debug(
    step="Investigating issue #{number}",
    step_number=1,
    total_steps=3,
    next_step_required=True,
    findings="...",
    hypothesis="..."
)
```

**Document:**
- Root cause
- Affected files
- Impact scope

**Output**: "✓ Checkpoint 3 - Root cause: [description]"

---

## Checkpoint 4: Plan Fix

Create minimal fix plan:

1. Files to modify
2. Exact changes needed
3. Tests to add

**Output**: "✓ Checkpoint 4 - Fix planned"

---

## Checkpoint 5: Implement Fix

Apply the fix following project patterns:

1. Make minimal code changes
2. Follow code standards
3. Add/update docstrings if needed

**Output**: "✓ Checkpoint 5 - Fix implemented"

---

## Checkpoint 6: Add Tests

Add tests that:

1. Reproduce the original issue (would fail before fix)
2. Verify the fix works
3. Prevent regression

```python
async def test_issue_{number}_fix() -> None:
    """Regression test for issue #{number}.

    Verifies that [description of fix].
    """
    # Test code
```

**Output**: "✓ Checkpoint 6 - Tests added"

---

## Checkpoint 7: Verify Fix

```bash
# Run all tests
make test

# Run linting
make lint

# Run coverage
make coverage
```

**Output**: "✓ Checkpoint 7 - All checks pass"

---

## Final Summary

```
Issue Fix Complete ✓

Issue: #{number} - [title]
Root Cause: [brief description]

Changes Made:
- `path/to/file.py` - [description]

Tests Added:
- `test_issue_{number}_fix`

Quality Checks:
- ✓ Tests pass
- ✓ Linting clean
- ✓ Coverage maintained

Ready for commit and PR.
```

---

## Commit Message Template

```
fix: [brief description] (#{number})

[More detailed description if needed]

Closes #{number}
```
