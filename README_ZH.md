# Hyper-Extract: 垂直领域 AI Agent 的知识引擎 🧠🚀

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

**Hyper-Extract** 是一个下一代知识提取框架，旨在将海量、非结构化的领域文档转化为**可搜索、可查询、可推理**的知识结构。

不要再把你的文档当作死气沉沉的文本切片。通过 Hyper-Extract，每一份 PDF、研报、说明书都能转化为 AI Agent 动态调用的“活体大脑”。

[English (README.md)](README.md) | [示例代码](examples/)

---

## 🌟 为什么选择 Hyper-Extract?

传统的 RAG 模型在垂直和专业领域往往因为丢失知识的**逻辑结构**而失效。Hyper-Extract 通过独特的**三层分级架构**解决这一痛点：

### 🧱 第一级：知识基础原语 (`hyperextract.types`)
知识的 "DNA"。我们根据信息复杂度的不同，将 "AutoType" 结构分为四个层级：

| 层级 | 基础原语 | 核心逻辑 | 适用场景 |
| :--- | :--- | :--- | :--- |
| **标量与文档型** | `AutoModel` | 多个切片 -> **一个**一致性的对象 | 研报摘要、百科条目、元数据提取 |
| **集合型** | `AutoList`, `AutoSet` | 独立项或唯一实体的去重集合 | 实体清单、术语表、RPG 手册 |
| **图谱型** | `AutoGraph`, `AutoHypergraph` | 二元 (Pairwise) 或多元 (N-ary) 关系 | 知识图谱、多因素复杂因果推理 |
| **时空感知型** | `AutoTemporalGraph`, `AutoSpatialGraph`, `AutoSpatioTemporalGraph` | 解析相对的时间/空间上下文 | 编年史、时政新闻、拓扑描述 |

### ⚙️ 第二级：核心提取引擎 (`hyperextract.methods`)
系统的 "大脑"。内置 SOTA 算法，让数据结构产生生产力：
- **Light-RAG / GraphRAG**: 在图谱结构上进行高效率的全局检索。
- **Hyper-RAG / CogRAG**: 基于复杂超图和认知层级的推理问答引擎。
- **Typical Methods**: 支持 iText2KG, KG-Gen 等经典提取逻辑。

### 🧠 第三级：12+ 行业领域专家模板 (`hyperextract.templates`)
你的专业 "灵魂"。开箱即用的行业 Schema 和 Prompt：
- **金融、医疗、法律、中医、工业、历史、生物、文学、旅游、新闻、农业、美食。**

---

## 🎭 瞬间转化：从静态文档到行业专家 Agent 🤖

"让每一行文本都具有交互性。"

| 领域 | 原始文档输入 | 转化后的 Agent 能力 |
| :--- | :--- | :--- |
| **💰 金融** | 研报、公告、招股书 | **投研助手 Agent** (推理各公司估值逻辑与驱动因素) |
| **🏥 医疗** | 临床指南、病案、说明书 | **诊疗分析 Agent** (从症状推演鉴别诊断路径) |
| **⚖️ 法律** | 合同协议、判决文书 | **合规风控 Agent** (一分钟内提取复杂责任与违约关系) |
| **🔧 工业** | 运维日志、技术规格书 | **排故专家 Agent** (关联故障现象与其根本原因) |
| **📜 历史** | 编年史、信札、传记 | **文史学家 Agent** (还原复杂的历史事件因果链条) |

---

## 🚀 快速上手：构建一个“可对话”的领域知识库

```python
from hyperextract.types import AutoGraph
from hyperextract.templates.zh.finance import ResearchNoteSummary
from langchain_openai import ChatOpenAI

# 1. 加载一个行业模板 (例如: 金融研报摘要)
llm = ChatOpenAI(model="gpt-5-mini")
kb = AutoGraph.from_template(ResearchNoteSummary, llm_client=llm)

# 2. “喂入” 领域文本 (自动完成知识提取与建模)
text = "苹果公司的估值核心逻辑在于其服务收入的增长以及 iPhone 16 的换机周期..."
kb.feed_text(text)

# 3. 针对结构化知识直接对话 (具有逻辑支撑的答案)
answer = kb.chat("苹果公司的估值驱动因素有哪些？")
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
