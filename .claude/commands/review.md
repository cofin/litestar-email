---
description: Quality gate and pattern extraction for feature completion
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, mcp__pal__analyze, mcp__pal__thinkdeep
---

# Review Workflow

You are reviewing the implementation: **$ARGUMENTS**

## Pre-Review Intelligence

1. **Load PRD**: Read `specs/active/{slug}/prd.md`
2. **Load Implementation**: Read all modified files
3. **Load Tests**: Read test files for coverage

## Critical Rules

1. **ALL GATES MUST PASS** - No exceptions
2. **PATTERN EXTRACTION** - Document new patterns discovered
3. **ARCHIVE ON COMPLETION** - Move specs to archive

---

## Quality Gate 1: Tests Pass

```bash
make test
```

**Requirement**: Zero failures

**Output**: "✓ Gate 1 - Tests: PASS"

---

## Quality Gate 2: Linting Clean

```bash
make lint
```

**Requirement**: Zero errors

**Output**: "✓ Gate 2 - Linting: PASS"

---

## Quality Gate 3: Coverage Target

```bash
make coverage
```

**Requirement**: 90%+ for modified modules

**Output**: "✓ Gate 3 - Coverage: [X]% (target: 90%)"

---

## Quality Gate 4: Anti-Pattern Scan

Scan for anti-patterns in modified files:

```bash
# Check for Optional usage
grep -r "Optional\[" src/litestar_email/ && echo "FAIL: Use T | None instead"

# Check for future annotations
grep -r "from __future__ import annotations" src/ && echo "FAIL: Remove future annotations"

# Check for relative imports
grep -r "from \.\." src/litestar_email/ && echo "FAIL: Use absolute imports"

# Check for missing __slots__
grep -r "class.*:" src/litestar_email/ | while read line; do
    file=$(echo "$line" | cut -d: -f1)
    grep -q "__slots__" "$file" || echo "WARN: Missing __slots__ in $file"
done
```

**Requirement**: Zero anti-patterns

**Output**: "✓ Gate 4 - Anti-pattern scan: PASS"

---

## Quality Gate 5: Pattern Compliance

Compare implementation against patterns identified in PRD:

1. Class structure matches existing backends
2. Naming conventions followed
3. Error handling consistent
4. Docstrings present and correct style

**Output**: "✓ Gate 5 - Pattern compliance: PASS"

---

## Pattern Extraction

If new patterns were discovered during implementation:

Write to `specs/guides/patterns/{pattern-name}.md`:

```markdown
# Pattern: [Name]

## When to Use
[Description of when this pattern applies]

## Implementation
[Code example]

## Example Files
- `src/litestar_email/backends/{file}.py`

## Notes
[Any gotchas or considerations]
```

**Output**: "✓ Patterns extracted: [list]"

---

## Archive Completed Work

```bash
# Move specs to archive
mv specs/active/{slug} specs/archive/{slug}
```

**Output**: "✓ Specs archived"

---

## Final Summary

```
Review Phase Complete ✓

Quality Gates:
- ✓ Tests: PASS
- ✓ Linting: PASS
- ✓ Coverage: [X]%
- ✓ Anti-patterns: NONE
- ✓ Pattern compliance: VERIFIED

Patterns Extracted:
- [list of new patterns, if any]

Feature Status: COMPLETE

Specs archived to: specs/archive/{slug}/
```

---

## If Any Gate Fails

1. **Do NOT archive** - feature is incomplete
2. **Document failure** in `specs/active/{slug}/recovery.md`
3. **List fixes needed**
4. **Re-run /implement or /test** as appropriate
