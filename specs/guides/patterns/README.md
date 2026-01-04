# Pattern Library

This directory contains reusable patterns extracted from completed features in litestar-email.

## How Patterns Are Captured

1. During implementation, new patterns are documented in `specs/active/{slug}/tmp/new-patterns.md`
2. During review phase, patterns are extracted to this directory
3. Future PRD phases consult this library first

## Pattern Categories

### Architectural Patterns

| Pattern | Description | Example File |
|---------|-------------|--------------|
| Backend Registry | Pluggable backend system with decorator registration | `backends/__init__.py` |
| Plugin Protocol | Litestar InitPluginProtocol implementation | `plugin.py` |
| Async Context Manager | Backend connection lifecycle management | `backends/base.py` |

### Type Handling Patterns

| Pattern | Description |
|---------|-------------|
| TYPE_CHECKING Guard | Import types under `if TYPE_CHECKING:` block |
| Stringified Annotations | Use `"TypeName"` for forward references |
| PEP 604 Unions | Use `T \| None` instead of `Optional[T]` |

### Testing Patterns

| Pattern | Description | Example File |
|---------|-------------|--------------|
| Async Function Tests | Use `pytest.mark.anyio` with async functions | `conftest.py` |
| Memory Backend Testing | Clear and check `InMemoryBackend.outbox` | `test_backends.py` |
| Fixture Chain | `anyio_backend` → `email_config` → `email_plugin` → `app` | `conftest.py` |

### Error Handling Patterns

| Pattern | Description |
|---------|-------------|
| fail_silently Flag | Suppress exceptions when `fail_silently=True` |
| Graceful Degradation | Return 0 sent count on failure instead of raising |

## Using Patterns

When starting a new feature:

1. **Search this directory** for similar patterns
2. **Read pattern documentation** before implementation
3. **Follow established conventions** exactly
4. **Add new patterns** during review phase if discovered

## Adding Patterns

When you discover a new reusable pattern:

1. Create `{pattern-name}.md` in this directory
2. Follow the template below
3. Update this README with the new pattern

### Pattern Template

```markdown
# Pattern: [Name]

## When to Use
[Description of when this pattern applies]

## Implementation

\`\`\`python
# Example code demonstrating the pattern
\`\`\`

## Example Files
- `src/litestar_email/path/to/example.py`

## Notes
- [Any gotchas or edge cases]
- [Performance considerations]
- [Related patterns]
```

## Index

### Core Patterns (Always Follow)

- **Backend Pattern**: All backends inherit from `BaseEmailBackend`
- **Plugin Pattern**: Use `InitPluginProtocol` for Litestar integration
- **Config Pattern**: Use `@dataclass(slots=True)` for configuration
- **Test Pattern**: Async function-based tests with anyio

### Optional Patterns (Use When Applicable)

- **Registry Pattern**: For pluggable component systems
- **Context Manager Pattern**: For resource lifecycle management

## Anti-Patterns (Never Use)

| Anti-Pattern | Why It's Bad | Correct Pattern |
|--------------|--------------|-----------------|
| `Optional[T]` | Old style, verbose | `T \| None` |
| `from __future__ import annotations` | Causes runtime issues | TYPE_CHECKING guard |
| Relative imports | Hard to refactor | Absolute imports |
| Class-based tests | Less flexible | Function-based tests |
| Missing `__slots__` | Memory waste | Always define `__slots__` |
