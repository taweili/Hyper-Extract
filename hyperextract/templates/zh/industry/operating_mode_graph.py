from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class ModeEntity(BaseModel):
    """
    工况实体，包括工况和条件。
    """

    name: str = Field(description="实体名称（如：自动运行模式、手动调试模式、待机模式、紧急停止模式、按下启动按钮、按下停止按钮、发生故障等）。")
    category: str = Field(
        description='类别：工况、条件。工况如自动运行、手动调试、待机等；条件如启动按钮、停止按钮、故障信号等。'
    )
    description: Optional[str] = Field(
        None,
        description="对该实体的描述。",
    )
    load_range: Optional[str] = Field(
        None,
        description="负荷范围（如：0-50%、50-80%、80-100%等），仅对工况类别有效。",
    )


class ModeTransition(BaseModel):
    """
    工况与工况之间的切换关系，或条件与工况之间的触发关系。
    """

    source: str = Field(description="源实体名称（工况或条件）。")
    target: str = Field(description="目标实体名称（工况或条件）。")
    relation_type: str = Field(
        description='关系类型：切换到、触发。'
    )
    transition_condition: Optional[str] = Field(
        None,
        description="切换条件（如：按下启动按钮、按下停止按钮、发生故障等）。",
    )
    transition_procedure: Optional[str] = Field(
        None,
        description="切换步骤。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是工业设备工况分析专家。从运行规程文档中提取工况和条件实体，以及它们之间的关系。\n\n"
    "规则:\n"
    "- 识别各种运行模式（工况），如自动运行、手动调试、待机、紧急停止等。\n"
    "- 识别各种触发条件，如按下启动按钮、按下停止按钮、发生故障等。\n"
    "- 识别每种工况的适用条件和负荷范围。\n"
    "- 提取工况之间的切换关系（切换到）。\n"
    "- 提取条件触发工况的关系（触发）。\n"
)

_NODE_PROMPT = (
    "你是工业设备工况分析专家。从运行规程文档中提取所有实体（节点）。\n\n"
    "提取规则:\n"
    "- 识别工况名称（如自动运行模式、手动调试模式、待机模式、紧急停止模式等）。\n"
    "- 识别条件名称（如按下启动按钮、按下停止按钮、发生故障、恢复正常等）。\n"
    "- 为每个实体指定类别（工况/条件）。\n"
    "- 记录每种工况的负荷范围。\n"
    "- 不建立实体之间的关系。\n"
)

_EDGE_PROMPT = (
    "你是工业设备工况分析专家。在获得实体清单的基础上，提取工况与条件之间的关系（边）。\n\n"
    "提取规则:\n"
    "- 识别工况之间的切换关系（源工况 切换到 目标工况）。\n"
    "- 识别条件对工况的触发关系（条件 触发 目标工况）。\n"
    "- 关系类型使用 切换到 或 触发。\n"
    "- 仅在提供的实体列表中建立关系。\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class OperatingModeGraph(AutoGraph[ModeEntity, ModeTransition]):
    """
    适用文档: 运行规程、设备操作手册、工况切换说明书。

    模板用于从运行规程中提取工况类型和切换条件。
    识别不同工况之间的切换条件和步骤。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> mode = OperatingModeGraph(llm_client=llm, embedder=embedder)
        >>> doc = "设备有两种运行模式：自动模式和手动模式。按下启动按钮从待机切换到自动模式..."
        >>> mode.feed_text(doc)
        >>> mode.show()
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
        初始化工况切换图谱模板。

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
            node_schema=ModeEntity,
            edge_schema=ModeTransition,
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
        使用 OntoSight 可视化工况切换图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的关系数。默认 3。
        """

        def node_label_extractor(node: ModeEntity) -> str:
            load = f" [{node.load_range}]" if node.load_range else ""
            return f"{node.name} ({node.category}){load}"

        def edge_label_extractor(edge: ModeTransition) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
