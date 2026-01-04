---
description: Create a PRD with pattern learning and adaptive complexity
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, mcp__context7__resolve-library-id, mcp__context7__query-docs, mcp__sequential-thinking__sequentialthinking, mcp__pal__planner
---

# Intelligent PRD Creation Workflow

You are creating a Product Requirements Document for: **$ARGUMENTS**

## Intelligence Layer (ACTIVATE FIRST)

Before starting checkpoints:

1. **Read MCP Strategy**: Load `.claude/mcp-strategy.md` for tool selection
2. **Learn from Codebase**: Read 3-5 similar implementations
3. **Assess Complexity**: Determine simple/medium/complex
4. **Adapt Workflow**: Adjust checkpoint depth

## Critical Rules

1. **CONTEXT FIRST** - Read existing patterns before planning
2. **NO CODE MODIFICATION** - Planning only
3. **PATTERN LEARNING** - Identify 3-5 similar features
4. **ADAPTIVE DEPTH** - Simple=6, Medium=8, Complex=10+ checkpoints
5. **RESEARCH GROUNDED** - Minimum 2000+ words research
6. **COMPREHENSIVE PRD** - Minimum 3200+ words

---

## Checkpoint 0: Intelligence Bootstrap

**Load project intelligence:**

1. Read `CLAUDE.md`
2. Read `specs/guides/patterns/README.md` (if exists)
3. Read `.claude/mcp-strategy.md`

**Learn from existing implementations:**

```bash
# Find similar features in this litestar-email project
grep -r "class.*Backend" src/litestar_email/ | head -5

# Read example backend files
cat src/litestar_email/backends/console.py
cat src/litestar_email/backends/memory.py
```

**Assess complexity:**

- **Simple**: Single file, config change, minor feature → 6 checkpoints
- **Medium**: New backend, API changes, 2-3 files → 8 checkpoints
- **Complex**: Architecture change, new protocol, 5+ files → 10+ checkpoints

**Output**: "✓ Checkpoint 0 complete - Complexity: [level], Checkpoints: [count]"

---

## Checkpoint 1: Pattern Recognition

**Identify similar implementations:**

1. Search for related patterns in `src/litestar_email/`
2. Read at least 3 similar files
3. Extract naming patterns (e.g., `*Backend`, `Email*`)
4. Note testing patterns from `src/tests/`

**Document:**

```markdown
## Similar Implementations

1. `src/litestar_email/backends/console.py` - Console output backend
2. `src/litestar_email/backends/memory.py` - In-memory testing backend
3. `src/litestar_email/backends/base.py` - Abstract base class

## Patterns Observed

- Class structure: Inherits from `BaseEmailBackend`
- Required method: `async send_messages(messages: list[EmailMessage]) -> int`
- Uses `__slots__` for memory efficiency
- Google-style docstrings
```

**Output**: "✓ Checkpoint 1 complete - Patterns identified"

---

## Checkpoint 2: Workspace Creation

```bash
# Create feature workspace
mkdir -p specs/active/{slug}/research
mkdir -p specs/active/{slug}/tmp
mkdir -p specs/active/{slug}/patterns
```

**Output**: "✓ Checkpoint 2 complete - Workspace at specs/active/{slug}/"

---

## Checkpoint 3: Intelligent Analysis

**Use appropriate tool based on complexity:**

- Simple: 10 structured thoughts
- Medium: Sequential thinking (15 thoughts)
- Complex: `mcp__pal__planner` for multi-phase planning

**Document analysis in workspace.**

**Output**: "✓ Checkpoint 3 complete - Analysis using [tool]"

---

## Checkpoint 4: Research (2000+ words)

**Priority order:**

1. Pattern Library: `specs/guides/patterns/`
2. Internal Guides: `specs/guides/`
3. Context7: `mcp__context7__query-docs` for Litestar documentation
4. WebSearch: Best practices for email libraries

**Verify:** `wc -w specs/active/{slug}/research/plan.md`

**Output**: "✓ Checkpoint 4 complete - Research (2000+ words)"

---

## Checkpoint 5: Write PRD (3200+ words)

Write to `specs/active/{slug}/prd.md`:

```markdown
# PRD: [Feature Name]

## Metadata
- **Feature**: [name]
- **Complexity**: [simple|medium|complex]
- **Checkpoints**: [count]
- **Similar Features**: [list from pattern analysis]

## Problem Statement
[Why this feature is needed]

## Goals & Non-Goals
### Goals
- [Specific, measurable goals]

### Non-Goals
- [What this feature will NOT do]

## Acceptance Criteria
- [ ] [Specific, testable criterion]
- [ ] All existing tests pass
- [ ] 90%+ coverage for new code
- [ ] Pattern compliance verified

## Technical Approach

### Architecture
[How it fits into existing backend system]

### Implementation
[Step-by-step approach following identified patterns]

### Testing Strategy
[How to test, using existing test patterns]

## Pattern Compliance

### Must Follow
- Inherit from `BaseEmailBackend`
- Implement `async send_messages()` method
- Use `__slots__`
- Add `@register_backend` decorator
- Google-style docstrings

### Anti-Patterns to Avoid
- No `Optional[T]` - use `T | None`
- No relative imports
- No `from __future__ import annotations`
- No class-based tests
```

**Verify:** `wc -w specs/active/{slug}/prd.md`

**Output**: "✓ Checkpoint 5 complete - PRD (3200+ words)"

---

## Checkpoint 6: Task Breakdown

Write to `specs/active/{slug}/tasks.md`:

```markdown
## Implementation Tasks

### Phase 1: Core Implementation
- [ ] Task 1.1: [Description]
- [ ] Task 1.2: [Description]

### Phase 2: Testing
- [ ] Task 2.1: Unit tests
- [ ] Task 2.2: Integration tests

### Phase 3: Documentation
- [ ] Task 3.1: Update exports in `__init__.py`
- [ ] Task 3.2: Add docstrings
```

**Output**: "✓ Checkpoint 6 complete - Tasks adapted to complexity"

---

## Checkpoint 7: Recovery Guide

Write to `specs/active/{slug}/recovery.md`:

```markdown
# Recovery Guide

## Session Context
- Feature: [name]
- Complexity: [level]
- Last checkpoint: [number]
- Current phase: [phase]

## To Resume
1. Read this file
2. Read `prd.md` for requirements
3. Read `tasks.md` for progress
4. Continue from last incomplete task

## Key Files
- Config: `src/litestar_email/config.py`
- Backends: `src/litestar_email/backends/`
- Tests: `src/tests/`
```

**Output**: "✓ Checkpoint 7 complete - Recovery guide with intelligence context"

---

## Checkpoint 8: Git Verification

```bash
# Verify no source code was modified
git status --porcelain src/ | grep -v "^??"
```

**Output**: "✓ Checkpoint 8 complete - No source code modified"

---

## Final Summary

```
PRD Phase Complete ✓

Workspace: specs/active/{slug}/
Complexity: [simple|medium|complex]
Checkpoints: [6|8|10+] completed

Intelligence:
- ✓ Pattern library consulted
- ✓ Similar features analyzed
- ✓ Tool selection optimized

Next: Run `/implement {slug}`
```
