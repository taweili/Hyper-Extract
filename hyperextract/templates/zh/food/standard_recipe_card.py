"""单品标准食谱 - 针对单个菜品提取完整的配料表、步骤说明及关键TIPS。

适用于后厨SOP卡片、烹饪教学。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoModel


class RecipeInfo(BaseModel):
    """标准食谱信息"""

    name: str = Field(description="菜名")
    cuisine: str = Field(description="菜系，如浙菜、川菜、粤菜等", default="")
    category: str = Field(description="分类，如热菜、凉菜、主食、甜品等", default="")
    flavor: str = Field(description="口味描述，如咸甜鲜香、麻辣等", default="")
    difficulty: str = Field(description="难度：简单/中等/困难", default="")
    cooking_time: str = Field(description="预估烹饪时间，如90分钟", default="")
    servings: str = Field(description="适合人数，如4-6人份", default="")
    main_ingredients: List[str] = Field(description="主料列表", default_factory=list)
    auxiliary_ingredients: List[str] = Field(
        description="辅料列表", default_factory=list
    )
    seasonings: List[str] = Field(description="调味品列表", default_factory=list)
    steps: List[str] = Field(description="烹饪步骤列表", default_factory=list)
    tips: List[str] = Field(description="关键控制点TIPS", default_factory=list)
    nutrition_info: str = Field(description="营养信息", default="")


_PROMPT = """## 角色与任务
你是一位专业的烹饪大师，请从文本中提取单个菜品的完整标准食谱信息。

## 提取规则
### 核心约束
1. 识别文本的核心菜品主体
2. 提取菜名、菜系、分类、口味等基本信息
3. 提取完整的原料信息（分为主料、辅料、调味品）
4. 提取详细的烹饪步骤
5. 提取关键控制点TIPS

### 领域特定规则
- 原料分类：主料（主要食材）、辅料（辅助食材）、调味品（调料）
- 烹饪步骤：按顺序提取，每步一个条目
- TIPS：提取烹饪中的关键技巧和注意事项

## 源文本:
{source_text}
"""


class StandardRecipeCard(AutoModel[RecipeInfo]):
    """
    适用文档: 标准食谱卡片、菜谱规范、烹饪教程

    功能介绍:
    针对单个菜品提取完整的配料表、步骤说明及关键TIPS，适用于后厨SOP卡片、烹饪教学。

    Example:
        >>> template = StandardRecipeCard(llm_client=llm, embedder=embedder)
        >>> template.feed_text("红烧肉：五花肉500克，生抽30毫升...")
        >>> print(template.data.name)
        >>> print(template.data.steps)
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
        初始化单品标准食谱模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            data_schema=RecipeInfo,
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
        展示标准食谱信息。

        Args:
            top_k: 问答使用的条目数量，默认为 3
        """

        def label_extractor(item: RecipeInfo) -> str:
            return f"{item.name} ({item.category})"

        super().show(
            label_extractor=label_extractor,
            top_k=top_k,
        )
