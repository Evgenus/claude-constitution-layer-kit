---
id: <style-guide — the id of this document; a stable kebab-case name, never changed afterwards>
type: current-state
title: Style guide — the defaults every governed document follows
status: active
---

# Style guide

The defaults every document of this repository follows unless a departure is declared for it. A default is a decision made once, so that no document decides it again; each is stated in one sentence and defined by its examples, a pair reading *departs / follows*. A departure is declared in the project's dials file, under `const-styling.departures`, naming the documents, the default departed from and the reason in one line — never in the document itself. A default is added here at the first concrete need, through the project's decision path, born with the document that needed it.

## Defaults

1. <a id="d1"></a>**Diagrams are Mermaid.** A diagram is a fenced block marked `mermaid`, which renders on GitHub, on GitLab and in editor previews with no server. PlantUML is used only where Mermaid cannot express the diagram, and the departure names the capability Mermaid lacks.
   - *Departs:* a sequence diagram in a fenced block marked `plantuml`, because the author knows PlantUML better.
   - *Follows:* the same sequence diagram in a fenced block marked `mermaid`.
   - *Departs:* a diagram kept as a PNG file drawn in a tool nobody else has.
   - *Follows:* a PlantUML block for a wireframe with salt widgets, declared as a departure with the reason "Mermaid has no wireframe diagram".
2. <a id="d2"></a>**Drawings made of characters are for trivial cases only.** A directory tree, an arrow between two names, a ruler of column widths: trivial, and kept as text in a fenced block marked `text`. Boxes and arrows that describe a flow, a hierarchy or a state machine of three or more parts are a diagram, and a diagram is Mermaid.
   - *Departs:* five boxes joined by arrows drawn with dashes and pipes, describing a request's path through services.
   - *Follows:* the same path as a Mermaid flowchart.
   - *Departs:* a state machine drawn with brackets and arrows in a fenced block.
   - *Follows:* a directory tree drawn with box-drawing characters in a fenced block marked `text`; `A -> B` written on one line to name a dependency.
3. <a id="d3"></a>**Pseudocode over formulas.** A computation is written as pseudocode in a fenced block, which every reader and every tool reads; a formula in a math block renders only in a web view and is invisible to a prose reader and to a linter.
   - *Departs:* a block between `$$` lines giving a rate as a fraction with subscripts.
   - *Follows:* three lines of pseudocode naming the inputs and the result.
   - *Departs:* an inline LaTeX expression for a threshold.
   - *Follows:* the threshold written in words and a code span: the limit is `max_size / 2`.
4. <a id="d4"></a>**Prose carries reasoning; a list carries items; a table carries rows of the same fields.** Prose says one thing at a time and holds an argument. A list holds items a reader will cite, each opening with a handle. A table is used only where every row has the same three or more fields and its first column is the row's key. One item is never a list, and an argument is never a table.
   - *Departs:* a paragraph of six sentences, each naming a different finding.
   - *Follows:* the six findings as a numbered list, one sentence each.
   - *Departs:* a list of one item.
   - *Follows:* the item as a sentence of the paragraph.
   - *Departs:* a table of two columns, "option" and "why", holding an argument.
   - *Follows:* the options as a lettered list, each with its reasons in prose.
   - *Departs:* a list where every item is "name — version — date — owner".
   - *Follows:* a table of four columns, the name first.
5. <a id="d5"></a>**Lists: dashes, numbers written out and counted on, one introducing sentence.** A bullet item opens with `- `. An ordered item carries the number the reader sees, each the one before it plus one, so that "item 3" is item 3 in the source; a list may start at any number and counts on from it. A list is introduced by one complete sentence, and each item is one sentence or one fragment, parallel in form.
   - *Departs:* items opening with `* ` in one list and `- ` in another.
   - *Follows:* `- ` everywhere.
   - *Departs:* every ordered item numbered 1.
   - *Follows:* 1, 2, 3, or 101, 102, 103.
   - *Departs:* "The steps:" followed by a list whose items are a verb phrase, then a full sentence, then a noun.
   - *Follows:* "The migration runs in three steps." followed by three items, each a sentence.
6. <a id="d6"></a>**Tables: a header row, the key first, `none` in an empty cell.** Every table has a header row and a delimiter row; every row has exactly the header's number of cells; the first column identifies the row; a cell that holds nothing says `none`, or the value that stands for nothing in that table, never emptiness or a dash.
   - *Departs:* a table whose first column is a description and whose last is the name.
   - *Follows:* the name first.
   - *Departs:* a cell left blank because the value does not apply.
   - *Follows:* `none` in the cell, or `n/a` where the table says so once.
   - *Departs:* a row with one cell fewer than the header, the last value dropped in rendering.
   - *Follows:* a cell per column, an escaped pipe `\|` for a pipe inside a cell.
7. <a id="d7"></a>**Headings: sentence case, one title, three levels at most, no skipped level.** A document has one level-one heading, its title; sections are level two; level three is the deepest; a heading is one level below the heading before it or steps back up; headings are in sentence case and carry no link and no code span beyond a name.
   - *Departs:* a second level-one heading half-way down the page.
   - *Follows:* a level-two heading there, or a second document.
   - *Departs:* a level-four heading for a note under a subsection.
   - *Follows:* a bold run-in label opening the paragraph: **Note on caching.** the paragraph.
   - *Departs:* a level-three heading directly under the title.
   - *Follows:* a level-two heading.
8. <a id="d8"></a>**Code font for what a reader types or a machine reads; every fenced block names its language.** A file name, a path, a command, a flag, a key, a value, an identifier, a message quoted from a tool: code span. A product name, a person, a concept: prose. A fenced block opens with its language after the fence — `bash`, `yaml`, `python`, `json`, `mermaid` — and with `text` for a directory tree, plain output or anything no highlighter should touch.
   - *Departs:* a fenced block opening with the fence alone.
   - *Follows:* the fence followed by `text`.
   - *Departs:* the flag --force written in prose without code font.
   - *Follows:* the flag `--force` in a code span.
   - *Departs:* "the `Git` tool" — a product name in code font.
   - *Follows:* "the git tool", or `git` where the command is meant.
9. <a id="d9"></a>**Bold for a run-in label or a handle; italic for a document's note about itself and a term at its first use; asterisks, never underscores.** Bold opens a paragraph or an item with its label or its handle, so a reader can point at it; italic marks a template's note to the writer, a document's note about its own status, and a term the sentence defines. Neither raises the voice: the words carry the emphasis. Emphasis is written with asterisks, since an underscore inside a name is text.
   - *Departs:* "this must **never** be done".
   - *Follows:* "this is never done", the word doing the work.
   - *Departs:* `_term_` with underscores.
   - *Follows:* *term* with asterisks; a name that carries underscores, such as `snake_case`, in a code span.
   - *Departs:* bold on a whole sentence.
   - *Follows:* bold on the label that opens it: **Limit.** the sentence.
10. <a id="d10"></a>**No callouts.** No note, tip, warning or caution box. An aside is a clause or a parenthesis in the sentence it belongs to; a warning about an act that cannot be undone is a sentence where the act is described, before the instruction that performs it.
    - *Departs:* an alert block opening with `[!WARNING]` above a command that deletes a directory.
    - *Follows:* "The command deletes the directory and nothing brings it back; move what matters out first." as the sentence before the command.
    - *Departs:* a blockquote opening with a bold "Note:" to hold a remark.
    - *Follows:* the remark as a sentence of the paragraph, or in parentheses.

## Departures and additions

A document that must depart from a default is not marked; the departure is an entry of the project's dials file, under `const-styling.departures`, naming the documents by path or by pattern, the defaults they depart from by their signature keys, and the reason in one line. The scan of the plugin reports a trace of a default in a document that no entry allows. A second document needing the same departure is the signal to widen the entry to the kind, or to change the default here.

A default not listed here is not a rule. When a document meets a question this page does not answer, the answer is made once, through the project's decision path, and added as the next numbered entry with its examples — never as a rule in one document or one template.
