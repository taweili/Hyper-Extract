from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class OperationEntity(BaseModel):
    """
    操作流程实体，包括步骤、状态、设备等。
    """

    name: str = Field(description="实体具体名称（如：开启辅助电源、启动液压系统、检查状态等）。")
    category: str = Field(
        description='类别：步骤、状态、设备。'
    )
    description: Optional[str] = Field(
        None,
        description="对该实体的详细操作描述。",
    )
    expected_result: Optional[str] = Field(
        None,
        description="执行该步骤后的预期结果。",
    )


class OperationTransition(BaseModel):
    """
    操作步骤之间的流转关系。
    """

    source: str = Field(description="当前步骤名称。")
    target: str = Field(description="下一步骤名称。")
    relation_type: str = Field(
        description='关系类型：下一步、触发、导致等。'
    )
    trigger_condition: Optional[str] = Field(
        None,
        description="触发下一步骤的条件。",
    )
    state_change: Optional[str] = Field(
        None,
        description="状态变化描述。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是工业操作流程分析专家。从运行规程文档中提取操作步骤、设备状态和预期结果。\n\n"
    "规则:\n"
    "- 识别各个操作步骤和执行顺序。\n"
    "- 记录每一步骤的详细操作内容。\n"
    "- 提取设备状态变化和预期结果。\n"
    "- 建立步骤之间的流转关系。\n"
)

_NODE_PROMPT = (
    "你是工业操作流程分析专家。从运行规程文档中提取所有实体（节点）。\n\n"
    "提取规则:\n"
    "- 识别操作步骤名称。\n"
    "- 识别设备状态名称。\n"
    "- 识别相关设备名称。\n"
    "- 记录每一步骤的操作描述和预期结果。\n"
    "- 不建立步骤之间的关系。\n"
)

_EDGE_PROMPT = (
    "你是工业操作流程分析专家。在获得实体清单的基础上，提取操作步骤之间的流转关系（边）。\n\n"
    "提取规则:\n"
    "- 识别步骤的执行顺序（当前步骤→下一步骤）。\n"
    "- 提取触发下一步骤的条件。\n"
    "- 记录设备状态的变化。\n"
    "- 仅在提供的实体列表中建立关系。\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class OperationFlowGraph(AutoGraph[OperationEntity, OperationTransition]):
    """
    适用文档: 运行规程、启停操作票、设备操作手册、安全操作规程。

    模板用于从运行规程中提取操作步骤、设备状态和预期结果。
    识别操作流程中的步骤顺序和状态变化，为操作培训和安全控制提供参考。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> operation = OperationFlowGraph(llm_client=llm, embedder=embedder)
        >>> doc = "开机流程：1. 检查电源是否正常；2. 开启控制柜主开关；3. 启动电机；4. 确认运行状态。电源正常后开启主开关，主开关合闸后启动电机。"
        >>> operation.feed_text(doc)
        >>> operation.show()
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
        初始化操作流程图谱模板。

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
            node_schema=OperationEntity,
            edge_schema=OperationTransition,
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
        使用 OntoSight 可视化操作流程图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的关系数。默认 3。
        """

        def node_label_extractor(node: OperationEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: OperationTransition) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
