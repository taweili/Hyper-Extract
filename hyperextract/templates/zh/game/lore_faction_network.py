"""世界观势力网 - 从游戏背景故事中提取势力关系。

该模板构建政治/社会关系图，显示游戏世界中角色、阵营和地区之间的互动。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# Schema 定义
# ==============================================================================

class LoreEntitySchema(BaseModel):
    """背景故事网络中的实体（角色、阵营、地区）。"""

    entity_id: str = Field(..., description="该实体的唯一标识符")
    entity_type: str = Field(
        ...,
        description="实体的类型：'英雄'(角色)、'阵营'(组织)或'地区'(地点)",
    )
    entity_name: str = Field(..., description="实体的名称")
    description: Optional[str] = Field(None, description="对该实体的背景或特征的简要描述")


class LoreRelationshipSchema(BaseModel):
    """背景故事网络中的关系。"""

    source_entity: str = Field(..., description="关系的来源实体名称")
    target_entity: str = Field(..., description="关系的目标实体名称")
    relationship_type: str = Field(
        ...,
        description="关系类型：'隶属'(忠诚)、'敌对'(冲突)、"
        "'背叛'(背叛)、'建立'(建立)、'盟友'(联盟)等",
    )
    context: Optional[str] = Field(None, description="该关系的背景信息或解释")


# ==============================================================================
# 提取 Prompt
# ==============================================================================

_PROMPT = """你是一位游戏背景故事分析专家，擅长世界构建和势力关系。
你的任务是从游戏背景故事文本中提取实体（节点）及其政治/社会关系（边）。

提取：
1. **实体(节点)**：提到的所有角色（英雄）、阵营（组织）和地区
   - 对于角色：名称，类型='英雄'
   - 对于阵营：名称，类型='阵营'
   - 对于地区：名称，类型='地区'

2. **关系(边)**：政治、军事和社会联系
   - 隶属：一个角色隶属于一个阵营或居住在一个地区
   - 敌对：两个阵营或实体处于冲突中
   - 背叛：一个角色/阵营背叛了另一个
   - 建立：一个角色建立了一个阵营
   - 盟友：阵营之间的正式联盟
   - 其他基于背景的关系类型

关键：每条边必须连接提取的节点列表中存在的两个实体。
不创建不是显式识别为节点的实体之间的边。

仅提取文本中明确说明的信息。

### 源文本：
"""

_NODE_PROMPT = """你是一位游戏背景故事实体识别专家。
你的任务是从文本中提取所有不同的实体，这些实体将成为背景故事网络的节点。

提取三种类型的实体：
1. **英雄/角色**：具有名字的个人（如"亚索"、"阿狸"）
2. **阵营/组织**：团体、组织、国家、公会（如"印度群岛"、"诺克萨斯"、"监视者"）
3. **地区/地点**：地理区域和地方（如"暗影岛"、"皮尔特沃夫"、"德玛西亚"）

对于每个实体，提供：
- 实体名称（如文中所示）
- 实体类型（英雄/阵营/地区）
- 如果有的话，简要描述

重点放在完整性上。提取每个提到的实体，无论多么短暂。

### 源文本：
"""

_EDGE_PROMPT = """你是一位游戏背景故事网络关系提取专家。
你的任务是提取已提供实体之间的关系（边）。

给定下面的已知实体列表，提取连接它们的所有关系：
- 隶属：角色属于阵营；阵营控制地区
- 敌对：实体进行武装冲突
- 背叛：一个实体背叛了另一个
- 建立：角色建立了一个阵营
- 盟友：阵营之间的正式联盟
- 反对：反对而不一定是战争

关键规则：
1. 仅提取连接已提供实体列表中的实体的边
2. 不要发明或虚构不在提供的列表中的新实体
3. 如果实体出现在文本但不在已知列表中，不创建涉及它的边
4. 关注文本中的显式关系陈述

仅提取明确陈述的关系。不推断文中未清楚描述的关系。

### 源文本：
"""


# ==============================================================================
# 模板类
# ==============================================================================

class LoreFactionNetwork(AutoGraph[LoreEntitySchema, LoreRelationshipSchema]):
    """适用于：游戏背景故事、背景文档、角色传记、设定指南

    从游戏背景故事中提取政治和社会关系图，显示游戏世界中
    角色、阵营和地区如何相互作用。

    该模板特别适用于：
    - 可视化阵营关系和层级
    - 理解角色忠诚度和冲突
    - 构建世界构建图
    - 分析游戏背景中的地缘政治动态

    示例：
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> from hyperextract.templates.zh.game import LoreFactionNetwork
        >>>
        >>> llm = ChatOpenAI(model="gpt-4", temperature=0)
        >>> embedder = OpenAIEmbeddings()
        >>>
        >>> lore_graph = LoreFactionNetwork(
        ...     llm_client=llm,
        ...     embedder=embedder,
        ...     extraction_mode="two_stage"
        ... )
        >>>
        >>> lore_graph.feed_text('''
        ... 亚索是来自Ionia地区的剑士。他属于传统主义阵营。
        ... 印度群岛与诺克萨斯为争夺东方领土而交战。
        ... 阿狸是一只狐狸精，当她转向诺克萨斯一方时背叛了亚索。
        ... ''')
        >>>
        >>> # 节点：亚索、印度群岛、诺克萨斯、阿狸
        >>> # 边：亚索->印度群岛(隶属)、印度群岛->诺克萨斯(敌对)、阿狸->亚索(背叛)
        >>> lore_graph.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        extraction_mode: str = "two_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        **kwargs: Any,
    ):
        """初始化世界观势力网模板。

        参数：
            llm_client：语言模型客户端，用于提取（如 ChatOpenAI）
            embedder：嵌入模型，用于语义索引（如 OpenAIEmbeddings）
            extraction_mode：'one_stage'(更快、更简单)或'two_stage'(更准确)
            chunk_size：单个文本块的最大字符数（默认2048）
            chunk_overlap：相邻块之间的重叠字符数（默认256）
            **kwargs：传递给 AutoGraph 父类的其他参数
        """
        super().__init__(
            node_schema=LoreEntitySchema,
            edge_schema=LoreRelationshipSchema,
            node_key_extractor=lambda x: x.entity_name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source_entity.strip().lower()}|"
                f"{x.relationship_type.strip().lower()}|"
                f"{x.target_entity.strip().lower()}"
            ),
            nodes_in_edge_extractor=lambda x: (
                x.source_entity.strip().lower(),
                x.target_entity.strip().lower(),
            ),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 5,
        top_k_for_chat: int = 5,
    ) -> None:
        """展示世界观势力网为交互式关系图。

        参数：
            top_k_for_search：搜索检索的前 K 个实体数
            top_k_for_chat：对话上下文中显示的前 K 个实体数
        """

        def node_label_extractor(node: LoreEntitySchema) -> str:
            """提取展示标签，显示实体类型"""
            type_emoji = {
                "英雄": "👤",
                "阵营": "🏛️",
                "地区": "🗺️",
            }
            emoji = type_emoji.get(node.entity_type, "●")
            return f"{emoji} {node.entity_name}"

        def edge_label_extractor(edge: LoreRelationshipSchema) -> str:
            """提取关系的展示标签"""
            return edge.relationship_type.replace("_", " ")

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
