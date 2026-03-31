---
name: squirrel-auto-testbench
description: >
  Squirrel Auto Testbench - 自动侧信道分析测试框架。
  包含 TVLA 测试数据分析、功耗轨迹生成、相关性分析等功能。
  触发关键词：
  - "squirrel"
  - "TVLA 测试"
  - "侧信道分析"
  - "生成测试数据"
  - "testbench"
  - "side-channel"
  - "功耗分析"
---

# Squirrel Auto Testbench

侧信道分析自动测试框架。

## 核心功能

- TVLA (Test Vector Leakage Assessment) 分析
- CPA (Correlation Power Analysis) - 预留
- DPA (Differential Power Analysis) - 预留
- LSTM 深度学习侧信道分析 - 预留

## 子 Skills

### squirrel-dataset-prepare

当用户请求以下场景时，**必须调用** 此子 skill：

- "生成 TVLA 测试数据"
- "准备测试数据"
- "generate test dataset"
- "TVLA test data"
- "生成测试脚本"
- "创建 TVLA 测试"

位置：`squirrel-skills/squirrel-dataset-prepare/`

## 目录结构

```
squirrel-auto-testbench/
├── SKILL.md                      # 主 skill
├── squirrel-skills/
│   └── squirrel-dataset-prepare/ # 测试数据准备 (子skill)
├── scripts/
│   └── generate_tvla_dataset.py  # TVLA 数据生成脚本
├── tvla-test/                    # TVLA 测试脚本
│   ├── run_tvla_weak.sh
│   ├── run_tvla_medium.sh
│   └── run_tvla_strong.sh
└── examples/                     # 示例数据
```

## 使用流程

1. 用户请求生成测试数据/脚本
2. 调用 `squirrel-dataset-prepare` 子 skill
3. 按照子 skill 指导执行

```bash
# 示例：使用子skill生成 TVLA 数据
# 1. 调用 squirrel-dataset-prepare skill
# 2. 执行生成脚本
./tvla-test/run_tvla_medium.sh

# 或手动生成
python3 scripts/generate_tvla_dataset.py \
  --output ./examples/tvla_test.zarr \
  --profile medium

# 运行 TVLA 分析
squirral tvla run --input ./examples/tvla_test.zarr --format zarr --output-dir ./out --algorithm AES
```
