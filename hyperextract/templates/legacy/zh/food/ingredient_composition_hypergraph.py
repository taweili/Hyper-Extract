"""食材配伍超图 - 建模菜品与其 {主料, 辅料, 调味品} 的复杂组合关系。

适用于成本核算、过敏原管理、新菜研发。

设计原则：
- 节点（IngredientNode）：存储食材的固有属性（名称、类别）
- 边（DishHyperedge）：存储菜品信息，以及食材在该菜品中的具体角色（主料/辅料/调味品）
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class IngredientNode(BaseModel):
    """食材节点"""

    name: str = Field(description="食材名称")
    category: str = Field(description="食材类别：主料/辅料/调味品")


class IngredientInDish(BaseModel):
    """食材在菜品中的信息"""

    name: str = Field(description="食材名称")
    role: str = Field(description="角色：主料/辅料/调味品")
    quantity: str = Field(description="用量，如500克、30毫升", default="")


class DishHyperedge(BaseModel):
    """菜品超边 - 存储菜品信息及食材在该菜品中的具体角色"""

    dish_name: str = Field(description="菜品名称")
    cuisine: str = Field(description="菜系", default="")
    main_ingredients: List[IngredientInDish] = Field(
        description="主料列表", default_factory=list
    )
    auxiliary_ingredients: List[IngredientInDish] = Field(
        description="辅料列表", default_factory=list
    )
    seasonings: List[IngredientInDish] = Field(
        description="调味品列表", default_factory=list
    )
    combo_description: str = Field(description="配伍描述", default="")


_PROMPT = """## 角色与任务
你是一位专业的烹饪大师，请从文本中提取菜品与食材的配伍关系，建模为超边结构。

## 核心概念定义
- **节点 (Node)**：食材实体，存储食材的名称和类别
- **边 (Edge)**：菜品超边，存储菜品信息及食材在该菜品中的具体角色

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 食材角色：主料（主要食材）、辅料（辅助食材）、调味品（调料）
- 提取每个食材的用量信息
- 提取配伍描述

## 源文本:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取菜品中的所有食材实体作为节点。

## 核心概念定义
- **节点 (Node)**：食材实体，存储食材的名称和类别

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 食材类别：主料、辅料、调味品

## 源文本:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知食材列表中提取菜品的配伍超边结构。

## 核心概念定义
- **边 (Edge)**：菜品超边，存储菜品信息及食材在该菜品中的具体角色

## 提取规则
### 核心约束
1. 仅从已知食材列表中提取边，不要创建未列出的食材
2. 关系描述应与原文保持一致

### 领域特定规则
- 食材角色：主料、辅料、调味品

## 食材列表:
{known_nodes}

## 源文本:
{source_text}
"""


class IngredientCompositionHypergraph(AutoHypergraph[IngredientNode, DishHyperedge]):
    """
    适用文档: 标准食谱、菜谱规范、烹饪教材

    功能介绍:
    将菜品建模为 {主料, 辅料, 调味品} 的层级化超边结构，适用于成本核算、过敏原管理、新菜研发。

    设计说明:
    - 节点（IngredientNode）：存储食材的名称和类别
    - 边（DishHyperedge）：存储菜品信息，以及食材在该菜品中的具体信息（用量、角色）

    Example:
        >>> template = IngredientCompositionHypergraph(llm_client=llm, embedder=embedder)
        >>> template.feed_text("红烧肉：五花肉500克，生姜30克，生抽30毫升...")
        >>> template.show()
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "two_stage",
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化食材配伍超图模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """

        def nodes_in_edge_extractor(edge: DishHyperedge) -> set:
            ingredients = []
            for ingredient_list in [
                edge.main_ingredients,
                edge.auxiliary_ingredients,
                edge.seasonings,
            ]:
                for ingredient in ingredient_list:
                    ingredients.append(ingredient.name)
            return set(ingredients)

        super().__init__(
            node_schema=IngredientNode,
            edge_schema=DishHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: x.dish_name,
            nodes_in_edge_extractor=nodes_in_edge_extractor,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            max_workers=max_workers,
            verbose=verbose,
            prompt=_PROMPT,
            prompt_for_node_extraction=_NODE_PROMPT,
            prompt_for_edge_extraction=_EDGE_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_nodes_for_search: int = 3,
        top_k_edges_for_search: int = 3,
        top_k_nodes_for_chat: int = 3,
        top_k_edges_for_chat: int = 3,
    ):
        """
        展示食材配伍超图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: IngredientNode) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: DishHyperedge) -> str:
            return f"{edge.dish_name}"

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
