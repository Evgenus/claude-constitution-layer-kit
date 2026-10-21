"""The founding lists and the Vale style the gate generates from its dials: one directory per run,
holding the configuration and the rule files, since Vale reads thresholds from rule files and the
kit reads them from the dials file. Nothing is synced or fetched: the rules are the module's own."""

from __future__ import annotations

from pathlib import Path

import yaml

from .model import STYLE, VALE_RULE_NAME, LanguageDials, Level, Rule

# Idioms and formal phrases a plain word does not replace one for one: said in plain words, or dropped.
FORBIDDEN: tuple[str, ...] = (
    "hit the ground running",
    "low-hanging fruit",
    "move the needle",
    "boil the ocean",
    "touch base",
    "circle back",
    "on the same page",
    "up to speed",
    "silver bullet",
    "at the end of the day",
    "needless to say",
    "it goes without saying",
    "as a matter of fact",
    "in the grand scheme of things",
    "when all is said and done",
    "a level playing field",
    "think outside the box",
    "the ball is in your court",
    "back to the drawing board",
    "bite the bullet",
    "cut corners",
    "get the ball rolling",
    "last but not least",
    "notwithstanding",
    "aforementioned",
    "heretofore",
    "hereinafter",
    "it should be noted that",
    "it is worth noting that",
    "it is important to note that",
)

# Words and phrases that have one plain word.
SIMPLER: dict[str, str] = {
    "prior to": "before",
    "subsequent to": "after",
    "in order to": "to",
    "utilize": "use",
    "utilise": "use",
    "leverage": "use",
    "commence": "begin",
    "terminate": "end",
    "endeavour": "try",
    "endeavor": "try",
    "facilitate": "help",
    "in the event that": "if",
    "with regard to": "about",
    "with respect to": "about",
    "in regard to": "about",
    "a number of": "some",
    "in excess of": "more than",
    "in the near future": "soon",
    "at this point in time": "now",
    "on a daily basis": "daily",
    "with the exception of": "except",
    "take into consideration": "consider",
    "in spite of the fact that": "although",
    "due to the fact that": "because",
    "in light of the fact that": "because",
    "for the purpose of": "to",
    "is able to": "can",
    "whilst": "while",
    "amongst": "among",
    "numerous": "many",
    "sufficient": "enough",
    "approximately": "about",
    "subsequently": "later",
}

# A form of "be" followed by a past participle: regular ones by their ending, the common irregular
# ones by name. Two words that only look like the shape — "is red", "is indeed" — are the honest limit
# of a pattern with no grammar, which is why the rule reports at warning by default.
PASSIVE_PATTERN = (
    r"\b(?:am|is|are|was|were|be|been|being)\s+(?:\w{2,}ed|given|taken|written|seen|known|shown|chosen"
    r"|driven|hidden|spoken|broken|frozen|forgotten|eaten|beaten|proven|fallen|stolen|forbidden|drawn"
    r"|thrown|grown|blown|flown|built|done|made|kept|left|lost|met|read|run|sent|set|told|thought"
    r"|brought|bought|caught|found|held|put|said|sold|won|begun|understood)\b"
)


def write_style(directory: Path, dials: LanguageDials) -> Path:
    """Writes the configuration and the style into `directory` and returns the configuration's
    path. A rule at `off` is not written; the levels of the rest are the dial's."""
    styles = directory / "styles" / STYLE
    styles.mkdir(parents=True)
    config = directory / "vale.ini"
    config.write_text(
        f"StylesPath = {directory / 'styles'}\nMinAlertLevel = suggestion\n[*.md]\nBasedOnStyles = {STYLE}\n",
        encoding="utf-8",
    )
    for rule, body in _rules(dials).items():
        level = dials.levels[rule]
        if level is Level.OFF:
            continue
        text = yaml.safe_dump({**body, "level": level.value}, sort_keys=False, allow_unicode=True)
        (styles / f"{VALE_RULE_NAME[rule]}.yml").write_text(text, encoding="utf-8")
    return config


def _rules(dials: LanguageDials) -> dict[Rule, dict[str, object]]:
    """Every rule's body without its level; the message is a bare placeholder, so the text the gate
    prints is the gate's own and the number, or the plain word, arrives alone."""
    return {
        Rule.GRADE: {
            "extends": "readability",
            "message": "%s",
            "grade": dials.grade_ceiling,
            "metrics": ["Flesch-Kincaid"],
        },
        Rule.SENTENCE: {
            "extends": "metric",
            "message": "%s",
            "scope": "sentence",
            "formula": "words",
            "condition": f"> {float(dials.sentence_words)}",
        },
        Rule.FORBIDDEN: {
            "extends": "existence",
            "message": "%s",
            "ignorecase": True,
            "tokens": list(dials.forbidden),
        },
        Rule.SIMPLER: {
            "extends": "substitution",
            "message": "%s",
            "ignorecase": True,
            "swap": dict(dials.simpler),
        },
        Rule.PASSIVE: {
            "extends": "existence",
            "message": "%s",
            "ignorecase": True,
            "raw": [PASSIVE_PATTERN],
        },
    }
