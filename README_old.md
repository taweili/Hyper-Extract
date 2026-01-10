
# Hyper-Extract 🧠

> **An Intelligent, LLM-Driven Knowledge Container Framework.**
>
> 一个基于 LLM 的智能知识提取与演化框架。不仅仅是存储数据，它能“阅读”、“思考”并“进化”。

## 📖 简介 (Introduction)

**Hyper-Extract** 是一个重新定义的非结构化数据处理框架。与传统的 ETL 工具不同，Hyper-Extract 的核心单元是 **Knowledge Container（知识容器）**。

每个容器（如 `SimpleGraph`, `HyperGraph`）都持有一个 **LLM 实例**。它们不仅仅是被动的数据结构，而是具有生命周期的智能体：

1.  **Extract (摄入)**: 主动利用 LLM 从文本中提取信息，并执行去重、对齐、合并。
2.  **Evolve (演化)**: 对已有知识进行内省（Introspection）。包括推理新关系、剪枝错误节点、图卷积传播等。
3.  **Dump (产出)**: 将清洗后的高质量知识导出为标准格式（JSON/NetworkX/Neo4j）。

## ✨ 核心特性 (Features)

*   **LLM Native**: 容器初始化即绑定 LangChain 模型实例，所有操作皆由大模型驱动。
*   **统一生命周期**: 所有知识类型遵循 `Extract` -> `Evolve` -> `Dump` 的标准范式。
*   **多模态结构支持**:
    *   **Graph**: 标准实体关系图谱 (Nodes + Edges)。
    *   **Hypergraph**: 支持超边（Hyperedge）连接多个节点的复杂语义结构 (HyperRAG 实现)。
*   **类型安全**: 全面基于 Pydantic Schema，确保结构化输出的稳定性。

## 🛠️ 安装 (Installation)

本项目使用 `uv` 进行包管理（也支持标准 pip）。

```bash
# 克隆项目
git clone https://github.com/your-username/hyper-extract.git
cd hyper-extract

# 使用 uv 安装依赖 (推荐)
uv sync

# 或者使用 pip
pip install -r requirements.txt
```

## 🚀 快速开始 (Quick Start)

### 1. 定义与初始化

```python
import asyncio
from langchain_openai import ChatOpenAI
from src.knowledge.graph.simple_graph import SimpleGraph

async def main():
    # 1. 准备大模型实例
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # 2. 初始化智能容器
    # 容器就像一个空的大脑，准备好接收信息
    kg = SimpleGraph(llm=llm)

    # 3. Extract: 摄入知识
    text = "Elon Musk co-founded OpenAI in 2015. He later left the board in 2018."
    print(f"正在提取: {text}...")
    await kg.extract(text)

    # 4. Evolve: 知识演化 (可选)
    # 例如：推断隐含关系或清理孤立节点
    await kg.evolve()

    # 5. Dump: 导出结果
    data = kg.dump(format="json")
    print("最终知识图谱:", data)

if __name__ == "__main__":
    asyncio.run(main())
```

## 📂 项目结构 (Project Structure)

```text
hyper-extract/
├── src/
│   ├── core/               # 核心抽象定义
│   ├── driver/             # LLM 驱动与适配器
│   ├── schema/             # Pydantic 数据结构定义 (GraphSchema, etc.)
│   └── knowledge/          # 知识容器实现
│       ├── base.py         # [核心] BaseKnowledge 基类
│       ├── graph/          # 普通图谱实现
│       │   ├── simple_graph.py     # 基础图提取
│       │   └── kg_gen_graph.py     # 复杂生成式图谱
│       └── hypergraph/     # 超图实现
│           ├── simple_hypergraph.py
│           └── hyperrag_hypergraph.py
├── tests/                  # 测试用例
├── main.py                 # 入口示例
├── pyproject.toml          # 项目配置
└── uv.lock                 # 依赖锁定
```

## 🧩 扩展指南 (Development)

如果你想添加一种新的知识结构（例如“思维导图”）：

1.  继承 `src.knowledge.base.BaseKnowledge`。
2.  定义你的数据 Schema (Pydantic)。
3.  实现 **`extract`**: 定义如何用 Prompt 将文本转化为你的 Schema。
4.  实现 **`evolve`** (可选): 定义如何优化你的数据结构。
5.  实现 **`dump`**: 定义导出格式。

## 📄 License

MIT License