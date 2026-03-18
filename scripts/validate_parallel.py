#!/usr/bin/env python3
"""Validate parallel treebank consistency across languages.

Checks that go beyond single-file UD validation:
  - Sentence ID consistency across all files
  - Sentence ID format (cairo-N, udtw23-N, N)
  - Required metadata (# text, # text[en])
  - Token count outliers across translations of the same sentence

Usage:
    python scripts/validate_parallel.py                     # validate all
    python scripts/validate_parallel.py data/tr_*.conllu    # specific files
    python scripts/validate_parallel.py --strict            # fail on warnings too
"""

import argparse
import re
import sys
from pathlib import Path

from conllu import parse_metadata

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SENT_ID_RE = re.compile(r"^(cairo-\d+(\.\d+)?|udtw23-\d+(\.\d+)?|\d+(\.\d+)?)$")


class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    @property
    def ok(self):
        return len(self.errors) == 0

    def summary(self):
        lines = []
        for e in self.errors:
            lines.append(f"  ERROR: {e}")
        for w in self.warnings:
            lines.append(f"  WARN:  {w}")
        return "\n".join(lines)


def validate_single_file(filepath, result):
    """Per-file checks: sent_id format, metadata presence, duplicates."""
    sentences = parse_metadata(filepath)
    name = filepath.name

    if not sentences:
        result.error(f"[{name}] No sentences found")
        return sentences

    seen_ids = {}
    for sent in sentences:
        sid = sent["sent_id"]
        line = sent.get("first_line", "?")

        # Duplicate sent_id
        if sid in seen_ids:
            result.error(
                f"[{name}:{line}] Duplicate sent_id '{sid}' (first at line {seen_ids[sid]})"
            )
        else:
            seen_ids[sid] = line

        # sent_id format
        if not SENT_ID_RE.match(sid):
            result.warn(f"[{name}:{line}] Non-standard sent_id format: '{sid}'")

        # Missing # text
        if sent["text"] is None:
            result.error(f"[{name}:{line}] Missing '# text' for sent_id '{sid}'")

    return sentences


def validate_cross_file(file_sentences, result, token_ratio_threshold=3.0):
    """Cross-file checks: ID consistency, English translations, token count outliers."""
    if len(file_sentences) < 2:
        return

    # Collect all IDs per file and globally
    all_ids = set()
    file_ids = {}
    for filepath, sentences in file_sentences.items():
        ids = {s["sent_id"] for s in sentences}
        file_ids[filepath.name] = ids
        all_ids |= ids

    # Check which files are missing which IDs
    for name, ids in file_ids.items():
        missing = all_ids - ids
        if missing:
            # Group into ranges for readability
            missing_sorted = sorted(missing)
            if len(missing_sorted) <= 10:
                missing_str = ", ".join(missing_sorted)
            else:
                missing_str = f"{len(missing_sorted)} sentences (e.g. {', '.join(missing_sorted[:5])}...)"
            result.warn(f"[{name}] Missing {missing_str}")

    # Check for English translations (at least one file should have them for shared IDs)
    has_english = {}
    for filepath, sentences in file_sentences.items():
        for sent in sentences:
            sid = sent["sent_id"]
            if sent["text_en"]:
                has_english[sid] = filepath.name

    ids_without_english = all_ids - set(has_english.keys())
    if ids_without_english:
        count = len(ids_without_english)
        if count <= 5:
            result.warn(
                f"No English translation for: {', '.join(sorted(ids_without_english))}"
            )
        else:
            result.warn(f"No English translation for {count} sentences")

    # Token count outlier detection
    token_counts = {}  # sid -> {filename: count}
    for filepath, sentences in file_sentences.items():
        for sent in sentences:
            sid = sent["sent_id"]
            if sid not in token_counts:
                token_counts[sid] = {}
            token_counts[sid][filepath.name] = sent["token_count"]

    for sid, counts in token_counts.items():
        if len(counts) < 2:
            continue
        values = list(counts.values())
        min_count = min(values)
        max_count = max(values)
        if min_count > 0 and max_count / min_count > token_ratio_threshold:
            details = ", ".join(f"{name}={c}" for name, c in sorted(counts.items()))
            result.warn(
                f"Token count outlier for '{sid}': {details} (ratio {max_count / min_count:.1f}x)"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Validate parallel treebank consistency"
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="CoNLL-U files to validate (default: all in data/)",
    )
    parser.add_argument(
        "--strict", action="store_true", help="Exit with error on warnings too"
    )
    parser.add_argument(
        "--token-ratio",
        type=float,
        default=3.0,
        help="Token count ratio threshold for outlier detection (default: 3.0)",
    )
    args = parser.parse_args()

    files = args.files or sorted(DATA_DIR.glob("*.conllu"))
    if not files:
        print("No CoNLL-U files found")
        sys.exit(1)

    result = ValidationResult()
    file_sentences = {}

    print(f"Validating {len(files)} parallel treebank files...\n")

    for filepath in files:
        filepath = Path(filepath)
        if not filepath.exists():
            result.error(f"File not found: {filepath}")
            continue
        sentences = validate_single_file(filepath, result)
        file_sentences[filepath] = sentences

    validate_cross_file(file_sentences, result, args.token_ratio)

    # Print results
    if result.errors or result.warnings:
        print(result.summary())
        print()

    n_err = len(result.errors)
    n_warn = len(result.warnings)
    print(
        f"{len(files)} files, {sum(len(s) for s in file_sentences.values())} sentences"
    )
    print(f"{n_err} errors, {n_warn} warnings")

    if n_err > 0:
        print("\n*** FAILED ***")
        sys.exit(1)
    elif args.strict and n_warn > 0:
        print("\n*** FAILED (strict mode) ***")
        sys.exit(1)
    else:
        print("\n*** PASSED ***")
        sys.exit(0)


if __name__ == "__main__":
    main()
