from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class BiologicalHazard(BaseModel):
    """
    在食品生产中必须控制的生物学危害。
    """

    name: str = Field(
        description='危害病原体名称，例如"沙门氏菌"、"单核细胞增生李斯特菌"、"O157:H7 大肠杆菌"等。'
    )
    hazard_type: str = Field(
        description='类型："细菌"、"病毒"、"寄生虫"、"真菌"。'
    )
    health_consequence: Optional[str] = Field(
        None, description='潜在健康影响，例如"严重肠胃炎"、"败血症"等。'
    )


class CriticalControlPoint(BaseModel):
    """
    食品生产中可以控制危害的步骤或工序。
    """

    name: str = Field(
        description='CCP 名称，例如"巴氏杀菌"、"金属检测"、"冷藏"等。'
    )
    process_stage: str = Field(
        description='生产阶段："原料"、"收货"、"加工"、"烹饪"、"冷却"、"包装"、"储存"。'
    )
    description: Optional[str] = Field(
        None, description="CCP 的详细描述。"
    )


class ControlMeasure(BaseModel):
    """
    连接危害和 CCP 的控制措施。
    """

    source: str = Field(description="生物学危害名称。")
    target: str = Field(description="CCP 名称。")
    critical_limit: str = Field(
        description='定义安全/不安全分界线的关键限值，例如">=72°C 持续 >=15 秒"、"pH < 4.6"等。'
    )
    monitoring_procedure: str = Field(
        description='如何监测 CCP，例如"每批次温度计读数"、"每天 pH 计测量"等。'
    )
    monitoring_frequency: str = Field(
        description='监测频率，例如"每 2 小时"、"每批次"、"每天"等。'
    )
    corrective_action: str = Field(
        description='如果不达到关键限值的行动，例如"销毁产品"、"重新加工"、"警报 QA"等。'
    )
    verification: Optional[str] = Field(
        None, description='验证有效性的方法，例如"每月进行培养测试"等。'
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是食品安全专家，熟悉 HACCP 原则。从 HACCP 计划和食品安全文件中提取危害、关键控制点及其控制措施。\n\n"
    "规则:\n"
    "- 识别与产品和工序相关的生物学危害。\n"
    "- 识别可以消除或控制危害的 CCP。\n"
    "- 提取关键限值、监测程序和纠偏行动。\n"
    "- 确保每个 CCP 链接到它控制的具体危害。"
)

_NODE_PROMPT = (
    "你是食品安全专家。从 HACCP 文件中提取所有危害和 CCP（节点）。\n\n"
    "提取规则:\n"
    "- 识别所有提及的生物学危害（病原体、过敏原如适用）。\n"
    "- 识别所有 CCP（烹饪、冷却、金属检测阶段）。\n"
    "- 按类型对每个危害进行分类（细菌、病毒、真菌、寄生虫）。\n"
    "- 按生产阶段对每个 CCP 进行分类。\n"
    "- 此阶段不建立控制关系。"
)

_EDGE_PROMPT = (
    "你是食品安全专家。在获得危害和 CCP 清单的基础上，提取控制关系（边）。\n\n"
    "提取规则:\n"
    "- 将每个危害连接到控制它的 CCP。\n"
    "- 提取具有精确阈值和单位的关键限值。\n"
    "- 从 HACCP 文件中提取监测程序和频率。\n"
    "- 提取超过限值时应采取的纠偏行动。\n"
    "- 在有文件记录时包括验证方法。\n"
    "- 仅在提供的列表中存在的危害和 CCP 之间创建边。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class FoodSafetyHACCPGraph(AutoGraph[BiologicalHazard, ControlMeasure]):
    """
    适用文档: HACCP 计划、食品安全计划（ISO 22000）、SOP 手册、FDA 指导文件、食品公司质量规程、供应商审计报告。

    模板用于系统地从基于 HACCP 的食品安全控制中提取和结构化信息。支持合规验证、供应商审计和整个食品生产运营中的持续安全监测。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> haccp = FoodSafetyHACCPGraph(llm_client=llm, embedder=embedder)
        >>> plan = "关键控制点：巴氏杀菌。危害：沙门氏菌。关键限值：72°C 持续 15 秒..."
        >>> haccp.feed_text(plan)
        >>> haccp.show()
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
        """
        初始化食品安全 HACCP 图谱模板。

        Args:
            llm_client (BaseChatModel): 用于危害和控制提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoGraph 的其他参数。
        """
        super().__init__(
            node_schema=BiologicalHazard,
            edge_schema=ControlMeasure,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: (
                f"{x.source.strip()}--({x.target.strip()}): {x.critical_limit.strip()}"
            ),
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
        """
        使用 OntoSight 可视化食品安全控制图。

        Args:
            top_k_nodes_for_search (int): 检索的危害/CCP 数。默认 3。
            top_k_edges_for_search (int): 检索的控制措施数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的节点数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的边数。默认 3。
        """

        def node_label_extractor(node: BiologicalHazard) -> str:
            if isinstance(node, BiologicalHazard):
                return f"{node.name} ({node.hazard_type})"
            return str(node)

        def edge_label_extractor(edge: ControlMeasure) -> str:
            return f"{edge.critical_limit}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
