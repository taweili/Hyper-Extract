# Hyper-Extract: 从文本到可交互的知识结构 🚀

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

**Hyper-Extract** 是一个下一代知识提取框架，旨在将非结构化文本转化为**可搜索、可查询、可问答**的结构化知识。

区别于传统的只负责“提取”的工具，Hyper-Extract 将提取出的结构（如列表、图谱、超图）自动转化为可交互的知识库。你可以直接与提取出的结构进行对话，进行精确的语义搜索，实现“提取即应用”。

[English README](README.md)

---

## 🌟 核心特性

- **📂 全模态结构支持**:
  - **基础结构**: List (列表), Set (集合), Graph (通用图谱)。
  - **时空动力学**: Temporal Graph (时序图), Spatial Graph (地理图), Spatio-Temporal Graph (时空图)。
  - **复杂关联**: Hypergraph (超图/多元图)，支持多对多复杂关系建模。
- **💬 结构化知识问答 (RAG 2.0)**:
  - 提取不仅仅是终点。Hyper-Extract 自动为提取出的实体和关系建立向量索引。
  - **Chat with Structure**: 直接针对图谱或集合进行问答，获得具有结构化逻辑支撑的答案。
- **🛠️ 工业级算法复现**:
  - 内置了多种 SOTA 提取与检索算法的复现，包括 `Auto-Gen`, `Hyper-RAG`, `Light-RAG`, `GraphRAG`, `CogRAG` 等。
- **🎭 领域专家模版库**:
  - 提供了 20+ 个领域的开箱即用模版，涵盖：金融、医疗、法律、游戏、农业、网络安全、物理、文学等。

---

## 🚀 快速上手

### 安装

```bash
pip install hyperextract
```

### 3步实现“对话知识图谱”

Hyper-Extract 让复杂结构的提取和使用变得异常简单：

```python
from pydantic import BaseModel, Field
from hyperextract.types import AutoGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 1. 定义你想要提取的结构 (Schema)
class entity(BaseModel):
    name: str = Field(description="实体名称")
    type: str = Field(description="类别，如：人、公司、地点")

class edge(BaseModel):
    source: str = Field(description="源实体")
    target: str = Field(description="目标实体")
    relation: str = Field(description="它们之间的关系")

# 2. 初始化提取器并从文本构建图谱
llm = ChatOpenAI(model="gpt-4o")
embedder = OpenAIEmbeddings()

graph_kb = AutoGraph(
    node_schema=entity,
    edge_schema=edge,
    # 唯一键提取规则，用于去重和关联
    node_key_extractor=lambda x: x.name,
    edge_key_extractor=lambda x: f"{x.source}_{x.relation}_{x.target}",
    nodes_in_edge_extractor=lambda x: (x.source, x.target),
    llm_client=llm, 
    embedder=embedder
)

text = "苹果公司由史蒂夫·乔布斯在加利福尼亚州创立，它是著名的iPhone制造商。"
graph_kb.feed_text(text) # 提取知识
graph_kb.build_index() # 构建向量索引 (用于后续问答)

# 3. 针对提取出的结构进行问答 (Actionable!)
answer = graph_kb.chat("乔布斯和苹果公司是什么关系？")
print(answer.content)
```

---

## 🎨 领域模版 (Templates)

本项目在 `hyperextract/templates` 下提供了丰富的领域定义，你可以直接导入使用，无需从头编写 Prompt 或 Schema：

| 领域 | 包含模版 | 描述 |
| :--- | :--- | :--- |
| **通用** | `General`, `IText2KG` | 适用于大多数日常知识提取。 |
| **科学** | `Physics`, `Chemistry`, `Biology` | 捕捉科学实验、元素、反应过程。 |
| **行业** | `Finance`, `Legal` | 提取合规、风险点、实体关联。 |
| **娱乐** | `Game`, `Movie`, `Food` | 完美支持游戏剧情、角色关系网、食谱制作。 |
| ... | | 更多 15+ 领域见 [templates 目录](hyperextract/templates) |

---

## 🏗️ 核心组件

- **`hyperextract.types`**: 核心 AutoTypes 数据类型（如 AutoModel, AutoGraph, AutoHypergraph 等）。
- **`hyperextract.methods`**: 知识提取算法与 RAG 策略（如 Hyper-RAG, Cog-RAG, iText2KG 等）。
- **`hyperextract.utils`**: 日志、合并策略等实用工具。

---

## 📚 已复现论文/算法

- **Auto-Graph**: 自动 Schema 适应的图提取。
- **Hyper-RAG**: 基于超图的检索增强生成。
- **Light-RAG**: 轻量化、高效率的图检索。
- **IText2KG / IText2KG-Star**: 迭代式知识图谱生成。
- **CogRAG**: 认知驱动的层次化检索。

---

## 🤝 贡献与反馈

欢迎提交 Issue 或 Pull Request 来完善这个项目！

- **开源协议**: [MIT LICENSE](LICENSE)
- **Star我们**: 如果这个项目对你有帮助，请给一个 ⭐️ 以示支持！
