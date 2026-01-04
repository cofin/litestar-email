---
description: Intelligent codebase exploration with context gathering
allowed-tools: Read, Glob, Grep, Bash, Task, mcp__context7__resolve-library-id, mcp__context7__query-docs, mcp__pal__analyze
---

# Codebase Exploration

You are exploring: **$ARGUMENTS**

## Exploration Approach

Use intelligent, targeted exploration to understand the codebase.

---

## Quick Reference: Project Structure

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
```

---

## Exploration Strategies

### 1. Find Implementation Patterns

```bash
# Find all classes
grep -r "^class " src/litestar_email/

# Find all async methods
grep -r "async def" src/litestar_email/

# Find all decorators
grep -r "^@" src/litestar_email/
```

### 2. Understand Data Flow

```bash
# Find how EmailMessage is used
grep -r "EmailMessage" src/

# Find how backends are registered
grep -r "register_backend" src/

# Find plugin integration points
grep -r "on_app_init" src/
```

### 3. Check Test Coverage

```bash
# List all test files
ls src/tests/

# Find test functions for specific module
grep "def test_" src/tests/test_backends.py
```

### 4. Find Configuration Options

```bash
# Read config class
cat src/litestar_email/config.py

# Find config usage
grep -r "EmailConfig" src/
```

---

## Deep Dive Commands

### Understand Backend Architecture

```bash
# Read the base class
cat src/litestar_email/backends/base.py

# Read an example implementation
cat src/litestar_email/backends/console.py

# See how backends are registered
cat src/litestar_email/backends/__init__.py
```

### Understand Plugin System

```bash
# Read the plugin implementation
cat src/litestar_email/plugin.py

# See how it integrates with Litestar
grep -A10 "on_app_init" src/litestar_email/plugin.py
```

### Understand Message System

```bash
# Read message classes
cat src/litestar_email/message.py

# See message usage in tests
grep -A5 "EmailMessage" src/tests/test_message.py
```

---

## Using MCP Tools for Research

### Litestar Documentation

```python
# Resolve library ID first
mcp__context7__resolve-library-id(
    query="Litestar plugin system",
    libraryName="litestar"
)

# Then query docs
mcp__context7__query-docs(
    libraryId="/litestar-org/litestar",
    query="How to create a plugin"
)
```

### Code Analysis

```python
# For deep architectural analysis
mcp__pal__analyze(
    step="Analyze backend architecture",
    step_number=1,
    total_steps=3,
    next_step_required=True,
    findings="...",
    analysis_type="architecture"
)
```

---

## Output Format

After exploration, provide:

```markdown
## Exploration Summary: [Topic]

### Key Findings
1. [Finding 1]
2. [Finding 2]

### Relevant Files
- `path/to/file.py` - [description]

### Code Patterns
[Any patterns observed]

### Recommendations
[If applicable]
```
