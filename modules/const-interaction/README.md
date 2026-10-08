# const-interaction

<a id="a1"></a>
## What it gives you

Answer in the shape the question has, the answer first; every assumption listed, every list item addressable; honesty over agreement; stop before a hard-to-reverse act and wait for a yes, with a gate on enumerated destructive commands.

In plain words: nine rules for every reply are printed into every session, and one of them has a gate. The rules say how to answer: the answer first, assumptions listed, every item citable, findings never softened, no hard-to-reverse act without a yes. The gate stops a listed destructive shell command until you confirm it.

<a id="a2"></a>
## Why use it

A short question is answered by a page. A yes-or-no question opens with three paragraphs of context, and the word arrives at the end, if at all. The assumption that made the answer possible is never said, so the user cannot correct it. A list of findings has no handles, so the user quotes a sentence to point at one. A request that is wrong is carried out with a softened note. A failure is reported as done because nobody checked. And a forced push, a hard reset or a recursive delete stays one keystroke away from a session that never learned the rule.

With the module installed, every session starts with the nine rules in its context. A yes-or-no question gets its word first. An assumption is written down where the user can correct it, and a list of findings carries handles. A forced push or a hard reset stops at a prompt that names the risk and the safer alternative. A scan finds the list items with no handle in the project's documents.

<a id="a3"></a>
## How Claude behaves with it

At every session start, nine rules for every reply are added to the session's context, about 2,400 characters. The reply matches the shape the question asks for: a yes-or-no question is answered with the word first. The answer stands first, and the elaboration follows only when asked. Every assumption is listed under its own heading, and one that would change the work is a question. A wrong or unreasonable request is said to be so. A failure is never hidden, and unverified work is never reported as done. Every list, table and option set carries a stable handle per item. A gap in the rules is a routine call noted in the commit, or, at recorded stakes, a question. A procedure the project has not written is never invented on the spot. Before a hard-to-reverse act, the consequence and the reversible alternative are stated and a yes is waited for. And chat is plain language for a reader whose first language is not English.

One of those rules has a gate. Before every shell command, the command is read. Where it matches an entry of the destructive list, the platform asks you to confirm. The default list has fourteen entries, a forced push and a hard reset among them. The prompt shows why the act is hard to reverse and what the reversible alternative is. You confirm once per command. Where no prompt can be shown, in a headless session, the command is denied with the same reason. The model then waits for a yes in chat.

```text
RED: destructive command: 'git push --force origin main' matches the entry git push with --force
  why: a forced push rewrites the branch on the remote: every other clone of it diverges, and the commits it replaced are unreachable there
  fix: push with --force-with-lease, which refuses when the remote moved, or push a new branch and open a pull request; to run it as written, confirm at the prompt — where no prompt can be shown, get the user's yes in chat and run it again, one yes per command; to stop gating it, remove the entry from const-interaction.destructive in constitution.yaml
```

A second check holds the handle rule for documents. A scan reports every bulleted list item in the project's Markdown files that opens with no handle: a number, a letter or a short key.

<a id="a4"></a>
## How it works

**At session start.** A hook prints the nine rules into the session's context. Then it prints one line naming how much a reply says beyond its answer. It prints one line when the destructive list is empty, so a gate that examines nothing is never silent. And it prints one line for each default wrapper or shell the project's dials drop or replace.

**Before a shell command.** A hook runs before every command of the platform's `Bash` tool. It splits the command as the platform does, on `&&`, `;`, `|` and the rest, and looks inside `$(…)`. It strips wrappers such as `sudo`, `env` and `time`, and reads the string a shell such as `bash -c` is told to run. It steps over a program's options to find its verb. Where a piece matches an entry, it answers the platform with the entry's teaching text and the ask decision. It cannot see a command built from a variable, an `eval`, a script file that deletes, or a deletion through a file tool. Nor can it see an argument the entries cannot name, such as `git checkout -- .`. The list is the gate; the class is the rule. An explain mode shows the reading of any command without running it.

**The list scan.** A command-line scan over every Markdown file git lists, exit code 2 on a finding. It reads a grammar: the handle forms are patterns. A project whose documents key items by a bold label or a link adds those forms.

**Settings.** The module works with no configuration: the default destructive list, the default wrappers and shells, every Markdown file, and six handle forms. One dial replaces the destructive list; an empty list gates nothing and says so at every session start. Two dials add or drop a wrapper or a shell. Two name the documents the list scan reads and the handle forms. One adds the project's own examples of a bad reply beside a good one, printed at session start. One sets how much a reply says beyond its answer. Two dials are every gate's: how loud a match is, and where the log goes. The quieter setting reports the match and lets the command run.

<a id="a5"></a>
## Get it

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>
```

Or install it from the marketplace the kit's install guide names: `claude plugin install const-interaction@<marketplace name> --scope project`. Then run the list scan from the project's root:

```bash
sh <plugin root>/scripts/check-list-handles.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](INSTALL.md). The complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
