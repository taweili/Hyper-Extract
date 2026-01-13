"""
基础知识模式实现。

包含两种核心模式：
- UnitKnowledge: 单元知识模式（适用于摘要、元数据等）
- ListKnowledge: 列表知识模式（适用于实体、事件等列表提取）
"""

import json
from typing import List, Any, Type, TypeVar, Generic, TYPE_CHECKING
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field, create_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from .base import BaseKnowledge, T

try:
    from src.config import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

# ==================== 两种基础知识模式 ====================

# UnitKnowledge: 单元知识模式


class UnitKnowledge(BaseKnowledge[T]):
    """
    单元知识模式 (Unit Knowledge Pattern) - 适用于任何 Pydantic Schema。

    特点：
    - 针对整篇文档提取 **唯一** 的一个结构化对象
    - 合并策略：字段级更新 (Upsert/Patch)
    - 索引策略：对对象的每个非空字段建立索引
    - 使用 LangChain 原生批处理（batch_as_completed）
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
        **kwargs,
    ):
        """
        :param data_schema: 数据 Schema 类（必须是 Pydantic BaseModel 子类）
        :param llm_client: LLM 客户端
        :param embedder: 向量化器
        :param prompt: 自定义提示词
        :param chunk_size: 长文本分块大小
        :param chunk_overlap: 分块重叠大小
        :param max_workers: 最大并发数
        :param show_progress: 是否显示进度
        """
        super().__init__(
            data_schema,
            llm_client,
            embedder,
            prompt=prompt or self._default_prompt(),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            show_progress=show_progress,
            **kwargs,
        )

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

    def clear(self):
        """清空所有知识"""
        self.metadata["updated_at"] = datetime.now()
        self._data = self.data_schema()
        self._index = None
        self._index_dirty = True
        logger.info("Cleared all knowledge")

    # ==================== 提取与聚合 ====================

    def extract(self, text: str, *, merge_mode: bool = False) -> T:
        """
        使用 LangChain 原生批处理提取知识

        :param text: 输入文本
        :param merge_mode: 合并模式（默认 False）
            - False: 替换模式 - 清空后仅使用新提取的数据
            - True: 累积模式 - 将现有数据与新数据合并
        :return: 提取到的知识数据
        """
        start_time = datetime.now()

        # 替换模式：先清空
        if not merge_mode:
            self.clear()

        # 判断是否需要分块
        if len(text) <= self.chunk_size:
            # 短文本：直接提取
            if self.show_progress:
                logger.info(f"Processing single text (length: {len(text)})...")

            extracted_data = self.llm_chain_extract.invoke({"chunk_text": text})
            extracted_data_list = [extracted_data]

        else:
            # 长文本：分块提取
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks")

            if self.show_progress:
                logger.info(f"Processing {len(chunks)} chunk(s)...")

            inputs = [{"chunk_text": chunk} for chunk in chunks]
            extracted_data_list = self.llm_chain_extract.batch(
                inputs, config={"max_concurrency": self.max_workers}
            )

        if self.show_progress:
            logger.info(f"Extracted {len(extracted_data_list)} chunks")

        logger.info("Merging extracted knowledge...")
        if merge_mode:
            extracted_data_list.insert(0, self.data)

        self._data = self.merge(extracted_data_list)

        # 统一修改状态
        self._index_dirty = True
        self.metadata["updated_at"] = datetime.now()

        logger.info("Knowledge extraction completed")
        logger.info(
            f"Duration: {(datetime.now() - start_time).total_seconds():.2f} seconds"
        )
        return self.data

    def merge(self, data_list: List[T]) -> T:
        """
        纯数据合并方法 - 字段级更新策略。

        合并策略：第一次提取的结果为准，后续只能补充缺失字段。
        使用 model_copy(update=...) 实现第一次优先合并。

        :param data_list: 需要合并的数据列表
        :return: 合并后的知识数据（新对象）
        """
        result = data_list[0].model_copy()

        for item in data_list[1:]:
            result = item.model_copy(update=result.model_dump(exclude_none=True))

        return result

    # ==================== 查询与索引 ====================

    def build_index(self):
        """从 _data 的所有字段构建索引"""
        # 检查是否有数据
        if self.size() == 0:
            logger.warning("No data to index")
            return

        if not self._index_dirty and self._index is not None:
            return

        documents = []
        for field_name in self.data_schema.model_fields:
            field_value = getattr(self._data, field_name)
            if field_value is not None:
                documents.append(
                    Document(
                        page_content=field_name,
                        metadata={"raw": {field_name: field_value}},
                    )
                )

        self._index = FAISS.from_documents(documents, self.embedder)
        self._index_dirty = False
        logger.info(f"Built FAISS index with {len(documents)} documents")

    def search(self, query: str, top_k: int = 3) -> List[Any]:
        """
        搜索所有列表字段。

        :param query: 查询字符串
        :param top_k: 返回结果数
        :return: 相关知识列表（单个 item，不是容器）
        """
        # 检查是否有数据
        if self.size() == 0:
            logger.warning("No items to search")
            return []

        if self._index is None or self._index_dirty:
            raise Exception(
                "Index is not built or dirty, please build the index first."
            )

        docs = self._index.similarity_search(query, k=top_k)

        # 恢复原始对象
        results = []
        for doc in docs:
            try:
                raw_data = doc.metadata["raw"]  # {field_name: field_value}
                results.append(raw_data)
            except Exception as e:
                logger.warning(f"Failed to restore item: {e}")

        logger.info(f"Found {len(results)} results for query: {query[:50]}...")
        return results

    def size(self) -> int:
        """返回字段数"""
        return len(self.data_schema.model_fields)

    # ==================== 序列化 ====================

    def dump(self, folder_path: str | Path):
        """
        导出知识到指定文件夹。

        保存到文件夹内：
        1. 结构化数据 (self._data) - 保存为 state.json
        2. 向量索引 (self._index) - FAISS 索引文件

        :param folder_path: 目标文件夹路径
        """

        folder = Path(folder_path)
        if folder.exists() and folder.is_file():
            raise Exception("Folder path is a file, please provide a folder path.")

        if not folder.exists():
            logger.info(f"Creating folder: {folder}")
            folder.mkdir(parents=True, exist_ok=True)

        try:
            # 1. 保存结构化数据
            data = {
                "schema_name": self.data_schema.__name__,
                "data_schema": self.data_schema.model_json_schema(),
                "data": self.data.model_dump(),
                "metadata": {
                    k: str(v) if isinstance(v, datetime) else v
                    for k, v in self.metadata.items()
                },
            }

            json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)
            data_file = folder / "state.json"
            with open(data_file, "w", encoding="utf-8") as f:
                f.write(json_str)
            logger.info(f"Saved data to {data_file}")

            # 2. 保存向量索引
            if self._index is not None:
                index_path = str(folder / "faiss_index")
                self._index.save_local(index_path)
                logger.info(f"Saved FAISS index to {index_path}")
            else:
                logger.warning("No index to save")

        except Exception as e:
            logger.error(f"Failed to dump knowledge: {e}")

    def load(self, folder_path: str | Path):
        """
        从文件夹加载知识。

        从文件夹加载：
        1. 结构化数据 (self._data) - 从 state.json 加载
        2. 向量索引 (self._index) - 从 FAISS 索引文件加载

        :param folder_path: 文件夹路径
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            raise ValueError(f"Folder does not exist: {folder_path}")

        # 1. 加载结构化数据
        data_file = folder / "state.json"
        if not data_file.is_file():
            raise ValueError(f"Data file not found: {data_file}")

        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Loaded data from {data_file}")

        self._data = self.data_schema.model_validate(data.get("data", {}))

        # 更新元数据
        if "metadata" in data:
            self.metadata.update(data["metadata"])
        self.metadata["updated_at"] = datetime.now()

        # 2. 加载向量索引
        index_path = str(folder / "faiss_index")
        if Path(index_path).exists():
            try:
                from langchain_community.vectorstores import FAISS

                self._index = FAISS.load_local(
                    index_path, self.embedder, allow_dangerous_deserialization=True
                )
                self._index_dirty = False
                logger.info(f"Loaded FAISS index from {index_path}")
            except Exception as e:
                logger.warning(f"Failed to load FAISS index: {e}")
                self._index = None
                self._index_dirty = True
        else:
            logger.warning("No index file found, will rebuild on next search")
            self._index = None
            self._index_dirty = True

        logger.info(f"Loaded knowledge successfully with {self.size()} fields")


# ==================== 列表知识模式 ===================

Item = TypeVar("Item", bound=BaseModel)


class ItemListSchema(BaseModel, Generic[Item]):
    """列表容器的通用 Schema"""

    items: List[Item] = Field(default_factory=list, description="Item list")


class ListKnowledge(BaseKnowledge[ItemListSchema[Item]], Generic[Item]):
    """
    列表知识模式 (List Collection Pattern)。

    特点：
    - 针对整篇文档提取 **一组** 对象列表（如实体、事件、引用等）
    - 合并策略：追加 (Append) + 基础去重（可由子类扩展）
    - 索引策略：对列表中的每个 Item 独立建立索引

    与 UnitKnowledge 的区别：
    - UnitKnowledge: 提取单个结构化对象（如摘要、元数据）
    - ListKnowledge: 提取多个独立对象的列表（如实体列表、事件列表）
    """

    if TYPE_CHECKING:
        # 类型检查时使用泛型版本，保持完整的类型提示
        item_list_schema: Type[ItemListSchema[Item]]

    def __init__(
        self,
        item_schema: Type[Item],
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
        :param item_schema: 列表中单个元素的 Schema 类
        :param llm_client: LLM 客户端
        :param embedder: 向量化器
        :param prompt: 自定义提示词
        :param chunk_size: 长文本分块大小
        :param chunk_overlap: 分块重叠大小
        :param max_workers: 最大并发数
        :param show_progress: 是否显示进度
        """
        self.item_schema = item_schema

        container_name = f"{item_schema.__name__}List"
        self.item_list_schema = create_model(
            container_name,
            items=(List[item_schema], Field(default_factory=list, description="Item list"))
        )

        super().__init__(
            data_schema=self.item_list_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt or self._default_prompt(),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            show_progress=show_progress,
            **kwargs,
        )

    @staticmethod
    def _default_prompt() -> str:
        """默认列表提取提示词"""
        return (
            "You are an expert knowledge extraction assistant. "
            "Extract all relevant items from the text into a list. "
            "Be comprehensive and ensure no item is missed. "
            "Extract all items without adding information not present in the text.\n\n"
            "### Source Text:\n"
        )

    @property
    def items(self) -> List[Item]:
        """获取内部列表"""
        return getattr(self._data, "items", [])

    def clear(self):
        """清空所有列表项"""
        self.metadata["updated_at"] = datetime.now()
        self._data = self.item_list_schema(items=[])
        self._index = None
        self._index_dirty = True
        logger.info("Cleared list knowledge")

    def extract(self, text: str, *, merge_mode: bool = False) -> ItemListSchema:
        """
        使用 LangChain 原生批处理提取列表

        :param text: 输入文本
        :param merge_mode: 合并模式（默认 False）
            - False: 替换模式 - 清空后仅使用新提取的数据
            - True: 累积模式 - 将现有数据与新数据合并
        :return: 提取到的 items 列表
        """
        start_time = datetime.now()

        # 替换模式：先清空
        if not merge_mode:
            self.clear()

        # 判断是否需要分块
        if len(text) <= self.chunk_size:
            # 短文本：一次性提取
            if self.show_progress:
                logger.info(f"Processing single text (length: {len(text)})...")

            extracted_data = self.llm_chain_extract.invoke({"chunk_text": text})
            extracted_data_list = [extracted_data]

        else:
            # 长文本：分块提取
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks")

            if self.show_progress:
                logger.info(f"Processing {len(chunks)} chunk(s)...")

            inputs = [{"chunk_text": chunk} for chunk in chunks]
            extracted_data_list = self.llm_chain_extract.batch(
                inputs, config={"max_concurrency": self.max_workers}
            )

        if self.show_progress:
            logger.info(f"Extracted {len(extracted_data_list)} chunks")

        logger.info("Merging extracted knowledge...")
        if merge_mode:
            extracted_data_list.insert(0, self.data)

        self._data = self.merge(extracted_data_list)

        # 统一修改状态
        self._index_dirty = True
        self.metadata["updated_at"] = datetime.now()

        logger.info("Knowledge extraction completed")
        logger.info(
            f"Duration: {(datetime.now() - start_time).total_seconds():.2f} seconds"
        )
        return self.items

    def merge(self, data_list: List[ItemListSchema]) -> ItemListSchema:
        """
        纯数据合并方法 - 列表追加策略。

        合并策略：收集所有容器对象中的 items，合并到一个大列表中。
        子类可以重写此方法实现更复杂的去重逻辑（如 EntityKnowledge）。

        :param data_list: 需要合并的容器对象列表
        :return: 合并后的知识数据（新的 ItemListSchema 对象）
        """
        all_items = []

        # 收集所有 items
        for data in data_list:
            copied_data = data.model_copy(deep=True)
            all_items.extend(copied_data.items)

        # 返回新的对象
        return self.item_list_schema(items=all_items)

    def build_index(self):
        """为列表中的每个 Item 构建独立索引"""
        items = self.items
        if not items:
            logger.warning("No items to index")
            return

        if not self._index_dirty and self._index is not None:
            return

        documents = []
        for idx, item in enumerate(items):
            # 序列化每个 Item 为 Document
            content = item.model_dump_json()  # 使用 JSON 字符串作为内容
            documents.append(
                Document(
                    page_content=content,
                    metadata={"raw": item.model_dump(), "index": idx},
                )
            )

        if documents:
            try:
                from langchain_community.vectorstores import FAISS

                self._index = FAISS.from_documents(documents, self.embedder)
                self._index_dirty = False
                logger.info(f"Built FAISS index with {len(documents)} items")
            except ImportError:
                logger.error("FAISS not available. Install with: pip install faiss-cpu")
                raise

    def search(self, query: str, top_k: int = 3) -> List[Any]:
        """
        搜索列表中的 items。

        :param query: 查询字符串
        :param top_k: 返回结果数
        :return: 相关的 item 列表
        """
        if not self.items:
            logger.warning("No items to search")
            return []

        if self._index is None:
            raise Exception("Vector store not initialized")

        docs = self._index.similarity_search(query, k=top_k)
        results = []
        for doc in docs:
            # 尝试还原为对象
            try:
                raw = doc.metadata.get("raw", {})
                item = self.item_schema.model_validate(raw)
                results.append(item)
            except Exception as e:
                logger.warning(f"Failed to restore item: {e}")
                results.append(doc.metadata.get("raw"))

        logger.info(f"Found {len(results)} results for query: {query[:50]}...")
        return results

    def size(self) -> int:
        """返回列表中的元素数量"""
        return len(self.items)

    def dump(self, folder_path: str) -> Any:
        """
        导出知识到指定文件夹（复用 UnitKnowledge 的实现）。
        容器本质也是 BaseModel，可以直接使用相同的序列化逻辑。
        """
        from pathlib import Path

        folder = Path(folder_path)
        folder.mkdir(parents=True, exist_ok=True)

        # 1. 保存结构化数据
        data = {
            "schema_name": self.item_list_schema.__name__,
            "item_schema_name": self.item_schema.__name__,
            "item_schema": self.item_schema.model_json_schema(),
            "data": self.data.model_dump(),
            "metadata": {
                k: str(v) if isinstance(v, datetime) else v
                for k, v in self.metadata.items()
            },
        }

        json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        data_file = folder / "state.json"
        with open(data_file, "w", encoding="utf-8") as f:
            f.write(json_str)
        logger.info(f"Saved data to {data_file}")

        # 2. 保存向量索引
        if self._index is not None:
            index_path = str(folder / "faiss_index")
            self._index.save_local(index_path)
            logger.info(f"Saved FAISS index to {index_path}")
        else:
            logger.warning("No index to save")

        return json_str

    def load(self, folder_path: str, **kwargs):
        """从文件夹加载知识"""
        from pathlib import Path

        folder = Path(folder_path)
        if not folder.is_dir():
            raise ValueError(f"Folder does not exist: {folder_path}")

        # 1. 加载结构化数据
        data_file = folder / "state.json"
        if not data_file.is_file():
            raise ValueError(f"Data file not found: {data_file}")

        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Loaded data from {data_file}")

        self._data = self.item_list_schema.model_validate(data.get("data", {}))

        # 更新元数据
        if "metadata" in data:
            self.metadata.update(data["metadata"])
        self.metadata["updated_at"] = datetime.now()

        # 2. 加载向量索引
        index_path = str(folder / "faiss_index")
        if Path(index_path).exists():
            try:
                from langchain_community.vectorstores import FAISS

                self._index = FAISS.load_local(
                    index_path, self.embedder, allow_dangerous_deserialization=True
                )
                self._index_dirty = False
                logger.info(f"Loaded FAISS index from {index_path}")
            except Exception as e:
                logger.warning(f"Failed to load FAISS index: {e}")
                self._index = None
                self._index_dirty = True
        else:
            logger.warning("No index file found, will rebuild on next search")
            self._index = None
            self._index_dirty = True

        logger.info(f"Loaded knowledge successfully with {self.size()} items")

# Set Knowledge
