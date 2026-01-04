# MCP Tool Strategy

Guide for selecting the right MCP tools based on task requirements.

## Tool Selection by Task Type

### Complex Architectural Decisions

**Primary**: `mcp__pal__thinkdeep`
```python
mcp__pal__thinkdeep(
    step="Analyzing backend architecture for new SMTP implementation",
    step_number=1,
    total_steps=5,
    next_step_required=True,
    findings="Initial analysis shows...",
    focus_areas=["architecture", "performance"],
    relevant_files=["/home/.../backends/base.py"]
)
```

**Fallback**: `mcp__sequential-thinking__sequentialthinking`
```python
mcp__sequential-thinking__sequentialthinking(
    thought="Step 1: Analyze existing backend structure...",
    thoughtNumber=1,
    totalThoughts=15,
    nextThoughtNeeded=True
)
```

### Library Documentation Lookup

**Primary**: `mcp__context7__query-docs`
```python
# First resolve the library ID
mcp__context7__resolve-library-id(
    query="Litestar plugin system",
    libraryName="litestar"
)

# Then query documentation
mcp__context7__query-docs(
    libraryId="/litestar-org/litestar",
    query="How to implement InitPluginProtocol"
)
```

**Fallback**: `WebSearch`
```python
WebSearch(query="Litestar 2.0 plugin development guide 2025")
```

### Multi-Phase Planning

**Primary**: `mcp__pal__planner`
```python
mcp__pal__planner(
    step="Planning SMTP backend implementation",
    step_number=1,
    total_steps=8,
    next_step_required=True
)
```

**Fallback**: Manual structured thinking with checkpoints

### Code Analysis

**Primary**: `mcp__pal__analyze`
```python
mcp__pal__analyze(
    step="Analyzing email message class structure",
    step_number=1,
    total_steps=4,
    next_step_required=True,
    findings="...",
    analysis_type="architecture",
    relevant_files=["/home/.../message.py"]
)
```

**Fallback**: Manual code review with grep/read

### Debugging

**Primary**: `mcp__pal__debug`
```python
mcp__pal__debug(
    step="Investigating email sending failure",
    step_number=1,
    total_steps=5,
    next_step_required=True,
    findings="Error occurs in...",
    hypothesis="Connection timeout due to...",
    confidence="medium"
)
```

**Fallback**: Manual investigation with bash/read

## Complexity-Based Selection

### Simple Features (6 checkpoints)

- Use basic tools: Read, Write, Edit, Bash
- Manual analysis acceptable
- Focus on speed
- Sequential thinking: 8-10 thoughts max

**Examples**: Config change, bug fix, single file modification

### Medium Features (8 checkpoints)

- Use `mcp__sequential-thinking__sequentialthinking` (12-15 steps)
- Include pattern analysis
- Moderate research depth

**Examples**: New backend, API endpoint, 2-3 files

### Complex Features (10+ checkpoints)

- Use `mcp__pal__thinkdeep` or `mcp__pal__planner`
- Deep pattern analysis
- Comprehensive research with Context7

**Examples**: Architecture change, new protocol, multi-component

## Tool Combinations

### PRD Creation

1. `mcp__context7__query-docs` - Research Litestar patterns
2. `mcp__sequential-thinking__sequentialthinking` - Structured analysis
3. `mcp__pal__planner` - For complex features

### Implementation

1. `mcp__context7__query-docs` - Reference documentation
2. `mcp__pal__thinkdeep` - Architectural decisions
3. `mcp__pal__debug` - When issues arise

### Review

1. `mcp__pal__analyze` - Code quality analysis
2. Bash tools - Quality gate execution

## Decision Matrix

| Task | Simple | Medium | Complex |
|------|--------|--------|---------|
| Research | WebSearch | Context7 | Context7 + ThinkDeep |
| Analysis | Manual | Sequential | Planner + ThinkDeep |
| Implementation | Basic tools | + Context7 | + All MCP tools |
| Debugging | Manual | Debug | Debug + Analyze |
| Review | Manual | Analyze | Analyze + ThinkDeep |

## Rate Limiting

- Context7: Max 3 calls per question
- Sequential Thinking: Adjust totalThoughts to complexity
- Pal Tools: Use step_number/total_steps for pacing

## When to Skip MCP Tools

- Single file fixes
- Obvious bugs with clear solutions
- Simple configuration changes
- Tasks under 6 checkpoints (simple)

Use basic tools (Read, Write, Edit, Bash) for speed.
