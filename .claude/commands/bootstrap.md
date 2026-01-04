---
description: Re-bootstrap AI development infrastructure (alignment mode)
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, mcp__sequential-thinking__sequentialthinking, mcp__pal__planner
---

# Project Bootstrap Command - Alignment Mode

You are re-bootstrapping the AI development infrastructure for this project.

## Alignment Mode Workflow

Since this project already has bootstrap infrastructure, this command will:

1. **Inventory existing configuration**
2. **Identify missing components**
3. **Preserve custom content**
4. **Update to latest templates**

---

## Step 1: Inventory Existing Configuration

```bash
# List existing commands
ls .claude/commands/*.md 2>/dev/null || echo "No commands"

# List existing agents
ls .claude/agents/*.md 2>/dev/null || echo "No agents"

# List existing skills
ls -d .claude/skills/*/ 2>/dev/null || echo "No skills"

# Check CLAUDE.md
head -5 CLAUDE.md 2>/dev/null | grep "Version"

# Check pattern library
ls specs/guides/patterns/*.md 2>/dev/null || echo "No patterns"

# Check quality gates
cat specs/guides/quality-gates.yaml 2>/dev/null | head -10 || echo "No quality gates"
```

---

## Step 2: Identify Missing Components

### Core Commands (must exist)
- [ ] prd.md
- [ ] implement.md
- [ ] test.md
- [ ] review.md
- [ ] explore.md
- [ ] fix-issue.md
- [ ] bootstrap.md

### Core Agents (must exist)
- [ ] prd.md
- [ ] expert.md
- [ ] testing.md
- [ ] docs-vision.md

### Infrastructure (must exist)
- [ ] specs/guides/patterns/README.md
- [ ] specs/guides/quality-gates.yaml
- [ ] .claude/mcp-strategy.md
- [ ] .claude/skills/litestar/README.md

---

## Step 3: Preserve Custom Content

Before updating any file:

1. Read existing content
2. Identify custom sections (not from template)
3. Store custom content
4. Merge into updated file

---

## Step 4: Generate Missing Components

For each missing component:

1. Generate from template
2. Adapt to project specifics
3. Write to appropriate location

---

## Step 5: Update Report

```markdown
## Alignment Report

### Existing Components
- Commands: [list]
- Agents: [list]
- Skills: [list]

### New Components Added
- [ ] [component name] - [reason]

### Updates Applied
- [ ] [file] - [change description]

### Custom Content Preserved
- [file] - [custom sections]

### Verification
- [ ] All commands present
- [ ] All agents present
- [ ] MCP strategy present
- [ ] Quality gates present
- [ ] Pattern library initialized
```

---

## Final Summary

```
Bootstrap Alignment Complete ✓

Existing: [N] commands, [M] agents, [P] skills
Added: [list of new components]
Updated: [list of updated components]
Preserved: [list of custom content]

Run `/explore` to verify configuration.
```
