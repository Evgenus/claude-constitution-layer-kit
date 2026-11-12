# const-questions

<a id="a1"></a>
## What it gives you

Ask only at recorded stakes or at a genuine blocker; else decide and note. One decision per message, in a fixed shape printed at every session start: lettered options with pros and cons, one recommendation, the decider named. Questions come from open slots, closed vocabularies are the options, defaults take an override, and vague input is restated. No open question inside a deliverable, with a gate on open-question markers in delivered documents.

In plain words: a session asks only when it must, and asks well when it does. A question is asked at recorded stakes. Recorded stakes mean a choice that sets a policy, a procedure, what a user sees or the structure of the work. So such a choice is worth a written record. It is also asked at a genuine blocker, which is a fact only the user holds, without which the work cannot go on. A smaller call is made at once and noted in the commit. The shape of a decision message is printed into every session: lettered options, pros and cons, one recommendation, the decider named. An open slot is a place in a template, a plan or a settings file that still waits for a value. The questions follow those slots in order. A closed vocabulary is a fixed list of allowed values, and it becomes the list of options. A default is the value used when nobody objects, so the question is "accept or override?". When a request is vague, the session first says how it read the request. A deliverable is a document handed over as finished. An open-question marker is a text such as `TODO` that says a question is still open. It is refused in a deliverable at the write.

<a id="a2"></a>
## Why use it

A session asks what it should have decided, and decides what it should have asked. Four questions arrive bundled in one message, each with no options and no recommendation. A question about where a scratch file goes blocks the work until it is answered. A request with two plausible readings is answered on one of them in silence. A delivered plan carries `TBD: who owns this` inside it. Once corrected, the opposite follows: every small uncertainty becomes a ceremony, until the person asked stops reading. Each correction is made in one session and lost with it.

With the module installed, every session starts with the shape of a decision message in its context. A choice reaches the user as lettered options with one recommendation. The skill decides first whether to ask at all; a small call is made and noted in the commit. A document with an open-question marker is refused at the write, so a plan is delivered with no marker left in it. Whether its decisions are resolved stays the skill's rule and the reviewer's.

<a id="a3"></a>
## How Claude behaves with it

At every session start, the shape of a decision message is added to the session's context. Options are lettered A, B, C. Each is a bullet with a one-sentence description and two indented sub-bullets, pros and cons, one line each. Then comes exactly one recommendation with its reasoning, and the decider is named. One decision per message, never a bundle. A one-fact clarification is a plain line. Before a session writes or edits a Markdown file, the file is checked for the texts that mark an open question, outside code. The default markers are `[decide:`, `TODO`, `TBD` and `FIXME`. A marker refuses the write, since a delivered document holds resolved decisions only.

```text
RED: docs/notes/plan.md:3: open question marker 'TBD' — TBD: who owns this
  why: a delivered document holds resolved decisions only: a marker left in it defers the question to a reader who may never see it
  fix: resolve the question in the text; if the decider is absent, replace the marker by a named blocker — 'blocked: <who> must decide <what>' — and halt that part; a draft whose own convention keeps markers until delivery is taken out of const-questions.territories by a negated pattern in constitution.yaml
```

The skill `ask-or-decide` loads before any message that puts a choice to the user. It decides whether the choice is the user's to make at all. A question is asked at recorded stakes, or at a genuine blocker, a fact only the user holds. Below that line the session makes the reasonable call and notes it in the commit. The skill takes the questions from the artifact's open slots, in order. It offers a closed vocabulary as the options where one exists, and proposes the default where one is sensible. It restates vague input before acting on it.

<a id="a4"></a>
## How it works

**At session start.** A hook prints the shape of a decision message, about 650 characters, into the session's context. It reads nothing and decides nothing, so no configuration changes it. It prints again after a resume, a compaction or a clear, when the earlier print is gone. It cannot see whether the session follows the shape.

**Before a write.** A hook runs before every `Write` and `Edit` of a Markdown file. It reads the file as it would be after the write and looks for the markers outside code spans and fenced blocks. A marker that begins or ends with a letter or a digit counts only as a whole word, so `TODOs` passes. A finding refuses the write. The hook cannot see a deferred question written in prose, with no marker. That is the skill's rule and the reviewer's.

**The scan.** The same check over every Markdown file git lists, from the command line, exit code 2 on a finding. Run it in CI and before a merge. It catches a file written by a shell command or another person, which the hook never sees.

**The skill.** A procedure in prose. Nothing in it blocks. Whether a question should have been asked, and the shape of the message, are judgment the skill shapes.

**Settings.** The module works with no configuration: every Markdown file git lists is covered, with the four markers above. One dial names the documents covered. A draft that keeps markers until it is delivered is taken out by a negated pattern there. Another dial names the marker texts. Two more are read by the skill alone: the project's own examples of what to ask and what to decide, and each decider's preferences. A decider's entry says what they want asked, what decided, and whether they pick by letter in chat or through the platform's question tool. Two dials are every gate's: how loud a finding is, and where the log goes.

<a id="a5"></a>
## Get it

Install the shared Python package first, with the command in the module's [install note](plugin/INSTALL.md): the module's scripts import it and stop without it.

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>/plugin
```

Or install it from the kit's marketplace: `claude plugin install const-questions@claude-constitution-layer-kit --scope project`. Then run the scan from the project's root:

```bash
sh <plugin root>/scripts/check-open-questions.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](plugin/INSTALL.md). The complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
