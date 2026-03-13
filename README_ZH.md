# Hyper-Extract

[English Version](./README.md) · [中文版](#)

---

<!-- 架构图 -->
![架构图](./docs/assets/fw.png)

---

## "Chat 已解决，下一步是知识"

将 LLM 输出的文本转化为**可搜索、可查询、可推理**的结构化知识。

---

## ❌ 以前 | ✅ 现在

<!-- 概念图 -->
![概念图](./docs/assets/concept.png)

| 以前 | 现在 |
| :--- | :--- |
| LLM 输出一堆文本 | 输出结构化知识 |
| ❌ 回答完就消失 | ✅ 可持久化存储 |
| ❌ 无法精准检索 | ✅ 可精准搜索 |
| ❌ 难以追溯源头 | ✅ 可追溯来源 |
| ❌ 碎片化无法复用 | ✅ 知识沉淀复用 |

---

## 🧩 8 种 AutoType

<!-- AutoTypes 图 -->
![AutoTypes](./docs/assets/autotypes.png)

| 类型 | 图标 | 功能 |
| :--- | :---: | :--- |
| **AutoModel** | 📋 | 提取为完整的数据模型 |
| **AutoList** | 📝 | 提取为列表 |
| **AutoSet** | 📦 | 提取并去重 |
| **AutoGraph** | 🔗 | 提取为知识图谱 |
| **AutoTemporalGraph** | ⏱️ | 提取为时序图 |
| **AutoSpatialGraph** | 📍 | 提取为空间图 |
| **AutoSpatioTemporalGraph** | 🌏 | 提取为时空图 |
| **AutoHypergraph** | 🌐 | 提取为超图 |

---

## 🔬 方法对比

| 方法 | 类型 | Model | List | Set | Graph | Temporal | Spatial | Spatiotemporal | Hypergraph |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **KG-Gen** | Graph | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **ATOM** | Atomic | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Graphiti** | Temporal | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **LightRAG** | Graph | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Hyper-RAG** | Hypergraph | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Hyper-Extract** | All-in-One | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🌍 12 个领域，200+ 模板

| 领域 | 模板数 | 领域 | 模板数 |
| :--- | :---: | :--- | :---: |
| 💰 金融 | 25+ | 📜 历史 | 12+ |
| 🏥 医疗 | 20+ | 🧬 生物 | 10+ |
| ⚖️ 法律 | 15+ | 🎭 文学 | 10+ |
| 🌿 中医 | 15+ | 📰 新闻 | 12+ |
| 🔧 工业 | 18+ | 🌾 农业 | 8+ |
| 🍜 美食 | 8+ | 🌐 通用 | 20+ |

---

## 🚀 快速开始

### 方式一：使用 YAML 配置（推荐）

```python
from hyperextract.utils.template_engine import Gallery, TemplateFactory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o-mini")
embedder = OpenAIEmbeddings()

# 直接获取模板（自动加载 presets 和 customs）
config = Gallery.get("ResearchNoteSummary")

# 创建模板
template = TemplateFactory.create(config, llm, embedder)
result = template.parse("苹果Q3营收达到949亿美元...")

answer = template.chat("营收增长的原因是什么？")
print(answer.content)
```

### 方式二：使用 Python 类（已废弃）

```python
from hyperextract.templates.legacy.zh.finance import ResearchNoteSummary
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o-mini")
embedder = OpenAIEmbeddings()

template = ResearchNoteSummary(llm_client=llm, embedder=embedder)
result = template.parse("苹果Q3营收达到949亿美元...")

answer = template.chat("营收增长的原因是什么？")
print(answer.content)
```

---

## 🔧 技术架构

<details>
<summary><strong>技术细节</strong></summary>

```
hyperextract/
├── types/                    # 8 种 AutoType
│   ├── model.py             # AutoModel
│   ├── list.py              # AutoList
│   ├── set.py               # AutoSet
│   ├── graph.py             # AutoGraph
│   ├── hypergraph.py        # AutoHypergraph
│   ├── temporal_graph.py    # AutoTemporalGraph
│   ├── spatial_graph.py     # AutoSpatialGraph
│   └── spatio_temporal_graph.py  # AutoSpatioTemporalGraph
│
├── methods/                  # 提取引擎
│   ├── rag/                 # RAG 方法
│   │   ├── light_rag.py
│   │   ├── hyper_rag.py
│   │   └── cog_rag.py
│   └── typical/             # 复现的方法
│       ├── kg_gen.py        # KG-Gen
│       └── atom.py          # ATOM
│
└── templates/                # 领域模板
    ├── zh/                  # 中文模板
    │   ├── finance/         # 25+ 模板
    │   ├── medicine/        # 20+ 模板
    │   └── ...
    └── en/                  # 英文模板
```

</details>

---

## 📚 文档与资源

- [📖 完整文档](docs/)
- [💻 示例代码](examples/)
- [🏷️ 模板 Gallery](hyperextract/templates/)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## ⭐ 支持

如果你觉得这个项目有帮助，请给我们一个 ⭐ 表示支持！

---

*用 ❤️ 为 AI 社区构建*
