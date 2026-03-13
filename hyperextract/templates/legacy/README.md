# Legacy Templates (废弃与归档模板)

> ⚠️ **警告**: 此目录包含废弃的 Python 模板和归档的领域模板。

## 目录结构

```
legacy/
├── presets/              # 归档的领域模板（6个）
│   ├── agriculture/     # 农业
│   ├── biology/         # 生物科学
│   ├── food/            # 美食餐饮
│   ├── history/         # 历史
│   ├── literature/      # 文学与影视
│   └── news/            # 新闻传媒
├── zh/                   # 废弃的Python模板
├── README_FULL.md       # 完整版英文文档
└── README_ZH_FULL.md    # 完整版中文文档
```

## 说明

此目录包含两部分内容：

### 1. 废弃的 Python 类模板 (`zh/`)

旧版本的 Python 类模板，已被 YAML 配置文件模板取代，将在未来版本中删除。

### 2. 归档的领域模板 (`presets/`)

以下6个领域模板已从核心模板中移除，归档至此：
- **agriculture** (农业) - 作物全生命周期管理、田间监测
- **biology** (生物科学) - 蛋白组、代谢通路、生态调查
- **food** (美食餐饮) - 标准化食谱、菜单分析
- **history** (历史) - 编年史、信札、口述历史
- **literature** (文学与影视) - 剧本、小说、设定集
- **news** (新闻传媒) - 调查报道、突发快讯

这些模板仍然可用，但不再是核心维护的领域。

## 迁移指南

### Python 类模板迁移（已废弃）

#### 旧的使用方式（已废弃）
```python
from hyperextract.templates.legacy.zh.general import LifeEventTimeline

template = LifeEventTimeline(llm_client=llm, embedder=embedder)
```

#### 新的使用方式（推荐）
```python
from hyperextract.utils.template_engine import Gallery, TemplateFactory

# 直接获取模板（自动加载 presets 和 customs）
config = Gallery.get("LifeEventTimeline")

# 创建模板
template = TemplateFactory.create(config, llm_client, embedder)
```

### 使用归档的领域模板

归档的领域模板（agriculture、biology、food、history、literature、news）仍可通过以下方式使用：

```python
from hyperextract.utils.template_engine import Gallery, TemplateFactory

# 添加归档模板路径
Gallery.add_path("hyperextract/templates/legacy/presets")

# 获取归档模板
config = Gallery.get("CropGrowthCycle")  # agriculture
template = TemplateFactory.create(config, llm_client, embedder)
```

## 删除时间线

### Python 类模板
- **当前版本**: 标记为废弃，但仍可使用
- **下个版本**: 在文档中明确推荐使用 YAML 配置方式
- **未来版本 (v2.0)**: 删除此目录

### 归档领域模板
- **当前版本**: 从核心模板移除，归档至 legacy/presets
- **维护状态**: 低优先级维护，仅修复关键bug
- **未来计划**: 根据用户反馈决定是否恢复或永久移除

## 相关文档

### 核心文档
- [核心模板使用说明](../README.md) - 6个核心领域模板
- [核心模板使用说明（中文）](../README_ZH.md) - 6个核心领域模板（中文版）

### 完整文档
- [完整版英文文档](./README_FULL.md) - 包含全部12个领域的详细说明
- [完整版中文文档](./README_ZH_FULL.md) - 包含全部12个领域的详细说明（中文版）

### 迁移指南
- [PYTHON转YAML配置指南](../PYTHON转YAML配置指南.md)
