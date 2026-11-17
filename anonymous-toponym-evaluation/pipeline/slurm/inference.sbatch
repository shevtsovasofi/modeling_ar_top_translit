#!/bin/bash
#SBATCH --job-name=toponym-rendering
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
#SBATCH --output=logs/render-%j.out
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
source .venv/bin/activate
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4
: "${INPUT_CSV:?Set INPUT_CSV}"
: "${MODEL_DIR:?Set MODEL_DIR to your local trained checkpoint}"
srun python pipeline/src/run_pipeline.py --input "$INPUT_CSV" \
 --output "results/generated-${SLURM_JOB_ID}.jsonl" --model "$MODEL_DIR" \
 --profile orthographic --diacritize-scope full --batch-size 16
