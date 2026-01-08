from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any, Dict
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings


# T 是具体的数据 Schema (如 GraphSchema, HypergraphSchema)
T = TypeVar("T", bound=BaseModel)


class BaseKnowledge(ABC, Generic[T]):
    """
    智能知识容器基类。

    核心特性：
    1. 持有 LLM 实例：它是"活"的，知道如何利用 LLM 处理数据。
    2. 极简生命周期：Extract -> Evolve -> Search -> Dump。
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        storage: str = "memory",
        **kwargs,
    ):
        """
        :param llm_client: LangChain 的 ChatModel 实例或兼容的 LLM 客户端。
        :param embedder: LangChain 的 Embeddings 实例或兼容的向量化客户端。
        :param storage: 后端存储类型。默认为 "memory"，也可以是数据库类型如 "postgres"、"mongodb" 等。
        """
        self.llm_client = llm_client
        self.embedder = embedder
        self.storage = storage
        self.metadata: Dict[str, Any] = {}

    # ================= 1. 提取 (Extract) [核心方法] =================

    @abstractmethod
    async def extract(self, text: str, **kwargs) -> T:
        """
        核心提取逻辑。从原始数据中提取对应类型的知识。

        职责：
        1. 构造 Prompt。
        2. 调用 self.llm 对 text 进行分析。
        3. 解析返回结果。
        4. 【重要】返回提取出的知识对象。

        注意：这里的实现可以很复杂，可以包含 '提取' -> '清洗' -> '去重合并' 的全过程。
        """
        pass

    # ================= 2. 演化 (Evolve) [可选实现] =================

    async def evolve(self, **kwargs):
        """
        知识演化/内省逻辑。

        默认行为：什么都不做（并非所有知识都需要演化）。

        子类用途：
        - 图卷积 (Convolution)：传播节点属性。
        - 聚类 (Clustering)：发现社区。
        - 剪枝 (Pruning)：删除置信度低的边。
        - 推理 (Reasoning)：基于现有知识生成新知识。
        """
        pass

    # ================= 3. 查询与搜索 (Search) =================

    @abstractmethod
    async def search(self, query: str, **kwargs) -> Any:
        """
        在当前已有的知识中进行查询。
        可以是语义搜索、关系查询或简单条件过滤。
        """
        pass

    # ================= 4. 读写操作 (Load & Dump) =================

    @abstractmethod
    def load(self, data: Any, **kwargs):
        """
        从外部恢复知识。数据可以是 dict, json string 或文件路径。
        """
        pass

    @abstractmethod
    def dump(self, format: str = "json") -> Any:
        """
        将内部知识导出为标准格式。
        """
        pass
