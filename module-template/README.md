# const-<aspect>

*Template. Every module ships this page beside its `INSTALL.md`: the module's landing page for a reader on GitHub, of the same kind as the kit's root README — user-facing, informational, in no policy's territory, with no envelope, binding nothing. It is written in plain language for a reader whose first language is not English, in short sentences, each term defined where it is first used; it restates no requirement row, cites no row number, no decision and no error-code handle, and links nothing of the kit beyond the module's own `INSTALL.md` and `MODULE.md`. Each heading carries its anchor, `a1` to `a5`. Every list and table row carries a handle. The page links only inside its own folder, so a copy keeps its links; a link that left the folder would gain one `../` level in the copy, as the links of the template's other documents do. Delete this note.*

<a id="a1"></a>
## What it gives you

One plain sentence: the manifest's `description`, copied as written, so that the two never differ.

<a id="a2"></a>
## Why use it

The problem in the user's own terms: what goes wrong in a project without the module, in two or three sentences, with no kit vocabulary a reader has not been given.

<a id="a3"></a>
## How Claude behaves with it

What a session does differently with the module loaded: what is refused and what the refusal says, what is added at session start, which skill or command appears and when, what the scan reports. Prose, plus one short real message of the module in a `text` fence, taken from the module's own message tables or from a run of its fixture — a message the module really prints.

<a id="a4"></a>
## How it works

One paragraph per tool the module ships, each opening with a bold label: each hook by its event — before a write, after a write, at session start, at turn end, before a shell command — the scan, each skill, each command or second entry point. Each says what the tool reads, what it decides, what it cannot see, and that the defaults work with no configuration; the dials are named in words, what can be tuned, never as a table. No file paths, no row numbers, no error-code handles, no decision numbers.

<a id="a5"></a>
## Get it

The install line for one session, `claude --plugin-dir <path to this module>`, and the marketplace form; the module's own scan command, `sh <plugin root>/scripts/<entry>.sh --scan`, or the command for a module with no scan; and one closing line: the full install procedure and every dial in [INSTALL.md](INSTALL.md), the complete description in [MODULE.md](MODULE.md).
