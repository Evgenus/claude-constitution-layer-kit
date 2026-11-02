# const-locations

<a id="a1"></a>
## What it gives you

Documents born in their canonical home: a command derives the home from the policy's territory, proves it resolves to exactly that policy, and writes the document from the kind's template with a valid envelope; a skill for creating documents through it and one for introducing a new kind — policy first, then territory, then document.

In plain words: a new document is created through a command, and a skill asks the session to use it instead of writing by hand. A kind is one sort of document, such as notes or records. A policy is the document that holds the rules for one kind. Its territory is the set of paths it claims, and the canonical home is the one place in that territory where a new document of the kind belongs. The command works that place out and puts the file there. It fills the file's envelope, the block of fields at the top (id, type, title, status), from the kind's template, the model file the project keeps for that kind. The other skill says what to do when no policy covers the new kind yet.

<a id="a2"></a>
## Why use it

A session is asked for a policy, a note or a record. It writes the file where the conversation happens to be looking: a new folder, the repository's root, beside the file it was reading. The file opens with whatever front matter the model saw last. It has a date field, an id that is not the file's name, or no status at all. Nothing ties it to a rule set, so nothing governs it. Its shape matches no sibling, so the next document of its kind copies it instead of the rule. Each one costs a move, an envelope repair and a link repair later, paid by someone who did not write it.

With the module installed, a session creates a governed document through the command. The file lands in the folder its policy names, with a valid header and the right template. Only then does the session write the body. For a kind that no policy covers, the second skill has the session create the policy first. Nothing here refuses a write: a document written by hand is not seen.

<a id="a3"></a>
## How Claude behaves with it

Nothing here refuses a write. When a session is about to create a governed Markdown document, the skill `new-document` loads on its own. It has the session run the module's command instead of writing the file by hand. The command reads the project's `constitution.yaml` and derives the home from the territory of the policy the session names. Before writing, it proves that the home lies in exactly that policy's territory, that nothing exists there, and that no document carries the id. Then it writes the file from the kind's template, when the project names one, with the id, the title and the status already filled. Without a template it writes the envelope alone. The session then fills the body. When the session names a kind no policy covers, the command refuses and says so. The second skill, `new-kind`, then takes over: the policy comes first, then its territory line in the dials file, then the first document.

```text
BROKEN: 'plc-nope' is not a policy: no document in the root policy's territory carries that id — fix: name one of: plc-notes, plc-records, plc-root; for a new kind, create its policy first — the new-kind procedure
BROKEN: the document could not be created — nothing was written
```

No session needs a permission rule for the skills or the command, not even one that cannot ask the user, such as a headless run. Plan mode is the one exception: there the command waits for the plan's approval. The module's hook approves its own command when the session runs it alone, with plain or single-quoted values. A command chained to another, or written another way, is asked for as any other.

<a id="a4"></a>
## How it works

**The command.** A script the session runs from inside the repository, with the policy's id, the file's stem and the title. It reads the root policy and the territories from `constitution.yaml`, and the optional list of templates per kind. It derives a home from three shapes of territory only. The shapes: a folder, a folder of Markdown files, or a folder with one free segment and a fixed file name. Any other shape gets an honest refusal that names the shapes that work. A dry run prints the home and the template and writes nothing. The command never checks or fills the body, never edits the dials file, and never takes a number for a numbered kind. That stem comes from the numbering procedure, and the command takes it as given. Every refusal happens before anything is written.

**What it cannot see.** It sees nothing it did not write. A document written without the command, through a shell, an editor or the `Write` tool, is not seen here at all. That is the job of the write-time guard of the envelope module, when it is installed. A document the command writes is no tool event either, so that guard sees it in its scan or at the next edit.

**The grant.** A hook that runs before each shell command that starts with `sh `. It approves one command: the module's own script, run alone, with values that are plain or in single quotes. For every other command it says nothing, and Claude Code asks as usual. It judges nothing and blocks nothing. A rule of yours that denies or asks for the command still wins over it. It reads no settings and no repository.

**The skill `new-document`.** A procedure in prose, loaded when a document is about to be created. It has the session name the kind, take the stem from where it is owned, run the command, and then fill the body from the template's placeholders. It reads the project's `constitution.yaml` and its policy documents. It cannot make a session follow it: the model may still write the file by hand.

**The skill `new-kind`.** A procedure in prose, loaded when a document is asked for that no policy covers, or when a repository has no `constitution.yaml` yet. It has the session price the new kind, create its policy through the command, add the territory line to the dials file by hand, and only then create the first document. It never edits the dials file for the session.

**Settings.** The module works with no configuration. Every kind whose territory has one of the three shapes gets its documents created with the envelope alone. One dial names the kinds that have a template, as pairs of a policy id and a path. The other names where the log goes. There is no loudness dial, since the module blocks nothing. A line that would mean nothing here is refused rather than kept in silence.

<a id="a5"></a>
## Get it

Install the shared Python package first, with the command in the module's [install note](plugin/INSTALL.md): the module's scripts import it and stop without it.

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>/plugin
```

Or install it from the kit's marketplace:

```bash
claude plugin install const-locations@claude-constitution-layer-kit --scope project
```

There is no scan: the module checks nothing after the fact. The command, from the project's root:

```bash
sh <plugin root>/scripts/new-document.sh --kind <policy id> --stem <stem> --title '<title>' --dry-run
```

The full install procedure and every dial are in [INSTALL.md](plugin/INSTALL.md). The complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
