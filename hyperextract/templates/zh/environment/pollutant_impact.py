from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types.graph import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class EnvironmentalEntity(BaseModel):
    """环境污染领域中的实体。"""

    name: str = Field(description="污染物、污染源或受影响实体的名称。")
    entity_type: str = Field(
        description="实体类型：'Pollutant'(污染物-化学物质、颗粒等), 'Source'(源头-工厂、车辆等), 'Target'(受体-水体、空气、土壤、生物)。"
    )
    description: Optional[str] = Field(
        None, description="额外信息，如化学性质、位置或特征。"
    )


class PollutantImpact(BaseModel):
    """污染物或污染源与受影响实体之间的影响关系。"""

    source: str = Field(description="污染物或污染源。")
    target: str = Field(description="受影响的实体（生态系统、生物、地点）。")
    impact_type: str = Field(
        description="影响类型：'bioaccumulation'(生物富集), 'toxicity'(毒性), 'contamination'(污染), 'ecosystem damage'(生态破坏), 'health effect'(健康影响)。"
    )
    severity: Optional[str] = Field(
        None, description="严重程度：'critical'(严重), 'high'(较高), 'moderate'(中等), 'low'(轻微)。如果有，包含定量数据。"
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = """
你是一位环境科学家，专长于污染评估和生态影响分析。
你的任务是从报告、监测数据和新闻文章中提取污染源、污染物及其环保影响。

指导原则：
1. 识别文本中提到的所有污染物（如汞、PM2.5、塑料、二氧化碳等）。
2. 识别污染源（工厂、车辆、农业径流等）和受影响的对象（河流、空气、土壤、人口、野生动物）。
3. 提取因果关系：哪种污染物影响了哪个实体以及如何影响。
4. 记录严重程度或定量影响信息（如"50毫克/升浓度"、"污染等级为严重"）。
5. 精确表示污染流向：从污染源指向受体。

输出格式：
- 污染物和受影响的实体应该是不同的节点。
- 影响应该有明确的源头（污染物/污染源）、目标（受体）、影响类型和严重程度（如果有）。
"""

_NODE_PROMPT = """
你是一位专注于污染评估的环境科学家。
你的任务是在第一个提取阶段只提取环境实体（污染物、污染源、受体），不提取污染影响。
专注于找到所有实体。

指导原则：
1. 识别提到的所有污染物（化学物质、颗粒、化合物）。
2. 识别所有污染源（工厂、车辆、场所）。
3. 识别所有受体目标（水体、生物体、人口、生态系统）。
4. 对于每个实体，捕获：名称、实体_类型，以及任何相关特征。
5. 避免重复：整合对同一实体的引用。

输出格式：
- 每个实体应为不同的节点，包含名称、类型（污染物/污染源/受体）和描述。
"""

_EDGE_PROMPT = """
你是一位分析污染影响的环境科学家。
你的任务是在第二个提取阶段只提取已给定实体间的因果关系。
你将获得环境实体（节点）列表。你的工作是识别它们之间的污染影响关系。

指导原则：
1. 根据确认的实体列表，找出文本中的所有污染影响关系。
2. 对于每个影响，捕获：源（污染物/污染源实体）、目标（受影响实体）、影响_类型和严重程度。
3. 保留方向性：污染物从污染源流向目标。
4. 仅提取给定实体间的影响；忽略独立的实体提及。
5. 包括定量测量（浓度、严重程度）如有。

输出格式：
- 每个影响是一条边：源 → 目标，包含影响_类型和严重程度。
"""

# ==============================================================================
# 3. 模板类
# =============================================================================="


class PollutantImpactMap(AutoGraph[EnvironmentalEntity, PollutantImpact]):
    """
    环境污染追踪与影响评估知识图谱模板。

    将环境监测报告和可持续性分析转化为结构化的污染源-受体关系，
    用于环保健康风险分析。

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4")
        >>> embedder = OpenAIEmbeddings()
        >>> 
        >>> pollutant_map = PollutantImpactMap(llm_client=llm, embedder=embedder)
        >>> text = "工厂排放的汞污染了河流，导致鱼类受到严重毒性影响。"
        >>> pollutant_map.feed_text(text)
        >>> pollutant_map.show()  # 可视化污染物影响及严重程度
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
        **kwargs: Any,
    ):
        """初始化污染物影响图模板。

        Args:
            llm_client (BaseChatModel)：用于提取污染物和影响信息的语言模型客户端。
            embedder (Embeddings)：用于索引污染物、污染源和受影响对象的嵌入模型。
            extraction_mode (str, optional)：提取策略。默认为 "one_stage"。
                - "one_stage"：同时提取污染物和影响（更快）。
                - "two_stage"：先提取污染物，再提取影响（准确度更高）。
            chunk_size (int, optional)：每个文本块的最大字符数。默认为 2048。
            chunk_overlap (int, optional)：块之间的重叠字符数，用于保持上下文连贯性。默认为 256。
            max_workers (int, optional)：用于并行处理的最大并发提取工作进程数。默认为 10。
            verbose (bool, optional)：如果为 True，则打印详细的提取进度和污染物追踪日志。默认为 False。
            **kwargs：传递给 AutoGraph 基类的其他参数。
        """
        super().__init__(
            node_schema=EnvironmentalEntity,
            edge_schema=PollutantImpact,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.impact_type.lower()})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ) -> None:
        """可视化污染物影响网络用于环境评估。

        使用 OntoSight 展示污染源、污染物及受影响对象和严重程度信息。
        在内部定义实体的前端展示标签（名称 + 实体类型）和影响标签（影响类型 + 严重程度）。

        Args:
            top_k_nodes_for_search (int, optional)：搜索触发时要检索的环境实体（污染物/污染源/受体）数量。默认为 3。
            top_k_edges_for_search (int, optional)：搜索触发时要检索的影响关系数。默认为 3。
            top_k_nodes_for_chat (int, optional)：聊天触发时要检索的环境实体数量。默认为 3。
            top_k_edges_for_chat (int, optional)：聊天触发时要检索的影响关系数。默认为 3。
        """

        def node_label_extractor(node: EnvironmentalEntity) -> str:
            return f"{node.name} ({node.entity_type})"

        def edge_label_extractor(edge: PollutantImpact) -> str:
            severity = f" [{edge.severity}]" if edge.severity else ""
            return f"{edge.impact_type}{severity}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
