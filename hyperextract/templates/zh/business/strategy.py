from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================


class StrategicNode(BaseModel):
    """
    组织实体、业务部门或战略目标。
    """

    name: str = Field(description="战略单元或目标的名称（如：'Azure'、'碳中和'）。")
    scope: str = Field(description="范围：'全球'、'区域'、'特定产品'、'集团层面'。")
    importance: Optional[str] = Field(
        None, description="重要性：'核心业务'、'新兴市场'、'传统存量'。"
    )


class StrategicPivot(BaseModel):
    """
    代表战略重点转移、投资或剥离的时间性转变。
    """

    source: str = Field(description="原始关注领域或施加动作的实体。")
    target: str = Field(description="新的目标、方向或目的。")
    action: str = Field(
        description="战略动作：'转型为'、'收购'、'剥离'、'合并'、'关停'、'规模化'。"
    )
    timestamp: str = Field(
        description="转型发生的时间（如：'2022年第四季度'、'2025-01-01'）。"
    )
    rationale: Optional[str] = Field(
        None, description="举措背后的原因（市场压力、CEO 变动、技术变革）。"
    )
    budget: Optional[str] = Field(None, description="与转型相关的财务承诺或预算。")


# ==============================================================================
# 2. Prompts
# ==============================================================================

STRATEGY_CONSOLIDATED_PROMPT = (
    "你是一位管理顾问和行业分析师。请提取公司战略的演变过程。\n\n"
    "规则：\n"
    "- 专注于 '转型（Pivots）'：从一个业务领域向另一个业务领域的转移。\n"
    "- 将特定动作与具体时间戳联系起来。\n"
    "- 捕获每次战略变革背后的深层原因（rationale）。"
)

STRATEGY_NODE_PROMPT = (
    "你是一位管理顾问。你的任务是识别战略实体和目标（节点）。\n\n"
    "提取规则：\n"
    "- 识别业务部门、特定产品以及公司高层目标（如：'可持续发展'）。\n"
    "- 确定每个单元的范围和组织重要性。\n"
    "- 专注于代表战略重点领域的名词和名词短语。\n"
    "- 在此阶段请勿提取战略性动作或转型。"
)

STRATEGY_EDGE_PROMPT = (
    "你是一位管理顾问。根据已识别的战略单元，映射战略随时间推移的转变（边）。\n\n"
    "提取规则：\n"
    "- 提取 '转型 (Pivots)' 以及如 '收购'、'剥离' 或 '关停' 之类的动作。\n"
    "- 将源（旧重点）与目标（新重点）通过精确的时间戳联系起来。\n"
    "- 捕捉深层原因以及提及的任何财务承诺（预算）。\n"
    "- 仅引用战略单元清单中存在的节点。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================


class StrategicChainGraph(AutoTemporalGraph[StrategicNode, StrategicPivot]):
    """
    用于追踪公司战略、长期组织变革和市场表现的时序模板。
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
        **kwargs: Any,
    ):
        super().__init__(
            node_schema=StrategicNode,
            edge_schema=StrategicPivot,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}-({x.action})->{x.target.strip()}"
            ),
            time_in_edge_extractor=lambda x: x.timestamp.strip(),
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=STRATEGY_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=STRATEGY_NODE_PROMPT,
            prompt_for_edge_extraction=STRATEGY_EDGE_PROMPT,
            **kwargs,
        )
