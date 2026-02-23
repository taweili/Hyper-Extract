from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema 定义
# ==============================================================================

class OpinionStance(BaseModel):
    """在该话题下，某个主体持有的观点与立场。"""
    entity: str = Field(description="表达观点的个人、组织、媒体或团体。")
    stance: str = Field(description="核心立场标签（如：支持、强烈反对、中立、质疑）。")
    key_argument: str = Field(description="支撑该立场的核心论点或诉求。")
    evidence_provided: List[str] = Field(description="主体提供的论据、数据或事实支撑。")
    potential_interest: Optional[str] = Field(description="该立场背后可能隐含的利益诉求或动机。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位多维舆情分析师。你的任务是从新闻报道、杂谈或评论中识别并归纳不同利益相关方的观点立场。\n\n"
    "提取要求：\n"
    "1. **主体识别**：清晰界定发声的主体。\n"
    "2. **立场解构**：不仅要记录‘说了什么’，还要通过细微的语调判断其核心态度（立场）。\n"
    "3. **论证梳理**：提取其陈述中具有说服力的事实依据。\n"
    "4. **横向沉淀**：如果多个文本提到了同一个主体的相同立场，请将新的论据补充到该主体条目中。\n"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class OpinionSet(AutoSet[OpinionStance]):
    """
    适用于：[舆情分析, 媒体评论, 辩论实录, 社论专栏]

    用于从新闻和评论中归纳不同主体观点分布及论据的知识挖掘模板。

    该模板使用 AutoSet 结构，根据“主体+立场”作为主键进行知识沉淀，适合梳理复杂议题下的舆论博弈格局。

    示例:
        >>> opinion_set = OpinionSet(llm_client=llm, embedder=embedder)
        >>> text = "环保组织A发表声明反对该项目，称其会破坏湿地。当地政府则表示项目能带动就业。"
        >>> opinion_set.feed_text(text).show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        **kwargs: Any
    ):
        super().__init__(
            schema=OpinionStance,
            # 以 实体 和 立场 的组合作为主键，沉淀同类观点
            key_extractor=lambda x: f"{x.entity.strip()}:{x.stance.strip()}",
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            **kwargs
        )

    def show(self, **kwargs):
        def label_func(item: OpinionStance) -> str:
            return f"【{item.stance}】{item.entity}: {item.key_argument}"
        super().show(item_label_extractor=label_func, **kwargs)
