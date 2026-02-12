from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types.set import AutoSet

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class SpeciesStatus(BaseModel):
    """物种的保护和濒危状态。"""

    name: str = Field(description="物种的学名或常用名。")
    endangered_level: str = Field(
        description="保护状态：'Extinct'(灭绝), 'Extinct in the Wild'(野外灭绝), 'Critically Endangered'(极危), 'Endangered'(濒危), 'Vulnerable'(易危), 'Near Threatened'(近危), 'Least Concern'(无危)。"
    )
    main_threats: Optional[str] = Field(
        None,
        description="物种面临的主要威胁（如'habitat loss'(栖息地丧失), 'poaching'(偷猎), 'climate change'(气候变化), 'pollution'(污染))。"
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = """
你是一位保护生物学和野生动物保护专家。
你的任务是从保护报告、IUCN红色名录摘要或生物多样性评估中提取濒危物种的信息。

指导原则：
1. 识别文本中提到的所有物种及其保护或濒危状态。
2. 对于每个物种，根据标准保护等级进行分类：灭绝、野外灭绝、极危、濒危、易危、近危或无危。
3. 提取危害物种的主要威胁（栖息地丧失、偷猎、气候变化、疾病、污染等）。
4. 确保物种名称和分类的科学准确性。
5. 避免重复：如果同一物种多次出现且状态和威胁相同，应合并为一个条目。

输出格式：
- 每个物种应该有名称、濒危等级和主要威胁。
- 将同一物种的多个提及合并为一个综合条目。
"""

# ==============================================================================
# 3. 模板类
# ==============================================================================


class EndangeredSpeciesList(AutoSet[SpeciesStatus]):
    """
    濒危和受威胁物种文档的唯一集合模板。

    将保护评估和生物多样性报告转化为一个去重的物种清单，
    包含其濒危状态和主要威胁，支持保护优先级设定和资源配置。

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4")
        >>> embedder = OpenAIEmbeddings()
        >>> 
        >>> endangered_list = EndangeredSpeciesList(llm_client=llm, embedder=embedder)
        >>> text = "大熊猫（易危）面临栖息地丧失。爪哇犀牛（极危）受到偷猎威胁。"
        >>> endangered_list.feed_text(text)
        >>> endangered_list.show()  # 显示去重的濒危物种
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
        **kwargs: Any,
    ):
        """初始化濒危物种清单模板。

        Args:
            llm_client (BaseChatModel)：用于提取物种和威胁信息的语言模型客户端。
            embedder (Embeddings)：用于物种去重和威胁描述索引的嵌入模型。
            chunk_size (int, optional)：每个文本块的最大字符数。默认为 2048。
            chunk_overlap (int, optional)：块之间的重叠字符数，用于保持上下文连贯性。默认为 256。
            max_workers (int, optional)：并发提取的最大工作进程数。默认为 10。
            verbose (bool, optional)：如果为 True，则打印详细的提取和去重进度日志。默认为 False。
            **kwargs：传递给 AutoSet 基类的参数，用于控制去重行为。
        """
        super().__init__(
            item_schema=SpeciesStatus,
            key_extractor=lambda x: x.name.strip().lower(),
            llm_client=llm_client,
            embedder=embedder,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """可视化濒危物种清单用于保护规划。

        使用 OntoSight 展示去重的唯一物种集合，包含濒危等级和威胁信息。
        在内部定义物种的前端展示标签（名称 + 濒危等级，用于保护优先级可视化）。

        Args:
            top_k_for_search (int, optional)：搜索触发时从去重集合中检索的物种数量。默认为 3。
            top_k_for_chat (int, optional)：聊天触发时从去重集合中检索的物种数量。默认为 3。
        """

        def item_label_extractor(item: SpeciesStatus) -> str:
            return f"{item.name} - {item.endangered_level}"

        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
