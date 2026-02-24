# Hyper-Extract 知识模板定义手册

本文档定义了在 `Hyper-Extract` 框架中实现特定领域知识抽取模板的标准工作流。

---

## 0. 核心协议：阅读源码

在编写任何代码之前，你**必须**：
1. **明确基类**：根据需求从下表中选择合适的基类。
2. **强制读码**：使用工具读取 `hyperextract/types/` 目录中对应基类的 Python 源码文件。

---

## 1. 设计阶段

### 1.1 文档源优先

在设计任何模板前，你**必须**明确回答以下问题：
*   **目标文档是什么？**：该模板是为该领域的哪类核心文档而设计？（如年报、SOP 手册、法律判决书）。
*   **文本逻辑是否原生？**：该结构是否在原始文档中自然存在，而非人为设计？
*   **提取证据清晰吗？**：文本中是否有显式的线索让 LLM 能够准确提取？

绝不设计为空中楼阁的知识图谱。模板必须映射真实文本的**已有逻辑结构**。

### 1.2 AutoType 选型映射表

| 数据特性 | 推荐基类 | 核心源码位置 | 关键约束 |
| :--- | :--- | :--- | :--- |
| **单对象** (摘要/元数据) | `AutoModel` | `hyperextract/types/model.py` | 每个文档只提一个对象 |
| **模式集合** (重复提取) | `AutoList` | `hyperextract/types/list.py` | 不去重。提取文本中出现的所有模式实例 |
| **键值累加器** (术语/清单) | `AutoSet` | `hyperextract/types/set.py` | 按精确键累加信息，需定义 `key_extractor` |
| **标准图谱** (实体-关系) | `AutoGraph` | `hyperextract/types/graph.py` | 标准二元关系 |
| **时序图谱** (含时间) | `AutoTemporalGraph` | `hyperextract/types/temporal_graph.py` | 边支持灵活时间格式 |
| **空间关系图谱** | `AutoSpatialGraph` | `hyperextract/types/spatial_graph.py` | 边支持灵活位置格式 |
| **时空演变图谱** | `AutoSpatioTemporalGraph` | `hyperextract/types/spatio_temporal_graph.py` | 同时支持灵活时间和位置 |
| **多元/复杂事件** | `AutoHypergraph` | `hyperextract/types/hypergraph.py` | 建模多个实体间的复杂关联关系 |

### 1.3 AutoHypergraph 应用场景说明

#### 核心定义
超边用于建模多个实体间的复杂关联关系，突破传统二元关系的限制，通过单一超边连接多个相关实体。

#### 核心价值
- 描述多个实体共同参与的事件或故事
- 保持事件的完整性，避免拆分成多个二元关系造成信息丢失
- 更符合人类认知中的"事件"概念（多参与者、多要素）

#### 典型应用场景
- **会议场景**：连接参会者、议题、地点、时间、决策结果
- **交易场景**：连接买方、卖方、产品、金额、时间、地点
- **案件场景**：连接嫌疑人、受害者、证人、时间、地点、证据
- **赛事场景**：连接参赛队伍、选手、比赛项目、时间、地点、结果

---

## 2. Schema 设计规范

### 2.1 核心原则
- **字段数量控制**：不超过 10 个核心字段
- **所有字段必须有 `description`**
- **代码标识符全英文**：类名、变量名、方法名必须使用英文
- **描述全中文**：对于 `zh` 目录下的模板，所有字段描述、注释、Prompt 必须使用中文

### 2.2 命名规范
- 类名：`PascalCase`（如 `FinancialReportGraph`）
- 变量/方法名：`camelCase`（如 `node_label_extractor`）

### 2.3 示例
```python
class FinancialEntity(BaseModel):
    """财务实体节点"""
    name: str = Field(description="实体名称，如公司名、产品名、部门名")
    category: str = Field(description="实体类型：公司、产品、部门")
    description: str = Field(description="简要描述", default="")

class FinancialRelation(BaseModel):
    """财务关系边"""
    source: str = Field(description="源实体")
    target: str = Field(description="目标实体")
    relationType: str = Field(description="关系类型：投资、收购、合作、竞争")
    timeInfo: Optional[str] = Field(
        description="时间信息，统一格式为年-月-日（如 2023-06-15）",
        default=None
    )
```

### 2.4 时空格式一致性原则

#### 单个模板内：严格一致
在同一个知识模板内部，时间格式和空间格式必须保持严格一致。所有提取出的时空信息应在信息提取阶段即完成标准化统一处理，确保数据的规范性和一致性，避免大模型处理时产生混乱。

**重要说明**：在 Prompt 中必须明确指定该模板采用的标准格式，要求 LLM 将所有时间/空间信息统一转换为该标准格式输出，而非保留原文的多种表达。

#### 不同模板间：灵活适配
不同知识模板之间的时间和空间格式可以根据具体领域需求灵活定义，但每个模板内部必须统一一种标准格式。以下是一些常见领域的格式建议（仅供参考）：
- **历史领域**：建议格式为年份（如 "2023"）或朝代（如 "清朝"）
- **金融领域**：建议格式为年-月-日（如 "2023-06-15"）
- **食谱领域**：建议格式为分:秒（如 "30:00"）
- **地理领域**：建议格式为省-市-区（如 "北京-朝阳"）

**注意**：格式的选择应基于目标文档的实际信息密度和领域惯例，而非过度设计。

---

## 3. 各 AutoType 特殊规范

### 3.1 AutoTemporalGraph（时序图谱）

#### 必须定义的提取器
- `node_key_extractor`: 实体唯一标识（如 `lambda x: x.name`）
- `edge_key_extractor`: 关系核心标识（不包含时间）
- `time_in_edge_extractor`: 从 Edge 中提取时间的函数
- `nodes_in_edge_extractor`: 从 Edge 中提取源/目标节点

#### Observation Time 参数
- 用户可指定，或自动默认当前日期
- 用于解析相对时间表达

#### Prompt 必须包含时间解析规则
```
### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年
   - "上月" → {observation_time} 的前一个月
   - "本季度" → {observation_time} 所在季度
   - "近期" → {observation_time} 最近 3 个月

2. 精确时间 → 保持原样
3. 时间缺失 → 留空，不要猜测
```

---

### 3.2 AutoSpatialGraph（空间图谱）

#### 必须定义的提取器
- `node_key_extractor`, `edge_key_extractor`
- `location_in_edge_extractor`: 从 Edge 中提取位置
- `nodes_in_edge_extractor`

#### Prompt 必须包含位置解析规则
```
### 位置解析规则
当前观察位置: {observation_location}

1. 相对位置解析（基于观察位置）:
   - "这里"、"本地" → {observation_location}
   - "附近"、"相邻" → {observation_location} 周边
   - "北边" → {observation_location} 北方

2. 精确位置 → 保持原样
3. 位置缺失 → 留空
```

---

### 3.3 AutoSet（键值累加器）

- 必须定义 `key_extractor`（精确键值匹配，非语义相似）
- Embedder 仅用于语义检索，不用于合并逻辑

---

## 4. Prompt 构建规范

### 4.1 完全预定义
- 用户无需编写任何 Prompt
- 所有 Prompt 预先定义并封装

### 4.2 图类型需定义 3 个 Prompt
| Prompt | 用途 |
|-------|------|
| `_PROMPT` | one_stage 模式：同时提取节点和边 |
| `_NODE_PROMPT` | two_stage 第一步：仅提取节点 |
| `_EDGE_PROMPT` | two_stage 第二步：基于已知节点提取边 |

### 4.3 Prompt 前置结构规范（图类型强制要求）

**图类型（AutoGraph/AutoHypergraph 等）必须遵循以下前置结构**：

```
## 角色与任务
你是一位专业的 xxx 专家，请从文本中提取 xxx...

## 核心概念定义（根据 AutoType 不同而变化）
- **概念1**：xxx
- **概念2**：xxx

## 提取规则
### 核心约束
#### _NODE_PROMPT / _PROMPT（节点提取）
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

#### _EDGE_PROMPT（边提取）
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 领域特定规则（可选）
不同领域存在专业术语或特定表述方式，可根据实际需求在对应Prompt中添加针对性规则。例如：
- 中医文献：古代剂量单位（两、钱、分、匕、枚等）可保留原文
- 金融领域：专业术语保持原文表述
- 医学领域：专业缩写保持原文

### 时空解析规则（仅时空图类型需要）
- 时间/位置解析规则...
```

**为什么需要概念定义？**
- 让大模型先理解要提取的"是什么"，再告诉它"怎么提取"
- 不同的 AutoType 有不同的核心概念，必须明确定义
- 概念定义必须放在 Prompt 的开头部分

**非图类型不需要核心概念定义**：
- **AutoModel**：直接提取结构化对象，对象定义已在 Pydantic Schema 中明确
- **AutoList**：直接提取条目列表，条目定义已在 Pydantic Schema 中明确
- **AutoSet**：直接提取元素集合，元素定义已在 Pydantic Schema 中明确

### 4.4 各 AutoType 的核心概念定义模板

#### AutoModel
```
## 核心概念定义
- **对象 (Object)**：从文本中提取的单一结构化对象，包含多个字段
```

#### AutoList
```
## 核心概念定义
- **条目 (Item)**：从文本中提取的重复模式实例
```

#### AutoSet
```
## 核心概念定义
- **元素 (Element)**：具有唯一键的知识单元，用于累积信息
```

#### AutoGraph
```
## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系
```

#### AutoHypergraph
```
## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：连接多个节点，表达多个实体间的复杂关联关系
```

#### AutoTemporalGraph / AutoSpatialGraph / AutoSpatioTemporalGraph
除了节点和边的定义，还需要添加时间/位置的定义：
```
## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系
- **时间**：xxx（根据实际需求定义）
- **位置**：xxx（根据实际需求定义）
```

---

## 5. 参数管理规范

### 5.1 标准暴露参数
| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| `llm_client` | `BaseChatModel` | ✓ | LLM 客户端 |
| `embedder` | `Embeddings` | ✓ | 嵌入模型 |
| `extraction_mode` | `str` | ✗ | 提取模式（仅图类型），默认 `"two_stage"` |
| `verbose` | `bool` | ✗ | 详细日志，默认 `False` |

### 5.2 可选特定类参数
| 参数 | 适用类型 | 说明 |
|-----|---------|------|
| `observation_time` | `AutoTemporalGraph`, `AutoSpatioTemporalGraph` | 观察时间，未指定时默认当前日期 |
| `observation_location` | `AutoSpatialGraph`, `AutoSpatioTemporalGraph` | 观察位置 |
| `max_workers` | 所有类型 | 最大工作线程数 |

### 5.3 隐藏参数（通过 **kwargs 传递）
- `chunk_size`, `chunk_overlap`
- `node_strategy_or_merger`, `edge_strategy_or_merger`
- 等其他技术参数

---

## 6. Show 函数设计规范

```python
def show(
    self,
    *,
    top_k_nodes_for_search: int = 3,
    top_k_edges_for_search: int = 3,
    top_k_nodes_for_chat: int = 3,
    top_k_edges_for_chat: int = 3,
):
    """
    展示知识图谱。
    
    Args:
        top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
        top_k_edges_for_search: 语义检索返回的边数量，默认为 3
        top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
        top_k_edges_for_chat: 问答使用的边数量，默认为 3
    """
    def node_label_extractor(node: MyNode) -> str:
        return node.name  # 简明 label，非唯一标识，展示友好
    
    def edge_label_extractor(edge: MyEdge) -> str:
        return edge.relationType
    
    super().show(
        node_label_extractor=node_label_extractor,
        edge_label_extractor=edge_label_extractor,
        top_k_nodes_for_search=top_k_nodes_for_search,
        top_k_edges_for_search=top_k_edges_for_search,
        top_k_nodes_for_chat=top_k_nodes_for_chat,
        top_k_edges_for_chat=top_k_edges_for_chat,
    )
```

---

## 7. 标准示例骨架

```python
from typing import Any, Callable, Optional
from datetime import datetime
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema (英文标识符，≤ 10 个字段，全中文描述)
# ==============================================================================

class FinancialEntity(BaseModel):
    """财务实体节点"""
    name: str = Field(description="实体名称，如公司名、产品名、部门名")
    category: str = Field(description="实体类型：公司、产品、部门")
    description: str = Field(description="简要描述", default="")

class FinancialRelation(BaseModel):
    """财务关系边"""
    source: str = Field(description="源实体")
    target: str = Field(description="目标实体")
    relationType: str = Field(description="关系类型：投资、收购、合作、竞争")
    timeInfo: Optional[str] = Field(
        description="时间信息，统一格式为年-月-日（如 2023-06-15）",
        default=None
    )
    details: str = Field(description="详细描述", default="")

# ==============================================================================
# 2. 预定义 Prompt（精简版）
# ==============================================================================

_NODE_PROMPT = """## 角色与任务
你是一位专业的[领域]专家，请从文本中提取所有实体作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的[领域]专家，请从给定实体列表中提取实体之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
1. 仅从已知实体列表中提取边，不要创建未列出的实体
2. 关系描述应与原文保持一致

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年
   - "上月" → {observation_time} 的前一个月

2. 精确时间 → 保持原样
3. 时间缺失 → 留空
"""

_PROMPT = """## 角色与任务
你是一位专业的[领域]专家，请从文本中提取实体和它们之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的实体
- **边 (Edge)**：节点之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并
2. 实体名称与原文保持一致
3. 仅从已知实体列表中提取边，不要创建未列出的实体
4. 关系描述应与原文保持一致

### 时间解析规则
当前观察日期: {observation_time}

1. 相对时间解析（基于观察日期）:
   - "去年" → {observation_time} 的前一年
   - "上月" → {observation_time} 的前一个月

2. 精确时间 → 保持原样
3. 时间缺失 → 留空

### 源文本:
"""

# ==============================================================================
# 3. 模板类
# ==============================================================================

class FinancialReportGraph(AutoTemporalGraph[FinancialEntity, FinancialRelation]):
    """
    适用文档: SEC 10-K/10-Q 财报、年报、季度报告
    
    功能介绍:
    从财报文档中提取公司、产品、部门等实体，以及它们之间的投资、收购、合作等关系，
    支持灵活的时间格式。
    
    Example:
        >>> template = FinancialReportGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        observation_time: str | None = None,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化财报知识图谱模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            observation_time: 观察时间，用于解析相对时间表达，
                如未指定则使用当前日期
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        if observation_time is None:
            observation_time = datetime.now().strftime("%Y-%m-%d")
        
        super().__init__(
            node_schema=FinancialEntity,
            edge_schema=FinancialRelation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
            time_in_edge_extractor=lambda x: x.timeInfo or "",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
            extraction_mode=extraction_mode,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ):
        """
        展示知识图谱。
        
        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """
        def node_label_extractor(node: FinancialEntity) -> str:
            return node.name
        
        def edge_label_extractor(edge: FinancialRelation) -> str:
            return edge.relationType
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
```

---

## 8. 运行时行为说明

调用 `feed_text()` 后，框架会自动处理文本并执行知识抽取：
```python
template = MyTemplate(llm_client=..., embedder=...)
template.feed_text("...")  # 自动触发提取
template.show()               # 可视化
```

关键点：
- `feed_text()` 自动触发完整流水线，无需调用 `extract()`
- 支持链式调用：`template.feed_text(...).show()`
- 支持累积：多次调用 `feed_text()` 累加知识
