from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class EmergencyEntity(BaseModel):
    """
    应急预案实体，包括事故场景、响应动作、部门等。
    """

    name: str = Field(description="实体名称（如：火灾、停电、报警、疏散人员、设备部等）。")
    category: str = Field(
        description='类别：事故场景、响应动作、部门。'
    )
    description: Optional[str] = Field(
        None,
        description="对该实体的描述。",
    )


class ResponseFlow(BaseModel):
    """
    应急响应流程关系。
    """

    source: str = Field(description="源实体名称（事故场景或响应动作）。")
    target: str = Field(description="目标实体名称（响应动作或部门）。")
    relation_type: str = Field(
        description='关系类型：触发、执行、负责。'
    )
    time_limit: Optional[str] = Field(
        None,
        description="响应时间要求（如：5分钟内、10分钟内）。",
    )
    success_criterion: Optional[str] = Field(
        None,
        description="成功标准（如：人员安全撤离、火势控制）。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是工业应急管理分析专家。从应急预案文档中提取事故场景、响应动作和部门，构建应急响应流程。\n\n"
    "规则:\n"
    "- 识别事故场景（如火灾、泄漏、停电、设备故障等）。\n"
    "- 识别响应动作（如报警、疏散人员、关闭电源等）。\n"
    "- 识别负责部门（如安保部、设备部、急救部等）。\n"
    "- 建立从事故场景到响应动作的流程关系。\n"
    "- 记录时间要求和成功标准。\n"
)

_NODE_PROMPT = (
    "你是工业应急管理分析专家。从应急预案文档中提取所有实体（节点）。\n\n"
    "提取规则:\n"
    "- 识别事故场景名称。\n"
    "- 识别响应动作名称。\n"
    "- 识别负责部门名称。\n"
    "- 为每个实体指定类别（事故场景/响应动作/部门）。\n"
    "- 不建立实体之间的关系。\n"
)

_EDGE_PROMPT = (
    "你是工业应急管理分析专家。在获得实体清单的基础上，提取应急响应流程关系（边）。\n\n"
    "提取规则:\n"
    "- 识别从事故场景到响应动作的关联。\n"
    "- 识别从响应动作到负责部门的关联。\n"
    "- 记录响应时间要求。\n"
    "- 记录成功标准。\n"
    "- 仅在提供的实体列表中建立关系。\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class EmergencyResponseGraph(AutoGraph[EmergencyEntity, ResponseFlow]):
    """
    适用文档: 应急预案、应急处置方案、安全规程。

    模板用于从应急预案中提取事故场景、响应动作和部门，构建应急响应流程。
    通过 category 区分异质节点，识别应急响应的流程和责任分工。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> emergency = EmergencyResponseGraph(llm_client=llm, embedder=embedder)
        >>> doc = "发生火灾时，应立即报警并启动应急预案。安保部负责疏散人员，设备部负责关闭电源..."
        >>> emergency.feed_text(doc)
        >>> emergency.show()
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
        初始化应急预案图谱模板。

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
            node_schema=EmergencyEntity,
            edge_schema=ResponseFlow,
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
        使用 OntoSight 可视化应急预案图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的关系数。默认 3。
        """

        def node_label_extractor(node: EmergencyEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: ResponseFlow) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
