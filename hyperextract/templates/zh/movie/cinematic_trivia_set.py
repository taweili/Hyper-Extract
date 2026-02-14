from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema 定义
# ==============================================================================

class CinematicTrivia(BaseModel):
    """电影要素、彩蛋、制作花絮或特殊叙事元素。"""
    topic: str = Field(description="电影要素或彩蛋的主题名称（如‘致敬《2001太空漫游》’、‘打破第四面墙’）。")
    description: str = Field(description="该要素的具体表现或花絮内容详情。")
    timestamp: Optional[str] = Field(description="元素在电影中出现的具体时间点（如 '01:23:45'）。")
    significance: List[str] = Field(description="该元素的艺术意义、叙事功能或对影迷的特殊含义。")
    source: List[str] = Field(description="该知识点的来源（如评论音轨、特定网站、IMDb）。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位资深的影评人和电影百科专家。你的任务是从影评、制作手册和花絮文本中提取结构化的电影百科知识点。\n\n"
    "分析指南：\n"
    "1. **主题去重**：将关于同一个知识点（如‘斯坦·李客串’）的多个片段合并。LLM 应确保名称标准化。\n"
    "2. **深度挖掘**：不仅提取是什么，还要提取这一设计背后的艺术意图（significance）。\n"
    "3. **信息累加**：通过多次读取文本，不断丰富同一个主题下的描述、时间点和来源记录。\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class CinematicTriviaSet(AutoSet[CinematicTrivia]):
    """
    适用于：[制作笔记, 评论音轨, 幕后花絮, 影迷趣闻, 长篇影评]

    用于构建和聚合电影百科知识、场景彩蛋与艺术表现元素的集合模板。

    该模板利用 AutoSet 的富集特性，能够跨文档聚合零散的影迷百科知识。

    示例:
        >>> trivia = CinematicTriviaSet(llm_client=llm, embedder=embedder)
        >>> trivia.feed_text("导演在86分钟处设置了一个致敬库布里克的隐藏镜头。").feed_text("那个红色的椅子其实是致敬《闪灵》。")
        >>> trivia.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        chunk_size: int = 2048,
        **kwargs: Any
    ):
        super().__init__(
            item_schema=CinematicTrivia,
            key_extractor=lambda x: x.topic.strip().lower(),
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            **kwargs
        )

    def show(self, **kwargs):
        def label(item: CinematicTrivia) -> str: return item.topic
        super().show(item_label_extractor=label, **kwargs)
