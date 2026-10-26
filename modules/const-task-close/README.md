# const-task-close

<a id="a1"></a>
## What it gives you

Task close as a single act: a change that touches code covered by current-state documents updates them or declares no impact; a close procedure that merges deltas, deletes working files and sets the record inactive; and a dirty tree at turn end warned or blocked.

In plain words: a current-state document is a page that says how things are now. When code changes, the page that describes it changes in the same change, one reviewed set of commits. Otherwise a line in a commit declares no impact and says why. A skill closes a task as one act. It merges into those pages what the change made different, the deltas. It deletes the working files, the scratch files made for the task. It sets the task's record, the file that tracks the task, to inactive, which means the task is history. At the end of every turn, one reply of Claude, a dirty tree, which holds uncommitted changes, is reported. Under the default, louder setting the session is asked to commit what is finished. Under the quieter setting the user sees a notice.

<a id="a2"></a>
## Why use it

A change lands in the code, and the page that describes the code stays as it was. Nobody notices at the commit, because the page is in another file and still reads well. A reader finds it later, following the page into code that no longer does what it says. Now someone has to work out which of the two is true. A smaller loss of the same shape happens inside one session. Work done through the shell or a script is left uncommitted at the end of a turn. The chat's rewind cannot see it, and a later edit cannot be rolled back to it.

With the module installed, the range check reads the branch before a merge. It turns red on a pair whose code changed while its documents did not. A commit of the change can declare no impact on the pair, with a reason. In CI, the pull request's description can carry the line, when the project hands it to the check. At turn end, under the default, louder setting, a dirty tree is reported once and the session is asked to commit what is finished. The page and the code then move together, or the change says why the page stands.

<a id="a3"></a>
## How Claude behaves with it

The project lists, in `constitution.yaml`, pairs of code and the documents that describe it, its coverage map. With the module loaded, two things change. At the end of every turn, under the default, louder setting, a working tree with uncommitted changes or untracked files is reported once. The session is asked to commit what is finished. The turn then continues once for the commit. Under the quieter setting, the user sees a notice and the model nothing. And before a merge, the range check reads the commits of the branch. A pair whose code the change touches must have one of its documents among the changed files. Otherwise a commit of the change carries a line that declares no impact on that pair, with a reason a reviewer reads. In CI the line may stand in the pull request's description instead, when the project hands it to the check.

```text
RED: api: the change touches 1 path(s) this pair describes (src/a.py) and none of its document(s): docs/notes/api.md
  why: task close is a single act: code and the current-state documents that describe it change together, or the change says why the documents stand
  fix: update docs/notes/api.md in this change, or declare no impact: add the trailer "No-Doc-Impact: api — <why the documents are unaffected>" to a commit of the range, in its last paragraph, where every line is Key: value — or the same line on its own in the pull request's description, given to the scan with --body <file>
```

Two skills load on their own. `close-task` loads when a task, a branch or a pull request is being finished. It merges the deltas into the documents the map names and runs the range check. It deletes the task's working files, sets the task's record inactive, and commits the close as one change. `commit-before-edit` loads before the first edit of any change, and when a change is done. Commit first, commit after each coherent change, never end a turn dirty: git is the rollback layer, and the chat's rewind is not.

<a id="a4"></a>
## How it works

**At turn end.** A hook runs when the session's turn ends. It asks git whether the working tree is clean, and reports a dirty tree once per turn with the commit to make. Under the default, louder setting, it is a request the model weighs, not a wall: the second stop of a turn always lets it end. Under the quieter setting, it is a notice to the user alone. It does not fire on a user interrupt, and never in a session that has not loaded the plugin.

**At session start.** A hook prints one line that names the two skills and the moment each applies. It reads nothing and checks nothing; it only tells the session when to load a skill. It runs again after a resume, a compaction or a clear.

**At a subagent's start.** A second hook gives the same line to every subagent, since a subagent starts with a context of its own and does not see the first line. It checks nothing either.

**The scan.** The range check, run from the command line. On a branch it examines the commits since the trunk; on the trunk, the last landed change. For each pair of the map it compares the changed paths with the pair's code and documents. It reads the declaration lines from the commits' trailers, or from a file holding the pull request's description. It reports every pair that is neither updated nor declared. It compares commits, so an update still sitting uncommitted in the tree does not count. It holds that a declaration is present, well formed and names a pair. Whether the reason is true stays with the reviewer, and every declaration used is printed for them.

**The skill `close-task`.** A procedure in prose for the close of a task: name what the change owes, merge the deltas, declare no impact only where it is true, delete the working files, set the record inactive, commit as one change, and check again. It checks nothing. The module names it at session start, at each subagent's start and after every red of the scan, so it is loaded when a task is being finished.

**The skill `commit-before-edit`.** A procedure in prose for committing first: commit a dirty tree before the first edit of any change, commit again after each coherent change, never end a turn dirty, and roll back through git. It checks nothing. The module names it in the same places and after every red of the turn-end hook.

**Settings.** The module works with no configuration in a repository that has a `constitution.yaml` naming `module_prefix: const-` at least. The turn-end hook then judges the tree, and the range check examines zero pairs and says so. With no such file, the hook and the scan skip, and each says so. The coverage map switches the range check on. Other dials name the trunk branch and the remote whose copy of it is read. Two more name the key of the declaration line, and patterns of a task's working files. The scan lists such files while they are still tracked. Two dials are every gate's: how loud the turn-end finding is, and where the log goes.

<a id="a5"></a>
## Get it

Install the shared Python package first, with the command in the module's [install note](plugin/INSTALL.md): the module's scripts import it and stop without it.

For one session, from a clone of the kit:

```bash
claude --plugin-dir <path to this module>/plugin
```

Or install it from the kit's marketplace: `claude plugin install const-task-close@claude-constitution-layer-kit --scope project`. Then run the range check from the project's root, on a branch:

```bash
sh <plugin root>/scripts/check-task-close.sh --scan
```

The full install procedure and every dial are in [INSTALL.md](plugin/INSTALL.md). The complete description of the module, with its rules, its messages and its limits, is [MODULE.md](MODULE.md).
