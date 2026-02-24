from typing import List, Optional, Any, Callable
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================

class ImagerySymbol(BaseModel):
    """文学作品中的意象或符号。"""
    symbol_name: str = Field(description="意象的名称（如‘月亮’、‘荒原’、‘白鲸’）。")
    literal_meanings: List[str] = Field(description="该意象在文中的字面指代或描述。")
    metaphorical_meanings: List[str] = Field(description="该意象隐含的象征意义或深层隐喻。")
    contexts: List[str] = Field(description="提取该意象的关键原文片段或章节摘要。")
    thematic_connection: Optional[str] = Field(description="该意象与作品主题（如‘孤独’、‘命运’）的关联。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位资深的文学批评家。你的任务是从文本中识别并分析反复出现的关键意象与符号。\n\n"
    "分析指南：\n"
    "1. **意象标准化**：请确保同一个意象（如‘月色’与‘月亮’）被归类到同一个标准的意象名称下，以便信息累加。\n"
    "2. **分层解读**：区分意象的字面描写（它是什么）与其象征意义（它代表了什么）。\n"
    "3. **信息聚合**：如果你在多处文本中发现了同一个意象，请持续丰富该意象的内涵、上下文和它对主题的贡献。\n"
)

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================

class SymbolismSet(AutoSet[ImagerySymbol]):
    """
    适用于：[诗歌, 现代主义小说, 文学评论, 散文]

    用于从文学作品中聚合与深度分析意象隐喻的集合模板。

    该模板利用 AutoSet 的键值累加特性，能够将散落在全书各处的关于同一个符号的信息（字面描写、深层隐喻、主题关联）自动合并为一个富集的词条。

    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-5-mini")
        >>> embedder = OpenAIEmbeddings()
        >>> # 初始化模板
        >>> symbolism = SymbolismSet(llm_client=llm, embedder=embedder)
        >>> # 多次喂入不同章节的文本
        >>> symbolism.feed_text("海明威笔下的大海是永恒的荒原，象征着不可战胜的自然。").feed_text("在大海深处，老人与马林鱼的搏斗体现了尊严。")
        >>> symbolism.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any
    ):
        """
        初始化 SymbolismSet 模板。

        Args:
            llm_client: 用于提取的语言模型客户端。
            embedder: 用于语义检索和可视化的嵌入模型。
            chunk_size: 文本块大小。
            chunk_overlap: 文本块重叠大小。
            max_workers: 最大并行工作线程数。
            verbose: 是否开启详细日志。
            **kwargs: 其他传给 AutoSet 的参数。
        """
        super().__init__(
            item_schema=ImagerySymbol,
            key_extractor=lambda x: x.symbol_name.strip().lower(), # 精确键值匹配
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """
        可视化意象与隐喻库。

        Args:
            top_k_for_search: 搜索时找回的相关条目数量。
            top_k_for_chat: 聊天时找回的相关条目数量。
        """
        def item_label_extractor(item: ImagerySymbol) -> str:
            return item.symbol_name

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
