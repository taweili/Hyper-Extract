"""执行程序流程图 - 提取规章中规定的申报、审批或操作的具体先后步骤。

适用于操作导引、SOP 流程可视化等。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class ProcedureStep(BaseModel):
    """流程步骤节点"""
    stepId: str = Field(description="步骤编号，如步骤1、步骤2")
    name: str = Field(description="步骤名称")
    description: str = Field(description="步骤详细描述")
    role: str = Field(description="执行角色", default="")
    inputRequired: str = Field(description="所需输入/材料", default="")
    outputResult: str = Field(description="输出/结果", default="")


class ProcedureTransition(BaseModel):
    """流程转换边"""
    source: str = Field(description="源步骤编号")
    target: str = Field(description="目标步骤编号")
    condition: str = Field(description="转换条件", default="")
    details: str = Field(description="详细说明", default="")


_PROMPT = """你是一位专业的流程分析专家。请从文本中提取规章中规定的申报、审批或操作的具体先后步骤，构建执行程序流程图。

### 节点提取规则
1. 提取所有流程步骤
2. 为每个步骤分配编号（如步骤1、步骤2）
3. 为每个步骤添加名称和详细描述
4. 记录执行角色（如有）
5. 记录所需输入或材料（如有）
6. 记录输出或结果（如有）

### 边提取规则
1. 仅从提取的步骤中创建转换边
2. 记录步骤之间的先后关系
3. 记录转换条件（如有）
4. 记录详细说明（如有）

### 约束条件
- 确保流程步骤的先后顺序准确
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""

_NODE_PROMPT = """你是一位专业的流程步骤识别专家。请从文本中提取所有流程步骤作为节点。

### 提取规则
1. 提取所有流程步骤
2. 为每个步骤分配编号（如步骤1、步骤2）
3. 为每个步骤添加名称和详细描述
4. 记录执行角色（如有）
5. 记录所需输入或材料（如有）
6. 记录输出或结果（如有）

### 源文本:
"""

_EDGE_PROMPT = """你是一位专业的流程转换识别专家。请从给定步骤列表中提取步骤之间的先后关系。

### 约束条件
1. 仅从下方已知步骤列表中提取边
2. 不要创建未列出的步骤

"""


class OperationalProcedure(AutoGraph[ProcedureStep, ProcedureTransition]):
    """
    适用文档: 操作手册、SOP、合规指南、审批流程

    功能介绍:
    提取规章中规定的申报、审批或操作的具体先后步骤。适用于操作导引、SOP 流程可视化等。

    Example:
        >>> template = OperationalProcedure(llm_client=llm, embedder=embedder)
        >>> template.feed_text("宇宙第一摸鱼公司请假审批流程...")
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
        初始化执行程序流程图模板。
        
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
            node_schema=ProcedureStep,
            edge_schema=ProcedureTransition,
            node_key_extractor=lambda x: x.stepId,
            edge_key_extractor=lambda x: f"{x.source}|{x.target}",
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
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        展示执行程序流程图。
        
        Args:
            top_k_for_search: 语义检索返回的节点/边数量，默认为 3
            top_k_for_chat: 问答使用的节点/边数量，默认为 3
        """
        def nodeLabelExtractor(node: ProcedureStep) -> str:
            return f"{node.stepId}: {node.name}"
        
        def edgeLabelExtractor(edge: ProcedureTransition) -> str:
            if edge.condition:
                return edge.condition
            return "→"
        
        super().show(
            node_label_extractor=nodeLabelExtractor,
            edge_label_extractor=edgeLabelExtractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
