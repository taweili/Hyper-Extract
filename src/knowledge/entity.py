"""
实体知识提取模块。

包含基于 GenericKnowledge 的实体提取实现。
"""

import json
from typing import List, Dict, Any, Type
from datetime import datetime
from pydantic import BaseModel, Field as PydanticField, create_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from .generic import GenericKnowledge
from .base import T

try:
    from src.config import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class BaseEntity(BaseModel):
    """
    实体基类 - 所有实体必须包含的核心字段。

    用户可继承此类添加自定义字段。
    """

    name: str = PydanticField(description="实体唯一名称", min_length=1)
    description: str = PydanticField(description="实体描述")

    class Config:
        """允许用户扩展字段"""

        extra = "allow"  # 允许额外字段
        validate_assignment = True  # 赋值时验证


class EntityKnowledge(GenericKnowledge[T]):
    """
    专门用于实体提取和管理的知识类。

    特点：
    1. 自动去重（基于 entity.name）
    2. LLM 智能合并（同名实体的字段合并）
    3. 每个实体作为独立文档建索引
    4. 支持实体级别的搜索
    """

    def __init__(
        self,
        entity_schema: Type[BaseEntity],
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        prompt: str = "",
        **kwargs,
    ):
        """
        :param entity_schema: 用户自定义的实体类（必须继承 BaseEntity）
        :param llm_client: LLM 客户端
        :param embedder: 向量化器
        :param prompt: 自定义提示词
        """
        self._entity_schema = entity_schema
        entity_list_schema = self._create_entity_list_schema(entity_schema)

        super().__init__(
            data_schema=entity_list_schema,
            llm_client=llm_client,
            embedder=embedder,
            prompt=prompt or self._default_prompt(),
            **kwargs,
        )

        self._merge_chain = self._create_merge_chain()
        
        # 全局实体映射（主存储）
        self._entity_map: Dict[str, BaseEntity] = {}
        self._entity_map_dirty = True  # 标记是否需要同步到 _data

    @staticmethod
    def _create_entity_list_schema(entity_class: Type[BaseEntity]) -> Type[BaseModel]:
        """使用 pydantic.create_model 动态创建 EntityList Schema"""
        return create_model(
            f"{entity_class.__name__}List",
            entities=(
                List[entity_class],
                PydanticField(default_factory=list, description="实体列表"),
            ),
            __base__=BaseModel,
        )

    @staticmethod
    def _default_prompt() -> str:
        """默认实体提取提示词"""
        return (
            "You are an expert entity extraction assistant. "
            "Carefully read the following text and extract all entities "
            "according to the specified schema. Be precise and comprehensive."
            "Extract all entities without adding information not present in the text.\n\n"
            "### Source Text:\n"
        )

    def _create_merge_chain(self):
        """创建 LLM 合并 chain，用于智能合并同名实体"""
        merge_template = """You are an expert at merging entity information. 
Given two instances of the same entity, intelligently merge their fields into one.

Rules:
1. Keep the 'name' field unchanged
2. Merge 'description' by combining both descriptions (remove duplicates)
3. For other fields: prefer non-null values, if both exist choose the more complete/accurate one

Entity A:
{entity_a}

Entity B:
{entity_b}

Please merge these two entities intelligently and return the result."""

        merge_prompt = ChatPromptTemplate.from_template(merge_template)

        return merge_prompt | self.llm_client.with_structured_output(
            self._entity_schema
        )

    # ==================== 数据管理 ====================

    @property
    def data(self) -> T:
        """懒更新：只在访问时才同步 entity_map 到 _data"""
        if self._entity_map_dirty:
            self._data.entities = [
                entity.model_copy(deep=True)
                for entity in self._entity_map.values()
            ]
            self._entity_map_dirty = False
        return self._data

    def clear(self):
        """清空所有实体"""
        self._entity_map.clear()
        self._entity_map_dirty = True
        self._data = self.data_schema()
        self._index = None
        self._index_dirty = True
        self.metadata["updated_at"] = datetime.now()
        logger.info("Cleared all entities")

    # ==================== 提取与聚合 ====================

    def merge(self, data_list: List[T]) -> T:
        """
        实体级别的智能合并（使用 LLM）。

        策略：
        1. 与已有的 entity_map 合并（累积效果）
        2. 使用 name 作为唯一标识符去重
        3. 对于同名实体，调用 LLM 进行智能合并

        :param data_list: 多个 EntityList 对象
        :return: 合并后的实体数据
        """
        if not data_list:
            logger.warning("Empty data list for merge")
            return self.data

        total_entities = 0
        duplicate_count = 0

        # 遍历新提取的数据，与已有的 entity_map 合并
        for entity_list_obj in data_list:
            for entity in entity_list_obj.entities:
                total_entities += 1
                entity_name = entity.name.strip()

                if not entity_name:  # 跳过空名称
                    logger.warning(f"Skipping entity with empty name: {entity}")
                    continue

                if entity_name in self._entity_map:
                    # 实体已存在 - 使用 LLM 执行合并
                    duplicate_count += 1
                    existing = self._entity_map[entity_name]
                    merged = self._merge_entity_with_llm(existing, entity)
                    if merged:
                        self._entity_map[entity_name] = merged
                    else:
                        logger.warning(
                            f"LLM merge failed for entity '{entity_name}', keeping existing"
                        )
                else:
                    # 新实体 - 深拷贝后添加
                    self._entity_map[entity_name] = entity.model_copy(deep=True)

        # 标记需要同步
        self._entity_map_dirty = True
        self._index_dirty = True

        logger.info(
            f"Merged {len(self._entity_map)} unique entities "
            f"from {total_entities} total (removed {duplicate_count} duplicates)"
        )

        return self.data

    def _merge_entity_with_llm(
        self, entity_a: BaseEntity, entity_b: BaseEntity
    ) -> BaseEntity:
        """
        使用 LLM 智能合并两个同名实体。

        :param entity_a: 第一个实体
        :param entity_b: 第二个实体
        :return: 合并后的实体（失败返回第一个实体）
        """
        try:
            # 准备输入
            entity_a_json = entity_a.model_dump_json(indent=2)
            entity_b_json = entity_b.model_dump_json(indent=2)

            # 调用 LLM 合并
            merged_entity = self._merge_chain.invoke(
                {
                    "entity_a": entity_a_json,
                    "entity_b": entity_b_json,
                }
            )

            logger.debug(f"Successfully merged entity: {merged_entity.name}")
            return merged_entity

        except Exception as e:
            logger.error(f"Error merging entity '{entity_a.name}' with LLM: {e}")
            return entity_a

    # ==================== 查询与索引 ====================

    def build_index(self):
        """
        为每个实体构建独立的向量索引文档。

        每个实体 → 一个 Document:
        - page_content: "{name}: {description}"
        - metadata: {"entity": entity.model_dump()}
        """
        if len(self._entity_map) == 0:
            logger.warning("No entities to index")
            return

        if not self._index_dirty and self._index is not None:
            return  # 索引已是最新

        documents = []
        for entity in self._entity_map.values():
            # 构建文档内容（用于向量化）
            content = self._build_entity_content(entity)

            # 保存完整实体数据到 metadata
            documents.append(
                Document(
                    page_content=content,
                    metadata={"entity": entity.model_dump(), "name": entity.name},
                )
            )

        try:
            from langchain_community.vectorstores import FAISS

            self._index = FAISS.from_documents(documents, self.embedder)
            self._index_dirty = False
            logger.info(f"Built FAISS index with {len(documents)} entities")
        except ImportError:
            logger.error("FAISS not available. Install: pip install faiss-cpu")
            raise

    def _build_entity_content(self, entity: BaseEntity) -> str:
        """
        构建实体的文本表示（用于向量化）。

        策略：
        - 基础："{name}: {description}"
        - 可选：添加其他字段
        """
        content_parts = [entity.name]

        if entity.description:
            content_parts.append(entity.description)

        # 添加其他字段（如果用户扩展了）
        for field_name in entity.model_fields:
            if field_name not in ("name", "description"):
                value = getattr(entity, field_name, None)
                if value is not None:
                    content_parts.append(f"{field_name}: {value}")

        return "\n".join(content_parts)

    def search(
        self, query: str, top_k: int = 3, return_raw: bool = False
    ) -> List[BaseEntity]:
        """
        语义搜索实体。

        :param query: 查询字符串
        :param top_k: 返回结果数
        :param return_raw: 是否返回原始实体对象（默认返回字典）
        :return: 实体列表
        """
        if len(self.entities) == 0:
            logger.warning("No entities to search")
            return []

        # 确保索引已构建
        if self._index is None or self._index_dirty:
            self.build_index()

        # 向量搜索
        docs = self._index.similarity_search(query, k=top_k)

        # 恢复实体对象
        results = []
        for doc in docs:
            try:
                entity_data = doc.metadata["entity"]
                if return_raw:
                    # 返回 Pydantic 对象
                    entity = self._entity_schema.model_validate(entity_data)
                    results.append(entity)
                else:
                    # 返回字典
                    results.append(entity_data)
            except Exception as e:
                logger.warning(f"Failed to restore entity: {e}")

        logger.info(f"Found {len(results)} entities for query: {query[:50]}...")
        return results

    def size(self) -> int:
        """返回实体数量（直接从 entity_map 读取）"""
        return len(self._entity_map)

    # ==================== 便捷属性 ====================

    @property
    def entities(self) -> List[BaseEntity]:
        """快速访问实体列表（触发懒更新）"""
        return self.data.entities

    @property
    def entity_schema(self) -> Type[BaseEntity]:
        """返回用户定义的实体 Schema"""
        return self._entity_schema

    @property
    def entity_names(self) -> List[str]:
        """返回所有实体名称（直接从 entity_map 读取）"""
        return list(self._entity_map.keys())

    # ==================== 可选增强方法 ====================

    def get_entity_by_name(self, name: str) -> BaseEntity:
        """按名称获取实体（O(1) 字典查找）"""
        return self._entity_map.get(name)

    def remove_entity(self, name: str) -> bool:
        """删除指定实体（直接从 entity_map 删除）"""
        if name in self._entity_map:
            del self._entity_map[name]
            self._entity_map_dirty = True
            self._index_dirty = True
            logger.info(f"Removed entity: {name}")
            return True
        return False

    # ==================== 序列化 ====================

    def load(self, folder_path: str, **kwargs):
        """加载后重建 entity_map"""
        super().load(folder_path, **kwargs)

        # 从 _data 重建 entity_map
        self._entity_map = {
            entity.name: entity.model_copy(deep=True)
            for entity in self._data.entities
        }
        self._entity_map_dirty = False

        logger.info(f"Loaded {len(self._entity_map)} entities")
