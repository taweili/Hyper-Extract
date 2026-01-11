"""
通用 Generic 实现。

包含基于 BaseKnowledge 的具体实现。
"""

import json
from typing import List, Dict, Any, Type
from datetime import datetime
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

from .base import BaseKnowledge, T

try:
    from src.config import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class GenericKnowledge(BaseKnowledge[T]):
    """
    通用知识实现 - 适用于任何 Pydantic Schema。

    特点：
    - 使用 LLM 的 with_structured_output 进行提取
    - 智能合并：列表字段 append + 去重，其他字段 LLM 合并
    - 支持向量化语义搜索
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

    def extract(self, text: str) -> T:
        """使用 LangChain 原生批处理提取知识"""
        start_time = datetime.now()

        # 判断是否需要分块
        if len(text) <= self.chunk_size:
            # 短文本：一次性提取
            if self.show_progress:
                logger.info(f"Processing single text (length: {len(text)})...")
            self._data = self.llm_chain.invoke({"chunk_text": text})
            self._index_dirty = True
        else:
            # 长文本：分块提取
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks")

            if self.show_progress:
                logger.info(f"Processing {len(chunks)} chunk(s)...")

            inputs = [{"chunk_text": chunk} for chunk in chunks]
            extracted_data_list = self.llm_chain.batch(
                inputs, config={"max_concurrency": self.max_workers}
            )
            if self.show_progress:
                logger.info(f"Extracted {len(extracted_data_list)} chunks")

            logger.info("Merging extracted knowledge...")
            self.merge(extracted_data_list)

        # 更新元数据
        self.metadata["updated_at"] = datetime.now()

        logger.info("Knowledge extraction completed")
        logger.info(f"Duration: {(datetime.now() - start_time).total_seconds():.2f} seconds")
        return self.data

    def merge(self, data_list: List[T]) -> T:
        """
        增量合并：第一次提取的结果为准。

        使用 model_copy(update=...) 实现第一次优先合并。

        :param data_list: 从各 chunk 提取的结果列表
        :return: 合并后的知识数据
        """

        self._data = data_list[0].model_copy()

        for item in data_list[1:]:
            self._data = item.model_copy(
                update=self._data.model_dump(exclude_none=True)
            )

        self._index_dirty = True
        return self.data

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

        try:
            from langchain_community.vectorstores import FAISS

            self._index = FAISS.from_documents(documents, self.embedder)
            self._index_dirty = False
            logger.info(f"Built FAISS index with {len(documents)} documents")
        except ImportError:
            logger.error("FAISS not available. Install with: pip install faiss-cpu")
            raise

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

        if self._index is None:
            raise Exception("Vector store not initialized")

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

    def dump(self, folder_path: str) -> Any:
        """
        导出知识到指定文件夹。

        保存到文件夹内：
        1. 结构化数据 (self._data) - 保存为 data.json
        2. 向量索引 (self._index) - FAISS 索引文件

        :param folder_path: 目标文件夹路径
        :return: 序列化后的数据（JSON 字符串）
        """
        from pathlib import Path

        folder = Path(folder_path)
        folder.mkdir(parents=True, exist_ok=True)

        # 1. 保存结构化数据
        data = {
            "schema_name": self.data_schema.__name__,
            "data": self.data.model_dump(),
            "metadata": {
                k: str(v) if isinstance(v, datetime) else v
                for k, v in self.metadata.items()
            },
        }

        json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        data_file = folder / "data.json"
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
        """
        从文件夹加载知识。

        从文件夹加载：
        1. 结构化数据 (self._data) - 从 data.json 加载
        2. 向量索引 (self._index) - 从 FAISS 索引文件加载

        :param folder_path: 文件夹路径
        """
        from pathlib import Path

        folder = Path(folder_path)
        if not folder.is_dir():
            raise ValueError(f"Folder does not exist: {folder_path}")

        # 1. 加载结构化数据
        data_file = folder / "data.json"
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
