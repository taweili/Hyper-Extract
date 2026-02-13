# Hyper-Extract 模板开发与 Master Prompt 协议

本文档定义了在 `Hyper-Extract` 框架中实现特定领域知识抽取模板的标准工作流。

## 0. 核心协议：阅读源码 (Source-First Protocol)

在编写任何代码之前，你**必须**：
1.  **明确基类**：根据需求从下表中选择合适的基类。
2.  **强制读码**：使用工具读取 `hyperextract/types/` 目录中对应基类的 Python 源码文件。
    *   *原因*：具体的 `__init__` 参数、`show` 方法签名和泛型约束以源码为准。

## 1. 设计阶段：可行性与选型

### 文档源优先 (Document-First Protocol)
在设计任何模板前，你**必须**明确回答以下问题：
*   **目标文档是什么？**：该模板是为该领域的哪类核心文档而设计？（如年报、SOP 手册、法律判决书、食品安全计划书）。
*   **文本逻辑是否原生？**：该结构是否在原始文档中自然存在，而非人为设计？（拒绝为"想当然的知识"设计结构）。
*   **提取证据清晰吗？**：文本中是否有显式的线索让 LLM 能够准确提取？

绝不设计为空中楼阁的知识图谱。模板必须映射真实文本的**已有逻辑结构**。

### 可提取性原则 (Extractability)
在设计 Schema 前自问：
*   **证据可用性**：输入文本是否显式包含该字段的证据？（拒绝为外部数据库才有的动态数据设计字段）。
*   **结构适配**：数据最自然的存在形式是什么？是无序重复、唯一集合还是复杂的多元关系？

### 选型映射表 (Mapping Table)

| 数据特性 | 推荐基类 | 核心源码位置 | 关键约束 |
| :--- | :--- | :--- | :--- |
| **单对象** (摘要/元数据) | `AutoModel` | `hyperextract/types/model.py` | 每个文档只提一个对象 |
| **模式集合** (重复提取) | `AutoList` | `hyperextract/types/list.py` | 不去重。提取文本中出现的所有模式实例 |
| **键值累加器** (术语/清单) | `AutoSet` | `hyperextract/types/set.py` | 按精确键累加信息，需定义 `key_extractor` |
| **标准图谱** (实体-关系) | `AutoGraph` | `hyperextract/types/graph.py` | 标准二元关系 |
| **时序图谱** (含时间戳) | `AutoTemporalGraph` | `hyperextract/types/temporal_graph.py` | 边必须包含时间字段 |
| **空间关系图谱** | `AutoSpatialGraph` | `hyperextract/types/spatial_graph.py` | 节点/边需包含位置坐标信息 |
| **时空演变图谱** | `AutoSpatioTemporalGraph` | `hyperextract/types/spatio_temporal_graph.py` | 同时描述空间移动与时间演变 |
| **多元/复杂事件** | `AutoHypergraph` | `hyperextract/types/hypergraph.py` | 超边连接 N 个节点 |

---

## 2. 实现规范 (Implementation Rules)

### A. Prompt 定义
*   **强制常数**：必须在类外部定义 `_PROMPT`（多行字符串）。
*   **内容要求**：明确定义专家角色、提取逻辑。如果某些字段有特定的提取格式要求，请在 Prompt 中强调。
*   **图谱/超图双阶段支持**：如果模板继承自 `AutoGraph`、`AutoHypergraph`、`AutoTemporalGraph`、`AutoSpatialGraph` 或 `AutoSpatioTemporalGraph`，你**必须定义三个独立的 Prompt** 以支持所有提取模式：
    1.  `_PROMPT`: 用于 "one_stage"（同时提取节点和边，速度快）。
    2.  `_NODE_PROMPT`: 用于 "two_stage" 第一步（仅提取节点，打基础）。
    3.  `_EDGE_PROMPT`: 用于 "two_stage" 第二步（基于已有节点提取边/超边，更精准）。
    
    在 `super().__init__` 中分别传递：
    ```python
    super().__init__(
        ...,
        prompt=_PROMPT,
        prompt_for_node_extraction=_NODE_PROMPT,
        prompt_for_edge_extraction=_EDGE_PROMPT,
        ...
    )
    ```

### B. 类结构
*   **Schema**：所有 Pydantic 字段必须包含 `description` 属性，这是 LLM 理解抽取目标的关键。
*   **文档注释 (Documentation)**：
    *   **类文档字符串 (Class Docstring)**：
        *   **强制声明（第一行）**：在类文档字符串的**最开头**，你**必须**用下列格式声明该模板的**适用文档类型**：
            ```
            Applicable to: [List specific document types, e.g., "SEC 10-K Item 1A, Prospectus Filings"]
            ```
        *   高层功能描述。
        *   一个展示如何初始化和使用的 **示例 (Example)**。
    *   **方法文档字符串 (Method Docstring)**：`__init__` 和 `show` 方法必须包含标准的 Google 风格文档字符串，详细说明每个参数 (`Args`)。
*   **参数准确性 (Parameter Accuracy)**：确保 `__init__` 中的每一个参数都在基类中存在。常见错误：`extraction_mode` 仅存在于 `AutoGraph` 系列中，**不存在**于 `AutoSet` 或 `AutoList` 中。
*   **初始化 (`__init__`)**：显式列参数（`llm_client`, `embedder` 等），并正确调用 `super().__init__(..., prompt=_TEMPLATE_PROMPT, ...)`。
*   **可视化 (`show`)**：必须覆盖 `show` 方法。
    *   **参数约束**：**禁止**在模板类的 `show` 方法签名中包含 `label_extractor` 参数。
    *   **实现要求**：你应该在 `show` 内部定义最适合该 Schema 的 **前端展示标签** 的提取函数，然后传给 `super().show(...)`。这样用户只需调用 `template.show()` 即可获得最佳效果。

---

## 3. 标准示例骨架 (Example Skeleton)

```python
from typing import Any, Callable
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from hyperextract.types import ... # 导入对应基类

# 1. 定义 Schema
class ItemSchema(BaseModel):
    name: str = Field(..., description="实体的名称")
    ...

# 2. 定义 Prompt
_PROMPT = """
你是一位[领域]专家。你的任务是从文本中提取[结构化知识]...
"""

# 3. 定义模板类
class MyTemplate(AutoType[ItemSchema]): # 替换为 AutoList, AutoSet 等
    """Google Style 类文档字符串。"""

    def __init__(
        self, 
        llm_client: BaseChatModel, 
        embedder: Embeddings, 
        chunk_size: int = 2048,
        **kwargs: Any
    ):
        super().__init__(
            item_schema=ItemSchema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            **kwargs
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ): 
        # 在内部定义展示逻辑
        def my_label_extractor(item: ItemSchema) -> str:
            return item.name

        super().show(
            item_label_extractor=my_label_extractor, # 传给基类
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
```


---

## 4. 运行时行为与使用说明 (Runtime Behavior & Usage)

### 自动提取 (Automatic Extraction)

调用 feed_text() 方法后，Hyper-Extract 框架会**自动并立即**处理文本并执行知识抽取：

\\python
template = MyTemplate(llm_client=..., embedder=...)

# 1. 输入文本
template.feed_text('你的输入文本...')

# 2. 框架自动处理！无需显式调用 extract()
# - 文本自动分块
# - Schema 自动抽取
# - 去重/关系建立自动完成

# 3. 直接查看结果或可视化
print(template.items)  # 查看提取的项目
template.show()         # 可视化知识图谱
\
**关键点**：
- feed_text() 动作会自动触发完整的提取流水线
- **不需要调用 extract() 方法**（这是内部实现细节）
- 支持链式调用：template.feed_text(...).show()
- 支持累积：多次调用 feed_text() 会累加知识

### 自定义提取模式 (Custom Extraction Mode)

对于 AutoGraph 系列模板，可在初始化时选择提取策略：

\\python
# 一阶段：同时提取节点和边（速度快）
template = MyGraph(llm_client=..., embedder=..., extraction_mode='one_stage')

# 二阶段：先提取节点，再提取边（精度高）
template = MyGraph(llm_client=..., embedder=..., extraction_mode='two_stage')
\

---

## 4. 运行时行为与使用说明 (Runtime Behavior & Usage)

### 自动提取 (Automatic Extraction)

调用 `feed_text()` 方法后，Hyper-Extract 框架会**自动并立即**处理文本并执行知识抽取：

```python
template = MyTemplate(llm_client=..., embedder=...)

# 1. 输入文本
template.feed_text("你的输入文本...")

# 2. 框架自动处理！无需显式调用 extract()
# - 文本自动分块
# - Schema 自动抽取
# - 去重/关系建立自动完成

# 3. 直接查看结果或可视化
print(template.items)  # 查看提取的项目
template.show()         # 可视化知识图谱
```

**关键点**：
- `feed_text()` 动作会自动触发完整的提取流水线
- **不需要调用 `extract()` 方法**（这是内部实现细节）
- 支持链式调用：`template.feed_text(...).show()`
- 支持累积：多次调用 `feed_text()` 会累加知识

### 自定义提取模式 (Custom Extraction Mode)

对于 `AutoGraph` 系列模板，可在初始化时选择提取策略：

```python
# 一阶段：同时提取节点和边（速度快）
template = MyGraph(llm_client=..., embedder=..., extraction_mode="one_stage")

# 二阶段：先提取节点，再提取边（精度高）
template = MyGraph(llm_client=..., embedder=..., extraction_mode="two_stage")
```
