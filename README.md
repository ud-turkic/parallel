# UD Turkic Parallel Treebanks

Tools and data for developing parallel Universal Dependencies treebanks across Turkic languages.

## Languages

| Code | Language | Treebank | Annotator(s) |
|------|----------|----------|-------------|
| az | Azerbaijani | TueCL | se |
| crh | Crimean Tatar | TueCL | crh |
| kaa | Karakalpak | TueCL | — |
| kum | Kumyk | TueCL | — |
| ky | Kyrgyz | TueCL | bc |
| sah | Sakha | TueCL | si |
| tr | Turkish | TueCL | cc, fa |
| tt | Tatar | TueCL | ct |
| uz | Uzbek | TueCL | aa |

## Repository Structure

```
parallel/
├── data/              CoNLL-U treebank files
├── scripts/           Parallel-specific processing scripts
├── analyses/          Jupyter notebooks for cross-linguistic analysis
├── little-prince/     Little Prince text extraction (parallel source)
├── docs/              Reference documents
├── pyproject.toml
└── README.md
```

## Setup

```bash
cd parallel
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Scripts

### Data Preparation

```bash
# Convert plain text to CoNLL-U (NLTK tokenization)
python scripts/parse.py -i1 <cairo_sents> -i2 <udtw23_sents> -i3 <general_sents>

# Generate parallel sentence markdown table
python scripts/tabulate_parallel_sentences.py --turkish data/tr_tuecl-ud-test.cc.conllu --azerbaijani data/az_tuecl-ud-test.se.conllu

# List all sentences from CoNLL-U to markdown
python scripts/list_sentences.py data/<file>.conllu --output sentence_list.md
```

### Validation, Comparison & Statistics

Generic UD tools have moved to [ud-turkic/tools](https://github.com/ud-turkic/tools):

```bash
# Validate CoNLL-U files
python run_validation.py -f data/*.conllu

# Compare two treebanks
python compare_treebanks.py data/treebank1.conllu data/treebank2.conllu

# Count tokens and statistics
python count_tokens.py data/<file>.conllu

# Fix SpaceAfter=No annotations
python fix_spaceafters.py <error_log> data/<file>.conllu
```

## Analysis Notebooks

Jupyter notebooks in `analyses/` for cross-linguistic analysis of the parallel treebanks:

| Notebook | Description |
|----------|-------------|
| `dependency_length.ipynb` | Dependency length distribution across Turkic languages |
| `edit_distance_parallel_corpus.ipynb` | Edit distance between parallel translations |
| `relative_clause_position.ipynb` | Relative clause positioning patterns |
| `subject_verb_agreement.ipynb` | Subject-verb agreement patterns |
| `ud_treebank_analyzer.ipynb` | General treebank statistics and visualization |

## CoNLL-U Conventions

### File Naming

`{lang_code}_{treebank}-ud-{split}.{annotator}.conllu`

Example: `az_tuecl-ud-test.se.conllu` (Azerbaijani, annotator "se")

### Sentence IDs

Sentence IDs encode their origin: `{set}-{lang}-{number}`

- `cairo-tr-1` … `cairo-tr-20` — Cairo workshop sentences (2023)
- `udtw23-tr-1` … `udtw23-tr-20` — UDTW 2023 sentences
- `tr-1` … `tr-88+` — General corpus sentences

## Data

### Parallel Texts

The `little-prince/` directory contains extracted text from The Little Prince in Turkic languages, used as a source for parallel annotation.

## Related Repositories

- [ud-turkic/tools](https://github.com/ud-turkic/tools) — Shared UD tooling (validation, comparison, token counting, clustering)
- [ud-turkic/general](https://github.com/ud-turkic/general) — Group coordination and meeting notes
- [ud-turkic/dissemination](https://github.com/ud-turkic/dissemination) — Academic papers
