---
name: squirrel-io-ready
description: >
  将新的侧信道分析程序快速集成到 Squirral 框架中。
  触发场景：
  - "集成新的分析器"
  - "添加 CPA/DPA/LSTM 分析器"
  - "创建自定义分析器"
  - "extend squirral"
  - "add new analyzer"
---

# Squirral IO Ready

将新的侧信道分析程序快速集成到 Squirral 框架中。

## 现有分析器结构

参考 `squirral/analysis/` 目录结构：

```
analysis/
├── __init__.py           # 统一导出
├── tvla/
│   ├── __init__.py       # 导出
│   ├── tvla_core.py     # 核心实现
│   ├── synthetic.py      # 合成数据
│   └── pipeline.py      # 流水线
├── cpa/                  # CPA 预留接口
├── dpa/                  # DPA 预留接口
└── lstm/                 # LSTM 预留接口
```

## 集成步骤

### 1. 创建分析器目录

```bash
mkdir -p squirral/analysis/<analyzer_name>/
```

### 2. 编写分析器类

必须继承 `Analyzer` 基类并实现以下内容：

```python
from squirral.base import Analyzer, AnalysisResult
from dataclasses import dataclass

@dataclass
class <Analyzer>Config:
    """配置类"""
    threshold: float = 4.5
    # ... 其他配置

@dataclass
class <Analyzer>AnalysisResult(AnalysisResult):
    """结果类"""
    method: str = "<analyzer_name>"
    t_values: np.ndarray | None = None
    leakage_points: np.ndarray | None = None

class <Analyzer>Analyzer(Analyzer):
    """分析器类"""
    
    name = "<analyzer_name>"
    description = "<分析器描述>"
    
    def __init__(self, config: dict | None = None):
        if config is None:
            config = {}
        if isinstance(config, dict):
            self.config = <Analyzer>Config(**config)
        else:
            self.config = config
    
    def analyze(
        self,
        traces: np.ndarray,
        labels: np.ndarray | None = None,
        plaintext: np.ndarray | None = None,
        key: np.ndarray | None = None,
        **kwargs,
    ) -> <Analyzer>AnalysisResult:
        """执行分析"""
        # 实现分析逻辑
        return <Analyzer>AnalysisResult(...)
    
    def detect_leakage_points(
        self,
        result: <Analyzer>AnalysisResult,
        threshold: float | None = None,
    ) -> np.ndarray:
        """检测泄漏点"""
        # 实现泄漏点检测
        return np.array(...)
```

### 3. 创建 `__init__.py`

```python
from .<analyzer_core> import (
    <Analyzer>Config,
    <Analyzer>AnalysisResult,
    <Analyzer>Analyzer,
)

__all__ = [
    "<Analyzer>Config",
    "<Analyzer>AnalysisResult", 
    "<Analyzer>Analyzer",
]
```

### 4. 更新导出

在 `analysis/__init__.py` 中添加：

```python
from .<analyzer_name> import (
    <Analyzer>Analyzer,
    <Analyzer>Config,
    <Analyzer>AnalysisResult,
)
```

在 `base.py` 的 `Squirral._register_default_analyzers()` 中注册：

```python
from squirral.analysis.<analyzer_name> import <Analyzer>Analyzer
self.register("<analyzer_name>", <Analyzer>Analyzer)
```

### 5. 更新 CLI (可选)

在 `cli.py` 中添加新的子命令：

```python
def _run_<analyzer>_command(args):
    # 实现 CLI 命令
```

## 示例：参考 TVLA 分析器

位置：`squirral/analysis/tvla/tvla_core.py`

关键点：
- `TVLAConfig` - 配置类
- `TVLAAnalysisResult` - 结果类  
- `TVLAAnalyzer` - 分析器类，继承 `Analyzer`
- 实现 `analyze()` 和 `detect_leakage_points()` 方法

## 输入格式

Squirral 支持的数据格式：

| 格式 | 后缀 | 说明 |
|------|------|------|
| Zarr | `.zarr` | 推荐，分块存储 |
| ETS | `.ets` | SCAREd 格式 |
| HDF5 | `.h5` | 通用格式 |

## 输出格式

分析结果保存为 Zarr 格式：

```
output.zarr/
├── /0/0/
│   ├── traces
│   ├── labels
│   └── ...
└── .zattrs
```

## 快速集成模板

```python
# 文件: squirral/analysis/my_analyzer/__init__.py
from .my_analyzer_core import MyAnalyzerConfig, MyAnalyzerAnalysisResult, MyAnalyzer

__all__ = ["MyAnalyzerConfig", "MyAnalyzerAnalysisResult", "MyAnalyzer"]
```

```python
# 文件: squirral/analysis/my_analyzer/my_analyzer_core.py
from squirral.base import Analyzer, AnalysisResult
from dataclasses import dataclass
import numpy as np

@dataclass
class MyAnalyzerConfig:
    threshold: float = 4.5

@dataclass 
class MyAnalyzerAnalysisResult(AnalysisResult):
    method: str = "my_analyzer"
    scores: np.ndarray | None = None

class MyAnalyzerAnalyzer(Analyzer):
    name = "my_analyzer"
    description = "My custom analyzer"
    
    def __init__(self, config: dict | None = None):
        self.config = MyAnalyzerConfig(**(config or {}))
    
    def analyze(self, traces, **kwargs):
        # 实现分析逻辑
        scores = np.random.randn(traces.shape[1])
        return MyAnalyzerAnalysisResult(scores=scores)
    
    def detect_leakage_points(self, result, threshold=None):
        threshold = threshold or self.config.threshold
        return np.where(np.abs(result.scores) > threshold)[0]
```
