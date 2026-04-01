# Hyper-Extract

[📖 English Version](./README.md) · [中文版](./README_ZH.md)

> **"Stop reading. Start understanding."**

> *"告别文档焦虑，让信息一目了然"*

**将文档转化为知识摘要 —— 一行命令即可。**

[![Python版本](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![开源协议](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![状态](https://img.shields.io/badge/status-active-success)]()

## 🚀 什么是 Hyper-Extract
Hyper-Extract 是一个智能的、由大语言模型（LLM）驱动的知识提取与演进框架。它极大地简化了将杂乱不堪的文本转化为持久化、强类型的知识摘要的过程。无论从基础的**集合（Collection/List）**和**结构化模型（Model）**，还是到高阶复杂的**知识图谱（Knowledge Graph）**、**超图（Hypergraph）**，甚至是**时空图谱（Spatio-Temporal Graph）**，它都能轻松拿捏。

![Hero & Workflow](docs/assets/hero-v2.jpg)

## ✨ 核心亮点

- 🔷 **8大自动数据结构（Auto-Types）：** 从基础的 `AutoModel`/`AutoList` 到高阶的 `AutoGraph`, `AutoHypergraph`, 以及 `AutoSpatioTemporalGraph`（时空图）。
- 🧠 **10+ 前沿提取引擎：** 开箱即用整合了业界顶尖的检索范式，例如 `graph_rag`, `light_rag`, 和 `hyper_rag`。
- 📝 **声明式 YAML 模板：** 零代码定义提取策略。内置覆盖 6 大领域的 80+ 预设模板。
- 🔄 **知识增量演进：** 支持动态喂入新文档（Feed），让提取的知识图谱自动补全和扩展。

---

## ⚡ 快速上手

### 1. 极速安装

```bash
uv pip install hyper-extract
```

### 2. CLI 命令行玩法

仅仅几行命令体验最纯粹的知识图谱交互。

> 默认采用兼顾性价比的组合：`gpt-4o-mini` + `text-embedding-3-small`。

```bash
he config init -k YOUR_API_KEY
he parse document.md -o ./output/ -l zh
he search ./output/ "有哪些关键事件？"
he feed ./output/ new_document.md
```

<details>
<summary><b>🛠️ 如何定义知识模板（YAML）？</b></summary>
<br>

无需编写长篇代码，只需使用优雅的 YAML 结构直接声明你想要的信息形态：

```yaml
name: Event Timeline
description: 提取金融动态及其时间依赖关系。
type: TemporalGraph
schema:
  nodes:
    - type: Event
      properties:
        - name: description
          type: string
  edges:
    - type: Timeline
      source: Event
      target: Event
      properties:
        - name: relation
          type: string
```
</details>

### 3. Python API 深度集成

```python
from hyperextract import Template

# 一行加载内置的 YAML 模板策略
ka = Template.create("finance/event_timeline")

# 解析提取
result = ka.parse(annual_report_text)
```

> 🔗 完整示例代码，请参阅 [examples/zh](./examples/zh/)

## 🧩 深入探究：8 种核心抽象类型

拒绝样板代码，纯干货聚焦数据本身。

![Knowledge Structures Matrix](docs/assets/8-types.jpg)

## 🛠️ 系统架构揭秘

系统底座基于坚实的铁三角架构：**Auto-Types** (提取结构)、**Methods** (执行策略)、以及 **Templates** (声明式配置)。

![Architecture](docs/assets/architecture-v10.jpg)

* **设计指南**: [模板设计指南](./hyperextract/templates/DESIGN_GUIDE.md)
* **内置模板**: [预设模板目录](./hyperextract/templates/presets/)

## 📈 与其他流行库的对比

| 特性 | GraphRAG | LightRAG | KG-Gen | ATOM | **Hyper-Extract** |
|------|:---:|:---:|:---:|:---:|:---:|
| 知识图谱支持 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 时序图谱 | ✅ | ❌ | ❌ | ✅ | ✅ |
| 空间图谱 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 超图提取 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 领域模板驱动 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 交互式 CLI | ❌ | ❌ | ❌ | ❌ | ✅ |
| 多语言支持 | 部分支持 | ❌ | ❌ | ❌ | ✅ |

## 📚 项目参考文档

* [CLI 命令行指南](./hyperextract/cli/README.md)
* [模板画廊](./hyperextract/templates/)
* [示例代码示例](./examples/)
* [完整架构文档](./docs/)

## 🤝 参与贡献与协议

热烈欢迎社区提交 Issues 和 PRs。
项目基于 **Apache-2.0** 协议开源。
