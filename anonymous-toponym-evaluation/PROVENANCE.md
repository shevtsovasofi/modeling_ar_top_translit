# Provenance and reproducibility scope

## Frozen evaluation inputs

- Predictions were extracted without textual modification from an original downloaded automatic-output table.
- References were extracted from the final human-supplied checked table, using reference_en and reference_ru only.
- Arabic inputs and stable object identifiers are retained. Manually edited prediction columns, personal source filenames, machine paths, operational logs, and original institutional run identifiers are not distributed.
- The standalone metric algorithm is unchanged. The wrapper reports relative paths and adds integrity and result assertions.

## Pipeline snapshot

The included local snapshot implements prefix-based longest generic-term matching, a 212-entry generic dictionary, an explicit orthographic article profile, and English/Russian rendering. It is the maintained rule implementation associated with this experiment, but matching it byte-for-byte to the original server run has not been verified. Do not describe the source snapshot as a proven exact reconstruction of the inference run.

The generic dictionary was reconstructed during implementation; it is not represented as a recovered historical dictionary. Nonfunctional provenance-category names were generalized for anonymity. The mappings themselves were not changed for this release. The human-oriented rendering profile description is newly written for the artifact. Manifest paths in future inference outputs are made relative or redacted. These metadata changes do not alter the frozen evaluation labels.

For exact generation reproducibility, the adapted model/tokenizer files, inference environment, original run manifest, input, and hash-matching rules/dictionary must also be archived. They are not included here. No model checkpoint is downloaded when reproducing evaluation.

## Upstream resources

- General-purpose initialization: https://huggingface.co/google/byt5-small
- Diacritization initialization: https://huggingface.co/basharalrfooh/Fine-Tashkeel
- Byte-level model implementation: https://github.com/google-research/byt5
- Geographic record identification: https://www.geonames.org/

These links attribute external resources; they do not identify the authors of this submission. No new license grant for upstream materials is implied by this artifact.
