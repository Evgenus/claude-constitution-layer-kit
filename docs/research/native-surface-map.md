---
id: research-native-surface-map
type: non-authoritative
title: Native surface map (verified 2026-08-28)
status: inactive
---

# Native surface map (verified 2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

Verified against official docs at code.claude.com (memory.md, skills.md, commands.md, hooks.md, settings-reference.md, sub-agents.md, output-styles.md).

## CLAUDE.md memory files
Loading: root/ancestor CLAUDE.md at session start; nested CLAUDE.md lazy-loads when files in that subtree are read; ~/.claude/CLAUDE.md and CLAUDE.local.md same pattern. Enforcement: advisory (delivered as user message after system prompt). Size: target ~200 lines/file (longer = reduced adherence). Imports: `@path/to/file` load with the containing file, max depth 4 hops; first-time approval dialog for external imports (NOT launch-only/organization-only — sketch corrected). Compaction: root CLAUDE.md survives /compact and re-injects.

## Path-scoped rules (.claude/rules/*.md)
Loading: lazy when Claude reads files matching `paths:` globs in frontmatter; rules WITHOUT `paths:` load at launch. Enforcement: advisory. User-level ~/.claude/rules/* applies to all projects. Glob: brace expansion, up to 1,000 patterns, 4 MiB/rule.

## Skills (.claude/skills/*/SKILL.md)
Loading: description at startup (discovery); body lazy on invocation (auto-relevance or /name; chains up to 6). Frontmatter: name, description, allowed-tools, model, permissionMode, when, tags. `.claude/commands/*.md` merged into skills (old path still works; skills canonical — sketch corrected). Enforcement: advisory.

## Slash commands
Built-in commands NOT deprecated (sketch corrected); custom commands are skills now. Some built-ins are bundled skills.

## Hooks
Events: PreToolUse, PostToolUse, UserPromptSubmit, Stop, SubagentStart/Stop, SessionStart, SessionEnd, PreCompact, Notification, PermissionRequest, others. Matchers: exact, pipe (`Bash|Edit`), regex, `*`, `mcp__*`. Exit codes: 0 = success (JSON parsed); 2 = blocking error with stderr fed to the model — per event: PreToolUse blocks the tool call, Stop blocks the stop, UserPromptSubmit blocks the prompt; on PostToolUse the tool has already run, so exit 2 blocks nothing and only feeds stderr back as feedback; overrides JSON allow. Other codes = non-blocking. JSON output: permissionDecision/permissionDecisionReason/additionalContext/updatedInput/systemMessage. Handler types: command, http, mcp_tool, prompt (LLM-judged — NOT deterministic), agent (NOT deterministic). Config: settings.json hierarchy. SessionEnd is non-blocking and has known fire-reliability gaps. Stop-hook exit 2 blocks the stop and feeds stderr back; loop hazard mitigated via stop_hook_active flag. **Stop fires once per assistant TURN, not per session** (docs: "Once per turn: UserPromptSubmit, Stop, StopFailure"; empirically confirmed 2026-08-29 on v2.1.251 — a logging Stop hook fired at the end of each of 2 turns in one resumed session, same session_id). There is no reliable blocking session-end event (SessionEnd is non-blocking and unreliable); anything gating "session end" must arm on a condition, not on the event itself. Hook input JSON (verified 2026-08-29 against CLI v2.1.220 binary; re-verified on v2.1.251): includes `transcript_path`, `cwd`, and — for Stop/SubagentStop — `stop_hook_active` and `last_assistant_message` (the final assistant text as a string), so a Stop hook can check sentinels in the last message without parsing the transcript.

## Settings & permissions
Hierarchy (high→low): managed → CLI --settings → .claude/settings.local.json → .claude/settings.json → ~/.claude/settings.json. permissions.{allow,deny,ask,defaultMode,additionalDirectories}; sandbox config; outputStyle key; hooks key.

## Subagents (.claude/agents/*.md)
Isolated context window; own system prompt; CLAUDE.md loads (except Explore/Plan built-ins); frontmatter: name, description, tools, model, permissionMode, skills, memory. AskUserQuestion unavailable inside subagents — they cannot talk to a decider (locally verified 2026-08-29 by dynamic probe: invocation fails with "No such tool available: AskUserQuestion. AskUserQuestion is not available inside subagents."; also GH #12890/#18721).

## AskUserQuestion in headless mode (verified 2026-08-29, CLI v2.1.220 binary; confirmed DYNAMICALLY on v2.1.251)
Dynamic confirmation (v2.1.251, `claude -p`): the tool is entirely absent from the headless tool list — not offered upfront and not present as a deferred tool ("No matching deferred tools found"); the session self-reports non-interactive. The "headless auto-resolves as empty" community claim is REFUTED. The tool declares `requiresUserInteraction() → true`; `isEnabled()` returns false in non-interactive sessions (exception: SDK contexts with an active dialog host — `sdkDialogHostActive`/`sdkSupportedDialogKinds`); the permission layer denies interaction-requiring tools in headless/async-agent contexts with "tool requires user interaction; no prompt available in headless mode" (and via `--permission-prompt-tool`: "not supported"). The model gets explicit unavailability or denial — never fabricated empty answers. Separately, interactive sessions may set `askUserQuestionTimeout` (default "never"); on timeout the tool resolves with "No response after Ns — the user may be away from keyboard. Proceed using your best judgment…".

## Output styles (.claude/output-styles/*.md)
Loading: once at session start; modifies system prompt; main conversation only (subagents unaffected). Frontmatter: name, description, keep-coding-instructions. Built-ins include Default/Concise/Explanatory. Project-level supported; selected via outputStyle in settings.json. Per-turn re-reminder (dynamically verified 2026-08-29 on v2.1.251): when the active style ≠ default, an `output_style` attachment is injected on EVERY user turn — rendered as a system-reminder "`{name} output style is active. {turnReminder ?? 'Remember to follow the specific guidelines for this style.'}`" — including in headless `-p` sessions; styles may define a custom `turnReminder`.

## Sketch verdicts
- Root CLAUDE.md always-on, ~200-line ceiling, survives compaction — VERIFIED
- Nested CLAUDE.md lazy per subtree — VERIFIED
- .claude/rules/*.md with paths: frontmatter — VERIFIED
- Skills load on activity — VERIFIED (descriptions at startup, body lazy)
- Hooks deterministic, exit 2 blocks — VERIFIED (command handlers; prompt/agent handlers are LLM-judged, not deterministic)
- @path imports launch-only/organization-only — REFUTED (all scopes, load with containing file, depth 4)
- Slash commands: custom .claude/commands/*.md — SUPERSEDED (merged into skills; built-in slash commands remain)

## Corrected ownership map
- Enforce (hard) → hooks with command handlers (exit 2), permissions allow/deny/ask, sandbox
- Always-on norms → short root CLAUDE.md (only compaction-surviving advisory surface)
- Contextual knowledge → nested CLAUDE.md, path-scoped rules (lazy), skills (lazy body)
- Procedures → skills (agent-invoked default; /name for human-initiated)
- Response shape/tone → output styles (system-prompt level, main conversation only)
- Delegation → subagents (isolated context; cannot reach the decider)
