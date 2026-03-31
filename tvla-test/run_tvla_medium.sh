#!/bin/bash
export NUM_TRACES=2000
export NUM_SAMPLES=3000
export LEAKAGE_START=500
export LEAKAGE_END=900
OUTPUT_DIR="${OUTPUT_DIR:-./examples}"
PROFILE="${PROFILE:-medium}"

python3 test-data-generator/generate_tvla_dataset.py \
  --output "$OUTPUT_DIR/tvla_test_medium.zarr" \
  --profile "$PROFILE"

squirral tvla run \
  --input "$OUTPUT_DIR/tvla_test_medium.zarr" \
  --format zarr \
  --output-dir "$OUTPUT_DIR/tvla_test_medium_out" \
  --algorithm AES

PYTHONPATH=./src python3 -c "
from squirral.analysis.tvla import analyze_convergence, TVLAConfig
from squirral.plot import plot_convergence
from squirral.data_io.loaders import load_zarr

fixed, random = load_zarr('$OUTPUT_DIR/tvla_test_medium.zarr')
result = analyze_convergence(fixed, random, max_trace_counts=1000, num_steps=20, seed=42)
config = TVLAConfig(threshold=4.5)
plot_convergence(result, config, '$OUTPUT_DIR/tvla_test_medium_out/convergence_plot.png')
print('Convergence plot saved')
"
