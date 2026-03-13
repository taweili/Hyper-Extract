"""结构化摘要 - 标准化提取 5W1H 要素。

适用于新闻聚合、自动简报。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoModel


class NewsSummaryInfo(BaseModel):
    """新闻摘要信息"""

    who: str = Field(description="核心人物/主体")
    what: str = Field(description="发生了什么")
    when: str = Field(description="时间")
    where: str = Field(description="地点")
    why: str = Field(description="原因")
    how: str = Field(description="如何发生")
    casualties: str = Field(description="伤亡情况", default="")
    response: str = Field(description="官方回应", default="")


_PROMPT = """## 角色与任务
你是一位专业的新闻编辑，请从新闻文本中提取结构化的5W1H要素，构建新闻摘要。

## 提取规则
1. 识别核心人物/主体（Who）
2. 识别发生了什么（What）
3. 识别时间（When）
4. 识别地点（Where）
5. 识别原因（Why）
6. 识别如何发生（How）
7. 识别伤亡情况（Casualties），如无则为空白
8. 识别官方回应（Response），如无则为空白

### 约束条件
- 只提取文本中明确提及的信息，不添加额外内容
- 保持客观准确，符合新闻写作风格
- 时间格式统一为年-月-日或具体时间点
- 地点要具体到城市或区域

## 新闻文本:
{source_text}
"""


class NewsSummaryModel(AutoModel[NewsSummaryInfo]):
    """
    适用文档: 新闻快讯、新闻聚合

    功能介绍:
    标准化提取 5W1H 要素（Who, What, When, Where, Why, How）。

    设计说明:
    - 输出（NewsSummaryInfo）：包含 who、what、when、where、why、how、casualties、response 字段

    Example:
        >>> template = NewsSummaryModel(llm_client=llm, embedder=embedder)
        >>> template.feed_text("某地发生交通事故...")
        >>> print(template.data.who)
        >>> print(template.data.what)
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化结构化摘要模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            data_schema=NewsSummaryInfo,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k: int = 3,
    ):
        """
        展示新闻摘要。

        Args:
            top_k: 问答使用的条目数量，默认为 3
        """

        def label_extractor(item: NewsSummaryInfo) -> str:
            return f"{item.when} {item.where}: {item.what[:30]}..."

        super().show(
            label_extractor=label_extractor,
            top_k=top_k,
        )
