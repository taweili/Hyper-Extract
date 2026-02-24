from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class QAParticipant(BaseModel):
    """
    财报电话会议问答环节的参与者。
    """

    name: str = Field(
        description="参与者姓名（例如分析师姓名、CEO、CFO）。"
    )
    role: str = Field(
        description='角色："分析师"、"CEO"、"CFO"、"COO"、"CTO"、"IR 负责人"、"其他管理层"。'
    )
    firm: Optional[str] = Field(
        None,
        description="所属机构（例如'摩根大通'、'高盛'），适用于分析师。",
    )


class QAInteraction(BaseModel):
    """
    分析师与管理层之间的问答互动。
    """

    source: str = Field(description="提问者姓名（分析师）。")
    target: str = Field(description="回答者姓名（管理层）。")
    topic: str = Field(
        description="问题主题（例如'利润率展望'、'AI 战略'、'资本配置'）。"
    )
    question_summary: str = Field(
        description="分析师问题的简要概述。"
    )
    answer_summary: str = Field(
        description="管理层回答的简要概述。"
    )
    sentiment: Optional[str] = Field(
        None,
        description="互动基调：'建设性'、'追问式'、'安抚性'、'回避性'、'直接'。",
    )
    commitment_made: Optional[str] = Field(
        None,
        description="管理层作出的具体承诺（例如'将在下季度提供更新'）。",
    )
    follow_up: Optional[bool] = Field(
        None,
        description="分析师是否就同一主题提出了追问。",
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是财报电话会议分析师。从本财报电话会议记录中提取分析师与管理层之间的问答互动。\n\n"
    "规则:\n"
    "- 识别每位分析师和管理层参与者。\n"
    "- 概述每个问题及其对应的回答。\n"
    "- 捕捉每次互动的主题和基调。\n"
    "- 记录管理层作出的任何承诺。\n"
    "- 跟踪针对同一主题的追问。"
)

_NODE_PROMPT = (
    "你是财报电话会议分析师。提取所有问答参与者（节点）。\n\n"
    "提取规则:\n"
    "- 按姓名和所属机构识别分析师。\n"
    "- 按姓名和职务识别管理层参与者。\n"
    "- 此阶段不提取问答互动。"
)

_EDGE_PROMPT = (
    "你是财报电话会议分析师。在获得参与者清单的基础上，提取问答互动（边）。\n\n"
    "提取规则:\n"
    "- 将每位分析师的问题连接到管理层的回答。\n"
    "- 简要概述问题和回答。\n"
    "- 捕捉主题、基调和任何承诺。\n"
    "- 仅在提供的列表中存在的节点之间创建边。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class AnalystQAGraph(AutoGraph[QAParticipant, QAInteraction]):
    """
    适用文档: 财报电话会议记录（问答部分）、投资者日问答、
    年度股东大会问答、分析师日活动记录。

    模板用于将分析师问题映射到管理层回答。支持分析师关注点分析、
    承诺跟踪以及识别分析师群体中的核心关切。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> qa = AnalystQAGraph(llm_client=llm, embedder=embedder)
        >>> transcript = "分析师：能否讨论一下利润率展望？CEO：我们预计利润率将..."
        >>> qa.feed_text(transcript)
        >>> qa.show()
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
        初始化分析师问答图谱模板。

        Args:
            llm_client (BaseChatModel): 用于问答提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=QAParticipant,
            edge_schema=QAInteraction,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip().lower()}|{x.topic.lower()}|{x.target.strip().lower()}"
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
        使用 OntoSight 可视化分析师问答图。

        Args:
            top_k_nodes_for_search (int): 检索的参与者数。默认 3。
            top_k_edges_for_search (int): 检索的问答互动数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的参与者数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的互动数。默认 3。
        """

        def node_label_extractor(node: QAParticipant) -> str:
            firm = f" @ {node.firm}" if node.firm else ""
            return f"{node.name} ({node.role}{firm})"

        def edge_label_extractor(edge: QAInteraction) -> str:
            sentiment = f" [{edge.sentiment}]" if edge.sentiment else ""
            return f"{edge.topic}{sentiment}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
