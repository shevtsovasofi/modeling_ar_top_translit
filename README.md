# modeling_ar_top_translit
# Arabic Toponym Rendering: Anonymous Evaluation Artifact

This repository reproduces the evaluation of English and Russian map labels generated from Arabic place names. It includes frozen automatic predictions, manually checked reference labels, the character-level evaluator, and an anonymized rule-based pipeline snapshot.

## Reproduce the reported scores

Python 3.10 or later is sufficient. No packages, GPU, network access, model weights, or API credentials are required for scoring.

```bash
python3 reproduce.py
```

Expected output:

```text
EN: F1=0.8545; exact=125/186
RU: F1=0.8378; exact=119/186
PASS: checksums and recomputed metrics match. Detailed output: results/scores.json
```

| Language | Character precision | Character recall | Character F1 | Exact match |
|---|---:|---:|---:|---:|
| English | 0.848343 | 0.860759 | **0.854506** | **125/186 (67.20%)** |
| Russian | 0.840691 | 0.834922 | **0.837796** | **119/186 (63.98%)** |

Predictions are the original automatic outputs, not manually corrected versions. The verification script checks SHA256 fingerprints, reruns the evaluator, and checks the resulting scores and exact-match counts. Expected values are assertions, not inputs to the metric calculation. Full-precision scores appear in `results/scores.json`; `results_summary.json` is the precomputed reference report.

## Repository layout

```
data/
  predictions_original.jsonl   Frozen automatic EN/RU predictions
  references_verified.csv     Reference EN/RU labels and Arabic inputs
pipeline/
  src/                        Inference and rendering snapshot
  config/                     Dictionary, name components, profile description
  tests/                      Control examples and regression tests
  slurm/                      Generic cluster inference template
score_labels.py               Standalone evaluator
reproduce.py                  Integrity check and score reproduction
expected.json                 Assertions for reported F1 and exact-match counts
SHA256SUMS.json                Fingerprints for the released source and data
PROTOCOL.md                   Data selection and metric definition
PROVENANCE.md                 Scope of reproducibility and anonymization
requirements-inference.txt    Optional inference environment
```

## Run the evaluator directly

```bash
mkdir -p results
python3 score_labels.py \
  --predictions data/predictions_original.jsonl \
  --references data/references_verified.csv \
  --id-column geonameid --en-column reference_en --ru-column reference_ru \
  --output results/direct_scores.json
```

## Test the rendering rules without a model

```bash
python3 -m unittest discover -s pipeline/tests
python3 pipeline/src/run_pipeline.py \
  --input pipeline/tests/sample.csv \
  --output results/rules_control.jsonl \
  --vocalized-column name_ar_diacritized --profile orthographic
```

The control mode uses supplied Arabic vocalization and is not an end-to-end neural benchmark. Existing result paths are not overwritten by the pipeline.

## Optional model inference

The renderer uses a locally stored fine-tuned Fine-Tashkeel checkpoint. Trained weights are **not included**. Downloading the upstream checkpoint alone does not reproduce the adapted model. The references in this artifact have no manually verified Arabic diacritization column and therefore cannot support an Arabic DER calculation by themselves.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-inference.txt
python pipeline/src/run_pipeline.py \
  --input data/references_verified.csv \
  --output results/new_predictions.jsonl \
  --model models/trained-checkpoint \
  --profile orthographic --diacritize-scope full --batch-size 2
```

Only `name_ar_unvocalized` is supplied to the neural model; reference labels are ignored by the inference path. The optional Slurm template requires local queue/account/resource configuration and a staged model. Create `logs/` and `results/` before submission. It intentionally contains no institution-specific settings.

**Reproducibility boundary:** rescoring the saved predictions is verified. Regenerating the exact same predictions is not claimed: the included local rule snapshot has not yet been matched to the original execution manifest, and adapted weights and the complete execution environment are absent. Metadata has been anonymized without changing frozen labels or the evaluation algorithm.

See `PROTOCOL.md` for the scoring definition and `PROVENANCE.md` for limitations.
