from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types.graph import AutoGraph

# ==============================================================================
# 1. Schema 定义
# ==============================================================================


class Species(BaseModel):
    """生态系统中的生物体。"""

    name: str = Field(description="生物的学名或常用名。")
    category: str = Field(
        description="分类学分类：'Mammal'(哺乳动物), 'Bird'(鸟类), 'Insect'(昆虫), 'Plant'(植物), 'Microorganism'(微生物)等。"
    )
    protection_level: Optional[str] = Field(
        None, description="保护等级：'Endangered'(濒危), 'Vulnerable'(易危), 'Least Concern'(无危)等。"
    )


class Interaction(BaseModel):
    """两个物种之间的生物互作关系。"""

    source: str = Field(description="初始物种（捕食者、竞争者等）。")
    target: str = Field(description="接收物种（猎物、竞争者、寄主等）。")
    interaction_type: str = Field(
        description="互作类型：'predation'(捕食), 'parasitism'(寄生), 'mutualism'(互利共生), 'commensalism'(偏利共生), 'competition'(竞争), 'symbiosis'(共生)。"
    )
    detail: Optional[str] = Field(
        None, description="互作的具体细节（如频率、季节性规律、生态影响等）。"
    )


# ==============================================================================
# 2. Prompts
# ==============================================================================

_PROMPT = """
你是一位生态学和生物多样性专家。
你的任务是从科学文献、野外调查报告或自然纪录片中提取生物互作网络。

指导原则：
1. 识别文本中提到的所有生物，并按类别分类（物种类型）。
2. 提取生物之间的关系（捕食、寄生、竞争、互利共生等）。
3. 对于每个互作，捕捉互作类型和具体的生态学细节（时间、频率、条件）。
4. 保持互作的方向性：例如"狮子捕食斑马"和"斑马躲避狮子"是不同的。
5. 如果提到了保护等级信息的，要进行记录。

输出格式：
- 每个物种应该是一个独立的实体，包括名称、类别和保护等级（如果有）。
- 每个互作应该清楚地表示源头（发起方生物）、目标（接收方生物）和互作类型。
"""

_NODE_PROMPT = """
你是一位生态学和生物多样性专家。
你的任务是在第一个提取阶段只提取文本中的物种和生物体，不提取它们之间的互作。
专注于识别文本中提到的所有不同生物体。

指导原则：
1. 列出文本中提到的所有物种、生物体或种群。
2. 对于每个生物体，捕获：名称、分类（例如捕食者、猎物、植物、分解者）、以及保护状态（如有）。
3. 避免重复：如果"狮子"和"非洲狮"指的是同一物种，统一为最具体的名称。
4. 忽略模糊的指代；仅提取明确提到的生物体。

输出格式：
- 每个生物体应为不同的节点，具有清晰的名称、分类和状态。
"""

_EDGE_PROMPT = """
你是一位分析物种互作的生态学家。
你的任务是在第二个提取阶段只提取已给定物种间的生物关系。
你将获得一份已提取物种（节点）的列表。你的工作是识别它们之间的互作。

指导原则：
1. 根据确认的物种列表，找出文本中提到的所有两两互作关系。
2. 对于每个互作，捕获：源物种、目标物种、互作类型（捕食、共生、竞争等）和详细信息。
3. 保留方向性："A 捕食 B" 是捕食（A→B），不同于 "B 躲避 A"。
4. 仅提取连接已给定物种的互作；忽略不在提供列表中的物种提及。
5. 包括生态学背景（季节性、频率、条件）作为详细信息。

输出格式：
- 每个互作是一条边：源物种 → 目标物种，包含关系类型和详细信息。
"""

# ==============================================================================
# 3. 模板类
# ==============================================================================


class SpeciesInteractionNetwork(AutoGraph[Species, Interaction]):
    """
    物种生态互作知识图谱模板。

    将科学文献和野外研究转化为结构化的互作网络，
    使得生态系统生物多样性和食物链分析成为可能。

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> llm = ChatOpenAI(model="gpt-4")
        >>> embedder = OpenAIEmbeddings()
        >>> 
        >>> network = SpeciesInteractionNetwork(llm_client=llm, embedder=embedder)
        >>> text = "狮子在非洲草原狩猎斑马。寄生蜂被鸟类捕食。"
        >>> network.feed_text(text)
        >>> network.show()  # 可视化物种互作网络
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
        """初始化物种互作网络模板。

        Args:
            llm_client (BaseChatModel)：用于物种和互作关系提取的语言模型客户端。
            embedder (Embeddings)：用于物种节点和互作边向量索引的嵌入模型。
            extraction_mode (str, optional)：提取策略。默认为 "one_stage"。
                - "one_stage"：同时提取物种和互作（更快）。
                - "two_stage"：先提取物种，再提取互作（准确度更高）。
            chunk_size (int, optional)：每个文本块的最大字符数。默认为 2048。
            chunk_overlap (int, optional)：块之间的重叠字符数，用于保持上下文连贯性。默认为 256。
            max_workers (int, optional)：并发提取的最大工作进程数。默认为 10。
            verbose (bool, optional)：如果为 True，则打印详细的提取进度日志。默认为 False。
            **kwargs：传递给 AutoGraph 基类的其他参数。
        """
        super().__init__(
            node_schema=Species,
            edge_schema=Interaction,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.interaction_type.lower()})-->{x.target.strip()}",
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
        """可视化物种互作网络用于生态分析。

        使用 OntoSight 可视化已提取的物种（节点）及其互作关系（边）。
        在内部定义物种的前端展示标签（名称 + 类别 + 保护等级）
        和互作关系标签（互作类型）。

        Args:
            top_k_nodes_for_search (int, optional)：搜索触发时要检索的物种节点数。默认为 3。
            top_k_edges_for_search (int, optional)：搜索触发时要检索的互作边数。默认为 3。
            top_k_nodes_for_chat (int, optional)：聊天触发时要检索的物种节点数。默认为 3。
            top_k_edges_for_chat (int, optional)：聊天触发时要检索的互作边数。默认为 3。
        """

        def node_label_extractor(node: Species) -> str:
            status = f" [{node.protection_level}]" if node.protection_level else ""
            return f"{node.name} ({node.category}){status}"

        def edge_label_extractor(edge: Interaction) -> str:
            return f"{edge.interaction_type}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
