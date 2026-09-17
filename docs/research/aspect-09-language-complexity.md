---
id: research-aspect-09-language-complexity
type: non-authoritative
title: Aspect 9: Language complexity — comparison (2026-08-28)
status: inactive
---

# Aspect 9: Language complexity — comparison (2026-08-28)

*Imported 2026-09-18 from the constitution design phase (research dated 2026-08-28). A dated snapshot, non-authoritative: it informed the traceability matrix and binds nothing; the matrix and the kernel hold what was decided. `D<n>` and `J<n>` cite that phase's decision register, which is not in this repository.*

**A. Native instruction, layered placement (native).** One line in root CLAUDE.md ("Write docs in plain English: short sentences, common words, no idioms — readable by non-native speakers"), with the fuller standard (target sentence length ~20 words, one idea per sentence, active voice, define terms on first use — essentially plainlanguage.gov / ISO 24495-1 distilled) in the styling-defaults doc, loaded lazily via .claude/rules/*.md with `paths: **/*.md` so any session touching docs gets it. Output styles are the wrong surface: main-conversation-only, invisible to authoring subagents. Maturity: this is just the verified native surface. Cost: ~1 always-on line + one lazy doc. Since the model writes the prose, instruction placement does nearly all the work.

**B. Repo script advisory metric (repo script).** ~40-line script computing avg sentence length + rough Flesch-Kincaid on changed .md, run in CI or a PostToolUse hook, warn-only, output labeled "proxy metric". Cost: tiny, zero dependencies. Weakness: hand-rolled syllable counting is crude; duplicates what Vale does better.

**C. Vale + Readability/write-good packages, advisory (third-party).** Vale (org `vale-cli`, active — core updated Jul 2026, action Aug 2026) with official-library packages: `Readability` (FK, SMOG, Coleman-Liau, LIX, Gunning fog etc. as per-file suggestion-level rules; low-churn ~12 commits but curated in the official library) and `write-good` (pattern rules: passive voice, wordy phrases, weasel words — more actionable than grade scores; proselint upstream is dormant, the Vale port survives in-library). Run in CI, warn-only, never exit-2. Cost: binary + release-URL pinning + .vale.ini + style sync; markdown syntax and code spans skew scores; grade formulas were built for graded schoolbook English and punish long-but-common technical words.

**D. Blocking readability gate (hooks + Vale).** Exit-2 PreToolUse/Stop hook on a grade threshold. Rejected: readability metrics are proxies; hard-gating them blocks legitimate technical prose and teaches metric-gaming (chopping sentences without gaining clarity).

**Recommendation: A alone as the baseline; add C (advisory-only) only if the human wants a deterministic signal.** Reasoning: plain-language output is a generation-time property — the cheapest, highest-leverage lever is the always-on line plus lazy detail where authoring happens. A deterministic check adds honest value only as a labeled advisory trend signal; per the settled findings Vale is the vehicle if wanted, and write-good's pattern rules deliver more per false positive than grade scores. B is strictly dominated by C.

**Open questions for the human:** (1) Is an advisory readability signal wanted at all, or is instruction-only sufficient? (2) If yes, CI-only or also a local warn-hook?
