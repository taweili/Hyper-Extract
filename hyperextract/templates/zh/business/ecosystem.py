from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.hypergraphs.base import AutoHypergraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class IndustryParticipant(BaseModel):
    """
    产业生态系统中的实体（公司、监管机构、非政府组织）。
    """
    name: str = Field(description="参与者名称（如：'台积电'、'欧盟委员会'）。")
    rank: Optional[str] = Field(None, description="市场地位：'一级供应商'、'市场领导者'、'挑战者'。")
    technological_focus: Optional[str] = Field(None, description="主要技术或领域（如：'5G'、'光刻技术'）。")

class CollectiveAlliance(BaseModel):
    """
    代表财团、联盟、市场卡特尔或联合标准制定机构的超边。
    """
    alliance_id: str = Field(description="联盟的名称或标识符（如：'芯片联盟'）。")
    participants: List[str] = Field(description="在该团体中进行合作或竞争的所有实体的名称列表。")
    shared_goal: str = Field(description="目标：'标准化'、'反垄断审查'、'联合研发'。")
    governance: Optional[str] = Field(None, description="参与原则或领导实体。")

# ==============================================================================
# 2. Prompts
# ==============================================================================

ECOSYSTEM_CONSOLIDATED_PROMPT = (
    "你是一位市场战略家和反垄断专家。请提取市场生态系统的动态。\n\n"
    "规则：\n"
    "- 使用超边（Hyperedges）将参与合资企业或联盟的多个实体（3个或更多）联系起来。\n"
    "- 捕获非二元的群体关系，如卡特尔、产业集群和监管联盟。\n"
    "- 清晰地定义这些群体的共同目标。"
)

ECOSYSTEM_NODE_PROMPT = (
    "识别生态系统中的所有业务和监管参与者。记录它们的市场地位核心技术重点。"
)

ECOSYSTEM_EDGE_PROMPT = (
    "提取集体联盟。将参与实体分组为集群（超边）。专注于财团、标准制定机构和联合市场行动。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class MarketEcosystemHyper(AutoHypergraph[IndustryParticipant, CollectiveAlliance]):
    """
    用于产业集群、生态系统联盟和复杂市场协同的超图模板。
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
            node_schema=IndustryParticipant,
            edge_schema=CollectiveAlliance,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: x.alliance_id.strip(),
            nodes_in_edge_extractor=lambda x: tuple(x.participants),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=ECOSYSTEM_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=ECOSYSTEM_NODE_PROMPT,
            prompt_for_edge_extraction=ECOSYSTEM_EDGE_PROMPT,
            **kwargs
        )
