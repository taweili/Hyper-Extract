from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSpatialGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================

class AcupointNode(BaseModel):
    """经络系统中的学位或体表部位。"""
    name: str = Field(description="穴位标准名称（如：足三里、合谷）或身体部位（如：外膝眼下三寸）。")
    belongs_to_meridian: Optional[str] = Field(description="归属经脉（如：足阳明胃经）。部位节点可留空。")
    function_main: Optional[str] = Field(description="主治功效概要（如：理脾胃、调气血）。")

class MeridianFlow(BaseModel):
    """描述经气在人体空间的流注方向或定位关系。"""
    source: str = Field(description="起点穴位或部位。")
    target: str = Field(description="终点穴位或部位。")
    direction: str = Field(description="流注方向（如：循行向下、绕过、直入）。")
    spatial_desc: str = Field(description="具体的空间定位描述（如‘循胫骨外廉’、‘入属于胃’）。这是关键的空间信息。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是一位精通《灵枢·经脉》的经络学家。你的任务是从古籍或医学解剖描述中，解析经络在人体上的空间循行路径及流注关系。\n\n"
    "### 核心提取规则：\n"
    "1. **解剖定位**：精准提取‘循、入、出、下、绕、挟’等描述空间拓扑的动词。\n"
    "2. **流注顺序**：确保提取的连接是有向的，反映经气（Qi）的流动方向。\n"
    "3. **归经标注**：对于所有穴位，必须尝试识别并归纳其所述的十二正经或奇经八脉。\n"
    "4. **空间细化**：在 `spatial_desc` 中完整保留‘循胫骨外廉’、‘入属于胃’等具体的解剖描述。"
)

_NODE_PROMPT = (
    "你是一位人体解剖与穴位专家。请识别文本中出现的穴位名称、解剖标志（如‘鼻之交頞’）及经脉系统。\n\n"
    "### 提取要求：\n"
    "1. **节点涵盖**：除了标准穴位名，也应提取作为转向点的解剖部位。\n"
    "2. **功能关联**：若文中提到穴位的主治作用，应将其记录在 `function_main` 字段。\n"
    "3. **层级区分**：区分经脉总称（如足阳明胃经）与具体穴位节点。"
)

_EDGE_PROMPT = (
    "你是一位经络循行分析师。请根据已识别的穴位与部位，建立经络的空间流注链条。\n\n"
    "### 空间连接要求：\n"
    "1. **动词驱动**：关注‘起于’、‘下循’、‘旁约’等词汇，确定方向（Direction）。\n"
    "2. **路径描述**：在 `spatial_desc` 中详细记录路径中的空间方位和解剖细节。\n"
    "3. **拓扑连续性**：构建连续的流注路径，避免出现孤立的节点对。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class MeridianAcupointSpatial(AutoSpatialGraph[AcupointNode, MeridianFlow]):
    """
    适用于：[针灸学教材, 经络挂图, 黄帝内经等经典]

    一个旨在映射人体经络空间循行轨迹及穴位分布的图谱模板。

    Key Features:
    - 将人体视为“气”流动的拓扑地图进行分析。
    - 捕获详细的解剖路径描述（如“沿胫骨外侧后缘”）。
    - 建立代表经气运行顺序的方向性关系。

    Example:
        >>> from hyperextract.templates.zh.tcm import MeridianAcupointSpatial
        >>> spatial = MeridianAcupointSpatial(llm_client=llm, embedder=embedder)
        >>> text = "胃足阳明之脉，起于鼻之交頞中，旁约太阳之脉，下循鼻外。"
        >>> spatial.feed_text(text).show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        **kwargs: Any
    ):
        """
        初始化 MeridianAcupointSpatial 图谱。

        Args:
            llm_client (BaseChatModel): 用于提取的语言模型客户端。
            embedder (Embeddings): 用于索引的嵌入模型。
            extraction_mode (str): 提取模式，'one_stage' 或 'two_stage'。默认为 'two_stage'。
            **kwargs: 传递给 AutoSpatialGraph 的额外参数。
        """
        super().__init__(
            node_schema=AcupointNode,
            edge_schema=MeridianFlow,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source}->{x.direction}->{x.target}",
            location_in_edge_extractor=lambda x: x.spatial_desc,
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
            observation_location="人体经络系统 (Human Meridian System)",
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            extraction_mode=extraction_mode,
            **kwargs
        )

    def show(self, **kwargs):
        """
        可视化经络流注网络。

        Args:
            **kwargs: 传递给基础 show() 方法的参数。
        """
        def n_label(node: AcupointNode) -> str:
            meridian = f"[{node.belongs_to_meridian}]" if node.belongs_to_meridian else ""
            return f"{meridian} {node.name}"
        def e_label(edge: MeridianFlow) -> str: return f"{edge.direction} ({edge.spatial_desc})"
        super().show(node_label_extractor=n_label, edge_label_extractor=e_label, **kwargs)
