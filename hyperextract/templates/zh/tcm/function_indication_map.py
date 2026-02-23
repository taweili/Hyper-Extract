"""主治功效映射 - 关联 方剂 -> 功能（如清热解毒） -> 主治证候。

适用于方剂推荐系统。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class GeneralEntity(BaseModel):
    """通用实体节点"""

    name: str = Field(description="实体名称")
    category: str = Field(description="实体类型：方剂、功能、主治证候")
    description: str = Field(description="简要描述", default="")


class GeneralRelation(BaseModel):
    """通用关系边"""

    source: str = Field(description="源实体")
    target: str = Field(description="目标实体")
    relationType: str = Field(description="关系类型：具有功能、主治")
    details: str = Field(description="详细描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的方剂学专家，请从文本中提取方剂、功能和主治证候之间的关联关系。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指通用实体，包括方剂、功能、主治证候等类型，用于表示知识图谱中的基本元素。
- **边 (Edge)**：本模板中的"边"指实体之间的二元关系，包括具有功能、主治等关系类型。

## 提取规则
### 节点提取规则
1. 提取所有实体：方剂、功能、主治证候
2. 为每个实体指定类型：方剂、功能、主治证候
3. 保持实体名称与原文一致
4. 为每个实体添加简要描述
5. **关键原子化要求**：如果文本中出现逗号、顿号、及、与、和等分隔的多个实体，必须将每个实体单独提取为一个独立节点，不要合并在一起。例如：
   - 原文"清热解毒、凉血止血"→拆分为"清热解毒"和"凉血止血"两个节点
   - 原文"头痛、发热、咳嗽"→拆分为"头痛"、"发热"、"咳嗽"三个节点
   - 原文"太阳病及阳明病"→拆分为"太阳病"和"阳明病"两个节点

### 关系提取规则
1. 提取方剂与功能之间的关系（具有功能）
2. 提取功能与主治证候之间的关系（主治）
3. 为每种关系添加详细描述

### 约束条件
- 每条边必须连接已提取的节点
- 不要创建未在文本中提及的实体或关系
- 保持客观准确，符合方剂学专业术语规范

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的实体识别专家，请从文本中提取所有方剂、功能和主治证候实体作为节点。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指通用实体，包括方剂、功能、主治证候等类型，用于表示知识图谱中的基本元素。

## 提取规则
1. 提取所有实体：方剂、功能、主治证候
2. 为每个实体指定类型：方剂、功能、主治证候
3. 保持实体名称与原文一致
4. 为每个实体添加简要描述
5. **关键原子化要求**：如果文本中出现逗号、顿号、及、与、和等分隔的多个实体，必须将每个实体单独提取为一个独立节点，不要合并在一起。例如：
   - 原文"清热解毒、凉血止血"→拆分为"清热解毒"和"凉血止血"两个节点
   - 原文"头痛、发热、咳嗽"→拆分为"头痛"、"发热"、"咳嗽"三个节点
   - 原文"太阳病及阳明病"→拆分为"太阳病"和"阳明病"两个节点

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的关系提取专家，请从给定实体列表中提取方剂、功能和主治证候之间的关联关系。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指通用实体，作为关系的参与者。
- **边 (Edge)**：本模板中的"边"指实体之间的二元关系，包括具有功能、主治等关系类型。

## 提取规则
1. 提取方剂与功能之间的关系（具有功能）
2. 提取功能与主治证候之间的关系（主治）
3. 为每种关系添加详细描述

### 约束条件
1. 仅从下方已知实体列表中提取边
2. 不要创建未列出的实体
3. 每条边必须包含 source、target、relationType

"""


class FunctionIndicationMap(AutoGraph[GeneralEntity, GeneralRelation]):
    """
    适用文档: 方剂规范、伤寒论、金匮要略、方剂学教材等

    功能介绍:
    关联 方剂 -> 功能（如清热解毒） -> 主治证候，适用于方剂推荐系统。

    Example:
        >>> template = FunctionIndicationMap(llm_client=llm, embedder=embedder)
        >>> template.feed_text("桂枝汤：解肌发表，调和营卫。主治太阳中风...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化主治功效映射模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=GeneralEntity,
            edge_schema=GeneralRelation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
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
        展示主治功效映射。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: GeneralEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: GeneralRelation) -> str:
            return edge.relationType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
