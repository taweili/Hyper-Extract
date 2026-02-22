"""合规行为超图 - 建模"在何种条件下，何种主体，必须/禁止执行何种操作"的复杂逻辑。

适用于合规审计、风险识别等。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class ComplianceElement(BaseModel):
    """合规要素 - 节点"""
    name: str = Field(description="要素名称")
    type: str = Field(description="要素类型：主体、操作、条件、其他")
    description: str = Field(description="简要描述", default="")


class ComplianceRule(BaseModel):
    """合规规则 - 超边"""
    rule_type: str = Field(description="规则类型：必须、禁止、允许、其他")
    action: str = Field(description="要求执行或禁止的操作内容")
    condition: str = Field(description="适用条件/前置要求", default="")
    penalty: str = Field(description="违规后果/处罚措施", default="")
    source_clause: str = Field(description="规则来源条款", default="")
    notes: str = Field(description="补充说明", default="")
    participants: List[str] = Field(description="参与要素名称列表")


_PROMPT = """你是一位专业的合规分析专家。请从文本中提取合规要素和规则，建模"在何种条件下，何种主体，必须/禁止执行何种操作"的复杂逻辑，构建合规行为超图。

### 节点提取规则
1. 提取规则中涉及的要素作为节点
2. 为每个要素指定类型：主体、操作、条件、其他
3. 为每个要素添加简要描述

### 超边提取规则
1. 仅从提取的要素中创建合规规则（超边）
2. 指定规则类型：必须、禁止、允许、其他
3. 填写要求执行或禁止的操作内容（必须）
4. 提取适用条件/前置要求（如有）
5. 提取违规后果/处罚措施（如有）
6. 提取规则来源条款（如有）
7. 添加补充说明（如有）
8. 列出所有参与要素名称（必须）

### 约束条件
- 确保规则逻辑准确
- 保持客观准确，不添加文本中没有的信息
- 每条超边必须包含 rule_type、action 和 participants
- 其他字段尽量填充，缺失的使用空字符串

### 源文本:
"""

_NODE_PROMPT = """你是一位专业的合规要素识别专家。请从文本中提取所有合规相关要素作为节点。

### 提取规则
1. 提取规则中涉及的要素
2. 为每个要素指定类型：主体、操作、条件、其他
3. 为每个要素添加简要描述

### 源文本:
"""

_EDGE_PROMPT = """你是一位专业的合规规则提取专家。请从给定节点（要素）列表中提取合规规则超边。

### 约束条件
1. 仅从下方已知要素列表中提取规则（超边）
2. 不要创建未列出的要素
3. 每条规则必须包含 rule_type、action 和 participants
4. 其他字段尽量填充，缺失的使用空字符串

"""


class ComplianceLogic(AutoHypergraph[ComplianceElement, ComplianceRule]):
    """
    适用文档: 合规指南、行政法规、公司管理制度

    功能介绍:
    建模"在何种条件下，何种主体，必须/禁止执行何种操作"的复杂逻辑。适用于合规审计、风险识别等。

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
            node_schema=ComplianceElement,
            edge_schema=ComplianceRule,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{sorted(x.participants)}_{x.rule_type}_{x.action}",
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
        def node_label_extractor(node: ComplianceElement) -> str:
            return f"{node.name} ({node.type})"

        def edge_label_extractor(edge: ComplianceRule) -> str:
            return f"[{edge.rule_type}] {edge.action}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
