"""版本更新日志 - 从补丁说明提取所有单独的游戏改动。

该模板提取游戏补丁的全面变更日志，所有修改、平衡更新和错误修复，
无去重，保留每个独立的变更条目。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoList

# ==============================================================================
# Schema 定义
# ==============================================================================

class PatchChangeSchema(BaseModel):
    """补丁说明中单个变更条目的数据结构。"""

    entity_name: str = Field(..., description="被修改的对象名称：角色名称、物品名称等")
    change_type: str = Field(
        ...,
        description="变更类型：'增强'(提升)、'削弱'(下降)、'机制调整'、'错误修复'、'重做'等",
    )
    old_value: Optional[str] = Field(None, description="修改前的数值或状态")
    new_value: Optional[str] = Field(None, description="修改后的数值或状态")
    patch_version: Optional[str] = Field(None, description="该变更生效的版本号或补丁日期")
    developer_note: Optional[str] = Field(None, description="开发者提供的变更理由或说明")


# ==============================================================================
# 提取 Prompt
# ==============================================================================

_PROMPT = """你是一位补丁说明分析专家和游戏平衡设计师。
你的任务是从补丁说明中提取每个单独的游戏变更的详细信息。

对于提到的每个变更或修改，提取：
1. **entity_name**：被修改的对象（角色、物品、能力、系统等）
2. **change_type**：变更的性质（增强、削弱、机制调整、错误修复、重做等）
3. **old_value**：变更前的数值、属性或机制
4. **new_value**：变更后的数值、属性或机制
5. **patch_version**：该变更实施的补丁版本或日期
6. **developer_note**：对变更的解释或理由（如提供）

关键：将每个单独的变更作为单个条目提取。
如果一个对象在一个补丁中有多个变更（例如，既被削弱攻击力又增强防御力），
为每个变更创建单独的条目以保留完整的变更历史。

仅提取文本中明确提及的信息。
全面捕捉所有修改，无论多么细微。

### 源文本：
"""


# ==============================================================================
# 模板类
# ==============================================================================

class PatchNoteChangelog(AutoList[PatchChangeSchema]):
    """适用于：官方补丁说明、版本变更日志、平衡更新

    从补丁文档中提取游戏修改的详细变更日志。

    与进行去重的 AutoSet 不同，该模板保留每个单独的变更作为单个条目。
    这对于以下方面至关重要：
    - 追踪每个对象的完整平衡历史
    - 分析同一补丁中对同一对象的多个变更
    - 审查游戏设计决定的演变
    - 构建全面的补丁数据库而不丢失数据

    示例：
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> from hyperextract.templates.zh.game import PatchNoteChangelog
        >>>
        >>> llm = ChatOpenAI(model="gpt-4", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>>
        >>> changelog = PatchNoteChangelog(
        ...     llm_client=llm,
        ...     embedder=embedder
        ... )
        >>>
        >>> # 输入补丁说明
        >>> changelog.feed_text('''
        ... 补丁 2.3.0 - 平衡更新
        ... 亚索：攻击力从50增加到55（增强后期伤害）
        ... 亚索：风之障壁冷却时间从25秒降低到20秒（生活质量改进）
        ... 无尽之刃：攻击力加成从80增加到85
        ... ''')
        >>>
        >>> # 每个变更都作为单独条目保留，不合并
        >>> # 即使亚索有2个变更，总共得到3条条目
        >>> changelog.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        """初始化版本更新日志模板。

        参数：
            llm_client：语言模型客户端，用于变更提取（如 ChatOpenAI）
            embedder：嵌入模型，用于语义索引（如 OpenAIEmbeddings）
            chunk_size：单个文本块的最大字符数（默认2048）
            chunk_overlap：相邻块之间的重叠字符数（默认256）
            **kwargs：传递给 AutoList 父类的其他参数
        """
        super().__init__(
            item_schema=PatchChangeSchema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """展示补丁变更日志为交互式数据库。

        参数：
            top_k_for_search：语义搜索返回的前 K 个结果数
            top_k_for_chat：对话上下文中显示的前 K 个结果数
        """

        def change_label_extractor(item: PatchChangeSchema) -> str:
            """提取展示标签：对象名称带变更类型"""
            return f"{item.entity_name} ({item.change_type})"

        super().show(
            item_label_extractor=change_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
