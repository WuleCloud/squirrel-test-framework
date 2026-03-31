#!/bin/bash
export NUM_TRACES=2000
export NUM_SAMPLES=3000
OUTPUT_DIR="${OUTPUT_DIR:-./examples}"

# 生成两个泄漏区间的 TVLA 数据
# 区间1: [300, 500)
# 区间2: [800, 1000)
# 使用 Python 直接生成

PYTHONPATH=./src python3 -c "
import numpy as np
from squirral.analysis.tvla import (
    generate_synthetic_tvla_dataset,
    build_labeled_traces,
)
from squirral.data_io.datasets import save_synthetic_zarr

# 生成基础数据
fixed, random = generate_synthetic_tvla_dataset(
    num_traces=$NUM_TRACES,
    num_samples=$NUM_SAMPLES,
    leakage_start=300,
    leakage_end=500,
    leakage_amplitude=1.2,
    noise_std=1.0,
    seed=42,
)

# 添加第二个泄漏区间
leakage_2_start = 800
leakage_2_end = 1000
leakage_2_amplitude = 1.2
fixed[:, leakage_2_start:leakage_2_end] += leakage_2_amplitude

# 构建带标签的轨迹
traces, labels = build_labeled_traces(fixed, random, shuffle=True, seed=42)

# 保存
output_path = '$OUTPUT_DIR/tvla_test_dual.zarr'
save_synthetic_zarr(
    output_path,
    traces=traces,
    labels=labels,
    fixed_traces=fixed,
    random_traces=random,
)

print(f'Saved: {output_path}')
print(f'Leakage windows: [300, 500) and [800, 1000)')
"

squirral tvla run \
  --input "$OUTPUT_DIR/tvla_test_dual.zarr" \
  --format zarr \
  --output-dir "$OUTPUT_DIR/tvla_test_dual_out" \
  --algorithm AES

PYTHONPATH=./src python3 -c "
from squirral.analysis.tvla import analyze_convergence, TVLAConfig
from squirral.plot import plot_convergence
from squirral.data_io.loaders import load_zarr

fixed, random = load_zarr('$OUTPUT_DIR/tvla_test_dual.zarr')
result = analyze_convergence(fixed, random, max_trace_counts=1000, num_steps=20, seed=42)
config = TVLAConfig(threshold=4.5)
plot_convergence(result, config, '$OUTPUT_DIR/tvla_test_dual_out/convergence_plot.png')
print('Convergence plot saved')
"
