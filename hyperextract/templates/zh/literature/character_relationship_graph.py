from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================


class Character(BaseModel):
    """文学作品中的人物实体。"""

    name: str = Field(description="人物的正式姓名或最常用称呼。")
    aliases: List[str] = Field(
        default_factory=list, description="人物的其他称呼、头衔或绰号。"
    )
    traits: List[str] = Field(
        default_factory=list, description="人物的核心性格、能力或生理特征。"
    )
    description: Optional[str] = Field(
        description="关于人物在作品中地位及核心情节的简要描述。"
    )


class Relationship(BaseModel):
    """人物之间的互动与联系。"""

    source: str = Field(description="发起关系的或关系的第一个人物名称。")
    target: str = Field(description="关系指向的或关系的第二个人物名称。")
    relation_type: str = Field(
        description="关系的性质（如：亲属、爱慕、仇恨、师徒、盟友）。"
    )
    sentiment: str = Field(description="关系的情感倾向（如：正面、负面、中立、复杂）。")
    evidence: str = Field(description="支持该关系的文本证据或关键情节简述。")


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位资深的文学评论家和角色分析专家。你的任务是从文学文本中提取人物及其关系网络。\n\n"
    "提取指南：\n"
    "1. **人物识别**：准确识别文本中出现的所有重要人物。记录他们的姓名、绰号及核心特征。\n"
    "2. **关系识别**：分析人物间的对话、行为互动及旁白，提取他们之间的深层联系。不仅仅限于亲属关系，也要捕捉情感纽带和利益冲突。\n"
    "3. **证据至上**：为每个关系提供简短的文本依据。\n"
    "- 确保边连接的两个人物都已在节点列表中列出。"
)

_NODE_PROMPT = "作为文学分析专家，请从文本中提取所有关键人物。记录其姓名、所有已知的别称、核心性格标签以及简要的生平或地位描述。"

_EDGE_PROMPT = "基于已提取的人物列表，识别他们之间的社交与情感关系。请说明关系的类型（如‘宿敌’）、情感色彩（如‘强烈恨意’）并提供证据。"

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================


class CharacterRelationshipGraph(AutoGraph[Character, Relationship]):
    """
    适用于：[小说, 剧本, 传记, 戏剧]

    用于提取文学作品中复杂人物关系的图谱模板。

    该模板旨在捕捉人物间的动态互动、情感倾向和结构化联系，支持多阶段提取以确保深度关系的准确性。

    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> # 初始化模板
        >>> characters = CharacterRelationshipGraph(llm_client=llm, embedder=embedder)
        >>> # 输入文本块
        >>> text = "贾宝玉是贾政之子，与林黛玉青梅竹马，彼此情深意切。"
        >>> characters.feed_text(text)
        >>> characters.show()
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
        初始化 CharacterRelationshipGraph 模板。

        Args:
            llm_client: 用于提取的语言模型客户端。
            embedder: 用于实体去重和索引的嵌入模型。
            extraction_mode: 提取模式，支持 "one_stage" 和 "two_stage"。
            chunk_size: 文本块大小。
            chunk_overlap: 文本块重叠大小。
            max_workers: 最大并行工作线程数。
            verbose: 是否开启详细日志。
            **kwargs: 其他传给 AutoGraph 的参数。
        """
        super().__init__(
            node_schema=Character,
            edge_schema=Relationship,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source}-{x.relation_type}-{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
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
        可视化人物关系图谱。

        Args:
            top_k_nodes_for_search: 搜索时找回的相关节点数量。
            top_k_edges_for_search: 搜索时找回的相关边数量。
            top_k_nodes_for_chat: 聊天时找回的相关节点数量。
            top_k_edges_for_chat: 聊天时找回的相关边数量。
        """

        def node_label_extractor(node: Character) -> str:
            return node.name

        def edge_label_extractor(edge: Relationship) -> str:
            return f"{edge.relation_type} ({edge.sentiment})"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
