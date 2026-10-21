# const-<aspect>

*Template. Every module has this page at the top of its folder, beside the `plugin/` folder that holds its `INSTALL.md`, as its landing page for a reader on GitHub. It is of the same kind as the kit's root README: user-facing, informational, in no policy's territory, with no envelope, binding nothing. It is written in plain language for a reader whose first language is not English. Sentences are short, and each term is defined where it is first used. It restates no requirement row and cites no row number, no decision and no error-code handle. It links nothing of the kit beyond the module's own `INSTALL.md` and `MODULE.md`. Each heading carries its anchor, `a1` to `a5`. Every list and table row carries a handle. The page links only inside its own folder, so a copy keeps its links. A link that left the folder would gain one `../` level in the copy, as the links of the template's other documents do. Delete this note.*

<a id="a1"></a>
## What it gives you

The manifest's `description`, copied as written, so that the two never differ. Then one short paragraph, opening "In plain words". It says what the module does in the reader's own words: what is checked, what is refused, what a skill brings.

<a id="a2"></a>
## Why use it

The problem in the user's own terms: what goes wrong in a project without the module, in two or three sentences. No kit vocabulary a reader has not been given. Then a second paragraph, opening "With the module installed". It says how the problem is resolved: what is refused, what is reported, what a session does differently, and what the reader gains.

<a id="a3"></a>
## How Claude behaves with it

What a session does differently with the module loaded. What is refused and what the refusal says; what is added at session start; which skill or command appears and when; what the scan reports. Prose, plus one short real message of the module in a `text` fence. The message is taken from the module's own message tables or from a run of its fixture: one the module really prints.

<a id="a4"></a>
## How it works

One paragraph per tool the module ships, each opening with a bold label. Each hook by its event: before a write, after a write, at session start, at turn end, before a shell command. Then the scan, each skill, each command or second entry point. Each paragraph says what the tool reads, what it decides, what it cannot see, and that the defaults work with no configuration. The dials are named in words, what can be tuned, never as a table. No file paths, no row numbers, no error-code handles, no decision numbers.

<a id="a5"></a>
## Get it

The install line for one session, `claude --plugin-dir <path to this module>/plugin`, and the marketplace form. The module's own scan command, `sh <plugin root>/scripts/<entry>.sh --scan`, or the command for a module with no scan. One closing line: the full install procedure and every dial in [INSTALL.md](plugin/INSTALL.md), the complete description in [MODULE.md](MODULE.md).
