from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, Any, Dict, Type, List
from datetime import datetime
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings


T = TypeVar("T", bound=BaseModel)


# ===================== 知识类 (Knowledge) =====================


class BaseKnowledge(ABC, Generic[T]):
    """
    统一的知识基类 - 集提取、存储、聚合、演化于一体。

    职责：
    1. 从文本中提取结构化知识（extract）
    2. 自动处理长文本分块
    3. 存储和聚合提取的知识
    4. 演化优化内部知识
    5. 序列化与反序列化
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        prompt: str = "",
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
        max_workers: int = 10,
        show_progress: bool = True,
        **kwargs,
    ):
        """
        初始化知识对象。

        :param llm_client: LLM 客户端（用于提取和演化）
        :param embedder: 向量化器（用于语义搜索和相似度计算）
        :param prompt: 用户自定义的提示词（用于 extract）
        :param chunk_size: 长文本分块大小
        :param chunk_overlap: 分块重叠大小
        :param max_workers: 最大并发数（用于并发提取）
        :param show_progress: 是否显示进度信息
        """
        self.llm_client = llm_client
        self.embedder = embedder
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.prompt = prompt
        self.max_workers = max_workers
        self.show_progress = show_progress

        # 向量存储相关（使用 FAISS）
        self._index = None
        self._index_dirty: bool = True  # 标记索引是否需要重建

        # 内部状态：存储提取的知识
        self._data: T = self._init_data()
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "total_extractions": 0,
            "total_chunks_processed": 0,
        }

    @property
    def schema_class(self) -> Type[T]:
        """
        返回当前知识类使用的 Schema 类。
        子类可覆盖此属性，或在泛型参数中指定。
        """
        # 默认实现：从泛型参数推导（仅当子类未覆盖时）
        raise NotImplementedError("schema_class must be implemented by subclass")

    @abstractmethod
    def _init_data(self) -> T:
        """
        初始化内部数据结构。

        :return: 初始化的知识容器
        """
        return self.schema_class()

    # ==================== 向量索引管理（模板方法模式）====================

    @abstractmethod
    def build_index(self):
        """
        构建或重建向量索引。

        子类必须实现此方法，定义如何构建向量索引。
        使用 FAISS 作为向量存储后端。
        """
        pass

    @abstractmethod
    def clear(self):
        """清空所有知识。"""
        pass

    # ==================== 核心方法：extract ====================

    @abstractmethod
    def extract(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        主提取方法 - 自动处理长文本分块、提取、聚合。

        流程：
        1. 判断文本长度，决定是否分块
        2. 对每个块调用 _extract_chunk() 进行提取
        3. 调用 merge() 将提取结果聚合到 self._data
        4. 返回提取统计信息

        :param text: 输入文本（可以是短文本或长文本）
        :return: 提取统计信息 {"chunks_processed": 3, "items_extracted": 15, ...}
        """
        pass

    # ==================== 存储与聚合 ====================

    @abstractmethod
    def merge(self, items: List[T], **kwargs) -> Dict[str, Any]:
        """
        将多个提取结果合并到内部状态 self._data。

        职责：去重、合并、冲突解决。
        子类必须实现此方法。

        :param items: 从各个块提取的知识列表
        :return: 合并统计信息 {"items_added": 10, "duplicates_removed": 2, ...}
        """
        pass

    # ==================== 查询接口 ====================

    @property
    def data(self) -> T:
        """
        获取所有存储的知识（只读）。

        :return: 内部知识数据
        """
        return self._data

    @abstractmethod
    def search(self, query: str, top_k: int = 10, **kwargs) -> List[Any]:
        """
        语义搜索知识。

        默认实现：
        1. 确保索引已构建（调用 build_index）
        2. 使用 vector_store.similarity_search 进行检索
        3. 从 Document.metadata 恢复原始数据结构

        子类可覆盖此方法实现自定义搜索逻辑。

        :param query: 查询字符串
        :param top_k: 返回结果数
        :return: 相关知识列表
        """
        pass

    @abstractmethod
    def size(self) -> int:
        """
        返回知识点数量。
        子类必须实现此方法。

        :return: 知识点数量
        """
        pass

    # ==================== 演化 ====================

    @abstractmethod
    def evolve(self, **kwargs) -> T:
        """
        演化内部知识。
        子类必须实现此方法。

        职责：
        - 推理隐含关系
        - 剪枝低置信度节点
        - 聚类优化
        - 知识补全

        :return: 新的内部知识数据
        """
        pass

    # ==================== 序列化 ====================

    @abstractmethod
    def dump(self, folder_path: str | Path) -> Any:
        """
        导出知识到指定文件夹。
        子类必须实现此方法。

        需要保存到文件夹内：
        1. 结构化数据 (self._data) - 保存为 JSON 文件
        2. 向量索引 (self._index) - FAISS 索引文件

        :param folder_path: 目标文件夹路径
        :return: 序列化后的数据
        """
        pass

    @abstractmethod
    def load(self, folder_path: str | Path, **kwargs):
        """
        从文件夹加载知识。
        子类必须实现此方法。

        需要从文件夹加载：
        1. 结构化数据 (self._data) - 从 JSON 文件加载
        2. 向量索引 (self._index) - 从 FAISS 索引文件加载

        :param folder_path: 文件夹路径
        """
        pass
