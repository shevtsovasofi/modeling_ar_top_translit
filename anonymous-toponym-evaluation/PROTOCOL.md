# Evaluation protocol

## Data

The released evaluation contains 186 unique geographic object identifiers. A candidate set of 200 names was sampled from a group-held-out test partition, with duplicate names, keys, object identifiers, and groups excluded according to the project selection procedure. Fourteen candidates were subsequently removed because the manually supplied vocalized Arabic form changed base spelling relative to the input. One interface-text entry was among those fourteen, so the total exclusion count is fourteen, not fifteen. Scores apply to this filtered subset and are not estimates obtained on the complete test partition.

`references_verified.csv` contains object identifier, Arabic input, and manually checked English/Russian reference strings. `predictions_original.jsonl` contains the original generated labels from the corresponding inference run. The files join by object identifier, never row order. All 186 released objects have nonempty reference and predicted labels in both languages.

Reference labels were supplied by the human reviewer. Independent multi-annotator verification, blind annotation, and inter-annotator agreement have not been established. A supplied working table also contained edits to several prediction cells; those edited predictions are deliberately excluded from this evaluation. The frozen original automatic outputs are scored against the final supplied reference labels. Reference selection and later corrections must be documented as new versions rather than silently changing this artifact.

Geographic identifiers are public GeoNames-style identifiers and are retained to permit record matching. No reviewer identity, institutional hostname, account name, or private source path is included. The full training corpus, train/dev splits, source collection process, and third-party checkpoint licenses are not reissued by this artifact.

## Normalization

Apply Unicode NFC and collapse whitespace using `" ".join(s.split())`. Preserve case, punctuation, hyphens, apostrophes, and letter differences. No hidden lowercasing, punctuation removal, transliteration normalization, or manual acceptance of variants is used.

## Character matching

For each label pair, find a unit-cost Levenshtein alignment: insertions, deletions, and substitutions each cost one. Among equal-cost alignments, select one with the largest number of equal-character matches. Sum matches and character counts across labels (micro averaging):

- Precision = matches / predicted characters.
- Recall = matches / reference characters.
- F1 = 2 * matches / (predicted characters + reference characters).

Counts:

| Language | Matching characters | Predicted characters | Reference characters |
|---|---:|---:|---:|
| English | 2176 | 2565 | 2528 |
| Russian | 2190 | 2605 | 2623 |

Exact match is equality of the entire normalized label. English: 125/186; Russian: 119/186.

The scorer rejects missing or duplicate object identifiers. Missing generated labels for existing objects count as empty predictions. Reference labels that are empty are excluded with an explicit count; this release has none. This character F1 definition is not interchangeable with every other metric called character-level F1.

## Interpretation

These are end-to-end English/Russian label scores, not Arabic diacritization DER or WER. No statistical significance, repeated-seed uncertainty estimate, or performance claim on all unseen place names follows from this artifact. Freeze the test labels and predictions; use a separate development set for further rule tuning.
