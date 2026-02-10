from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.graphs import AutoGraph

# ==============================================================================
# 1. Schema 定义 (Schema Definitions)
# ==============================================================================

class AgriEntity(BaseModel):
    """农业领域实体（如作物、土壤、病虫害、防治措施、农机具）。"""
    name: str = Field(description="农业实体的名称。")
    category: str = Field(
        description="类别：'作物', '生长阶段', '土壤/气候条件', '农事活动', '逆境/病虫害', '农资/肥料'。"
    )
    description: Optional[str] = Field(description="实体的具体特征或状态描述。")

class AgriRelation(BaseModel):
    """农业实体间的关系（如'需求'、'受...影响'、'继...之后'）。"""
    source: str = Field(description="源实体名称。")
    target: str = Field(description="目标实体名称。")
    relation_type: str = Field(
        description="类型：'处于阶段', '影响', '需要操作', '施用于', '进入下一阶段'。"
    )
    specification: Optional[str] = Field(description="具体的用量、时机或影响细节。")

# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

CROP_CYCLE_PROMPT = (
    "你是一位资深农艺师。请从文本中提取作物生长与管理图谱。\n\n"
    "提取指南：\n"
    "- 识别作物及其具体的生长阶段（如：播种、开花、成熟）。\n"
    "- 将土壤条件、天气要求以及必要的农事活动（灌溉、施肥）关联到具体的阶段。\n"
    "- 记录任何提及的威胁因素（如病虫害）及其对作物的影响。"
)

CROP_CYCLE_NODE_PROMPT = (
    "请提取关键农业组成要素：作物类型、生长阶段、环境条件（土壤/pH值/温度）、农事任务以及生物逆境（病虫害/真菌）。为每一项提供清晰的类别。"
)

CROP_CYCLE_EDGE_PROMPT = (
    "在作物周期中建立逻辑链路。按顺序连接生长阶段，将农事任务关联到其所属的阶段，并将环境要求映射到它们影响的实体上。使用'需要'、'抑制'等具体的对应关系类型。"
)

# ==============================================================================
# 3. 模板类 (Template Class)
# ==============================================================================

class CropCycleGraph(AutoGraph[AgriEntity, AgriRelation]):
    """
    用于映射作物生长阶段、环境要求和农事活动的模板。
    
    适用于精准农业、作物管理指南以及季节性种植规划。
    
    示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> graph = CropCycleGraph(llm_client=llm, embedder=embedder)
        >>> text = "玉米在营养生长阶段需要大量的氮肥。"
        >>> graph.feed_text(text)
        >>> print(graph.nodes) # 提取出：玉米、氮肥、营养生长阶段
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
        初始化 CropCycleGraph 模板。

        Args:
            llm_client: 用于提取的语言模型客户端。
            embedder: 用于去重的嵌入模型。
            extraction_mode: "one_stage" 或 "two_stage"。
            chunk_size: 每个分块的最大字符数。
            chunk_overlap: 分块间的重叠字符数。
            max_workers: 并行处理的最大 worker 数量。
            verbose: 是否开启进度日志。
            **kwargs: 传递给 AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=AgriEntity,
            edge_schema=AgriRelation,
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
            prompt=CROP_CYCLE_PROMPT,
            prompt_for_node_extraction=CROP_CYCLE_NODE_PROMPT,
            prompt_for_edge_extraction=CROP_CYCLE_EDGE_PROMPT,
            **kwargs
        )
