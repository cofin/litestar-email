# AI Agent Guidelines for litestar-email

**Version**: 2.0 (Intelligent Edition) | **Updated**: 2025-12-16

This is **litestar-email**, an official Litestar plugin that provides helpers for sending email within a Litestar application.

---

## Intelligence Layer

This project uses an **intelligent agent system** that:

1. **Learns from codebase** before making changes
2. **Adapts workflow depth** based on feature complexity
3. **Accumulates knowledge** in pattern library
4. **Selects tools** based on task requirements

### Complexity-Based Checkpoints

| Complexity | Checkpoints | Triggers |
|------------|-------------|----------|
| Simple | 6 | CRUD, config change, single file |
| Medium | 8 | New service, API endpoint, 2-3 files |
| Complex | 10+ | Architecture change, multi-component |

---

## Quick Reference

### Technology Stack

| Category | Tool |
|----------|------|
| Framework | Litestar 2.0+ |
| Testing | pytest + anyio |
| Linting | ruff |
| Type Checking | mypy + pyright |
| Package Manager | uv |
| Build Backend | hatchling |

### Essential Commands

```bash
make install       # Install all dependencies
make test          # Run all tests
make lint          # Run linting (pre-commit + type-check + slotscheck)
make fix           # Auto-format code
make check-all     # Run all checks (lint + test + coverage)
make coverage      # Run tests with coverage report
```

---

## Code Standards (Critical)

### Python

| Rule | Standard |
|------|----------|
| Type hints | PEP 604 (`T \| None`, NOT `Optional[T]`) |
| Future imports | Do **not** use `from __future__ import annotations` |
| Docstrings | Google style |
| Tests | Function-based, `pytest.mark.anyio` |
| Line length | 120 characters |
| Imports | Absolute only (relative imports banned) |
| Classes | Must define `__slots__` |

### Required File Header

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Type-only imports here
    pass
```

### Typing Notes

- Use stringified annotations (e.g. `"Litestar"` / `"EmailConfig"`) when referencing types that are only imported
  under `TYPE_CHECKING`.

---

## Slash Commands

| Command | Description |
|---------|-------------|
| `/prd [feature]` | Create PRD with pattern learning |
| `/implement [slug]` | Pattern-guided implementation |
| `/test [slug]` | Testing with 90%+ coverage |
| `/review [slug]` | Quality gate and pattern extraction |
| `/explore [topic]` | Explore codebase |
| `/fix-issue [#]` | Fix GitHub issue |
| `/bootstrap` | Re-bootstrap (alignment mode) |

---

## Subagents

| Agent | Mission |
|-------|---------|
| `prd` | PRD creation with pattern recognition |
| `expert` | Implementation with pattern compliance |
| `testing` | Test creation (90%+ coverage) |
| `docs-vision` | Quality gates and pattern extraction |

---

## Project Structure

```
src/litestar_email/
├── __init__.py           # Public exports
├── config.py             # EmailConfig dataclass
├── plugin.py             # EmailPlugin (InitPluginProtocol)
├── message.py            # EmailMessage, EmailMultiAlternatives
├── backends/
│   ├── __init__.py       # Backend registry & get_backend()
│   ├── base.py           # BaseEmailBackend ABC
│   ├── console.py        # ConsoleBackend (development)
│   └── memory.py         # InMemoryBackend (testing)
└── py.typed              # PEP 561 marker

src/tests/
├── conftest.py           # Test fixtures
├── test_plugin.py        # Plugin tests
├── test_message.py       # Message tests
└── test_backends.py      # Backend tests

.claude/
├── commands/        # Slash commands
├── agents/          # Subagent definitions
├── skills/          # Framework skills
└── mcp-strategy.md  # MCP tool selection guide
```

---

## Development Workflow

### For New Features (Pattern-First)

1. **PRD**: `/prd [feature]` - Analyzes similar features first
2. **Implement**: `/implement [slug]` - Follows identified patterns
3. **Test**: Auto-invoked - Tests pattern compliance
4. **Review**: Auto-invoked - Extracts new patterns to library

### Quality Gates

All code must pass:

- [ ] `make test` passes
- [ ] `make lint` passes
- [ ] 90%+ coverage for modified modules
- [ ] Pattern compliance verified
- [ ] No anti-patterns

---

## MCP Tools

### Tool Selection Guide

See `.claude/mcp-strategy.md` for detailed tool selection.

### Context7 (Litestar Docs)

```python
mcp__context7__resolve-library-id(libraryName="litestar")
mcp__context7__get-library-docs(
    context7CompatibleLibraryID="/litestar-org/litestar",
    topic="plugins",  # or: websocket, routing, testing
    mode="code"
)
```

### Sequential Thinking (Analysis)

```python
mcp__sequential-thinking__sequentialthinking(
    thought="Step 1: Analyze the plugin structure...",
    thought_number=1,
    total_thoughts=12,
    next_thought_needed=True
)
```

### Pal Tools

- `mcp__pal__planner` - Multi-phase planning
- `mcp__pal__thinkdeep` - Deep analysis
- `mcp__pal__analyze` - Code analysis
- `mcp__pal__debug` - Debugging

---

## Anti-Patterns (Must Avoid)

| Pattern | Issue | Fix |
|---------|-------|-----|
| `Optional[T]` | Old style | Use `T \| None` |
| `from typing import Optional` | Unnecessary | Remove import |
| `from ..` | Relative import | Use absolute import |
| Missing `__slots__` | Memory waste | Add `__slots__` to classes |
| Class-based tests | Not preferred | Use function-based tests |
| `from __future__ import annotations` | Disallowed | Remove it; use stringified annotations + `TYPE_CHECKING` imports |

---

## Architecture

The plugin follows the standard Litestar plugin pattern with a pluggable backend system:

```
Litestar App
    │
    ├── EmailPlugin (InitPluginProtocol)
    │       │
    │       └── EmailConfig
    │
    └── Backends
            ├── ConsoleBackend (development)
            ├── InMemoryBackend (testing)
            ├── [Future: SMTPBackend]
            ├── [Future: SendGridBackend]
            └── [Future: ResendBackend]
```

### Integration Points

- `on_app_init()` - App initialization hook
- Backend registry via `@register_backend` decorator
- Factory function `get_backend()` for instantiation

---

## Testing

### Test Pattern

```python
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from litestar import Litestar
    from litestar_email import EmailConfig, EmailPlugin

pytestmark = pytest.mark.anyio


def test_feature(app: "Litestar", email_config: "EmailConfig") -> None:
    """Test description."""
    from litestar_email import EmailMessage

    message = EmailMessage(subject="Test", body="Body", to=["test@example.com"])
    assert message.subject == "Test"
```

### Available Fixtures (conftest.py)

- `anyio_backend` - Returns "asyncio"
- `email_config` - Test configuration
- `email_plugin` - Plugin instance
- `app` - Litestar app with plugin

### Testing with InMemoryBackend

```python
from litestar_email.backends import InMemoryBackend

def test_sends_email():
    InMemoryBackend.clear()
    # ... code that sends email ...
    assert len(InMemoryBackend.outbox) == 1
```

---

## Resources

- **Litestar Docs**: <https://docs.litestar.dev/>
