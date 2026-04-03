# 🚀 Hyper-Extract

> *"告别文档焦虑，让信息一目了然"*
> **"Stop reading. Start understanding."**

**智能知识提取 CLI — 一条命令，将文档转化为结构化知识。**

![Hero & Workflow](assets/hero.png)

[![Python版本](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success)]()

## 什么是 Hyper-Extract？

Hyper-Extract 是一个智能的、基于 LLM 的知识提取与演化框架。它极大地简化了将高度非结构化文本转换为持久化、可预测、强类型知识摘要的过程。它能够轻松地将信息提取为多种格式——从简单的**集合**（列表/集合）和 **Pydantic 模型**，到复杂的**知识图谱**、**超图**，甚至**时空图**。

## ✨ 核心特性

- 🔷 **8 种自动类型：** 从基础的 `AutoModel`/`AutoList` 到高级的 `AutoGraph`、`AutoHypergraph` 和 `AutoSpatioTemporalGraph`。
- 🧠 **10+ 提取引擎：** 开箱即用的前沿检索范式支持，如 `GraphRAG`、`LightRAG`、`Hyper-RAG` 和 `KG-Gen`。
- 📝 **声明式 YAML 模板：** 零代码提取定义。包含 6 个领域 80+ 预设模板。
- 🔄 **增量演化：** 动态输入新文档，持续扩展和更新提取的知识。

## ⚡ 快速开始

### 安装

```bash
uv pip install hyper-extract
```

### 命令行方式

```bash
# 配置 OpenAI API Key
he config init -k YOUR_OPENAI_API_KEY

# 提取知识
he parse examples/en/tesla.md -t general/biography_graph -o ./output/ -l en

# 查询知识库
he search ./output/ "Tesla 的主要成就有哪些？"

# 可视化知识图谱
he show ./output/

# 增量补充知识
he feed ./output/ examples/en/tesla_question.md

# 查看更新后的知识图谱
he show ./output/
```

### Python API 方式

#### 安装

```bash
# 克隆仓库
git clone https://github.com/yifanfeng97/hyper-extract.git
cd hyper-extract

# 安装依赖
uv sync
```

#### 配置

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件配置 API Key 和 Base URL
# OPENAI_API_KEY=your-api-key
# OPENAI_BASE_URL=https://api.openai.com/v1
```

#### 使用

```python
import os
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()

from hyperextract import Template

# 创建模板
ka = Template.create("general/biography_graph")

# 解析文档
with open("examples/en/tesla.md", "r") as f:
    text = f.read()
result = ka.parse(text)

# 可视化知识图谱
ka.show(result)

# 增量补充知识
with open("examples/en/tesla_question.md", "r") as f:
    new_text = f.read()
ka.feed(result, new_text)

# 查看更新后的知识图谱
ka.show(result)
```

## 🧩 8 种自动类型

我们的框架化繁为简，让您无需编写样板代码。

![知识结构矩阵](assets/autotypes.png)

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

### 示例：AutoGraph 可视化

使用 `AutoGraph` 提取后的知识图谱可视化：

![AutoGraph 可视化](assets/zh_show.png)

## 🛠️ 系统架构

Hyper-Extract 采用**三层架构**：

- **Auto-Types** 定义了知识提取的数据结构。8 种强类型结构（AutoModel、AutoList、AutoSet、AutoGraph、AutoHypergraph、AutoTemporalGraph、AutoSpatialGraph、AutoSpatioTemporalGraph）作为所有提取的输出格式。

- **Methods** 基于 Auto-Types 提供提取算法。包括典型方法（KG-Gen、iText2KG、iText2KG*）和 RAG 增强方法（GraphRAG、LightRAG、Hyper-RAG、HypergraphRAG、Cog-RAG）。

- **Templates** 提供领域特定的配置，包含开箱即用的 prompt 和数据结构。覆盖 6 大领域（金融、法律、医疗、中医、工业、通用），提供 80+ 预设模板，用户无需了解底层 Auto-Types 和 Methods 即可直接使用。

可通过 **CLI**（`he parse`、`he search`、`he show`...）或 **Python API**（`Template.create()`）使用。

![架构图](assets/arch.png)

## 📈 与其他库对比

| 特性 | GraphRAG | LightRAG | KG-Gen | ATOM | **Hyper-Extract** |
|------|:--------:|:--------:|:------:|:----:|:-----------------:|
| 知识图谱 |    ✅    |    ✅    |   ✅   |  ✅  |        ✅         |
| 时序图谱 |    ✅    |    ❌    |   ❌   |  ✅  |        ✅         |
| 空间图谱 |    ❌    |    ❌    |   ❌   |  ❌  |        ✅         |
| 超图 |    ❌    |    ❌    |   ❌   |  ❌  |        ✅         |
| 领域模板 |    ❌    |    ❌    |   ❌   |  ❌  |        ✅         |
| CLI 工具 |    ✅    |    ❌    |   ❌   |  ❌  |        ✅         |
| 多语言 |    ✅    |    ❌    |   ❌   |  ❌  |        ✅         |

## 📚 文档

- [快速开始](cli/index.md) - 快速上手
- [领域模板](templates/index.md) - 开箱即用的模板

## 🤝 贡献与许可

欢迎贡献！请提交 Issues 和 PRs。
基于 **Apache-2.0** 许可证。
