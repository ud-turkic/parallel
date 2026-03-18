"""Shared CoNLL-U parsing utilities for parallel treebank scripts.

Provides two levels of parsing:
  - parse_metadata(): fast, extracts only sent_id/text/text[en] + token counts
  - parse_tokens():   full parse, returns token-level fields for comparison
"""

import re
from pathlib import Path

FIELDS = [
    "id",
    "form",
    "lemma",
    "upos",
    "xpos",
    "feats",
    "head",
    "deprel",
    "deps",
    "misc",
]

_SENT_ID_RE = re.compile(r"# sent_id\s*=\s*(.+)")
_TEXT_RE = re.compile(r"# text\s*=\s*(.+)")
_TEXT_EN_RE = re.compile(r"# text\[en\]\s*=\s*(.+)")


def parse_metadata(filepath):
    """Parse a CoNLL-U file, extracting metadata and token counts per sentence.

    Returns a list of dicts with keys:
      sent_id, text, text_en, token_count, first_line, last_line
    """
    filepath = Path(filepath)
    sentences = []
    current = _new_meta()
    in_sentence = False

    with open(filepath, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.rstrip("\n")

            if not line.strip():
                if current["sent_id"] is not None:
                    current["last_line"] = line_num
                    sentences.append(current)
                    current = _new_meta()
                    in_sentence = False
                continue

            if line.startswith("# sent_id"):
                m = _SENT_ID_RE.match(line)
                if m:
                    current["sent_id"] = m.group(1).strip()
                    current["first_line"] = line_num
                    in_sentence = True
            elif line.startswith("# text[en]"):
                m = _TEXT_EN_RE.match(line)
                if m:
                    current["text_en"] = m.group(1).strip()
            elif line.startswith("# text"):
                m = _TEXT_RE.match(line)
                if m:
                    current["text"] = m.group(1).strip()
            elif not line.startswith("#") and in_sentence:
                fields = line.split("\t")
                if fields[0].isdigit():
                    current["token_count"] += 1

        if current["sent_id"] is not None:
            current["last_line"] = line_num
            sentences.append(current)

    return sentences


def parse_tokens(filepath):
    """Parse a CoNLL-U file into a dict of sent_id -> (text, token_lines).

    Each token_lines entry is the raw tab-separated line (for exact comparison).
    Returns: dict[str, tuple[str | None, list[str]]]
    """
    filepath = Path(filepath)
    sentences = {}
    current_lines = []
    current_sent_id = None
    current_text = None

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                if current_sent_id and current_lines:
                    sentences[current_sent_id] = (current_text, current_lines)
                    current_lines = []
                    current_sent_id = None
                    current_text = None
                continue
            if line.startswith("#"):
                m = _SENT_ID_RE.match(line)
                if m:
                    current_sent_id = m.group(1).strip()
                m = _TEXT_RE.match(line)
                if m:
                    current_text = m.group(1).strip()
            else:
                current_lines.append(line)

        if current_sent_id and current_lines:
            sentences[current_sent_id] = (current_text, current_lines)

    return sentences


def parse_metadata_dict(filepath):
    """Like parse_metadata but returns a dict keyed by sent_id.

    Convenient for lookups. Returns: dict[str, dict]
    """
    return {s["sent_id"]: s for s in parse_metadata(filepath)}


def _new_meta():
    return {
        "sent_id": None,
        "text": None,
        "text_en": None,
        "token_count": 0,
    }
