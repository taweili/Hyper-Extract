<div align="center">

# 🚀 Hyper-Extract

**智能知识提取 CLI —— 一行命令，将文档转化为结构化知识。**

[📖 English Version](./README.md) · [中文版](./README_ZH.md)

[![Python版本](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![开源协议](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![状态](https://img.shields.io/badge/status-active-success)]()

<br/>

> **"Stop reading. Start understanding."**  
> *"告别文档焦虑，让信息一目了然"*

<br/>

<img src="docs/assets/hero.jpg" alt="Hero & Workflow" width="100%">

<br/>
</div>

Hyper-Extract 是一个智能的、由大语言模型（LLM）驱动的知识提取与演进框架。它极大地简化了将杂乱不堪的文本转化为持久化、强类型的知识摘要的过程。无论从基础的**集合（Collection/List）和**结构化模型（Model），还是到高阶复杂的**知识图谱（Knowledge Graph）**、**超图（Hypergraph）**，甚至是**时空图谱（Spatio-Temporal Graph）**，它都能轻松拿捏。

## ✨ 核心亮点

- 🔷 **8大基础知识结构数据结构（Auto-Types）：** 从基础的 `AutoModel`/`AutoList` 到高阶的 `AutoGraph`, `AutoHypergraph`, 以及 `AutoSpatioTemporalGraph`（时空图）。
- 🧠 **10+ 前沿提取引擎：** 开箱即用整合了业界顶尖的检索范式，例如 `GraphRAG`、`LightRAG`、`Hyper-RAG` 和 `KG-Gen`。
- 📝 **声明式 YAML 模板：** 零代码定义提取策略。内置覆盖 6 大领域的 80+ 预设模板。
- 🔄 **知识增量演进：** 支持动态喂入新文档（Feed），让提取的知识图谱自动补全和扩展。

***

## ⚡ 快速上手

### 1. 极速安装

```bash
uv pip install hyper-extract
```

### 2. CLI 命令行玩法

仅仅几行命令体验最纯粹的知识交互。

> 默认采用`gpt-4o-mini` 作为大模型基座， `text-embedding-3-small`作为文本嵌入模型。

```bash
# 配置 OpenAI API Key
he config init -k YOUR_OPENAI_API_KEY

# 提取知识（使用 examples/zh/sushi.md 作为示例输入）
he parse examples/zh/sushi.md -t general/biography_graph -o ./output/ -l zh

# 查询知识库
he search ./output/ "苏轼有哪些重要的作品？"

# 增量补充知识
he feed ./output/ another_sushi_document.md
```

<details>
<summary><b>🐍 Python API 深度集成</b></summary>
<br>

```python
from hyperextract import Template

ka = Template.create("general/biography_graph")
result = ka.parse(text)
```

> 🔗 完整示例代码，请参阅 [examples/zh](./examples/zh/)

</details>

## 🧩 8 种核心知识结构

拒绝样板代码，纯干货聚焦数据本身。

![Knowledge Structures Matrix](docs/assets/autotypes.png)

### 示例：AutoGraph 知识图谱可视化

以下是 `AutoGraph` 类型提取后的知识图谱可视化效果：

![AutoGraph 可视化](docs/assets/zh_show.png)

## 🛠️ 系统架构

系统底座基于坚实的铁三角架构：**Auto-Types** (提取结构)、**Methods** (执行策略)、以及 **Templates** (声明式配置)。

![Architecture](docs/assets/arch.png)

### 📋 模板结构示例

以下是一个完整的 YAML 模板示例，定义了知识图谱提取：

```yaml
language: zh

name: 知识图谱
type: graph
tags: [general]

description: '从文本中提取实体及其关系，构建知识图谱。'

output:
  entities:
    fields:
    - name: name
      type: str
      description: '实体名称'
    - name: type
      type: str
      description: '实体类型'
  relations:
    fields:
    - name: source
      type: str
      description: '源实体'
    - name: target
      type: str
      description: '目标实体'
    - name: type
      type: str
      description: '关系类型'

guideline:
  target: '从文本中提取实体及其关系。'
  rules_for_entities:
    - '提取有意义的实体'
    - '保持命名一致'
  rules_for_relations:
    - '仅在文本明确表达时创建关系'

identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
  relation_members:
    source: source
    target: target

display:
  entity_label: '{name} ({type})'
  relation_label: '{type}'
```

### 📚 相关文档

- **预设模板**: 浏览覆盖 6 大领域的 [80+ 即用型模板](./hyperextract/templates/presets/)
- **设计指南**: 学习如何[创建自定义模板](./hyperextract/templates/DESIGN_GUIDE_ZH.md)

## 📈 与其他流行库的对比

| 特性      | GraphRAG | LightRAG | KG-Gen | ATOM | **Hyper-Extract** |
| ------- | :------: | :------: | :----: | :--: | :---------------: |
| 知识图谱支持  |     ✅    |     ✅    |    ✅   |   ✅  |         ✅         |
| 时序图谱    |     ✅    |     ❌    |    ❌   |   ✅  |         ✅         |
| 空间图谱    |     ❌    |     ❌    |    ❌   |   ❌  |         ✅         |
| 超图提取    |     ❌    |     ❌    |    ❌   |   ❌  |         ✅         |
| 领域模板驱动  |     ❌    |     ❌    |    ❌   |   ❌  |         ✅         |
| 交互式 CLI |     ❌    |     ❌    |    ❌   |   ❌  |         ✅         |
| 多语言支持   |   部分支持   |     ❌    |    ❌   |   ❌  |         ✅         |

## 📚 项目参考文档

- [CLI 命令行指南](./hyperextract/cli/README.md)
- [模板画廊](./hyperextract/templates/)
- [示例代码示例](./examples/)
- [完整架构文档](./docs/)

## 🤝 参与贡献与协议

热烈欢迎社区提交 Issues 和 PRs。
项目基于 **Apache-2.0** 协议开源。
