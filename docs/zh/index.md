# Hyper-Extract 🧠✨

> **一个智能的、基于 LLM 的知识提取与演化框架**
>
> 借助大语言模型的力量，将非结构化文本转化为结构化、可演化的知识容器。

---

## 🎯 愿景

**Hyper-Extract** 将知识提取重新定义为一个智能的、自我演化的过程。我们不是将数据结构视为被动容器，而是赋予它们 **LLM 驱动的智能**，使其能够主动地从非结构化文本中提取、合并、演化和索引知识。

Hyper-Extract 中的每个知识容器都遵循统一的生命周期：

1. **Extract（提取）** - 使用 LLM 从文本智能提取，自动处理分块和合并
2. **Evolve（演化）** - 通过推理、剪枝和优化实现自我优化
3. **Index（索引）** - 提供语义向量搜索能力
4. **Serialize（序列化）** - 完整保存和加载知识状态

---

## ✨ 核心特性

### 🤖 LLM 原生设计
- **深度 LangChain 集成**：每个容器都使用 LLM 和嵌入模型初始化
- **结构化输出**：利用 `with_structured_output` 实现类型安全的 Pydantic 模式提取
- **智能合并**：针对分块提取的优先级合并策略

### 🏗️ 统一架构
- **抽象基类**：`BaseKnowledge[T]` 为所有知识类型提供一致的接口
- **泛型类型支持**：使用 `Generic[T]` 实现完整的 Python 类型提示
- **生命周期管理**：标准化的 `extract` → `merge` → `evolve` → `search` → `dump/load` 流程

### 🔍 语义搜索
- **FAISS 集成**：快速的向量相似度搜索
- **自动索引**：支持懒加载和脏数据跟踪
- **字段级搜索**：可以在所有 schema 字段中搜索，并保留元数据

### 📦 知识模式

#### ✅ 已实现
- **UnitKnowledge**：单对象提取，适用于文档级信息（摘要、元数据）
- **ListKnowledge**：列表提取，适用于实体、事件和结构化列表
- **SetKnowledge**：唯一集合，支持自动去重和智能合并策略

#### 🚧 开发中
- **EntityKnowledge**：实体中心的提取，支持属性管理
- **RelationKnowledge**：关系提取，支持实体链接
- **GraphKnowledge**：知识图谱构建（节点 + 边）
- **HypergraphKnowledge**：超图表示，用于复杂的多实体关系

---

## 🛠️ 安装

### 前置要求
- Python 3.10+
- OpenAI API 密钥（或兼容的 LLM 提供商）

### 使用 uv 安装（推荐）
```bash
# 克隆仓库
git clone https://github.com/your-username/hyper-extract.git
cd hyper-extract

# 使用 uv 安装依赖
uv sync
```

### 使用 pip 安装
```bash
pip install -e .
```

---

## 🚀 快速开始

### 1. 定义知识 Schema

```python
from pydantic import BaseModel, Field
from typing import List

class ArticleKnowledge(BaseModel):
    """文章知识提取的 Schema"""
    title: str = Field(default="", description="文章标题")
    author: str = Field(default="", description="作者名称")
    summary: str = Field(default="", description="文章摘要")
    key_points: List[str] = Field(default_factory=list, description="关键要点")
    topics: List[str] = Field(default_factory=list, description="主题标签")
```

### 2. 初始化知识容器

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from hyperextract.knowledge.generic import UnitKnowledge

# 初始化 LLM 和嵌入模型
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

# 创建知识容器
knowledge = UnitKnowledge(
    data_schema=ArticleKnowledge,
    llm_client=llm,
    embedder=embedder
)
```

### 3. 提取知识

```python
# 从文本提取
text = """
《深度学习导论》是由李明教授撰写的一本综合性教材...
"""

knowledge.extract(text)
print(knowledge.data)  # 访问提取的结构化知识
```

### 4. 语义搜索

```python
# 构建索引
knowledge.build_index()

# 搜索相关内容
results = knowledge.search("深度学习的主要应用", k=3)
for doc, score in results:
    print(f"相关度: {score}, 内容: {doc.page_content}")
```

### 5. 持久化

```python
# 保存到磁盘
knowledge.dump("./my_knowledge")

# 加载
loaded_knowledge = UnitKnowledge.load(
    "./my_knowledge",
    data_schema=ArticleKnowledge,
    llm_client=llm,
    embedder=embedder
)
```

---

## 📚 文档导航

- **[快速入门指南](user-guide/getting-started.md)** - 详细的入门教程
- **[知识模式指南](user-guide/knowledge-patterns.md)** - 了解不同的知识提取模式
- **[API 参考](api/base.md)** - 完整的 API 文档

---

## 🤝 贡献

欢迎贡献！请查看我们的贡献指南了解详情。

---

## 📄 许可证

本项目基于 MIT 许可证开源。
