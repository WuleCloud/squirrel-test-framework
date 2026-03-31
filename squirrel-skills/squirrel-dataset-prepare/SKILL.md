---
name: squirrel-dataset-prepare
description: >
  准备测试数据集。用于生成侧信道分析所需的测试数据，包括 TVLA 测试数据、CPA 测试数据等。
  触发场景：
  - "生成 TVLA 测试数据"
  - "准备测试数据"
  - "generate test dataset"
  - "TVLA test data"
  - "CPA test data"
---

# Dataset Prepare

为侧信道分析准备测试数据集。

## Supported Dataset Types

### TVLA Test Data

当用户请求 TVLA 测试数据时：

1. 使用 `scripts/generate_tvla_dataset.py` 生成数据
2. 默认输出格式为 **Zarr** (`.zarr`)
3. 支持三种泄漏强度预设：

| Profile | leakage_amplitude | noise_std | 用途 |
|---------|------------------|-----------|------|
| weak | 0.6 | 1.0 | 弱泄漏测试 |
| medium | 1.2 | 1.0 | 中等泄漏 (默认) |
| strong | 2.0 | 1.0 | 强泄漏测试 |

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--profile` | 泄漏强度预设 (weak/medium/strong) | medium |
| `NUM_TRACES` | 轨迹数（每组） | 2000 |
| `NUM_SAMPLES` | 样本数（每条轨迹） | 3000 |
| `LEAKAGE_START` | 泄漏窗口起始索引 | 500 |
| `LEAKAGE_END` | 泄漏窗口结束索引 | 900 |

## Data Format

默认使用 **Zarr** 格式：

```
dataset.zarr/
├── .zgroup
├── /0/0/
│   ├── traces          # (num_traces, num_samples)
│   ├── labels          # (num_traces,) - 0=random, 1=fixed
│   ├── fixed_traces   # (num_fixed, num_samples)
│   └── random_traces  # (num_random, num_samples)
└── .zattrs
```

## Usage

### 使用预设配置

```bash
# 弱泄漏
python3 scripts/generate_tvla_dataset.py \
  --output ./examples/tvla_weak.zarr \
  --profile weak

# 中等泄漏 (默认)
python3 scripts/generate_tvla_dataset.py \
  --output ./examples/tvla_medium.zarr \
  --profile medium

# 强泄漏
python3 scripts/generate_tvla_dataset.py \
  --output ./examples/tvla_strong.zarr \
  --profile strong
```

### 使用环境变量

```bash
export NUM_TRACES=2000
export NUM_SAMPLES=3000
export LEAKAGE_START=500
export LEAKAGE_END=900

python3 scripts/generate_tvla_dataset.py --output ./examples/tvla_custom.zarr --profile medium
```

### 自定义参数

```bash
python3 scripts/generate_tvla_dataset.py \
  --output ./examples/tvla_custom.zarr \
  --profile medium \
  --num-traces 5000 \
  --num-samples 5000 \
  --leakage-start 1000 \
  --leakage-end 2000
```

## TVLA Analysis

```bash
squirral tvla run \
  --input ./examples/tvla_medium.zarr \
  --format zarr \
  --output-dir ./examples/tvla_medium_out \
  --algorithm AES
```

## Output Location

生成的 Zarr 文件保存在：
- `/home/wuleler/.config/opencode/skills/squirrel-auto-testbench/examples/`

## Future Support

- CPA 测试数据
- 其他侧信道分析测试数据
