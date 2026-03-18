#!/usr/bin/env python3
"""Compare local parallel treebank files against their published UD counterparts.

Fetches the latest version of each TueCL treebank from the UniversalDependencies
GitHub organization and compares it token-by-token against the local file.

Usage:
    python scripts/compare_with_published.py                    # compare all
    python scripts/compare_with_published.py --lang tr az       # specific languages
    python scripts/compare_with_published.py --fetch-only       # just download, no diff
    python scripts/compare_with_published.py --cache-dir /tmp   # custom cache directory
"""

import argparse
import sys
import urllib.request
import collections
from pathlib import Path

from conllu import FIELDS, parse_tokens

# Language code -> UD repo name
PUBLISHED_TREEBANKS = {
    "az": "UD_Azerbaijani-TueCL",
    "ky": "UD_Kyrgyz-TueCL",
    "tr": "UD_Turkish-TueCL",
    "uz": "UD_Uzbek-TueCL",
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def fetch_published(lang_code, repo_name, cache_dir):
    """Fetch a published CoNLL-U file from GitHub, with caching."""
    filename = f"{lang_code}_tuecl-ud-test.conllu"
    cached = cache_dir / filename
    if cached.exists():
        return cached

    url = f"https://raw.githubusercontent.com/UniversalDependencies/{repo_name}/master/{filename}"
    print(f"  Fetching {url}")
    try:
        urllib.request.urlretrieve(url, cached)
    except urllib.error.HTTPError as e:
        print(f"  Failed to fetch {filename}: {e}", file=sys.stderr)
        return None
    return cached


def compare_sentences(local_sents, published_sents):
    """Compare two parsed treebanks sentence by sentence.

    Returns a dict with:
      - only_local, only_published: list of sent_ids
      - common: number of shared sentences
      - identical: number of identical sentences
      - changed: list of (sent_id, changes) where changes is a list of token diffs
    """
    local_ids = set(local_sents)
    pub_ids = set(published_sents)
    common_ids = sorted(local_ids & pub_ids)

    result = {
        "only_local": sorted(local_ids - pub_ids),
        "only_published": sorted(pub_ids - local_ids),
        "common": len(common_ids),
        "identical": 0,
        "changed": [],
        "field_counts": collections.Counter(),
    }

    for sid in common_ids:
        local_text, local_lines = local_sents[sid]
        pub_text, pub_lines = published_sents[sid]

        if local_lines == pub_lines:
            result["identical"] += 1
            continue

        changes = []

        # Token count mismatch
        if len(local_lines) != len(pub_lines):
            changes.append(
                {
                    "type": "token_count",
                    "local": len(local_lines),
                    "published": len(pub_lines),
                }
            )
            result["changed"].append((sid, local_text or pub_text, changes))
            continue

        for local_line, pub_line in zip(local_lines, pub_lines):
            if local_line == pub_line:
                continue
            local_fields = local_line.split("\t")
            pub_fields = pub_line.split("\t")
            if len(local_fields) != 10 or len(pub_fields) != 10:
                changes.append(
                    {"type": "malformed", "local": local_line, "published": pub_line}
                )
                continue

            diff_fields = []
            for i, name in enumerate(FIELDS):
                if local_fields[i] != pub_fields[i]:
                    diff_fields.append((name, local_fields[i], pub_fields[i]))
                    result["field_counts"][name] += 1

            if diff_fields:
                changes.append(
                    {
                        "type": "fields",
                        "token_id": local_fields[0],
                        "form": local_fields[1],
                        "diffs": diff_fields,
                    }
                )

        if changes:
            result["changed"].append((sid, local_text or pub_text, changes))
        else:
            result["identical"] += 1

    return result


def format_report(lang_code, local_path, published_path, result):
    """Format comparison results as a readable report."""
    lines = []
    lines.append(f"## {lang_code.upper()} — {local_path.name} vs published")
    lines.append("")

    # Summary
    lines.append(f"- Common sentences: {result['common']}")
    lines.append(f"- Identical: {result['identical']}")
    lines.append(f"- Changed: {len(result['changed'])}")
    if result["only_local"]:
        lines.append(
            f"- Only in local ({len(result['only_local'])}): {', '.join(result['only_local'])}"
        )
    if result["only_published"]:
        lines.append(
            f"- Only in published ({len(result['only_published'])}): {', '.join(result['only_published'])}"
        )
    lines.append("")

    # Field change counts
    if result["field_counts"]:
        lines.append("### Token changes by field")
        for field, count in result["field_counts"].most_common():
            lines.append(f"  {field}: {count}")
        lines.append("")

    # Per-sentence details
    if result["changed"]:
        lines.append("### Changed sentences")
        lines.append("")
        for sid, text, changes in result["changed"]:
            lines.append(f"**{sid}**: {text}")
            for change in changes:
                if change["type"] == "token_count":
                    lines.append(
                        f"  Token count mismatch: local={change['local']}, published={change['published']}"
                    )
                elif change["type"] == "malformed":
                    lines.append("  Malformed line")
                elif change["type"] == "fields":
                    tid = change["token_id"]
                    form = change["form"]
                    field_strs = [
                        f"{name}: {local} → {pub}"
                        for name, local, pub in change["diffs"]
                    ]
                    lines.append(f"  {tid} ({form}): {'; '.join(field_strs)}")
            lines.append("")

    return "\n".join(lines)


def find_local_file(lang_code):
    """Find the local CoNLL-U file for a language code in the data directory."""
    # First try the plain name (no annotator initials)
    plain = DATA_DIR / f"{lang_code}_tuecl-ud-test.conllu"
    if plain.exists():
        return plain

    # Then try with annotator initials
    matches = sorted(DATA_DIR.glob(f"{lang_code}_tuecl-ud-test.*.conllu"))
    if matches:
        return matches[0]

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Compare local parallel treebanks against published UD versions"
    )
    parser.add_argument(
        "--lang",
        nargs="*",
        help=f"Language codes to compare (default: all published: {', '.join(sorted(PUBLISHED_TREEBANKS))})",
    )
    parser.add_argument(
        "--fetch-only",
        action="store_true",
        help="Only fetch published files, don't compare",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / ".published-cache",
        help="Directory to cache fetched files",
    )
    parser.add_argument(
        "--output", "-o", type=Path, help="Write report to file instead of stdout"
    )
    args = parser.parse_args()

    langs = args.lang or sorted(PUBLISHED_TREEBANKS)
    args.cache_dir.mkdir(parents=True, exist_ok=True)

    reports = []

    for lang in langs:
        if lang not in PUBLISHED_TREEBANKS:
            print(
                f"No published TueCL treebank for '{lang}', skipping", file=sys.stderr
            )
            continue

        repo = PUBLISHED_TREEBANKS[lang]
        print(f"[{lang}] {repo}")

        published_path = fetch_published(lang, repo, args.cache_dir)
        if not published_path:
            continue

        if args.fetch_only:
            print(f"  Cached at {published_path}")
            continue

        local_path = find_local_file(lang)
        if not local_path:
            print(f"  No local file found for {lang}, skipping")
            continue

        print(f"  Local:     {local_path.name}")
        print(f"  Published: {published_path.name}")

        local_sents = parse_tokens(local_path)
        pub_sents = parse_tokens(published_path)
        result = compare_sentences(local_sents, pub_sents)
        report = format_report(lang, local_path, published_path, result)
        reports.append(report)

        # Print quick summary
        print(
            f"  {result['common']} common, {result['identical']} identical, {len(result['changed'])} changed"
        )
        if result["only_local"]:
            print(f"  {len(result['only_local'])} only in local")
        if result["only_published"]:
            print(f"  {len(result['only_published'])} only in published")

    if reports and not args.fetch_only:
        full_report = "\n---\n\n".join(reports)
        if args.output:
            args.output.write_text(full_report, encoding="utf-8")
            print(f"\nReport written to {args.output}")
        else:
            print("\n" + "=" * 60)
            print(full_report)


if __name__ == "__main__":
    main()
