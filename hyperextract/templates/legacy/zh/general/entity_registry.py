"""实体注册表 - 去重并汇总文本中出现的所有唯一实体。

适用于实体发现、命名实体识别等场景。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet


class RegistryEntry(BaseModel):
    """注册表条目"""
    name: str = Field(description="实体名称，保持与原文一致")
    category: str = Field(description="实体类型：人物、机构、地点、产品、概念、其他")
    description: str = Field(description="简要描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的实体识别专家，请从文本中提取所有唯一实体，形成实体注册表。

## 提取规则
1. 提取所有实体：人物、机构、地点、产品、概念等
2. 为每个实体指定类型：人物、机构、地点、产品、概念、其他
3. 保持实体名称与原文一致
4. 为每个实体添加简要描述

### 约束条件
- 去重：同一实体只保留一条记录
- 保持客观准确，不添加文本中没有的信息
- 实体名称大小写需与原文保持一致

## 源文本:
{source_text}
"""


class EntityRegistry(AutoSet[RegistryEntry]):
    """
    适用文档: 任意文本、网页抓取内容、新闻报道

    功能介绍:
    去重并汇总文本中出现的所有唯一实体（如人名、机构名），形成实体注册表。支持实体发现和命名实体识别。

    Example:
        >>> template = EntityRegistry(llm_client=llm, embedder=embedder)
        >>> template.feed_text("银河星际宣布神舟-50首飞成功...")
        >>> print(list(template))
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化实体注册表模板。
        
        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            item_schema=RegistryEntry,
            key_extractor=lambda x: x.name,
            llm_client=llm_client,
            embedder=embedder,
            prompt=_PROMPT,
            max_workers=max_workers,
            verbose=verbose,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        展示实体注册表。
        
        Args:
            top_k_for_search: 语义检索返回的条目数量，默认为 3
            top_k_for_chat: 问答使用的条目数量，默认为 3
        """
        def itemLabelExtractor(item: RegistryEntry) -> str:
            return f"{item.name} ({item.category})"
        
        super().show(
            item_label_extractor=itemLabelExtractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
