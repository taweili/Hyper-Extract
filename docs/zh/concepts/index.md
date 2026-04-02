# 核心概念

## 概述

Hyper-Extract 是一个知识提取框架，可从各种文档中提取结构化知识。本文档介绍核心概念，帮助您理解系统的工作原理。

## 核心概念

### 模板 (Template)

模板使用 YAML 定义要提取的内容，提供声明式的方式来指定提取模式，无需编写代码。

详细了解：[模板](./templates.md)

### 自动类型 (AutoType)

Hyper-Extract 支持 8 种自动类型，每种类型针对不同的提取场景：

| 类型 | 说明 | 使用场景 |
|------|------|---------|
| `model` | 单个结构化对象 | 提取单一记录 |
| `list` | 有序列表 | 提取排序项目 |
| `set` | 去重集合 | 提取唯一实体 |
| `graph` | 二元关系图 | 提取实体关系 |
| `hypergraph` | 多元关系图 | 提取多方关系 |
| `temporal_graph` | 时序图 | 添加时间维度 |
| `spatial_graph` | 空间图 | 添加空间维度 |
| `spatio_temporal_graph` | 时空图 | 添加时间和空间 |

详细了解：[自动类型](./auto-types.md)

### 提取方法 (Methods)

Hyper-Extract 支持多种提取方法：

- **本地模型**：使用本地部署的模型
- **API 模型**：使用云端 API（如 OpenAI、Claude）
- **混合模式**：结合多种方法

详细了解：[提取方法](./methods.md)

## 快速开始

1. [安装](../getting-started/installation.md)
2. [快速教程](../getting-started/quickstart.md)
3. [模板设计](./templates.md)

## 下一步

- 浏览 [模板库](../reference/template-gallery.md)
- 查看 [领域模板](../guides/domain-templates/index.md)
- 了解 [Python API](../guides/python-api.md)
