from typing import Optional, Any, Callable
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types.graph import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class AgriPestEntity(BaseModel):
    """农业病虫害防治领域的实体（如害虫、病害、作物、症状、防治方法）。"""

    name: str = Field(description="病虫害、作物、病原体或药剂的名称。")
    category: str = Field(
        description="类别：'害虫', '病害', '寄主作物', '受害症状', '防治方法', '化学药剂'。"
    )
    description: Optional[str] = Field(
        None, description="详细描述、生物学特征或发生规律。"
    )


class AgriPestRelation(BaseModel):
    """农业实体之间的关系（如'危害'、'导致'、'防治手段'）。"""

    source: str = Field(description="源实体名称。")
    target: str = Field(description="目标实体名称。")
    relation_type: str = Field(
        description="类型：'危害', '寄生', '导致症状', '防治手段', '对...敏感', '发生于'。"
    )
    detail: Optional[str] = Field(
        None, description="具体的发生环境、用药剂量或危害程度。"
    )


# ==============================================================================
# 2. 提示词 (Prompt)
# ==============================================================================

_PROMPT = """
你是一位资深农艺师和植物保护专家。
你的任务是从文本中提取详尽的农作物病虫害及其防治知识图谱。

指南：
1. 识别生物威胁：包括害虫、真菌、细菌、病毒或杂草。
2. 建立威胁与寄主作物、具体受害症状（如：叶斑、秆腐、卷叶）之间的链接。
3. 映射病虫害综合防治 (IPM) 策略，包括生物防治、物理防治和化学防治方法。
4. 提取文本中提到的具体农药名称、施用剂量及最佳施药时期。
"""

# ==============================================================================
# 3. 模板类
# ==============================================================================


class AgriPestControl(AutoGraph[AgriPestEntity, AgriPestRelation]):
    """
    农业病虫害防治知识图谱模板。
    
    将技术手册和防治指南转化为结构化的防治策略。
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
        """初始化 AgriPestControl 模板。"""
        super().__init__(
            node_schema=AgriPestEntity,
            edge_schema=AgriPestRelation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.relation_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ) -> None:
        """可视化病虫害防治知识图谱。"""

        def node_label_extractor(node: AgriPestEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: AgriPestRelation) -> str:
            return f"{edge.relation_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
