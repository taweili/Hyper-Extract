from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. 模式定义 (Schema)
# ==============================================================================

class ManufacturingEntity(BaseModel):
    """汽车供应链或生产线上的实体（供应商、工厂、组装环节）。"""
    name: str = Field(description="公司名称、工厂名称或生产工艺名称。")
    category: str = Field(
        description="类别：'供应商'、'工厂'、'工艺'、'原材料'、'质检'。"
    )
    specification: Optional[str] = Field(description="产能、资质认证或交付周期。")

class SupplyChainRelation(BaseModel):
    """汽车制造中参与方与环节之间的连接关系。"""
    source: str = Field(description="上游供应商或工艺环节。")
    target: str = Field(description="下游工厂或产品。")
    relation_type: str = Field(
        description="类型：'供货给'、'组装于'、'处理自'、'认证用于'。"
    )
    logistics_details: Optional[str] = Field(description="贸易术语、运输时间或供应量承诺。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

MFG_GRAPH_PROMPT = (
    "你是一位大型汽车制造商的供应链分析师。请提取汽车制造与供应链图谱。\n\n"
    "准则：\n"
    "- 识别各级供应商（一级、二级供应商）及其提供的零部件。\n"
    "- 映射从原材料到整车下线的组装序列。\n"
    "- 捕捉工厂的地理位置及特定的物流限制条件。"
)

MFG_NODE_PROMPT = (
    "提取供应商、制造工厂和关键生产步骤。标注它们在车辆生产周期中的角色。"
)

MFG_EDGE_PROMPT = (
    "定义物料流和工艺流。连接供应商到组装工厂，以及工厂到最终的整车交付环节。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================

class AutomotiveMfgGraph(AutoGraph[ManufacturingEntity, SupplyChainRelation]):
    """
    汽车制造图谱模板，用于生产线流程、供应链物流和供应商管理。
    
    有助于可视化全球汽车制造生态系统中的依赖关系。
    
    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI()
        >>> embedder = OpenAIEmbeddings()
        >>> graph = AutomotiveMfgGraph(llm_client=llm, embedder=embedder)
        >>> text = "宁德时代向特斯拉柏林超级工厂供应电池芯，用于 Model Y 的组装。"
        >>> graph.feed_text(text)
        >>> print(graph.edges) # 供应链流动信息
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
        初始化汽车制造图谱模板。

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
            node_schema=ManufacturingEntity,
            edge_schema=SupplyChainRelation,
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
            prompt=MFG_GRAPH_PROMPT,
            prompt_for_node_extraction=MFG_NODE_PROMPT,
            prompt_for_edge_extraction=MFG_EDGE_PROMPT,
            **kwargs
        )
