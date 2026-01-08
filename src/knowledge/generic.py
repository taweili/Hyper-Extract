"""
通用 Generic 实现。

包含基于 BaseExtractor 和 BaseCollection 的具体实现。
"""

import os
import json
from typing import List, Dict, Any, Callable, Optional, Type
from datetime import datetime
from pydantic import BaseModel, ValidationError
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from .base import BaseExtractor, BaseCollection, T

try:
    from src.config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class GenericExtractor(BaseExtractor[T]):
    """
    通用提取器。使用 LLM 的 with_structured_output 实现提取。
    """

    async def aparse(self, text: str, **kwargs) -> T:
        """
        使用 with_structured_output 异步解析。
        """
        try:
            # 创建支持结构化输出的 LLM
            structured_llm = self.llm_client.with_structured_output(self.schema_class)

            # 调用 LLM
            result: T = await structured_llm.ainvoke(text)

            logger.info(f"Successfully parsed: {type(result).__name__}")
            return result

        except ValidationError as e:
            logger.error(f"Schema validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during parsing: {e}")
            raise


class GenericCollection(BaseCollection[T]):
    """
    通用集合实现。支持任何 Pydantic BaseModel Schema。
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        schema_class: Type[T],
        storage: str = "memory",
        **kwargs,
    ):
        """
        :param llm_client: LLM 实例
        :param embedder: 向量化器实例
        :param schema_class: Schema 类
        :param storage: 存储类型
        """
        super().__init__(llm_client, embedder, schema_class, storage, **kwargs)
        self._items: Dict[str, T] = {}
        self._updated_at: Dict[str, datetime] = {}

    # ================= 存储层实现 =================

    async def add(self, item_id: str, item: T, **kwargs):
        """添加知识点"""
        self._items[item_id] = item
        self._updated_at[item_id] = datetime.now()
        logger.info(f"Added item: {item_id}")

    async def remove(self, item_id: str, **kwargs) -> bool:
        """删除知识点"""
        if item_id in self._items:
            del self._items[item_id]
            del self._updated_at[item_id]
            logger.info(f"Removed item: {item_id}")
            return True
        return False

    async def update(self, item_id: str, item: T, **kwargs):
        """更新知识点"""
        if item_id in self._items:
            self._items[item_id] = item
            self._updated_at[item_id] = datetime.now()
            logger.info(f"Updated item: {item_id}")
        else:
            await self.add(item_id, item, **kwargs)

    def get(self, item_id: str) -> Optional[T]:
        """获取单个知识点"""
        return self._items.get(item_id)

    def list_all(self) -> List[T]:
        """列出所有知识点"""
        return list(self._items.values())

    def search(self, filter_fn: Callable[[T], bool]) -> List[T]:
        """按条件查询"""
        return [item for item in self._items.values() if filter_fn(item)]

    def size(self) -> int:
        """返回知识点数量"""
        return len(self._items)

    def clear(self):
        """清空所有知识点"""
        self._items.clear()
        self._updated_at.clear()
        logger.info("Cleared all items")

    # ================= 融合层实现 =================

    async def aggregate(self, items: List[T], **kwargs) -> Dict[str, Any]:
        """
        默认融合实现：简单去重合并。
        
        子类可覆盖此方法实现更复杂的融合逻辑。
        """
        logger.info(f"Aggregating {len(items)} items...")

        # 简单的聚合：直接添加到容器
        for idx, item in enumerate(items):
            item_id = f"item_{len(self._items)}_{idx}"
            await self.add(item_id, item)

        return {
            "input_count": len(items),
            "output_count": len(items),
            "deduplicated": 0,
        }

    # ================= 演化层实现 =================

    async def evolve(self, **kwargs) -> Dict[str, Any]:
        """
        默认演化实现：空操作。
        
        子类可覆盖此方法实现知识演化、推理、剪枝等逻辑。
        """
        logger.debug("Default evolve: no operation")
        return {"evolved": False, "message": "Default implementation"}

    # ================= 序列化实现 =================

    def dump(self, format: str = "json") -> Any:
        """导出容器内的知识"""
        if not self._items:
            logger.warning("No items to dump")
            return None

        try:
            if format.lower() == "json":
                data = {
                    k: v.model_dump() for k, v in self._items.items()
                }
                return json.dumps(data, indent=2, ensure_ascii=False)

            elif format.lower() == "dict":
                return {k: v.model_dump() for k, v in self._items.items()}

            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Error dumping: {e}")
            raise

    def load(self, data: Any, **kwargs):
        """从外部数据恢复知识"""
        try:
            if isinstance(data, str):
                # 检查是否是文件路径
                if os.path.isfile(data):
                    with open(data, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    logger.info(f"Loaded from file: {data}")
                else:
                    # 尝试解析为 JSON 字符串
                    data = json.loads(data)
                    logger.info("Loaded from JSON string")

            # 恢复为 Schema 对象
            if isinstance(data, dict):
                for item_id, item_data in data.items():
                    item = self.schema_class.model_validate(item_data)
                    self._items[item_id] = item
                    self._updated_at[item_id] = datetime.now()

                logger.info(f"Loaded {len(self._items)} items")

        except Exception as e:
            logger.error(f"Error loading: {e}")
            raise
