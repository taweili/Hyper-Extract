# Hyper-Extract 🖥️

[English Version](./README.md) · [中文版](#)

---

## 首个 CLI 优先的知识提取引擎

> 只需一行命令，将任何文档转化为**可搜索、可查询、可推理**的结构化知识。

**8 种知识结构** · **5 种提取方法** · **200+ 领域模板** · **中英文支持**


<!-- 架构图 -->
![架构图](docs/assets/fw.png)

---

## ⚡ 一行命令提取知识

```bash
# 安装
uv pip install hyperextract

# 提取 → 构建 → 问答 (逐行执行)
he parse report.md -o kb -t graph -l zh    # 提取知识
he talk kb -i                                # 交互式问答
he search kb "营收增长原因"                   # 语义搜索
he show kb                                   # 可视化
```

### 💻 CLI 命令

| 命令 | 说明 |
|---------|-------------|
| `he parse` | 从文本/文件提取知识 |
| `he talk` | 与知识库交互问答 |
| `he search` | 语义搜索 |
| `he show` | 可视化知识图谱 |
| `he list` | 列出可用模板/方法 |
| `he config` | 配置 LLM/Embedding |
| `he info` | 查看知识库信息 |
| `he feed` | 向现有知识库追加内容 |
| `he build-index` | 构建向量索引 |

---

## "Chat 已解决，下一步是 CLI + 知识结构"

将 LLM 输出的文本转化为**可搜索、可查询、可推理**的结构化知识。

---

## ❌ 以前 | ✅ 现在

<!-- 概念图 -->
![概念图](./docs/assets/concept.png)

| 以前 | 现在 |
| :--- | :--- |
| LLM 输出一堆文本 | 结构化知识（8种类型） |
| ❌ 需要写 Python 代码 | ✅ CLI 优先（`he` 命令） |
| ❌ 只支持简单图谱 | ✅ 图谱/时序/空间/超图... |
| ❌ 回答完就消失 | ✅ 可持久化存储 |
| ❌ 无法精准检索 | ✅ 语义搜索 |
| ❌ 难以追溯源头 | ✅ 可追溯来源 |
| ❌ 只有一种语言 | ✅ 中英文双语支持 |
| ❌ 碎片化无法复用 | ✅ 知识沉淀复用 |

---

## 🧩 8 种知识结构（不只是简单图谱）

> 与其他只支持基础图谱的工具不同，Hyper-Extract 支持**复杂、多维的知识结构**。

<!-- AutoTypes 图 -->
![AutoTypes](./docs/assets/autotypes.png)

| 类型 | 图标 | 功能 |
| :--- | :---: | :--- |
| **AutoModel** | 📋 | 提取为完整的数据模型 |
| **AutoList** | 📝 | 提取为列表 |
| **AutoSet** | 📦 | 提取并去重 |
| **AutoGraph** | 🔗 | 提取为知识图谱 |
| **AutoTemporalGraph** | ⏱️ | 提取为时序图（时间线） |
| **AutoSpatialGraph** | 📍 | 提取为空间图（地理位置） |
| **AutoSpatioTemporalGraph** | 🌏 | 提取为时空图（时间+空间） |
| **AutoHypergraph** | 🌐 | 提取为超图（多方关系） |

---

## 🔬 提取方法对比

> Hyper-Extract 实现了**多种**提取方法，而非只有一种。

| 方法 | 类型 | 图谱 | 时序 | 空间 | 时空 | 超图 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **KG-Gen** | 图谱 | ✅ | ❌ | ❌ | ❌ | ❌ |
| **ATOM** | 原子 | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Graphiti** | 时序 | ❌ | ✅ | ❌ | ❌ | ❌ |
| **LightRAG** | 图谱 | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Hyper-RAG** | 超图 | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Hyper-Extract** | **全能型** | ✅ | ✅ | ✅ | ✅ | ✅ |

**选择适合你需求的方法，或让 AutoTypes 自动选择。**

---

## 🌍 12 个领域，200+ 开箱即用模板

> 针对**不同行业**预置的模板 —— 无需设计schema，直接提取知识。

| 领域 | 模板数 | 领域 | 模板数 |
| :--- | :---: | :--- | :---: |
| 💰 金融 | 25+ | 📜 历史 | 12+ |
| 🏥 医疗 | 20+ | 🧬 生物 | 10+ |
| ⚖️ 法律 | 15+ | 🎭 文学 | 10+ |
| 🌿 中医 | 15+ | 📰 新闻 | 12+ |
| 🔧 工业 | 18+ | 🌾 农业 | 8+ |
| 🍜 美食 | 8+ | 🌐 通用 | 20+ |

**✅ 双语支持** — 模板同时支持中文和英文

---

## 🚀 快速开始

### 方式一：CLI（推荐）⚡

```bash
# 从文档提取知识
he parse document.pdf -o my_kb -t knowledge_graph -l zh

# 与知识库问答
he talk my_kb -i

# 语义搜索
he search my_kb "公司营收增长原因"

# 可视化知识图谱
he show my_kb
```

### 方式二：Python API

```python
from hyperextract.utils.template_engine import Gallery, TemplateFactory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4o-mini")
embedder = OpenAIEmbeddings()

config = Gallery.get("ResearchNoteSummary")
template = TemplateFactory.create(config, llm, embedder)
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
├── cli/                      # 💻 CLI 接口（he 命令）
│   ├── commands/            # parse, talk, search, show...
│   └── __main__.py          # 入口
│
├── types/                    # 🧩 8 种知识结构
│   ├── model.py             # AutoModel
│   ├── list.py              # AutoList
│   ├── set.py               # AutoSet
│   ├── graph.py             # AutoGraph
│   ├── hypergraph.py        # AutoHypergraph
│   ├── temporal_graph.py    # AutoTemporalGraph
│   ├── spatial_graph.py     # AutoSpatialGraph
│   └── spatio_temporal_graph.py  # AutoSpatioTemporalGraph
│
├── methods/                  # 🔬 提取引擎
│   ├── rag/                 # LightRAG, HyperRAG, CogRAG
│   └── typical/             # KG-Gen, ATOM（复现）
│
└── templates/                # 🌍 200+ 领域模板
    ├── zh/                  # 中文模板（25+ 领域）
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
