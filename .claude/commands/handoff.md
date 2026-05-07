# /handoff — MEX Safety Platform Session Handoff

Produce a structured handoff summary so a new session can pick up immediately with no context loss.

## Instructions

Read the following in order, then produce the handoff report below:

1. `C:/Users/Owner/.claude/projects/c--Users-Owner-Desktop-MEX-mex-safety-platform/memory/MEMORY.md` — memory index
2. `C:/Users/Owner/.claude/projects/c--Users-Owner-Desktop-MEX-mex-safety-platform/memory/project_build_status.md` — build status
3. `C:/Users/Owner/.claude/projects/c--Users-Owner-Desktop-MEX-mex-safety-platform/memory/feedback_conclusion_style.md` — style feedback
4. `CLAUDE.md` — project rules and architecture

Then verify current state:
- Run `git status` if the repo has git, or list any uncommitted/unsaved files you're aware of
- Note any files you edited this session

---

## Handoff Report Format

```
## MEX Safety Platform — Session Handoff
**Date:** <today>

### What's Working
<bullet list — confirmed built and functional layers>

### What's In Progress
<any work started this session that isn't complete>

### Next Priority Tasks
<numbered list from build status, most urgent first>

### Known Issues (deferred)
<brief list — don't elaborate>

### Active Feedback Rules
<any style/approach feedback the next session should apply>

### Files to Be Aware Of
<any files touched this session or that need attention soon>

### Start Next Session With
<one sentence: what to do first when you open a new session>
```

Keep it tight — bullet points, no padding. This is a handoff doc, not a report.
