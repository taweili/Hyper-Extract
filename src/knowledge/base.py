from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, Any, Dict, Type, List
from datetime import datetime
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate


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
        data_schema: Type[T],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        prompt: str = "",
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
        max_workers: int = 10,
        show_progress: bool = True,
    ):
        """
        初始化知识对象。

        :param data_schema: 数据 Schema 类（必须是 Pydantic BaseModel 子类）
        :param llm_client: LLM 客户端（用于提取和演化）
        :param embedder: 向量化器（用于语义搜索和相似度计算）
        :param prompt: 用户自定义的提示词（用于 extract）
        :param chunk_size: 长文本分块大小
        :param chunk_overlap: 分块重叠大小
        :param max_workers: 最大并发数（用于并发提取）
        :param show_progress: 是否显示进度信息
        """
        self._data_schema = data_schema
        self.llm_client = llm_client
        self.embedder = embedder
        self.prompt = prompt or self._default_prompt()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_workers = max_workers
        self.show_progress = show_progress

        # 初始化提示词模板和 LLM 链
        self.prompt_template = ChatPromptTemplate.from_template(f"{self.prompt}{{chunk_text}}")
        self.llm_with_schema = self.llm_client.with_structured_output(self._data_schema)
        self.llm_chain = self.prompt_template | self.llm_with_schema

        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ". ", "! ", "? ", " ", ""],
        )

        # 向量存储相关（使用 FAISS）
        self._index = None
        self._index_dirty: bool = True  # 标记索引是否需要重建

        # 内部状态：存储提取的知识
        self._data: T = self._data_schema()
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    @staticmethod
    def _default_prompt() -> str:
        """默认提取提示词"""
        return (
            "You are an expert knowledge extraction assistant. "
            "Your task is to carefully analyze the following text and extract structured information "
            "according to the specified schema. Be precise, comprehensive, and faithful to the source text. "
            "Extract all relevant details without adding information not present in the text.\n\n"
            "### Source Text:\n"
        )

    # ==================== 数据管理 ====================

    @property
    def data_schema(self) -> Type[T]:
        """
        返回当前知识类使用的 Schema 类。

        :return: Pydantic Schema 类
        """
        return self._data_schema

    @property
    def data(self) -> T:
        """
        获取所有存储的知识（只读）。

        :return: 内部知识数据
        """
        return self._data

    @abstractmethod
    def clear(self):
        """清空所有知识。"""
        pass

    # ==================== 提取与聚合 ====================

    @abstractmethod
    def extract(self, text: str, *, append_mode: bool = False) -> T:
        """
        主提取方法 - 自动处理长文本分块、提取、聚合。

        流程：
        1. 根据 append_mode 决定是否清空现有数据
        2. 判断文本长度，决定是否分块
        3. 对每个块进行提取
        4. 调用 merge() 将提取结果聚合到 self._data
        5. 返回提取到的结果

        :param text: 输入文本（可以是短文本或长文本）
        :param append_mode: 是否累积模式（默认 False）
            - False（默认）: 替换模式 - 先清空现有知识，再提取新数据
            - True: 累积模式 - 保留现有知识，合并新数据
        :return: 提取到的知识数据
        """
        pass

    @abstractmethod
    def merge(self, data_list: List[T]) -> T:
        """
        将多个提取结果合并到内部状态 self._data。

        职责：去重、合并、冲突解决。
        子类必须实现此方法.

        :param data_list: 从各个块提取的知识列表
        :return: 合并后的知识数据
        """
        pass

    # ==================== 演化 ====================

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

    # ==================== 索引与查询 ====================

    @abstractmethod
    def build_index(self):
        """
        构建或重建向量索引。

        子类必须实现此方法，定义如何构建向量索引。
        使用 FAISS 作为向量存储后端。
        """
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> List[Any]:
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
