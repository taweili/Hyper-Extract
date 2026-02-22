"""合规行为超图 - 建模“在何种条件下，何种主体，必须/禁止执行何种操作”的复杂逻辑。

适用于合规审计、风险识别等。
"""

from typing import Any, List, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class ComplianceEntity(BaseModel):
    """合规实体节点"""
    name: str = Field(description="实体名称")
    type: str = Field(description="实体类型：主体、操作、条件、约束、其他")
    description: str = Field(description="简要描述", default="")


class ComplianceRule(BaseModel):
    """合规规则超边（连接多个实体）"""
    ruleType: str = Field(description="规则类型：必须、禁止、允许、其他")
    participants: List[str] = Field(description="参与实体名称列表")
    condition: str = Field(description="适用条件", default="")
    action: str = Field(description="操作内容")
    details: str = Field(description="详细说明", default="")


_PROMPT = """你是一位专业的合规分析专家。请从文本中提取合规实体和规则，建模“在何种条件下，何种主体，必须/禁止执行何种操作”的复杂逻辑，构建合规行为超图。

### 节点提取规则
1. 提取所有合规相关实体
2. 为每个实体指定类型：主体、操作、条件、约束、其他
3. 为每个实体添加简要描述

### 超边提取规则
1. 仅从提取的实体中创建合规规则超边
2. 指定规则类型：必须、禁止、允许、其他
3. 列出所有参与实体（主体、操作、条件等）
4. 描述适用条件（如有）
5. 描述操作内容
6. 添加详细说明（如有）

### 约束条件
- 确保规则逻辑准确
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""

_NODE_PROMPT = """你是一位专业的合规实体识别专家。请从文本中提取所有合规相关实体作为节点。

### 提取规则
1. 提取所有合规相关实体
2. 为每个实体指定类型：主体、操作、条件、约束、其他
3. 为每个实体添加简要描述

### 源文本:
"""

_EDGE_PROMPT = """你是一位专业的合规规则提取专家。请从给定实体列表中提取合规规则超边。

### 约束条件
1. 仅从下方已知实体列表中提取超边
2. 不要创建未列出的实体

"""


class ComplianceLogic(AutoHypergraph[ComplianceEntity, ComplianceRule]):
    """
    适用文档: 合规指南、行政法规、公司管理制度

    功能介绍:
    建模“在何种条件下，何种主体，必须/禁止执行何种操作”的复杂逻辑。适用于合规审计、风险识别等。

    Example:
        >>> template = ComplianceLogic(llm_client=llm, embedder=embedder)
        >>> template.feed_text("宇宙第一摸鱼公司合规手册...")
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
        初始化合规行为超图模板。
        
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
            node_schema=ComplianceEntity,
            edge_schema=ComplianceRule,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.ruleType}_{sorted(x.participants)}",
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
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
        展示合规行为超图。
        
        Args:
            top_k_for_search: 语义检索返回的节点/边数量，默认为 3
            top_k_for_chat: 问答使用的节点/边数量，默认为 3
        """
        def node_label_extractor(node: ComplianceEntity) -> str:
            return f"{node.name} ({node.type})"
        
        def edge_label_extractor(edge: ComplianceRule) -> str:
            return edge.ruleType
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
