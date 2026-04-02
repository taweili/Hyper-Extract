# Hyper-Extract

> **"告别文档焦虑，让信息一目了然"**

**一行命令，将文档转化为结构化知识摘要。**

![Hero & Workflow](assets/hero-v2.jpg)

[![Python版本](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success)]()

## 什么是 Hyper-Extract？

Hyper-Extract 是一个智能的、基于 LLM 的知识提取与演化框架。它极大地简化了将高度非结构化文本转换为持久化、可预测、强类型知识摘要的过程。它能够轻松地将信息提取为多种格式——从简单的**集合**（列表/集合）和 **Pydantic 模型**，到复杂的**知识图谱**、**超图**，甚至**时空图**。

## 核心特性

- 🔷 **8 种自动类型：** 从基础的 `AutoModel`/`AutoList` 到高级的 `AutoGraph`、`AutoHypergraph` 和 `AutoSpatioTemporalGraph`。
- 🧠 **10+ 提取引擎：** 开箱即用的前沿检索范式支持，如 `graph_rag`、`light_rag` 和 `hyper_rag`。
- 📝 **声明式 YAML 模板：** 零代码提取定义。包含 6 个领域 80+ 预设模板。
- 🔄 **增量演化：** 动态输入新文档，持续扩展和更新提取的知识。

## 快速开始

### 安装

```bash
uv pip install hyper-extract
```

### 命令行方式

```bash
he config init -k YOUR_API_KEY
he parse document.md -o ./output/ -l zh
he search ./output/ "关键事件有哪些？"
he feed ./output/ new_document.md
```

### Python API 方式

```python
from hyperextract import Template

# 加载预设 YAML 模板
ka = Template.create("finance/event_timeline")

# 提取并自动解析文档
result = ka.parse(annual_report_text)
```

## 文档

- [快速开始](getting-started/index.md) - 快速上手
- [核心概念](concepts/index.md) - 理解核心概念
- [使用指南](guides/index.md) - 逐步教程
- [参考文档](reference/index.md) - API 和配置参考

## 8 种自动类型

| 类型 | 描述 |
|------|------|
| AutoModel | Pydantic 模型提取 |
| AutoList | 列表/集合提取 |
| AutoSet | 唯一集合提取 |
| AutoGraph | 知识图谱提取 |
| AutoHypergraph | 超图提取 |
| AutoTemporalGraph | 时序知识图谱 |
| AutoSpatialGraph | 空间知识图谱 |
| AutoSpatioTemporalGraph | 时空知识图谱 |

## 架构

![Architecture](assets/architecture-v2.png)

系统构建在稳固的三元组上：**自动类型**（多类型结构）、**方法**（执行策略）和**模板**（声明式模式）。

## 许可证

基于 **Apache-2.0** 许可证。
