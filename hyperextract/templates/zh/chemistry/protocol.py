from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.graphs.temporal_graph import AutoTemporalGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class LabOperation(BaseModel):
    """
    化学或生物实验方案中的具体步骤或动作（如：'离心'、'滴定'）。
    """
    op_id: str = Field(description="动作名称（如：'离心'、'加热'、'加入'）。")
    equipment: Optional[str] = Field(None, description="使用的设备（如：'微量离心机'、'本生灯'）。")
    reagents_added: List[str] = Field(default_factory=list, description="此具体步骤中引入的化学物质。")
    precautions: Optional[str] = Field(None, description="安全或准确性警告（如：'在冰上操作'）。")

class ProtocolTransition(BaseModel):
    """
    实验步骤之间的顺序转换，捕获持续时间和顺序。
    """
    transition_id: str = Field(description="步骤转换的唯一标识符。")
    source_step: str = Field(description="前序操作。")
    target_step: str = Field(description="后续操作。")
    duration: Optional[str] = Field(None, description="步骤内或步骤间的耗时（如：'15 分钟'、'过夜'）。")
    timestamp: str = Field(description="顺序编号或相对时间标记（如：'T+0'、'步骤 2'）。")
    wait_condition: Optional[str] = Field(None, description="继续操作的条件（如：'直到形成沉淀'）。")

# ==============================================================================
# 2. Prompts
# ==============================================================================

PROTOCOL_CONSOLIDATED_PROMPT = (
    "你是一位擅长实验方案记录的实验室技术员。请提取顺序性的实验步骤。\n\n"
    "规则：\n"
    "- 将每个操作表示为一个节点（Node）。\n"
    "- 将操作之间的顺序和持续时间表示为时间边（Temporal Edges）。\n"
    "- 捕获与每个步骤相关的特定试剂/设备。\n"
    "- 精确映射时间线（例如：'步骤 1' -> '步骤 2'）。"
)

PROTOCOL_NODE_PROMPT = (
    "你是一位实验室技术员。你的任务是识别出单个实验方案操作（节点）。\n\n"
    "提取规则：\n"
    "- 识别离散的动作（如：离心、孵育、滴定）。\n"
    "- 记录使用的设备以及在该特定步骤中添加的任何试剂。\n"
    "- 捕捉与该操作相关的安全预防措施。\n"
    "- 在此阶段请勿建立步骤之间的顺序或时间关系。"
)

PROTOCOL_EDGE_PROMPT = (
    "你是一位实验室技术员。根据实验室操作清单，提取顺序流向（边）。\n\n"
    "提取规则：\n"
    "- 按时间顺序将源步骤连接到目标步骤。\n"
    "- 识别转换的持续时间以及特定的时间戳或顺序编号。\n"
    "- 记录在进入下一步操作之前所需的任何等待条件。\n"
    "- 仅引用提供的操作清单中存在的操作。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class LabProtocolTemporal(AutoTemporalGraph[LabOperation, ProtocolTransition]):
    """
    用于捕获逐步实验室程序和实验工作流的时间图模板。
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
            node_schema=LabOperation,
            edge_schema=ProtocolTransition,
            node_key_extractor=lambda x: x.op_id.strip(),
            edge_key_extractor=lambda x: x.transition_id.strip(),
            nodes_in_edge_extractor=lambda x: (x.source_step.strip(), x.target_step.strip()),
            time_in_edge_extractor=lambda x: x.timestamp.strip(),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=PROTOCOL_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=PROTOCOL_NODE_PROMPT,
            prompt_for_edge_extraction=PROTOCOL_EDGE_PROMPT,
            **kwargs
        )
