"""战争演变史 - 从历史文献中提取时间相关的战争关系。

捕捉领土控制、权力交接和军事事件的时间范围，用于精确的历史分析。
"""

from typing import Any, Optional, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

class HistoricalEntitySchema(BaseModel):
    entity_id: str = Field(..., description="唯一标识符")
    entity_type: str = Field(..., description="'政权'、'城市'或'将领'")
    entity_name: str = Field(..., description="实体名称")

class TemporalEventSchema(BaseModel):
    source_entity: str = Field(..., description="行为实体")
    target_entity: str = Field(..., description="受影响实体")
    edge_type: str = Field(..., description="'占领'、'统治'、'围攻'等")
    start_timestamp: Optional[int] = Field(None, description="起始年份")
    end_timestamp: Optional[int] = Field(None, description="结束年份")
    description: Optional[str] = Field(None, description="事件详情")

_PROMPT = """提取历史实体（节点）和时间事件（边），显示领土控制和权力交接。
确保所有边连接提取的节点列表中存在的实体。

### 源文本：
"""

_NODE_PROMPT = """提取所有提到的历史实体：政权、城市、军事领导人及其描述。"""

_EDGE_PROMPT = """提取已知实体之间的时间关系。为每个关系提供确切的年份范围。"""

class WarTimelineGraph(AutoTemporalGraph[HistoricalEntitySchema, TemporalEventSchema]):
    """适用于：历史编年史、战争记录、教科书章节

    提取时间知识图，捕捉领土控制和军事事件的精确时间范围。
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        observation_time: str = "2024-01-01",
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        super().__init__(
            node_schema=HistoricalEntitySchema,
            edge_schema=TemporalEventSchema,
            node_key_extractor=lambda x: x.entity_name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source_entity.lower()}|{x.edge_type.lower()}|{x.target_entity.lower()}"
            ),
            time_in_edge_extractor=lambda x: f"{x.start_timestamp or ''}",
            nodes_in_edge_extractor=lambda x: (x.source_entity.lower(), x.target_entity.lower()),
            llm_client=llm_client,
            embedder=embedder,
            observation_time=observation_time,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(self, *, top_k_nodes_for_search: int = 3, top_k_edges_for_search: int = 3, top_k_nodes_for_chat: int = 3, top_k_edges_for_chat: int = 3) -> None:
        def node_label(node: HistoricalEntitySchema) -> str:
            return f"{node.entity_name} ({node.entity_type})"
        def edge_label(edge: TemporalEventSchema) -> str:
            return f"{edge.edge_type} ({edge.start_timestamp or '?'})"
        super().show(
            node_label_extractor=node_label,
            edge_label_extractor=edge_label,
            top_k_nodes_for_search=top_k_nodes_for_search, top_k_edges_for_search=top_k_edges_for_search, top_k_nodes_for_chat=top_k_nodes_for_chat, top_k_edges_for_chat=top_k_edges_for_chat,
        )
