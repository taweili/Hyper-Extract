from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================

class LogicNode(BaseModel):
    """代表论点中的主张、证据或前提的节点。"""
    statement: str = Field(description="核心主张、事实或观察结果。")
    node_type: str = Field(
        description="节点类型：主张 (Claim), 证据 (Evidence), 前提 (Premise)。"
    )
    source_attribution: Optional[str] = Field(description="该逻辑点的来源或出处。")

class LogicRelation(BaseModel):
    """两个陈述之间的逻辑连接。"""
    source: str = Field(description="源陈述。")
    target: str = Field(description="目标陈述。")
    inference: str = Field(
        description="逻辑链路：支持 (Supports), 反驳 (Contradicts), 证明, 导致, 解释。"
    )

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位逻辑分析师。请将文本中的论证结构提取并转化为一个有向图。\n\n"
    "提取指南：\n"
    "- 识别主要主张（结论）以及引向这些结论的证据或前提。\n"
    "- 明确映射一个陈述是如何支持或反驳另一个陈述的。\n"
    "- 不仅要提取事实，更要提取“论证”和“推理”的流向。"
)

_NODE_PROMPT = (
    "请提取论证中的各个基本构成要素。识别核心主张、支持性证据和底层前提。对于每一项，确定其类型并记录提及的任何来源出处。"
)

_EDGE_PROMPT = (
    "映射提取出的主张与证据之间的逻辑流向。重点关注各个陈述之间是如何相互 支持、反驳 或 导致 彼此的。确保每条边都代表推理链中的一个步骤。"
)

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================

class LogicGraph(AutoGraph[LogicNode, LogicRelation]):
    """
    用于分析推理、论证和因果链的模板。
    
    该模板旨在映射分析报告、科学论文或辩论记录的逻辑结构。它捕捉主张、证据以及它们之间的逻辑链接（支持/反驳）。
    
    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # 初始化模板
        >>> lg = LogicGraph(llm_client=llm, embedder=embedder)
        >>> # 从文本中提取逻辑
        >>> text = "由于碳含量上升，气候正在变暖。"
        >>> lg.feed_text(text)
        >>> print(lg.edges)  # 输出显示：碳含量上升 --(支持)--> 气候正在变暖
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
        """
        初始化 LogicGraph 模板。

        Args:
            llm_client: 用于提取的语言模型客户端。
            embedder: 用于逻辑点去重和索引的嵌入模型。
            extraction_mode: 提取策略：
                - "one_stage": 同时提取节点和边（速度更快）。
                - "two_stage": 先提取节点，再提取边（准确度更高）。
            chunk_size: 每个文本块的最大字符数。
            chunk_overlap: 文本块之间的重叠字符数。
            max_workers: 并行处理的最大线程数。
            verbose: 如果为 True，则打印详细的进度日志。
            **kwargs: 传给 AutoGraph 构造函数的其他参数。
        """
        super().__init__(
            node_schema=LogicNode,
            edge_schema=LogicRelation,
            node_key_extractor=lambda x: x.statement.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.inference.lower()})-->{x.target.strip()}",
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
            **kwargs
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
        Visualize the graph using OntoSight.
    
        Args:
            top_k_nodes_for_search (int): Number of nodes to retrieve for search context. Default 3.
            top_k_edges_for_search (int): Number of edges to retrieve for search context. Default 3.
            top_k_nodes_for_chat (int): Number of nodes to retrieve for chat context. Default 3.
            top_k_edges_for_chat (int): Number of edges to retrieve for chat context. Default 3.
        """
        def node_label_extractor(node: LogicNode) -> str:
            return f"{node.statement}"
    
        def edge_label_extractor(edge: LogicRelation) -> str:
            return f"{edge.inference}"
    
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
