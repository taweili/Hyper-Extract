"""辨证论治逻辑图 - 建模 {症状群} -> 证型 -> 治则 -> {处方} 的完整推理链条。

适用于医案数据挖掘、名老中医经验传承。
"""

from typing import Any, List
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from hyperextract.types import AutoHypergraph


class TCMEntity(BaseModel):
    """中医实体节点"""

    name: str = Field(description="实体名称，如症状、证型、治则、药物等")
    category: str = Field(description="实体类型：症状、证型、治则、药物")
    description: str = Field(description="简要描述", default="")


class SyndromeReasoningEdge(BaseModel):
    """辨证论治逻辑边"""

    nodes: List[str] = Field(
        description="参与推理的节点列表，按推理顺序排列：[症状1, 症状2, ..., 证型, 治则, 药物1, 药物2, ...]"
    )
    reasoningType: str = Field(description="推理类型：辨证论治、随证加减")
    reasoningProcess: str = Field(description="推理过程描述", default="")
    source: str = Field(description="推理来源，如医案名称、章节等", default="")


_NODE_PROMPT = """## 角色与任务
你是一位专业的中医辨证论治专家，请从文本中提取所有关键实体作为节点。

## 核心概念定义
- **节点 (Node)**：图谱中的实体
- **边 (Edge)**：连接多个节点的超边，表达复杂的推理关系

## 提取规则
1. 提取所有症状、证型、治则、药物等实体
2. 为每个实体指定类型：症状、证型、治则、药物
3. 保持实体名称与原文一致
4. 症状应包含望闻问切所获得的各种临床表现
5. 证型应包含中医诊断的证候类型
6. 治则应包含治疗原则和方法
7. 药物应包含处方中的各种中药

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的中医辨证论治专家，请从给定实体列表中提取辨证论治的推理逻辑。

## 核心概念定义
- **节点 (Node)**：图谱中的实体
- **边 (Edge)**：连接多个节点的超边，表达复杂的推理关系

## 提取规则
1. 仅从下方已知实体列表中提取边
2. 不要创建未列出的实体
3. 每条边必须包含 nodes、reasoningType、reasoningProcess
4. nodes 列表必须按推理顺序排列：[症状1, 症状2, ..., 证型, 治则, 药物1, 药物2, ...]
5. reasoningType 应为"辨证论治"或"随证加减"
6. reasoningProcess 应详细描述从症状到证型、证型到治则、治则到处方的推理过程

"""

_PROMPT = """## 角色与任务
你是一位专业的中医辨证论治专家，请从文本中提取中医实体和它们之间的辨证论治推理逻辑。

## 核心概念定义
- **节点 (Node)**：图谱中的实体，如症状、证型、治则、药物等
- **边 (Edge)**：连接多个节点的超边，表达复杂的推理关系

## 提取规则
### 节点提取规则
1. 提取所有症状、证型、治则、药物等实体
2. 为每个实体指定类型：症状、证型、治则、药物
3. 保持实体名称与原文一致

### 边提取规则
1. 提取从症状到证型、证型到治则、治则到处方的完整推理链条
2. 每条边必须包含 nodes、reasoningType、reasoningProcess
3. nodes 列表必须按推理顺序排列：[症状1, 症状2, ..., 证型, 治则, 药物1, 药物2, ...]
4. reasoningType 应为"辨证论治"或"随证加减"
5. reasoningProcess 应详细描述推理过程

### 文言文特殊处理指导
- **症状表述解析**：文言症状常采用简洁表述，需完整理解其含义（如"恶寒发热"指怕冷和发热两个症状）
- **证型术语理解**：文言中证型表述需准确识别（如"太阳中风证"、"阳明腑实证"）
- **省略句式处理**：文言常省略主语或连接词，需根据上下文补充理解
- **医案结构识别**：医案通常有"症状→辨证→治法→方药"的结构，需按此顺序提取

### 源文本:
"""

# ==============================================================================
# 3. 模板类
# ==============================================================================


class SyndromeReasoningGraph(AutoHypergraph[TCMEntity, SyndromeReasoningEdge]):
    """
    适用文档: 中医医案、名医临床实录

    功能介绍:
    从中医医案中提取辨证论治的完整推理链条，建模 {症状群} -> 证型 -> 治则 -> {处方} 的逻辑关系，
    支持复杂的多实体关联关系。

    Example:
        >>> template = SyndromeReasoningGraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("...")
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
        初始化辨证论治逻辑图模板。

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
            node_schema=TCMEntity,
            edge_schema=SyndromeReasoningEdge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.reasoningType}|{'-'.join(x.nodes)}",
            nodes_in_edge_extractor=lambda x: x.nodes,
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
        展示辨证论治逻辑图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: TCMEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: SyndromeReasoningEdge) -> str:
            return edge.reasoningType

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
