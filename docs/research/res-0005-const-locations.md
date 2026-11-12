---
id: res-0005-const-locations
type: non-authoritative
title: Research comparison — const-locations (2026-09-22)
status: active
---

# Research comparison — const-locations (2026-09-22)

Surveyed 2026-09-22; local `claude --version` prints `2.1.251 (Claude Code)`. Experiments ran with git 2.54.0, Python 3.12.4, PyYAML 6.0.2 and, in a scratch virtual environment, ruamel.yaml 0.19.1, on macOS, in a scratch directory outside any repository of the kit. The live runs used `claude -p` with the model the session reports as `claude-opus-5[1m]`. Official Claude Code pages were read in their Markdown form (`curl -sL https://code.claude.com/docs/en/<page>.md`), and every quotation below was checked against that text. A statement about a tool's behaviour is written only where the experiment that showed it is named, with the version tried. A tool read but not run is marked so.

Scope: the rows of [`const-locations`](../requirements.md#const-locations) — [requirement A2.4](../requirements.md#a2-4), documents created by command from the policy's template into the canonical home, and [requirement A2.5](../requirements.md#a2-5), the new-kind procedure — and the specification's optional dial, "default policy for otherwise-unclaimed governed roots". The module claims no gate: [dec-0015-pre-module-audit-rulings](../decisions/dec-0015-pre-module-audit-rulings.md) moved the resolution gate to [`const-meta-types`](../requirements.md#const-meta-types) and left this module "advisory creation". Vocabulary: envelope ([kernel §1](../constitution/CONVENTIONS.md#k1)), meta-type ([kernel §2](../constitution/CONVENTIONS.md#k2)), territory, policy and kind ([kernel §3](../constitution/CONVENTIONS.md#k3)), dials file and the portability rule ([kernel §6](../constitution/CONVENTIONS.md#k6)); a *home* is the path a new document of a kind is born at, a *generator* a script that writes files and is never a gate ([template §6](../../module-template/MODULE.md#t6), rule 3). What the kit's gates share is described in [kit-shared-gate-code](../../shared/GATE.md) and is surveyed here only for fit (section 7). The kit is consumer zero: its dials file declares nine policy namespaces on the survey date, and the kinds this module would create are exactly those; the record skill of `const-decision-records` and the catalog skill of `const-catalogs` were read as the precedents, each for one kind. Sources by authority: official Claude Code documentation, tool documentation and repositories, experiments reported here (E1–E5; E6 and p11 added 2026-09-23, dated where they stand). The four earlier comparisons — the [first](res-0001-const-meta-types.md), the [second](res-0002-const-decision-records.md), the [third](res-0003-const-catalogs.md) and the [fourth](res-0004-const-referencing.md) — were a starting point, never evidence: every platform fact relied on here was re-read today (section 9).

The surveyed tools, keyed once; a date is the latest release on the survey date, from the repository's releases page or registry entry, or the last commit where no release exists. None was run; each was read at the URL given.

- t1. [Hugo](https://gohugo.io/content-management/archetypes/) v0.166.0, 2026-09-09: archetypes, `hugo new content`.
- t2. [Templater](https://silentvoid13.github.io/Templater/settings.html) 2.25.1, 2026-09-19, and Obsidian's [core Templates](https://github.com/obsidianmd/obsidian-help/blob/master/en/Plugins/Templates.md).
- t3. [Dendron schemas](https://wiki.dendron.so/notes/c5e5adde-5459-409b-b34d-a0d75cbb1052/): "currently in maintenace only" (its [readme](https://github.com/dendronhq/dendron/blob/master/README.md), spelling as there); last commit 2025-06-01; the CLI's last npm release 0.124.2, 2024-03-10.
- t4. [adr-tools](https://github.com/npryce/adr-tools) 3.0.0, 2018-07-25; last commit 2020-03-30: shell.
- t5. [log4brains](https://github.com/thomvaill/log4brains) v1.1.0, 2024-12-17: Node.
- t6. [dotnet-adr](https://github.com/endjin/dotnet-adr) tag 1.1.8, NuGet 2024-03-21; last commit 2025-07-23: .NET.
- t7. [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/overview.html) v2.7.1, 2026-03-04; t8. [copier](https://github.com/copier-org/copier/blob/master/docs/configuring.md) v9.18.2, 2026-09-07: Python.
- t9. [plop](https://github.com/plopjs/plop/blob/main/README.md) 4.0.5, 2026-01-22: Node. t10. [Rails generators](https://guides.rubyonrails.org/generators.html), Rails v8.1.3.1, 2026-07-29. t11. [jekyll-compose](https://github.com/jekyll/jekyll-compose) v0.12.0, 2019-12-28; last commit 2020-12-24.

## 1. Creation from a template: the native surface ([requirement A2.4](../requirements.md#a2-4))

What the platform offers today for "create a document of kind K", from the [skills](https://code.claude.com/docs/en/skills) page unless another is named — the `slash-commands` page is the same document: the two Markdown files fetched today are byte-identical.

- a1. **A skill with supporting files.** `skills/<name>/SKILL.md` plus files beside it, each "loaded when needed", so a template beside the skill costs nothing until invocation. `${CLAUDE_SKILL_DIR}` is "the skill's subdirectory within the plugin, not the plugin root"; `${CLAUDE_PLUGIN_ROOT}` is "Substituted only in plugin skills". Both are substituted "in two places: the skill's markdown content, and Bash rules in the `allowed-tools` frontmatter", so a skill can name a generator command and pre-approve exactly it. The three path variables "aren't present in the environment of commands Claude runs through the Bash tool" ([plugins reference](https://code.claude.com/docs/en/plugins-reference)) — a skill writes the placeholder, never `$CLAUDE_PLUGIN_ROOT`. This is how the record skill ships its template (`${CLAUDE_SKILL_DIR}/record-template.md`).
- a2. **The frontmatter fields that exist today**, verified one by one against the page's table: `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`, `license`, `compatibility`. "All fields are optional. Only `description` is recommended." `disable-model-invocation: true` — "Only you can invoke the skill", its description "not in context"; `user-invocable: false` — "Only Claude can invoke the skill"; the default is both, "Description always in context, full skill loads when invoked". `paths` limits automatic loading to "files matching the patterns", in the memory page's glob format — a territory is a runtime dial, so a module can write at most `**/*.md` there, as the first comparison found.
- a3. **Arguments.** `$ARGUMENTS` is the whole string. `$ARGUMENTS[N]` and `$N` are 0-based — "`$0` for the first argument or `$1` for the second". `arguments: [kind, stem]` makes `$kind` and `$stem` named placeholders, which expand "to an empty string" when unfilled, while an indexed one "stays in the content unchanged". With no placeholder the platform appends `ARGUMENTS: <value>`.
- a4. **The `!` injection form exists.** "The `` !`<command>` `` syntax runs shell commands before the skill content is sent to Claude", in "the session shell's current working directory". "A failed command aborts the entire skill invocation, not just its own placeholder. Claude never sees the skill content for that invocation" — "any non-zero exit code counts as a failure". Outside auto mode a permission check other than allow "aborts the invocation" too. A skill that injects the generator's output at load time therefore fails closed on a bare repository with no `constitution.yaml`, where a module must still work ([kernel §6](../constitution/CONVENTIONS.md#k6)) — unless the generator exited 0 on a configuration failure, which rule 8 of [template §6](../../module-template/MODULE.md#t6) forbids.
- a5. **Command files.** "Custom commands have been merged into skills". A command file "supports the same frontmatter except `name` and `paths`" and has no directory for supporting files. In a plugin, `commands/` is "Skills as flat Markdown files. Use `skills/` for new plugins" ([plugins reference](https://code.claude.com/docs/en/plugins-reference)). Nothing a command file does that a skill with `disable-model-invocation: true` does not.
- a6. **Agents.** A plugin's `agents/<name>.md` is a subagent ([plugins reference](https://code.claude.com/docs/en/plugins-reference)); a skill with `context: fork` runs in one that "doesn't see your conversation history". Creating a document is no delegation boundary: the title, the kind and the reason are in the conversation.
- a7. **Lifecycle.** A loaded skill "stays there across later turns". The listing "scales at 1% of the model's context window", each entry capped at 1,536 characters. `skillListingBudgetFraction` and `skillListingMaxDescChars` exist on the [settings reference](https://code.claude.com/docs/en/settings-reference).
- a8. **Live (E5).** A throwaway plugin holding one skill and nothing else — description of 356 characters opening "Create a governed document in its canonical home from its policy's template. Use when about to create any new Markdown document in a repository that has a `constitution.yaml`" — in four non-interactive sessions on a scratch repository with a dials file, a root policy and a notes policy. Prompts: "Write a policy for how test files are named in this project" (three runs, one with the description reworded to open "Write a policy, a note, a record …") and "Add a working note … under docs/notes/". In all four the model listed the repository, read the dials file and both policies, then called the `Skill` tool on the plugin's skill *before writing* — the session's `slash_commands` listed it as `loc-plugin:create-governed-document` — and wrote the document at the home the procedure derives, with a four-field envelope whose `id` was the stem, the policy's body shape, and a closing `LOCATIONS:` line naming path and policy. In the three policy runs it also appended a namespace with a `territory` to `constitution.yaml`, as the scratch root policy's rule 2 asks.

Which surface fits which act. "A command a human types" is the template's command row, "only for acts a human deliberately initiates". The kit's root policy already names one: "When module `const-locations` is installed, its creation command writes the document here from the policy template" ([plc-0001-root-policy](../policies/plc-0001-root-policy.md), rule 3). "A procedure the model follows when it is about to create a governed document" is the default skill, which E5 shows the model reaching for from the listing alone. Under the platform's merge (a5) the two are one skill: typed as `/const-locations:<name> <kind> <stem>`, or invoked by the model with the same arguments. A second skill with `disable-model-invocation: true` would only hide the description from the model — the one thing E5 shows is worth keeping.

Step down from the native option, named: the skill can carry the procedure and the template, but it cannot read the dials file — patterns, anchors, aliases, the root's territory — except by having the model read YAML as prose; deriving the home and proving that the written path resolves to exactly the named policy is what section 7's generator is for, and the skill names it.

**Recommendation: one skill, model-invocable and user-invocable (the default), taking `kind` and `stem` as named arguments, carrying the procedure of [requirement A2.4](../requirements.md#a2-4) and naming the generator of section 7 through `${CLAUDE_PLUGIN_ROOT}`; no command file, no agent, no `!` injection (a4); confirmed as advisory.** For the decider: whether `allowed-tools` pre-approves the generator's command line, the page's own pattern (a1), or the consumer's permission rules are left to it.

## 2. Hook-side assists for creation, without a gate

The [hooks reference](https://code.claude.com/docs/en/hooks), verified field by field:

- b1. `PreToolUse` returns its decision "inside a `hookSpecificOutput` object": `permissionDecision` (`allow` / `deny` / `ask` / `defer`), `permissionDecisionReason`, `updatedInput` — "Replaces the entire input object, so include unchanged fields alongside modified ones" — and `additionalContext`, "String added to Claude's context alongside the tool result". Rewriting is named as such: "`PreToolUse`: `updatedInput` … `PostToolUse`: `updatedToolOutput` … `UserPromptSubmit`: can't replace the prompt".
- b2. `additionalContext` is accepted by the session, prompt, tool, stop and model-switch events — eleven in all. For the tool events it lands "next to the tool result"; "capped at 10,000 characters", each string "measured separately". `systemMessage` is universal, a "Warning message shown to the user", which "some events discard".
- b3. Several handlers: "the most restrictive answer applies, in the order `deny`, `defer`, `ask`, `allow`. Text from `additionalContext` is kept from every hook"; and "When multiple `PreToolUse` hooks return `updatedInput` … the last one to finish takes effect. Since hooks run in parallel, the order is non-deterministic" ([hooks guide](https://code.claude.com/docs/en/hooks-guide)).
- b4. **Live, `additionalContext` (E3).** A handler on `Write` returning, for a new file under the notes territory, one paragraph naming the policy, the kind and its template. In the run that used `Write`, the model's call carried an envelope with `id` unequal to the stem, a `date` field and no `status`; the paragraph appeared beside the tool result, and the model's next call was an `Edit` setting `id` to the stem and `status: active` in place of `date`, attributed in its reply to "the locations hook". One rewrite, the write itself untouched.
- b5. **Live, `updatedInput` (E4).** A handler that rebuilds the envelope from the kind's template and returns it as `updatedInput` with an `additionalContext` line saying so: the file on disk carried the rebuilt envelope; the model read it back with `sed` and reported the change. Without the context line the tool result says only "File created successfully" and the model's picture of the file is wrong — the first comparison's ground for rejecting `updatedInput` ("silently rewriting an envelope is the opposite of a teaching error"). A first attempt skipped its own rewrite because the content already opened with `---`: an assist that rewrites must judge field by field.
- b6. **The model does not always write with `Write`.** In every run that left the tool choice open — the two hook runs before they were repeated with "Use the Write tool", and all four skill runs — the model created the document with a `cat > file <<'EOF'` heredoc through `Bash`. A handler on `Write|Edit` never fired in those six; the two envelopes written blind carried the same three defects as b4. Shared honest limit 1 of [kit-shared-gate-code §4](../../shared/GATE.md#g4) was the common case here, not a corner.
- b7. **The same event, twice.** `const-meta-types` runs at `PreToolUse` on `Write|Edit` over the same territory. A second handler adds a Python start per write (about 52 ms, the fourth comparison's m8). Under b3 an `updatedInput` here would race any other rewriter.

Against [law 5 of CLAUDE.md](../../CLAUDE.md#law-5): a handler that never blocks and only teaches is advisory content on a gate's channel — a check in all but its verdict, indistinguishable from a gate in `hooks.json`. `updatedInput` is worse: neither block nor advice, it changes what the model believes it wrote, honest only with context attached (b5).

**Recommendation: no hook — the module ships no handler on any tool event; the rule travels in the skill (section 1) and the proof is the generator's own check (section 7); confirmed as advisory.** Recorded, not recommended: b4 as the one gentle assist that worked live, for the day a consumer reports documents born by `Write` with a bad envelope despite the skill; b5 never.

## 3. Deriving the canonical home from a territory

A territory is a gitignore pattern over repository-relative paths ([kernel §6](../constitution/CONVENTIONS.md#k6)); it enumerates a kind's documents and names no directory. The kit's nine territories, classified by a prototype (E2) that reads `constitution.yaml`, keeps the namespaces whose id has a document in the root's territory, and asks of each pattern whether a home follows without judgment; every derived home was then checked with `git check-ignore` against its own pattern, as the shared `Matcher` does:

| key | policy | territory | class | home | check |
|---|---|---|---|---|---|
| c1 | [plc-0001-root-policy](../policies/plc-0001-root-policy.md) | `docs/policies/**` | directory prefix | `docs/policies/<stem>.md` | matches |
| c2 | [plc-0002-kernel](../policies/plc-0002-kernel.md) | `kernel/**` | directory prefix | `kernel/<stem>.md` | matches |
| c3 | [plc-0003-intent-page](../policies/plc-0003-intent-page.md) | `/INTENT.md` | single file | none: nothing new is born in a territory of one path | — |
| c4 | [plc-0004-decision-records](../policies/plc-0004-decision-records.md) | `docs/decisions/**` | directory prefix | `docs/decisions/<stem>.md` | matches |
| c5 | [plc-0005-research](../policies/plc-0005-research.md) | `docs/research/**` | directory prefix | `docs/research/<stem>.md` | matches |
| c6 | [plc-0006-module-documents](../policies/plc-0006-module-documents.md) | `modules/*/MODULE.md` | one free segment | `modules/<segment>/MODULE.md` once the segment is given | matches with a segment |
| c7 | [plc-0007-requirements](../policies/plc-0007-requirements.md) | `docs/requirements.md` | single file | none | — |
| c8 | [plc-0008-rollout-plan](../policies/plc-0008-rollout-plan.md) | `docs/rollout-plan.md` | single file | none | — |
| c9 | [plc-0009-shared-code](../policies/plc-0009-shared-code.md) | `shared/GATE.md` | single file | none | — |

Three classes cover the kit:

- **a** **directory prefix** — one pattern, `<dir>/**` or `<dir>/**/*.md`, no other glob character — whose home is `<dir>/<stem>.md`;
- **a** **single file**, where creation is meaningless and the honest answer names the file;
- **a pattern with** **one free segment**, whose home follows once the segment is supplied.

A territory of two patterns, a negation, or a `*` inside a file name is a fourth class the kit does not have: no home follows.

How the surveyed tools map a kind to a location:

- **t1** takes the kind from the first segment of the path on the command line — `hugo new content posts/x.md` picks `archetypes/posts.md`, then `default.md`, and creates the parent ([content factory](https://github.com/gohugoio/hugo/blob/master/hugolib/content_factory.go));
- **t2's** folder rules map an existing folder to a template, "most specific (deepest) matching folder wins";
- **t3** has no directories — a schema's `pattern` is a glob over dot-hierarchy names;
- **t4** has one directory from `.adr-dir`, else `doc/adr`, created with `mkdir -p` ([`adr-new`](https://github.com/npryce/adr-tools/blob/master/src/adr-new));
- **t5** reads `project.adrFolder` from `.log4brains.yml` and errors on a missing folder;
- **t6** takes `-p PATH`, else `path` in `adr.config.json`, else the working directory;
- **t7 and t8** render a whole tree, the template being the kind;
- **t9 and t10** name the path in code;
- **t11** fixes `_posts/`, `_drafts/`, `_<collection>/` per command.

Every tool takes the directory as convention (t1, t4, t11), configuration (t2, t3, t5, t6) or code (t7–t10). None derives it from an enumerating pattern, because none has one — the territory is the kit's new element, and what makes design A possible.

The three designs against the kit's nine kinds:

- **A. Derive from the pattern when a home follows; otherwise refuse with a teaching message.** Covers c1, c2, c4, c5 mechanically; c6 with a `--segment` argument; c3, c7, c8, c9 as an honest refusal naming the single file. Nothing to configure; a home can never disagree with its territory. Cannot serve a fourth-class territory.
- **B. A per-kind `home` in the module's own dial.** Covers all nine and the fourth class. A second statement of where a kind lives, beside the territory: the two can drift, and the generator must check the home against the territory anyway — after which A's computation is what remains.
- **C. Ask the human.** Covers everything and proves nothing; the write is judged afterwards by [`const-meta-types`](../requirements.md#const-meta-types)' gate when installed, or by nothing. What the model did in E5 and what the kit's policies do today ("by hand from this document's shape").

The specification's optional dial, "default policy for otherwise-unclaimed governed roots": after [dec-0008-policies-by-location](../decisions/dec-0008-policies-by-location.md) a namespace is a policy's because its id has a document in the root's territory, a territory precedes its first document, and "Outside claimed territory the constitution is silent" ([kernel §3](../constitution/CONVENTIONS.md#k3)). A default policy for an unclaimed root would be a claim made outside the policy's namespace, which is the kernel's to hold. The dial has no meaning left; a document outside every territory is a kind without a policy, answered by section 5.

**Recommendation: A, with the one-segment extension and C as the refusal's named fallback — the generator derives the home for a directory-prefix territory, takes the free segment as an argument where the pattern has exactly one, and for a single-file or fourth-class territory prints what it cannot derive and why; every derived path is checked against the policy's territory through `git check-ignore` before anything is written. The optional dial is dropped.** B restates a territory in a second place. For the decider: whether a `home` override for a fourth-class territory only — absent for every kind of the kit — may sit in the module's namespace.

## 4. Where a kind's template lives

The kernel "specifies no internal policy format"; a policy's body "is prose for humans and agents" ([kernel §3](../constitution/CONVENTIONS.md#k3)).

Where the surveyed tools keep a template:

- **t1**, `archetypes/<kind>.md` by convention, then `default.md`, then a built-in;
- **t2**, a folder named in settings;
- **t3**, a `template:` key on the schema node — a policy-side key in the kit's terms;
- **t4**, `$ADR_TEMPLATE`, else `templates/template.md` beside the records, else the tool's own;
- **t5**, `template.md` inside the record folder;
- **t6**, a NuGet package or `templatePath` in its configuration;
- **t7–t10**, the template is the kind;
- **t11**, none — the front matter comes from `_config.yml` defaults.

Placeholders: Go templates in t1 (`{{ .Date }}`), `<% tp.file.title %>` in t2, Handlebars in t3 and t9, Jinja in t7 and t8, ERB in t10, `sed` over the words `NUMBER`, `TITLE`, `DATE`, `STATUS` in t4; t6 strips a YAML block and rewrites two headings by regular expression. A front matter block in the template is the norm wherever the tool's documents carry one.

The candidates, each against the kernel-alone test (a bare repository, no dials file), the kit's own three templates, and the fill:

- **A. A `template` key in the policy's namespace.** A module reads the policy namespaces "To resolve territory" and "reads no other module's namespace". The dials schema holds "the kernel-owned keys and the keys of a policy's namespace" ([kernel §6](../constitution/CONVENTIONS.md#k6)). A new key read there is a change to the schema and to that sentence — a kernel change, recorded always ([law 9 of CLAUDE.md](../../CLAUDE.md#law-9)). Kernel-alone: no dials, no key, the envelope only. The kit would write `template: module-template/MODULE.md` under the module-documents policy, a path into a sibling plugin under the records policy, and a new file for research. The natural reading — a policy declares its template — and the costliest.
- **B. A per-kind entry in the module's own namespace**, `const-locations: templates: [{policy: <id>, template: <repository-relative path>}]`, read by nobody else. Kernel-alone: absent, so the generator writes the four-field envelope with the fields it can fill and an empty body, and says so in its closing line. The kit's three:
  - `module-template/MODULE.md` for module documents;
  - **the record template** inside the `const-decision-records` plugin for records — a consumer's dial may name any file of its own repository, and for the kit that file lies inside a plugin;
  - **a template the kit writes once**, outside every territory, for research.

  Where the `lanes` of [`const-referencing`](../requirements.md#const-referencing) and the `catalogs` of [`const-catalogs`](../requirements.md#const-catalogs) already put project facts.
- **C. A convention beside the policy** — `<policy stem>.template.md` in the root's territory, or a `templates/` directory the dial names. The first fails on the kernel: a file in the root policy's territory *is a policy* ([kernel §3](../constitution/CONVENTIONS.md#k3)), and a template's envelope holds placeholders, so `const-meta-types` blocks it as a policy with an invalid envelope and `const-catalogs` as one without a number. The second is B with a fixed directory in place of a path per kind: fewer words, and a directory the consumer must create where B names files it has.
- **D. The policy body's own shape as the template.** What the kit does today and what the model did in E5: read the policy, infer the envelope and sections. Prose, not a template — nothing marks the placeholders — and [requirement A2.4](../requirements.md#a2-4)'s own words, "templates are outputs of commands, never exemplars to imitate", are written against exactly this. Kernel-alone it is all there is: the fallback of every other design, named as such.

The fill — what the generator supplies without judgment:

- `id` from the stem (one name for a numbered kind, [requirement A13.1](../requirements.md#a13-1); the catalog skill: "`id`: that file name without `.md`, exactly");
- `status: active` for a new document — a record "born `inactive`" ([kernel §5](../constitution/CONVENTIONS.md#k5)) is the record skill's later act;
- `title` from the human, an argument.

`type` is the one field it cannot derive: the policy states it in prose ("`non-authoritative`: a comparison informs a mechanism choice and binds nothing", [plc-0005-research](../policies/plc-0005-research.md) rule 1), so under B the template fixes the type, and with no template the generator takes it as an argument. The record template shows the placeholder shape the kit has: `<…>` prose, two body shapes parted by comments, the skill saying which to delete; substituting into `<…>` would need a vocabulary the kit has not defined, and every tool above has one. A numbered kind adds the number: it is `const-catalogs`' — its skill takes it "from the scan's count line" — and arrives inside the stem as an argument; this module hands over only home and template.

**Recommendation: B — a `templates` list in the module's own namespace, one entry per policy id, absent by default; with no entry the generator writes the four-field envelope from stem, title and a `type` argument, an empty body, and a closing line saying the kind has no template. Placeholders stay the record template's `<…>` prose, never substituted; the envelope fields the generator can fill are written as values.** A is a kernel change; C's first half the kernel refuses, its second is B with less; D is what B degrades to. For the decider: whether an entry may carry `type`, and whether the kit's record template should have one home under `docs/` with the record skill linking to it, rather than a dial pointing into a plugin.

## 5. The new-kind procedure ([requirement A2.5](../requirements.md#a2-5))

The sequence the kit's documents fix:

- **a kind without a policy** gets one first ([plc-0001-root-policy](../policies/plc-0001-root-policy.md), rule 5);
- **adding a policy** is `process` stakes — "a record in `docs/decisions/` and one human yes" (rule 3);
- **the policy** is a document in the root's territory with the envelope of rule 1;
- **its namespace** with a `territory` line in `constitution.yaml` claims the kind's paths (rule 2);
- **then the first document**, by section 1.

Four writes, three of them judged by other gates when installed — the record by [`const-decision-records`](../requirements.md#const-decision-records), the policy and the first document by `const-meta-types` — and the dials file, validated by every reader at each read ([kernel §6](../constitution/CONVENTIONS.md#k6)).

How the tools bootstrap a kind:

- **t4's** `adr init [DIR]` writes `.adr-dir` and the first record;
- **t5's** `log4brains init` creates configuration, template and a first record;
- **t6's** `adr environment init` creates `docs/adr`;
- **t1** needs a new `archetypes/<kind>.md`;
- **t3** a new `<name>.schema.yml` with `parent: root`;
- **t7–t10** a new template repository, generator or class;
- **t11** a `--collection` flag plus a configuration key.

Tools that hold one kind initialise it with a command that writes configuration and a first item. Tools that hold many add a file per kind and edit no configuration. The kit is the second shape — a policy document per kind — with one line of configuration from the first.

Should a script edit `constitution.yaml`? The kit's file carries eighteen comment lines, thirty-six inline comments, three anchors (`&policies`, `&decisions`, `&research`) and their aliases in the catalog entries. E1, on a copy:

- e1. **PyYAML 6.0.2, `safe_load` then `dump`.** Every comment gone; keys sorted unless `sort_keys=False`; the three aliased lists re-emitted as anchors under generated names `&id001`–`&id003`, so the file parses to the same data and reads as something else. Not a round trip.
- e2. **ruamel.yaml 0.19.1, round-trip loader, defaults.** Comments, anchor names and order preserved; 51 changed lines — every sequence item dedented by two columns, one long quoted string wrapped at the 80-column default, inline comments shifted.
- e3. **ruamel.yaml, tuned** — `indent(mapping=2, sequence=4, offset=2)`, `width=4096`: byte-identical; a namespace `plc-0010-notes: {territory: ["docs/notes/**"]}` inserted after the last policy changed nothing else, the flow style of the list asked for explicitly.
- e4. **A textual insertion** before the file's `# --- module namespaces` banner leaves every other byte alone and parses; it depends on a banner the module cannot know. The one portable place is the end of the file, where the model appended its namespace in every E5 policy run (`cat >> constitution.yaml`).

The costs of a generator edit: a second YAML library declared and preflighted (rule 7 of [template §6](../../module-template/MODULE.md#t6)) for an act that happens once per kind; indentation settings that reproduce the kit's file and may not reproduce a consumer's; a write to the one file every gate reads, where a slip is a configuration failure for all at once — inside a procedure that already has a human reading a record and a policy.

**Recommendation: the procedure is skill prose, the dials file edited by hand — the skill states the four steps in order, gives the exact namespace lines (id as key, a `territory` list, a pattern a directory-prefix home can be derived from), says the end of the file will do, and names the readers that validate it on the next write; no generator touches `constitution.yaml`.** e3 is recorded as the feasible path if a consumer reports the manual step failing; PyYAML is not one. Confirmed as advisory.

## 6. Always-on carrier

Does "a new document is born in its canonical home, from its template" need a `SessionStart` line, the kit's precedent being the fourth module's `print-chat-rule.sh`, or is the listing enough? The deciding case: an agent asked "write a policy for X".

- f1. **E5, four of four.** With nothing but the throwaway skill — no `SessionStart` hook, no `CLAUDE.md`, `--setting-sources project` so no user-level skill shared the listing — the model invoked the skill before writing in every run, on both prompts and both descriptions. Its first acts were always to list the repository and read `constitution.yaml`: the dials file made it look for a governed way to write, and the description was what it found. Four runs, one model, two prompts: a sample, not a proof; the platform's advice for the failing case is to "Strengthen the skill's `description`" or "use hooks to enforce behavior deterministically".
- f2. **What the listing shows** for a plugin skill:
  - **the** `init` message lists `loc-plugin:create-governed-document` among `slash_commands`;
  - **the name** is "Frontmatter `name` or the directory name, namespaced by plugin";
  - **the description** is "always in context" under the default fields (a7).
- f3. **A `SessionStart` line** costs its characters in every session and after every compaction to say what the listing says. The fourth comparison recommended one for a rule about *every chat message*, which no activity triggers. Creation has a trigger — the model is about to write — and E5 shows the trigger reaching the listing.
- f4. **What the listing cannot do:** reach a model that writes through the shell without looking (b6). In E5 the skill was invoked before the heredoc, so the heredoc followed the procedure; a `SessionStart` line would not change the tool choice either.

**Recommendation: no always-on content — the description is the carrier; "none" in the module's always-on slot, the description's size in characters stated in the module's document; confirmed as advisory.** Signal: a consumer session where a governed document was born outside the procedure with the plugin installed.

## 7. Fit with the shared gate code

Described, not decided; part names as in [kit-shared-gate-code §1](../../shared/GATE.md#g1).

- g1. **A generator on the mover's pattern.** The fourth module's `move-document.py` is the precedent: a thin entry file checking the interpreter floor and the presence of `scripts/const_gate`, then a package `main` with an `Identity` of its own, a parser whose usage error is a configuration failure, `preflight.check`, and only then its acts — under `cli.guarded(identity, Mode.ACT, body, closing)`, the same guard, exit codes and log, with a closing line of its own ([kit-shared-gate-code §2](../../shared/GATE.md#g2), item 1). What this module's body needs:
  - `pipeline.locate_scan` for the root and the dials;
  - `dials` for the kernel-owned keys and the policy territories, `Dials.own` for the `templates` list;
  - `index.build_index` inside `with Matcher() as matcher` — the [kernel §3](../constitution/CONVENTIONS.md#k3) lookup, which is how `--kind <policy id>` is checked to be a policy's id and not merely a namespace;
  - `Matcher.match` to prove that the derived home lies in exactly that policy's territory before the write;
  - `envelope` for a template's block;
  - `output` and `route_log`.

  Its own code: section 3's classes and derivation, section 4's fill, its messages.
- g2. **Prose only.** The skill tells the model to read `constitution.yaml`, find the policy, take the pattern's prefix. E5 shows this done correctly on a two-namespace file with plain lists. The kit's file has anchors, aliases, comments and a free-segment pattern, and the derivation becomes judgment exactly where a gate later judges it. Nothing proves the path before the write.
- g3. **POSIX shell.** Cannot read YAML ([dec-0015-pre-module-audit-rulings](../decisions/dec-0015-pre-module-audit-rulings.md)): a script that reads the dials file is Python 3 with PyYAML. Out.

The strains g1 would put on the shared code:

- s1. **No hook event.** No stdin event; `events` and `locate_write` unused, `locate_scan` serves. The mover runs this way already.
- s2. **No `severity`.** `dials` parses `severity` and `log_dir` for every namespace and defaults both. A module without a gate carries neither. The kit's dials file, which writes "every dial the kernel and the installed modules know", would hold its first namespace with no `severity` line.
- s3. **An argument that is a policy id, and a `type`.** `MetaType` is a shared closed vocabulary the `type` argument parses into; the policy id is checked against the index (g1). Neither is a shared change.
- s4. **A proof that is the generator's own.** The mover's acts end "by running the whole-tree check"; this module has no gate to end with. Its proof is the `Matcher` check of g1 and, as [requirement A2.4](../requirements.md#a2-4) says, its output "is caught by" `const-meta-types`' gates — an enhancement, never a dependency (section 8).
- s5. **A second entry point with no first.** `Identity` names a `gate`; the fixtures' `Subject` describes a gate's write that passes and one that blocks. A module that is only a generator hands the harness no gate: the shared items that drive one do not apply, and the acceptance list would say which — the widening [kit-shared-gate-code §1](../../shared/GATE.md#g1) allows "for a gate shaped differently", here for none. The links are owed anyway, though the rule says "A module that wires a hook owes the links".
- s6. **Writing a file.** The mover refuses "when the target exists"; the generator writes one new file and refuses likewise. A template read from a consumer path (section 4, B) is a file opened outside the plugin, under the shared `repository` root.

**Recommendation: g1 — a generator, `new-document.py` beside a POSIX wrapper, thin entry, `const_gate` linked, its own package, `Mode.ACT` under `cli.guarded`, arguments `--kind <policy id> --stem <stem> [--segment <segment>] [--type <meta-type>] [--title <text>]`, printing the derived home and policy on a `HOME:` line, writing the file from the template of section 4 or the envelope alone, refusing before any write when the kind is not a policy, the home cannot be derived, the path matches another policy, or the file exists.** Step down from the native option, named: no platform component reads YAML or evaluates a gitignore pattern. s2 and s5 are widenings that keep their rule for the other modules. s5's fixture shape and a `--dry-run` that prints the home and writes nothing — the mode the catalog skill's handoff (section 8) would call — are for the decider.

## 8. Sibling handoffs, as optional enhancements only

Described without deciding. Today:

- `const-decision-records` creates a record "From the template, never from a blank page or from another record" with its own `record-template.md`, and asks the number from `const-catalogs` when installed;
- `const-catalogs` numbers an item and says "If the project provides a template or a creation procedure for the kind, start from it and bring this number and this name to it";
- **its optional enhancement 3** expects `const-locations` to hand "the kind's home and template to the writing step of this module's skill".

Each is executable with the kernel alone: the record skill asks where records live when no dials file says, the catalog skill reads its own dial.

- h1. **The record skill creates; `const-locations` supplies the home.** The record skill keeps its template and body shapes. When `const-locations` is installed, its step "Where" reads the generator's `HOME:` line instead of the policy's territory as prose. Both executable alone; the template stays where its rules are.
- h2. **`const-locations` creates; the record skill supplies the template.** The kit's `templates` dial names the record template's path (section 4, B); the generator writes the file; the record skill fills `stakes`, `decider` and the body. Executable alone on both sides, but two writers of one file in one act, and a template that lives in one plugin and is named from another's dial.
- h3. **`const-catalogs` numbers; either supplies the stem.** The number is the catalog's; the stem `<prefix>-<nnnn>-<slug>` is composed by the catalog skill and handed as `--stem` to whichever creates. Its enhancement 3 reads naturally as h1 with the catalog skill in the record skill's place.
- h4. **What keeps every module executable alone:** all three, as long as the handoff is a stem in and a `HOME:` line out, never an import of another's code or a read of another's namespace ([law 3 of CLAUDE.md](../../CLAUDE.md#law-3)). h1 and h3 keep the *kind's rules* where they are owned and the *place* here. h2 makes this module the writer of every kind, [requirement A2.4](../requirements.md#a2-4)'s wording.

## 9. Platform facts, re-verified, and discrepancies

Re-verified today against the Markdown form of each page; quotations from the [skills](https://code.claude.com/docs/en/skills) page unless another is named:

- p1. **Skill frontmatter.** The twenty fields of a2; frontmatter is read "only when the opening `---` is the file's first line". Booleans accept more forms since v2.1.218 — a module keeps to `true` and `false`. Breaks: a field the module relies on disappearing.
- p2. **Path variables.** `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}` substituted in skill content and `allowed-tools` Bash rules; in plugin content "Anywhere the placeholder appears" for "Skill and agent content"; not in the Bash tool's environment ([plugins reference](https://code.claude.com/docs/en/plugins-reference)). Breaks: the skill's command line to the generator.
- p3. **Arguments.** `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N` 0-based, named `arguments`; an unreceived argument appended as `ARGUMENTS: <value>`. Breaks: `kind` and `stem`.
- p4. **Invocation control.** `disable-model-invocation`, `user-invocable` and their table; "If Claude tries anyway, Claude Code blocks the call". Breaks: the model-invocable creation.
- p5. **Listing.** Descriptions in context, bodies on invocation, 1,536 characters per entry, 1% of the context window, the two settings on the [settings reference](https://code.claude.com/docs/en/settings-reference). Breaks: section 6.
- p6. **`!` injection.** Runs before the content is sent; a non-zero exit "aborts the entire skill invocation"; permission checks first. Not used, on this fact.
- p7. **`PreToolUse` output.** `permissionDecision`, `permissionDecisionReason`, `updatedInput`, `additionalContext` ([hooks reference](https://code.claude.com/docs/en/hooks)); the second and fourth exercised on 2.1.251 (E3, E4). Not shipped.
- p8. **Several handlers.** "most restrictive answer applies"; `additionalContext` "kept from every hook"; `updatedInput` "the last one to finish takes effect" ([hooks guide](https://code.claude.com/docs/en/hooks-guide)).
- p9. **`SessionStart`.** Plain stdout added as context; matchers `startup`, `resume`, `clear`, `compact`, `fork`; runs in the background at launch while "Claude's first response still waits for the hooks to finish". No carrier recommended.
- p10. **Plugin layout and loading.** `commands/` is "Skills as flat Markdown files. Use `skills/` for new plugins". Components sit at the plugin root; `--plugin-dir` "Each flag takes one path" ([CLI reference](https://code.claude.com/docs/en/cli-reference)); for `--plugin-dir` "only symlinks that resolve within the plugin's own directory are preserved" ([plugins reference](https://code.claude.com/docs/en/plugins-reference)). The fourth comparison's observation that such a plugin ran in place was not re-observed today (the hook scripts wrote nothing beside themselves). Breaks: the `scripts/const_gate` link, held by shared limit 3.
- p11. **Skill permission rules** — added 2026-09-23, after a live finding on the module as built. "Permission syntax: `Skill(name)` for exact match, `Skill(name *)` for prefix match with any arguments"; an allow rule is matched "only against the skill's own name and the name in Claude's invocation", which for a plugin skill is the plugin-qualified name of f2; a rule that is the bare tool name, `Skill`, matches every use of the tool, as `Bash` "Matches all Bash commands" ([skills](https://code.claude.com/docs/en/skills), "Restrict Claude's skill access"; [permissions](https://code.claude.com/docs/en/permissions)). `allowed-tools` "grants permission for the listed tools during the turn that invokes the skill". The page says Claude Code "applies a project skill's `allowed-tools` whenever you or Claude invoke the skill, including in a `-p` run" ("Pre-approve tools for a skill"). For a plugin skill the model invoked in a `-p` run, the grant was not applied on 2.1.251 (E6). Whether a plugin skill is meant to differ from a project skill there is not documented. In a `-p` run, `dontAsk` "denies every call that would otherwise prompt", except what "`--allowedTools` entries or `permissions.allow` rules cover", and under `acceptEdits` "other shell commands and network requests still need an `--allowedTools` entry or a `permissions.allow` rule"; `--permission-prompts none` "requires Claude Code v2.1.259 or later" ([headless](https://code.claude.com/docs/en/headless)). Breaks: the model's own invocation of the creation skill in a session that cannot ask — the module's platform fact 7, its honest limit 10 and step 3 of its install note.

Stale, imprecise or missing in the four earlier comparisons, as they bear on this module:

- a. **Two frontmatter fields new to the kit's record:** `license` and `compatibility`, from the Agent Skills specification; "Claude Code accepts the field but doesn't act on it". The second comparison's list of eighteen is short by these. No design changes.
- b. **Argument indices.** No earlier comparison stated that `$0` is the first argument and `$1` the second; the brief for this survey wrote `$1` for the first. The page is unambiguous.
- c. **`effort` in the common input fields.** The fourth comparison's item l reported E17's payloads on 2.1.251 carrying "no `effort`". Today's `PreToolUse` payloads on the same version carried `effort: {level: high}` beside `prompt_id` and `permission_mode`, and still no `scratchpad_dir` (E3, E4). Whether the field appears only when an effort is set is not verified; a parser tolerates both.
- d. **The `!` form's failure mode** — "aborts the entire skill invocation" — was not in the earlier record. It decides against injecting a generator's output at load time (a4).
- e. **`updatedInput` racing** — "the last one to finish takes effect … non-deterministic" — was not in the earlier record (p8).
- f. **Skill `hooks`.** The second comparison listed the field. The [hooks reference](https://code.claude.com/docs/en/hooks) now says a skill's hooks are registered "when you or Claude invoke the skill" and kept "for the rest of the session", with `once: true` to drop one after its first run. A creation skill could register section 2's assist for the session that invoked it, blurring the class no less. Recorded, not recommended.
- g. **How the model writes.** No earlier comparison recorded that, given a free choice, the model created documents by shell heredoc rather than `Write` — six of six runs here (b6). The first three modules' gates on `Write|Edit` were sized on the platform's documentation of the tools. Shared limit 1 states the gap, and this survey is the first to measure how wide it is for creation.
- h. **`paths` glob budget.** The memory page states "one budget of 1,000 expanded patterns and 4 MiB" per rule's `paths` list, and that a `[` that is no bracket expression "matches nothing". The first comparison's "at most `**/*.md`" reading stands.

## Experiments

Each in a scratch directory outside any repository of the kit, except E2, which read the kit's `constitution.yaml` and wrote nothing; git 2.54.0, Python 3.12.4, PyYAML 6.0.2, ruamel.yaml 0.19.1 in a virtual environment, Claude Code 2.1.251.

- E1. A copy of the kit's dials file (6,440 characters, 107 lines: 18 comment lines, 36 lines with an inline comment, 3 anchors, 3 aliases). PyYAML `safe_load` + `dump`: 94 lines, no comments, keys sorted (`sort_keys=False` keeps loaded order), anchors renamed `&id001`–`&id003`. ruamel.yaml round-trip, defaults: comments, anchors and order kept, 51 changed lines. Tuned (`indent(mapping=2, sequence=4, offset=2)`, `width=4096`): byte-identical; a namespace inserted after the last policy: three added lines, nothing else changed; PyYAML reads the result. A textual insertion before the module-namespaces banner: parses, rest identical.
- E2. A 40-line prototype over the kit's `constitution.yaml`: nine policy namespaces classified into four directory prefixes, one free-segment pattern and four single files; each derived home probed with `git check-ignore --no-index` in a fresh null repository holding the territory as `.gitignore` — every probe matched its own pattern. Table c1–c9.
- E3. Live, non-interactive, a plugin with one `PreToolUse` handler on `Write` returning `additionalContext` for a new file under `docs/notes/`, the payload saved; consumer: `constitution.yaml` with a root policy and a notes policy, both documents present. Run 1, free tool choice: the note written by `cat <<'EOF'`, the hook silent, an envelope without `status`, `id` not the stem, a `date` field. Run 2, "Use the Write tool": the hook fired (payload fields as in section 9, item c), the context appeared beside the tool result, and the model's next call was an `Edit` setting `id` to the stem and `status: active` in place of `date`.
- E4. As E3 with a handler returning `updatedInput`. Run 1, free choice: heredoc, hook silent. Run 2, "Use the Write tool": the handler's own condition skipped the rewrite (the content already opened with `---`); the file kept `date` and an `id` unequal to the stem. Run 3, a handler rebuilding the envelope field by field and saying so in `additionalContext`: the file on disk carried `id` equal to the stem, `status: active`, no `date`; the model read it back with `sed` and reported the rewrite.
- E5. Live, non-interactive, `--setting-sources project`, a plugin holding one skill only (description 356 characters, body 876), on the E3 repository. Four runs, the prompts of a8. In each: `Bash` listing and reads, then `Skill` on the plugin's skill with the request as its argument, then one heredoc write at `docs/policies/test-naming-policy.md` or `docs/notes/<date>-<slug>.md` with a four-field envelope, `id` equal to the stem, the policy's body shape and a `LOCATIONS:` line; in the three policy runs a namespace appended to `constitution.yaml` by `cat >>`. Turns: 7, 8, 7, 7.
- E6. Added 2026-09-23, on Claude Code 2.1.251 and the same model: `claude -p` with `--output-format json`, the module as built loaded with `--plugin-dir`, `--setting-sources project`, on a scratch repository holding a root policy and a notes policy and no settings file; the prompt asked for a working note "Retry budgets" under `docs/notes/`; read from the result's `permission_denials` and the tree. Seven runs. `--permission-mode acceptEdits` alone: the model's `Skill` call on `const-locations:new-document` denied, twice, and the note written by hand with `type: current-state` — the wrong meta-type, the policy saying `non-authoritative` — the reply naming the guess. `--allowedTools "Skill(const-locations:new-document)"` without a Bash rule, three runs, one of them with `acceptEdits`: the skill loaded and its steps 1 and 2 were followed, then every call of `new-document.sh`, the `--dry-run` included, was denied ("This command requires approval") and the model stopped without writing, as the skill's step 5 asks; the same with the skill's `allowed-tools` rewritten to the plugin's literal absolute path, denied the same, so the placeholder is not the cause. Both rules, `Skill(const-locations:new-document)` and `Bash(sh <plugin root>/scripts/new-document.sh *)`: no denial, `CREATED:`, the four-field envelope with `type: non-authoritative`. The prompt typed as `/const-locations:new-document notes-policy retry-budgets` with no allow rule: no denial, the command ran under the skill's own `allowed-tools`, the note created. Turns: 15; 12, 10, 8; 8; 9; 9. Repeated the same day on fresh scratch repositories with the module at this change, three runs, `acceptEdits` in each:
  - **both rules**, no denial and `CREATED:` (12 turns);
  - **the** `Skill` rule alone, the command denied and nothing written (10);
  - **the typed form** with no rule, no denial and the note created (6).

## Recommendations summary

1. [Requirement A2.4](../requirements.md#a2-4), the creation surface — advisory **CONFIRMED**: one default skill, model- and user-invocable, with `kind` and `stem` as named arguments and the template read through the module's own dial; no command file, no agent, no `!` injection (a failed injection aborts the invocation, and a bare repository has nothing to inject). The model reached the skill from its listing in four of four live runs.
2. Hook-side assists — none, **CONFIRMED** as advisory with no hook: `additionalContext` at `PreToolUse` worked live and `updatedInput` rewrote the disk, but six of six free-choice runs wrote by shell heredoc where no handler fires, `const-meta-types` already holds the event, and a rewrite is neither block nor advice. Recorded as the candidate if a consumer reports envelopes born wrong through `Write` despite the skill.
3. The home — **build**: derived from the territory when it is a directory prefix (four of the kit's nine kinds), from the one free segment given as an argument (one kind), refused with a teaching message for a single-file territory (four kinds) or any other pattern; every home proved against the policy's territory by `git check-ignore` before the write. A per-kind `home` dial is not recommended. The specification's "default policy for otherwise-unclaimed governed roots" is **OVERTURNED** as meaningless after [dec-0008-policies-by-location](../decisions/dec-0008-policies-by-location.md).
4. The template — **build**: a `templates` list in the module's own namespace, one entry per policy id, absent by default, degrading to the four-field envelope alone; a policy-side key is a kernel change, a template beside the policy is refused by the kernel itself, the policy's prose is the fallback and never the template. The generator fills `id`, `status` and `title`; `type` comes from the template or an argument; the number is `const-catalogs`' and arrives in the stem.
5. [Requirement A2.5](../requirements.md#a2-5), the new-kind procedure — advisory **CONFIRMED**: skill prose in four steps, the dials file edited by hand with the exact lines given. A generator edit is feasible only with ruamel.yaml tuned to the file's layout (byte-identical on the kit's file, E1) and is not recommended for a once-per-kind act inside a `process`-stakes procedure. PyYAML is not a round-trip path.
6. Always-on carrier — "none" **CONFIRMED**: the skill description is the carrier, shown reaching the model in E5; no `SessionStart` line.
7. Shared code — a generator on the mover's pattern, `Mode.ACT` under `cli.guarded`, the index and the `Matcher` for the proof; strains: an own-namespace with no `severity`, a second entry point with no first, a proof that is the generator's own check rather than a gate's scan. Described only.
8. Sibling handoffs — three options described; each keeps every module executable alone when the handoff is a stem in and a `HOME:` line out. The record skill and the catalog skill keep their kinds' rules, this module the place.
9. Platform facts — p1 to p10 verified; eight items (a–h) missing or newly relevant in the earlier comparisons, one of which changes a design: the model's preference for shell writes on creation, which is why no hook is recommended and why the proof must be the generator's own. Added 2026-09-23: p11, the permission rules a model-invoked skill and its command need in a session that cannot ask (E6) — the recommendation of section 1 stands, with the consumer's allow rules named in the module's install note.
