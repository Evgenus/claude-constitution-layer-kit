# const-questions

<a id="a1"></a>
## What it gives you

Ask only at recorded stakes or a genuine blocker, else decide and note; one decision per message in a fixed shape — lettered options with pros and cons, one recommendation, the decider named — printed at every session start; questions derived from open slots, closed vocabularies as the options, defaults with override, vague input restated; no open question inside a deliverable, with a gate on open-question markers in delivered documents.

<a id="a2"></a>
## Why use it

A session asks what it should have decided, and decides what it should have asked. Four questions arrive bundled in one message, each with no options and no recommendation. A question about where a scratch file goes blocks the work until it is answered. A request with two plausible readings is answered on one of them in silence. A delivered plan carries `TBD: who owns this` inside it. Once corrected, the opposite follows: every small uncertainty becomes a ceremony, until the person asked stops reading. Each correction is made in one session and lost with it.

<a id="a3"></a>
## How Claude behaves with it

At every session start, the shape of a decision message is added to the session's context: options lettered A, B, C, each a bullet with a one-sentence description and two indented sub-bullets, pros and cons, one line each; then exactly one recommendation with its reasoning, and the decider named. One decision per message, never a bundle. A one-fact clarification is a plain line. Before a session writes or edits a Markdown file, the file is checked for the texts that mark an open question, `[decide:`, `TODO`, `TBD` and `FIXME` by default, outside code; a marker refuses the write, since a delivered document holds resolved decisions only.

```text
RED: docs/notes/plan.md:3: open question marker 'TBD' — TBD: who owns this
  why: a delivered document holds resolved decisions only: a marker left in it defers the question to a reader who may never see it
  fix: resolve the question in the text; if the decider is absent, replace the marker by a named blocker — 'blocked: <who> must decide <what>' — and halt that part; a draft whose own convention keeps markers until delivery is taken out of const-questions.territories by a negated pattern in constitution.yaml
```

The skill `ask-or-decide` loads before any message that puts a choice to the user. It decides whether the choice is the user's to make at all: a question is asked at recorded stakes or at a genuine blocker, a fact only the user holds; below that line the session makes the reasonable call and notes it in the commit. It takes the questions from the artifact's open slots in order, offers a closed vocabulary as the options where one exists, proposes the default where one is sensible, and restates vague input before acting on it.

<a id="a4"></a>
## How it works

**At session start.** A hook prints the shape of a decision message, about 650 characters, into the session's context. It prints again after a resume, a compaction or a clear, when the earlier print is gone.

**Before a write.** A hook runs before every `Write` and `Edit` of a Markdown file. It reads the file as it would be after the write and looks for the markers outside code spans and fenced blocks; a marker that begins or ends with a letter or a digit counts only as a whole word, so `TODOs` passes. A finding refuses the write. It cannot see a deferred question written in prose, with no marker, which is the skill's rule and the reviewer's.

**The scan.** The same check over every Markdown file git lists, from the command line, exit code 2 on a finding. Run it in CI and before a merge; it catches a file written by a shell command or another person, which the hook never sees.

**The skill.** A procedure in prose. Nothing in it blocks; whether a question should have been asked, and the shape of the message, are judgment the skill shapes.

**Settings.** The module works with no configuration: every Markdown file git lists is covered, with the four markers above. Dials name the documents covered, where a draft that keeps markers until it is delivered is taken out by a negated pattern, and the marker texts. Two more are read by the skill alone: the project's own examples of what to ask and what to decide, and per decider what they want asked, what decided, and whether they pick by letter in chat or through the platform's question tool. Two dials are every gate's: how loud a finding is, and where the log goes.

<a id="a5"></a>
## Get it

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>
```

Or install it from the marketplace the kit's install guide names: `claude plugin install const-questions@<marketplace name> --scope project`. Then run the scan from the project's root:

```bash
sh <plugin root>/scripts/check-open-questions.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](INSTALL.md); the complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
