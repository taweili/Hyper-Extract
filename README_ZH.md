# 🔍 Hyper-Extract

> **"Stop reading. Start understanding."**

> *"告别文档焦虑，让信息一目了然"*

将文档转化为**知识摘要** —— 一行命令即可。

![Hero](docs/assets/hero-v2.jpg)

[📖 English Version](./README.md) · [中文版](./README_ZH.md)

---

## ✨ 核心特性

- 🔷 **知识结构** — Model, List, Set, Graph, Hypergraph, TemporalGraph, SpatialGraph, SpatioTemporalGraph
- 💻 **交互式CLI** — 提取、构建、与知识摘要交互
- ⚡ **增量更新** — 持续使用新问题更新知识摘要

---

## ⚡ 快速开始

### 使用 uv 安装

```bash
uv pip install hyper-extract
```

### CLI 使用

```bash
he config init -k YOUR_API_KEY
he parse document.md -o ./output/ -l zh
he search ./output/ "有哪些关键事件？"
he feed ./output/ new_document.md
he show ./output/
```

<details>
<summary>🐍 Python API</summary>

```python
from hyperextract import Template

ka = Template.create("finance/event_timeline")
result = ka.parse(annual_report_text)
# result.timeline = [Event("Q1营收", "2024-01"), ...]
```

</details>

> 🔗 详细 CLI 使用请查看 [CLI 指南](./hyperextract/cli/README.md)

---

## 📖 知识摘要

> 从简单结构化到复杂时空图谱 —— **10+ 提取方法**，覆盖 **6 大领域**，共 **38+ 模板**。

<details>
<summary>🔧 8 种知识结构</summary>

| 类型 | 适用场景 | 示例 |
|------|----------|------|
| AutoModel | 结构化报告 | 财报摘要 |
| AutoList | 有序列表 | 会议要点 |
| AutoSet | 去重集合 | 产品目录 |
| AutoGraph | 二元关系 | 社交网络 |
| AutoHypergraph | 多元事件 | 合同纠纷 |
| AutoTemporalGraph | 时序关系 | 新闻时间线 |
| AutoSpatialGraph | 空间关系 | 配送路线 |
| AutoSpatioTemporalGraph | 时空事件 | 历史战役 |

</details>


<details>
<summary>🔍 提取方法 (10+)</summary>

| 方法 | 类型 | 描述 |
|------|------|------|
| graph_rag | graph | Graph-RAG + 社区检测 |
| light_rag | graph | 轻量级实体关系提取 |
| hyper_rag | hypergraph | 超图多实体关系 |
| cog_rag | graph | 认知检索增强 |
| itext2kg | graph | 高质量三元组提取 |
| kg_gen | graph | 结构化知识生成 |
| atom | graph | 时序图谱 + 证据归因 |

</details>

<details>
<summary>🌍 领域模板 (6领域 / 80+模板)</summary>

模板使用 YAML 编写，定义提取目标和输出结构。
- **编写指南**: [模板设计指南](./hyperextract/templates/DESIGN_GUIDE.md)
- **预设模板**: [presets 目录](./hyperextract/templates/presets/)

| 领域 | 模板数 | 典型场景 |
|------|--------|----------|
| General | 13 | 工作流、传记、概念图 |
| Finance | 5 | 财报分析、风险因子 |
| Medicine | 5 | 临床记录、药物相互作用 |
| TCM | 5 | 方剂配伍、经络走向 |
| Industry | 5 | 设备拓扑、事故分析 |
| Legal | 5 | 合同条款、判例引用 |

</details>

---

## 📈 与同类项目对比

| 特性 | GraphRAG | LightRAG | KG-Gen | ATOM | **Hyper-Extract** |
|------|:---:|:---:|:---:|:---:|:---:|
| 知识图谱 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 时序图谱 | ✅ | ❌ | ❌ | ✅ | ✅ |
| 空间图谱 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 超图 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 领域模板 | ❌ | ❌ | ❌ | ❌ | ✅ |
| CLI工具 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 多语言 | 部分 | ❌ | ❌ | ❌ | ✅ |
| 可视化 | 部分 | ❌ | ❌ | ❌ | ✅ |

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [CLI 指南](./hyperextract/cli/README.md) | 命令行工具完整参考 |
| [模板库](./hyperextract/templates/) | 38+ 领域模板 |
| [示例代码](./examples/) | Python API 使用示例 |
| [完整文档](./docs/) | 架构设计与实现细节 |

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

Apache-2.0
