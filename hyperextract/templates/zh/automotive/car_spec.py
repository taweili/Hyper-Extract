from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.graphs import AutoGraph

# ==============================================================================
# 1. 模式定义 (Schema)
# ==============================================================================

class CarComponent(BaseModel):
    """车辆组件或参数类别（发动机、电池、自动驾驶、传动系统）。"""
    name: str = Field(description="车型名称或具体组件名称。")
    category: str = Field(
        description="类别：'车型'、'动力系统'、'底盘'、'安全系统'、'信息娱乐'。"
    )
    specification: Optional[str] = Field(description="详细参数（如：马力、电量、版本）。")

class CarSystemRelation(BaseModel):
    """汽车系统间的层级或技术关系。"""
    source: str = Field(description="父系统或车辆型号。")
    target: str = Field(description="子组件或功能。")
    relation_type: str = Field(
        description="类型：'配备'、'动力源自'、'集成'、'兼容'。"
    )
    performance_note: Optional[str] = Field(description="性能指标或集成细节。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

CAR_SPEC_GRAPH_PROMPT = (
    "你是一位汽车工程师和技术评论员。请提取车辆的技术参数图谱。\n\n"
    "准则：\n"
    "- 识别车型及其核心系统（发动机、电机、电池、支驾系统）。\n"
    "- 映射组件层级关系（例如：电池包含电芯，发动机使用涡轮增压器）。\n"
    "- 捕捉可量化的参数，如 0-100km/h 加速、续航里程、峰值功率和扭矩。"
)

CAR_SPEC_NODE_PROMPT = (
    "提取车型和技术组件。重点关注名称及其可测量的参数指标（如：500马力、80kWh）。"
)

CAR_SPEC_EDGE_PROMPT = (
    "定义技术依赖关系。展示哪些组件属于哪个汽车系统。使用诸如'动力源自'或'配备'等关系。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class CarSpecGraph(AutoGraph[CarComponent, CarSystemRelation]):
    """
    汽车参数图谱模板，用于提取车辆技术数据和参数层级。
    
    适用于竞品分析、汽车垂直媒体和技术文档处理。
    
    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI()
        >>> embedder = OpenAIEmbeddings()
        >>> graph = CarSpecGraph(llm_client=llm, embedder=embedder)
        >>> text = "特斯拉 Model 3 高性能版采用双电机全轮驱动，可输出 510 马力。"
        >>> graph.feed_text(text)
        >>> print(graph.nodes) # 车辆及其组件参数
    """
    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "one_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any
    ):
        """
        初始化汽车参数图谱模板。

        Args:
            llm_client: 语言模型客户端。
            embedder: 嵌入模型。
            extraction_mode: 提取模式，"one_stage" 或 "two_stage"。
            chunk_size: 分块大小。
            chunk_overlap: 分块重叠大小。
            max_workers: 最大并行工作线程数。
            verbose: 是否开启详细日志。
            **kwargs: 传递给 AutoGraph 的额外参数。
        """
        super().__init__(
            node_schema=CarComponent,
            edge_schema=CarSystemRelation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.relation_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CAR_SPEC_GRAPH_PROMPT,
            prompt_for_node_extraction=CAR_SPEC_NODE_PROMPT,
            prompt_for_edge_extraction=CAR_SPEC_EDGE_PROMPT,
            **kwargs
        )
