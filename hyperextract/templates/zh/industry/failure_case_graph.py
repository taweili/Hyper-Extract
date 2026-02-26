from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class CaseEntity(BaseModel):
    """
    故障案例实体，包括现象、原因、措施、教训等。
    """

    name: str = Field(description="现象/措施等实体的名称。")
    category: str = Field(
        description='类别：现象、原因、措施、教训。'
    )
    description: Optional[str] = Field(
        None,
        description="对该实体内涵的进一步阐述和说明。",
    )
    equipment: Optional[str] = Field(
        None,
        description="涉及设备名称。",
    )


class CaseChain(BaseModel):
    """
    故障案例环节之间的关联关系。
    """

    source: str = Field(description="上游环节名称。")
    target: str = Field(description="下游环节名称。")
    relation_type: str = Field(
        description='关系类型：导致、采取、产生、发现'
    )
    time_sequence: Optional[str] = Field(
        None,
        description="时序关系：发现、分析、处理、总结。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是工业设备故障分析专家。从故障案例文档中提取故障现象、原因、处理措施和经验教训。\n\n"
    "规则:\n"
    "- 识别故障现象和异常表现。\n"
    "- 分析故障原因和根本原因。\n"
    "- 提取处理措施和解决方案。\n"
    "- 总结经验教训和改进建议。\n"
    "- 建立从发现到处理的完整链条。\n"
)

_NODE_PROMPT = (
    "你是工业设备故障分析专家。从故障案例文档中提取所相关实体（节点）。\n\n"
    "提取规则:\n"
    "- 识别故障现象和异常表现。\n"
    "- 识别故障原因和根本原因。\n"
    "- 识别处理措施和解决方案。\n"
    "- 识别经验教训和改进建议。\n"
    "- 记录涉及的设备名称。\n"
    "- 不建立环节之间的关系。\n"
)

_EDGE_PROMPT = (
    "你是工业设备故障分析专家。在获得实体清单的基础上，提取故障环节之间的关联关系（边）。\n\n"
    "提取规则:\n"
    "- 识别从现象到原因的关联。\n"
    "- 识别从原因到措施的关联。\n"
    "- 识别从措施到教训的关联。\n"
    "- 时序关系：发现 → 分析 → 处理 → 总结。\n"
    "- 仅在提供的实体列表中建立关系。\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class FailureCaseGraph(AutoGraph[CaseEntity, CaseChain]):
    """
    适用文档: 故障案例库、事故分析报告、设备异常记录、检修报告。

    模板用于从故障案例文档中提取故障现象、原因、措施和教训。
    识别从发现到处理的完整故障演进链条，为设备维护和预防提供参考。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> failure_case = FailureCaseGraph(llm_client=llm, embedder=embedder)
        >>> doc = "2024年1月，A生产线主电机突发异响并伴随振动加剧。检查发现轴承磨损严重，立即更换轴承后恢复正常。此故障提醒需加强轴承日常巡检。"
        >>> failure_case.feed_text(doc)
        >>> failure_case.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化故障案例图谱模板。

        Args:
            llm_client (BaseChatModel): 用于实体和关系提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。默认为 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=CaseEntity,
            edge_schema=CaseChain,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.relation_type})-->{x.target.strip()}"
            ),
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
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
    ) -> None:
        """
        使用 OntoSight 可视化故障案例图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的关系数。默认 3。
        """

        def node_label_extractor(node: CaseEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: CaseChain) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
