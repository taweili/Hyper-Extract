from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class SafetyEntity(BaseModel):
    """
    安全管控实体，包括危险源、风险点、管控措施、责任人等。
    """

    name: str = Field(description="实体名称（如：高温高压设备、触电风险、佩戴防护用品、安全主管等）。")
    category: str = Field(
        description='类别：危险源、风险点、管控措施、责任人。'
    )
    description: Optional[str] = Field(
        None,
        description="对该实体的描述。",
    )


class SafetyRelation(BaseModel):
    """
    安全管控关系。
    """

    source: str = Field(description="源实体名称（危险源或风险点）。")
    target: str = Field(description="目标实体名称（管控措施或责任人）。")
    relation_type: str = Field(
        description='关系类型：管控、负责等。'
    )
    control_measure: Optional[str] = Field(
        None,
        description="管控措施具体内容。",
    )
    responsible_person: Optional[str] = Field(
        None,
        description="责任人姓名或部门。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是工业安全管理分析专家。从安全规程文档中提取危险源、风险点和管控措施，构建安全管控关系。\n\n"
    "规则:\n"
    "- 识别危险源（如高温高压设备、电气设备、化学品等）。\n"
    "- 识别风险点（如触电风险、烫伤风险、机械伤害等）。\n"
    "- 识别管控措施（如佩戴防护用品、定期检修、通风换气等）。\n"
    "- 识别责任人（如安全主管、设备负责人等）。\n"
    "- 建立从危险源/风险点到管控措施/责任人的关系。\n"
)

_NODE_PROMPT = (
    "你是工业安全管理分析专家。从安全规程文档中提取所有实体（节点）。\n\n"
    "提取规则:\n"
    "- 识别危险源名称。\n"
    "- 识别风险点名称。\n"
    "- 识别管控措施名称。\n"
    "- 识别责任人名称。\n"
    "- 为每个实体指定类别（危险源/风险点/管控措施/责任人）。\n"
    "- 不建立实体之间的关系。\n"
)

_EDGE_PROMPT = (
    "你是工业安全管理分析专家。在获得实体清单的基础上，提取安全管控关系（边）。\n\n"
    "提取规则:\n"
    "- 识别从危险源到管控措施的关联。\n"
    "- 识别从风险点到管控措施的关联。\n"
    "- 识别从管控措施到责任人的关联。\n"
    "- 记录管控措施的具体内容。\n"
    "- 记录责任人信息。\n"
    "- 仅在提供的实体列表中建立关系。\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class SafetyControlGraph(AutoGraph[SafetyEntity, SafetyRelation]):
    """
    适用文档: 安全规程、安全风险评估报告、职业健康安全手册。

    模板用于从安全规程中提取危险源、风险点和管控措施，构建安全管控关系。
    通过 category 区分异质节点，识别安全风险与管控责任的对应关系。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> safety = SafetyControlGraph(llm_client=llm, embedder=embedder)
        >>> doc = "高温设备存在烫伤风险，需佩戴防护手套。由设备负责人负责监督检查..."
        >>> safety.feed_text(doc)
        >>> safety.show()
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
        初始化安全管控图谱模板。

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
            node_schema=SafetyEntity,
            edge_schema=SafetyRelation,
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
        使用 OntoSight 可视化安全管控图。

        Args:
            top_k_nodes_for_search (int): 检索的实体数。默认 3。
            top_k_edges_for_search (int): 检索的关系数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的实体数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的关系数。默认 3。
        """

        def node_label_extractor(node: SafetyEntity) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: SafetyRelation) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
