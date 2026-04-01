# 核心概念

本节解释 Hyper-Extract 的核心概念。

## 本节内容

- [自动类型](auto-types.md) - 用于知识表示的 8 种数据结构
- [提取方法](methods.md) - 10+ 种知识提取引擎
- [模板](templates.md) - 用于提取的声明式 YAML 模式

## 核心概念

### 自动类型

Hyper-Extract 提供 8 种自动类型，从简单的集合到复杂的图：

| 类型 | 用例 |
|------|------|
| AutoModel | 结构化数据提取 |
| AutoList | 列表/集合提取 |
| AutoSet | 唯一项提取 |
| AutoGraph | 知识图谱提取 |
| AutoHypergraph | 复杂关系提取 |
| AutoTemporalGraph | 时序知识图谱 |
| AutoSpatialGraph | 空间知识图谱 |
| AutoSpatioTemporalGraph | 时空知识图谱 |

### 提取方法

选择适合您提取任务的方法：

| 方法 | 最佳用途 |
|------|----------|
| atom | 简单、直接的提取 |
| graph_rag | 基于图的检索 |
| light_rag | 轻量级检索 |
| hyper_rag | 超图提取 |
| cog_rag | 认知检索 |

### 模板

模板使用声明式 YAML 定义要提取的内容。它们提供：

- 类型安全的模式
- 验证规则
- 自定义提取逻辑

## 了解更多

- [自动类型](auto-types.md) - 深入了解每种类型
- [方法](methods.md) - 比较提取方法
- [模板](templates.md) - 创建自定义模板
