from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.graphs.base import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class StakeholderNode(BaseModel):
    """
    在业务中持有股份或拥有控制权的法人或自然人。
    """
    name: str = Field(description="公司注册全称或个人全名。")
    type: str = Field(description="类型：'自然人'、'上市公司'、'私有公司'、'国有企业'、'风险投资'。")
    jurisdiction: Optional[str] = Field(None, description="注册地或居住地所属的国家或地区。")
    is_ubo: bool = Field(False, description="该实体是否被识别为最终受益人（UBO）。")

class OwnershipRelation(BaseModel):
    """
    两个实体之间的持股或控制联系。
    """
    source: str = Field(description="股东或母公司实体。")
    target: str = Field(description="被拥有或控制的公司（子公司）。")
    stake_percentage: Optional[float] = Field(None, description="持股比例（0.0 到 100.0）。")
    control_type: str = Field("Equity", description="联系性质：'股权收购'、'投票权'、'代持股份'、'直接控制'。")
    as_of_date: Optional[str] = Field(None, description="记录该所有权的时间点或财务周期。")

# ==============================================================================
# 2. Prompts
# ==============================================================================

EQUITY_CONSOLIDATED_PROMPT = (
    "你是一位企业法务助理和财务分析师。请提取复杂的股权结构。\n\n"
    "规则：\n"
    "- 优先识别每个实体持有的股份比例。\n"
    "- 区分直接股东和最终受益人（UBO）。\n"
    "- 映射从母公司到最小子公司的层级结构。"
)

EQUITY_NODE_PROMPT = (
    "你是一位企业法务助理和财务分析师。你的任务是识别出公司结构中的所有利益相关者（节点）。\n\n"
    "提取规则：\n"
    "- 识别公司、投资基金、政府机构和自然人个人。\n"
    "- 将其分类为 '自然人'、'上市公司'、'私有公司' 等。\n"
    "- 在明确的情况下，标记被识别为最终受益人（UBO）的实体。\n"
    "- 在此阶段请勿提取持股比例或控制联系。"
)

EQUITY_EDGE_PROMPT = (
    "你是一位企业法务助理和财务分析师。根据利益相关者清单，映射所有权和控制关系（边）。\n\n"
    "提取规则：\n"
    "- 提取股东（源）与公司（目标）之间持有的确切股份比例。\n"
    "- 指定控制的性质（如：投票权、直接控制、代持股份）。\n"
    "- 仅在提供的利益相关者清单中的成员之间建立边。\n"
    "- 捕获所有权记录的 '截至日期' 或历史时期。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class EquityStructureGraph(AutoGraph[StakeholderNode, OwnershipRelation]):
    """
    用于企业登记、并购分析及 KYC/UBO 追踪的高精度模板。
    """
    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "one_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any
    ):
        super().__init__(
            node_schema=StakeholderNode,
            edge_schema=OwnershipRelation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}->{x.target.strip()}_at_{x.stake_percentage}%",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=EQUITY_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=EQUITY_NODE_PROMPT,
            prompt_for_edge_extraction=EQUITY_EDGE_PROMPT,
            **kwargs
        )
