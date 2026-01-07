from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any, Optional, Dict
from pydantic import BaseModel

# T 是具体的数据 Schema (如 GraphSchema, HypergraphSchema)
T = TypeVar("T", bound=BaseModel)

class BaseKnowledge(ABC, Generic[T]):
    """
    智能知识容器基类。
    
    核心特性：
    1. 持有 LLM 实例：它是"活"的，知道如何利用 LLM 处理数据。
    2. 极简生命周期：Extract (摄入) -> Evolve (演化) -> Dump (产出)。
    """

    def __init__(self, llm: Any, initial_data: Optional[T] = None):
        """
        :param llm: LangChain 的 ChatModel 实例或兼容的 Driver 包装器。
        :param initial_data: 可选的初始数据。
        """
        self.llm = llm
        self.data: T = initial_data or self._get_schema_class()()
        self.metadata: Dict[str, Any] = {}

    @property
    @abstractmethod
    def _get_schema_class(self) -> type[T]:
        """[配置] 定义该容器持有的数据结构类"""
        pass

    # ================= 1. 摄入 (Extract) [必须实现] =================

    @abstractmethod
    async def extract(self, text: str, **kwargs):
        """
        核心摄入逻辑。
        
        职责：
        1. 构造 Prompt。
        2. 调用 self.llm 对 text 进行分析。
        3. 解析返回结果。
        4. 【重要】将结果 merge/update 到 self.data 中。
        
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

    # ================= 3. 产出 (Dump) [必须实现] =================

    @abstractmethod
    def dump(self, format: str = "json") -> Any:
        """
        将内部知识导出为标准格式。
        """
        pass
    
    # ------------------ 通用辅助方法 ------------------
    
    def clear(self):
        """清空知识库"""
        self.data = self._get_schema_class()()
