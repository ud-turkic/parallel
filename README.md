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

## Setup

```bash
cd parallel
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Scripts

### Validation

```bash
# Validate CoNLL-U files against UD standards
python run_validation.py -f *.conllu
```

### Comparison & Statistics

```bash
# Compare two treebanks with matching sentence IDs
python compare_treebanks.py treebank1.conllu treebank2.conllu

# Count tokens and gather POS/feature/deprel statistics
python count_tokens.py <conllu_file>
```

### Data Preparation

```bash
# Generate parallel sentence markdown table
python tabulate_parallel_sentences.py <args>

# Convert plain text to CoNLL-U (NLTK tokenization)
python parse.py -i1 <cairo_sents> -i2 <udtw23_sents> -i3 <general_sents>

# List all sentences from CoNLL-U to markdown
python list_sentences.py <args>
```

### Fixes

```bash
# Fix SpaceAfter=No annotations using validation log
python fix_spaceafters.py <args>
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

- [ud-turkic/tools](https://github.com/ud-turkic/tools) — Shared tooling (cross-language clustering, annotation tables)
- [ud-turkic/general](https://github.com/ud-turkic/general) — Group coordination and meeting notes
- [ud-turkic/dissemination](https://github.com/ud-turkic/dissemination) — Academic papers
