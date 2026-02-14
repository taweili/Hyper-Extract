from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoTemporalGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class IngredientState(BaseModel):
    """
    食材/材料在食谱工序特定阶段的状态。
    """

    name: str = Field(
        description="状态描述符，例如混合液、加热面团、冷却浆液。"
    )
    composition: str = Field(
        description="这个状态中的物质，例如蛋+糖、面粉+水+盐。"
    )
    physical_state: Optional[str] = Field(
        None, description="物理形态：液体、固体、粉末、面团、乳液、泡沫。"
    )


class ProcessingStep(BaseModel):
    """
    连接两个食材状态的转换步骤。
    """

    step_id: str = Field(description="步骤标识符，例如步骤 1、1.1、混合。")
    source_state: str = Field(description="开始时的食材状态。")
    target_state: str = Field(description="加工后的食材状态。")
    action: str = Field(
        description="加工动作，例如混合、加热、冷却、静置、揉搓、发酵。"
    )
    process_conditions: Optional[str] = Field(
        None, description="综述持续时间、温度、设备及工艺参数。"
    )


# ==============================================================================
# 2. 提示词 (Prompts)
# ==============================================================================

_PROMPT = (
    "你是食品科学家。提取配方工序步骤。\n\n"
    "规则:\n"
    "- 识别加工动作及能量转换。\n"
    "- 提取步骤前后的食材状态。\n"
    "- 捕捉 **工艺条件 (process_conditions)**（时间、温度、设备等）。\n"
    "- 保持严格的先后顺序。"
)

_NODE_PROMPT = (
    "你是食品科学家。提取食材状态（节点）。\n\n"
    "提取规则:\n"
    "- 识别不同阶段的状态（原始、混合、熟制）。\n"
    "- 列出存在的组成物质。\n"
    "- 记录其物理形态。"
)

_EDGE_PROMPT = (
    "你是食品科学家。提取加工步骤（边）。\n\n"
    "提取规则:\n"
    "- 通过动作连接源状态与目标状态。\n"
    "- **process_conditions**: 合并记录时间、温度、设备等参数。\n"
    "- 保持精确的步骤顺序。\n"
    "- 仅连接存在的节点。"
)

# ==============================================================================
# 3. 模板类
# ==============================================================================


class RecipeProcessGraph(AutoTemporalGraph[IngredientState, ProcessingStep]):
    """
    适用文档: 工业配方单、食谱 SOP、食品科学研究、生产批记录、厨师食谱、烹饪手册、R&D 实验规程。

    模板用于提取和映射具有精确时间和参数的顺序食品生产工序。支持食谱标准化、工序优化以及烹饪和工业食品环境中的知识转移。

    使用示例:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> embedder = OpenAIEmbeddings()
        >>> recipe = RecipeProcessGraph(llm_client=llm, embedder=embedder)
        >>> process = "步骤 1：将蛋和糖混合 5 分钟。步骤 2：加热至 175°C"
        >>> recipe.feed_text(process)
        >>> recipe.show()
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
        初始化食谱工序图谱模板。

        Args:
            llm_client (BaseChatModel): 用于状态和步骤提取的 LLM。
            embedder (Embeddings): 用于去重的嵌入模型。
            extraction_mode (str): "one_stage" 或 "two_stage"。
            chunk_size (int): 每个分块的最大字符数。
            chunk_overlap (int): 分块之间的重叠。
            max_workers (int): 并行处理工作线程数。
            verbose (bool): 是否启用进度日志。
            **kwargs: AutoTemporalGraph 的其他参数。
        """
        super().__init__(
            node_schema=IngredientState,
            edge_schema=ProcessingStep,
            node_key_extractor=lambda x: x.name.strip().lower(),
            edge_key_extractor=lambda x: x.step_id.strip(),
            nodes_in_edge_extractor=lambda x: (
                x.source_state.strip(),
                x.target_state.strip(),
            ),
            time_in_edge_extractor=lambda x: x.step_id.strip(),
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
        使用 OntoSight 可视化食谱工序时间线。

        Args:
            top_k_nodes_for_search (int): 检索的状态数。默认 3。
            top_k_edges_for_search (int): 检索的步骤数。默认 3。
            top_k_nodes_for_chat (int): 对话上下文中的状态数。默认 3。
            top_k_edges_for_chat (int): 对话上下文中的步骤数。默认 3。
        """

        def node_label_extractor(node: IngredientState) -> str:
            return f"{node.name} ({node.physical_state if node.physical_state else '未知'})"

        def edge_label_extractor(edge: ProcessingStep) -> str:
            temp = f" {edge.temperature}" if edge.temperature else ""
            return f"{edge.action} ({edge.duration}){temp}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
