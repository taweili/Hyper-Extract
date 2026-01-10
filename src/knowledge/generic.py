"""
通用 Generic 实现。

包含基于 BaseKnowledge 的具体实现。
"""

import json
import hashlib
from typing import List, Dict, Any, Optional, Type
from datetime import datetime
from pydantic import ValidationError
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

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
    - 基于 JSON 哈希进行去重
    - 支持向量化语义搜索
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        schema_class: Type[T],
        deduplication_strategy: str = "hash",
        **kwargs,
    ):
        """
        :param llm_client: LLM 实例
        :param embedder: 向量化器实例
        :param schema_class: Schema 类
        :param deduplication_strategy: 去重策略（"hash" 或 "semantic"）
        :param kwargs: 其他参数（prompt, max_workers, show_progress 等）
        """
        super().__init__(llm_client, embedder, **kwargs)
        self._schema_class = schema_class
        self.deduplication_strategy = deduplication_strategy
        self._items: List[T] = []  # 内部存储列表
        self._item_hashes: set = set()  # 用于基于哈希的去重

    @property
    def schema_class(self) -> Type[T]:
        """返回当前使用的 Schema 类"""
        return self._schema_class

    def build_index(self):
        """
        构建或重建向量索引（使用 FAISS）。
        """
        if not self._index_dirty and self._index is not None:
            return  # 索引已是最新
        
        # 1. 将 items 转为 Document 列表
        documents = []
        for i, item in enumerate(self._items):
            documents.append(Document(
                page_content=item.model_dump_json(),
                metadata={
                    "index": i,
                    "hash": self._compute_hash(item),
                    "raw": item.model_dump(),
                }
            ))
        
        if not documents:
            logger.warning("No documents to index")
            return
        
        # 2. 使用 FAISS 构建向量存储
        try:
            from langchain_community.vectorstores import FAISS
            self._index = FAISS.from_documents(
                documents=documents,
                embedding=self.embedder
            )
            self._index_dirty = False
            logger.info(f"Built FAISS index with {len(documents)} documents")
        except ImportError:
            logger.error("FAISS not available. Install with: pip install faiss-cpu")
            raise

    def extract(self, text: str, **kwargs) -> Dict[str, Any]:
        """主提取方法 - 自动处理长文本分块、提取、聚合"""
        import asyncio
        from datetime import datetime
        start_time = datetime.now()

        # 1. 分块
        chunks = self._chunk_text(text) if len(text) > self.chunk_size else [text]
        if self.show_progress:
            logger.info(f"Processing {len(chunks)} chunk(s) with max_workers={self.max_workers}...")

        # 2. 并发提取
        async def extract_all():
            from asyncio import Semaphore
            semaphore = Semaphore(self.max_workers)
            
            async def limited_extract(i: int, chunk: str) -> Optional[T]:
                async with semaphore:
                    try:
                        if self.show_progress:
                            logger.info(f"Extracting chunk {i + 1}/{len(chunks)}...")
                        return await self._extract_chunk(chunk, **kwargs)
                    except Exception as e:
                        logger.error(f"Error extracting chunk {i + 1}: {e}")
                        return None
            
            tasks = [limited_extract(i, chunk) for i, chunk in enumerate(chunks)]
            return await asyncio.gather(*tasks)

        # 运行异步提取
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果已在异步环境中，尝试使用 nest_asyncio（如果可用）
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                    results = loop.run_until_complete(extract_all())
                except ImportError:
                    logger.warning("nest_asyncio not available, creating new event loop")
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    results = loop.run_until_complete(extract_all())
            else:
                results = loop.run_until_complete(extract_all())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(extract_all())
        
        chunk_results = [r for r in results if r is not None]

        # 3. 合并
        logger.info("Merging extracted knowledge...")
        aggregate_stats = self.merge(chunk_results, **kwargs)

        # 4. 更新元数据
        self.metadata["updated_at"] = datetime.now()
        self.metadata["total_extractions"] += 1
        self.metadata["total_chunks_processed"] += len(chunks)

        # 5. 返回统计
        duration = (datetime.now() - start_time).total_seconds()
        return {
            "success": True,
            "chunks_processed": len(chunks),
            "chunks_succeeded": len(chunk_results),
            "aggregate_stats": aggregate_stats,
            "duration_seconds": duration,
            "timestamp": start_time.isoformat(),
        }

    def _chunk_text(self, text: str) -> List[str]:
        """将长文本分块"""
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", "。", "！", "？", ". ", "! ", "? ", " ", ""],
            )
            chunks = splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks")
            return chunks
        except ImportError:
            logger.warning("langchain_text_splitters not available, using simple chunking")
            chunks = []
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                chunks.append(text[i:i + self.chunk_size])
            return chunks

    async def _extract_chunk(self, chunk: str, **kwargs) -> T:
        """
        使用 LLM 的 with_structured_output 提取单个块。
        
        :param chunk: 文本块
        :return: 提取的知识对象
        """
        try:
            structured_llm = self.llm_client.with_structured_output(self.schema_class)
            
            # 如果有自定义 prompt，则在消息前加上
            if self.prompt:
                full_text = f"{self.prompt}\n\n{chunk}"
            else:
                full_text = chunk
            
            result: T = await structured_llm.ainvoke(full_text)
            logger.info(f"Extracted from chunk: {type(result).__name__}")
            return result
        except ValidationError as e:
            logger.error(f"Schema validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during extraction: {e}")
            raise

    def merge(self, items: List[T], **kwargs) -> Dict[str, Any]:
        """
        合并提取结果到内部列表。
        
        :param items: 提取的知识列表
        :return: 合并统计
        """
        added = 0
        duplicates = 0
        
        for item in items:
            # 计算哈希用于去重
            item_hash = self._compute_hash(item)
            
            if item_hash not in self._item_hashes:
                self._items.append(item)
                self._item_hashes.add(item_hash)
                added += 1
                logger.debug(f"Added item: {item_hash[:8]}...")
            else:
                duplicates += 1
                logger.debug(f"Skipped duplicate: {item_hash[:8]}...")
        
        # 更新 self.data（如果 Schema 有 items 字段）
        if hasattr(self._data, "items") and hasattr(self._data.items, "append"):
            # 如果 data.items 是列表，更新它
            self._data.items = self._items
        
        # 标记索引需要重建
        self._index_dirty = True
        
        return {
            "items_added": added,
            "duplicates_removed": duplicates,
            "total_items": len(self._items),
        }

    def _compute_hash(self, item: T) -> str:
        """计算知识对象的哈希值"""
        item_json = item.model_dump_json(sort_keys=True)
        return hashlib.sha256(item_json.encode()).hexdigest()

    def search(self, query: str, top_k: int = 10, **kwargs) -> List[T]:
        """
        基于向量索引的语义搜索。
        
        :param query: 查询字符串
        :param top_k: 返回结果数
        :return: 最相关的知识列表
        """
        if not self._items:
            logger.warning("No items to search")
            return []
        
        try:
            # 1. 确保索引已构建
            self.build_index()
            
            if self._index is None:
                logger.warning("Vector store not available, falling back to text matching")
                raise Exception("Vector store not initialized")
            
            # 2. 使用向量存储进行语义搜索
            docs = self._index.similarity_search(query, k=top_k)
            
            # 3. 从 metadata 恢复原始对象
            results = []
            for doc in docs:
                try:
                    item = self.schema_class.model_validate(doc.metadata["raw"])
                    results.append(item)
                except Exception as e:
                    logger.warning(f"Failed to restore item from metadata: {e}")
                    continue
            
            logger.info(f"Found {len(results)} results for query: {query[:50]}...")
            return results
        
        except Exception as e:
            logger.error(f"Error during vector search: {e}, falling back to text matching")
            # 降级到简单的文本匹配
            return [
                item for item in self._items
                if query.lower() in item.model_dump_json().lower()
            ][:top_k]

    def size(self) -> int:
        """返回知识点数量"""
        return len(self._items)

    async def evolve(self, **kwargs) -> T:
        """
        默认演化实现：空操作。
        
        子类可覆盖此方法实现知识演化、推理、剪枝等逻辑。
        
        :return: 内部知识数据
        """
        logger.debug("Default evolve: no operation")
        return self._data

    def get_all_items(self) -> List[T]:
        """获取所有知识项列表"""
        return self._items.copy()

    def dump(self, filepath: str) -> Any:
        """
        导出知识为 JSON 文件。

        :param filepath: 文件路径
        :return: 序列化后的数据（JSON 字符串）
        """
        from pathlib import Path
        
        data = {
            "schema_class": self._schema_class.__name__,
            "items": [item.model_dump() for item in self._items],
            "metadata": {k: str(v) if isinstance(v, datetime) else v for k, v in self.metadata.items()},
        }
        json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json_str)
        
        logger.info(f"Dumped {len(self._items)} items to {filepath}")
        return json_str

    def load(self, path_or_json: str | dict, **kwargs):
        """
        加载知识。

        :param path_or_json: JSON 文件路径或 JSON 字符串或字典
        """
        from pathlib import Path
        
        # 解析输入
        if isinstance(path_or_json, dict):
            data = path_or_json
            logger.info("Loading from dictionary")
        elif isinstance(path_or_json, str):
            path = Path(path_or_json)
            if path.is_file():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                logger.info(f"Loaded from file: {path}")
            else:
                # 尝试作为 JSON 字符串解析
                data = json.loads(path_or_json)
                logger.info("Loaded from JSON string")
        else:
            raise ValueError(f"Unsupported data type: {type(path_or_json)}")

        # 加载 items
        items_data = data.get("items", [])
        self._items = [self.schema_class.model_validate(item) for item in items_data]
        
        # 重建哈希集
        self._item_hashes = {self._compute_hash(item) for item in self._items}
        
        # 更新元数据
        if "metadata" in data:
            self.metadata.update(data["metadata"])
        self.metadata["updated_at"] = datetime.now()
        
        # 标记索引需要重建
        self._index_dirty = True
        
        logger.info(f"Loaded {len(self._items)} knowledge items successfully")

    def clear(self):
        """清空所有知识"""
        try:
            self._data = self.schema_class()
        except Exception:
            self._data = self.schema_class.model_construct()
        self._items.clear()
        self._item_hashes.clear()
        self.metadata["updated_at"] = datetime.now()
        self.metadata["total_extractions"] = 0
        self.metadata["total_chunks_processed"] = 0
        
        # 清空向量索引
        self._index = None
        self._index_dirty = True
        
        logger.info("Cleared all knowledge")
