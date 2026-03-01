"""物种相互作用网 - 从生态学文献中提取物种间的捕食、竞争、共生等关系。

适用于生态学专著、食物网分析报告、物种调查文献。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class SpeciesNode(BaseModel):
    """物种节点"""
    name: str = Field(description="物种名称，如绿藻、鲢鱼、苍鹭")
    category: str = Field(description="物种类别：生产者、消费者、分解者")
    species_type: str = Field(description="具体分类：浮游植物、浮游动物、底栖动物、鱼类、鸟类、哺乳动物、植物、微生物")
    description: str = Field(description="简要描述", default="")


class SpeciesRelation(BaseModel):
    """物种关系边"""
    source: str = Field(description="源物种名称")
    target: str = Field(description="目标物种名称")
    relation_type: str = Field(description="关系类型：捕食、寄生、竞争、互利共生、共生")
    details: str = Field(description="关系详细描述，包括具体行为或机制", default="")


_PROMPT = """## 角色与任务
你是一位专业的生态学专家，请从文本中提取物种及其之间的相互作用关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的物种实体
- **边 (Edge)**：物种之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的物种，禁止将多个物种合并为一个节点
2. 物种名称与原文保持一致
3. 准确判断物种的营养级：生产者（植物、藻类）、消费者（动物）、分解者（细菌、真菌）

### 边提取约束
1. 边只能连接已提取的物种节点
2. 关系描述应与原文保持一致

### 领域特定规则
- 关系类型包括：捕食、寄生、竞争、互利共生、共生
- 捕食关系：捕食者 → 被捕食者
- 竞争关系：竞争同一资源的物种之间
- 互利共生：双方都受益的关系

## 生态学文献:
{source_text}
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的生态学专家，请从文本中提取所有物种作为节点。

## 核心概念定义
- **节点 (Node)**：从文档中提取的物种实体
- **边 (Edge)**：物种之间的关系

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的物种，禁止将多个物种合并为一个节点
2. 物种名称与原文保持一致
3. 准确判断物种的营养级：生产者（植物、藻类）、消费者（动物）、分解者（细菌、真菌）

### 领域特定规则
- 生态学术语保持原文，如物种名称（鲢鱼、绿藻）、生态关系（捕食、竞争）
- 注意区分不同营养级的物种

## 生态学文献:
{source_text}
"""

_EDGE_PROMPT = """## 角色与任务
请从已知物种列表中提取物种之间的关系。

## 核心概念定义
- **节点 (Node)**：从文档中提取的物种实体
- **边 (Edge)**：物种之间的关系

## 提取规则
### 核心约束
1. 仅从已知物种列表中提取边，不要创建未列出的物种
2. 关系描述应与原文保持一致
3. 每条边必须连接两个已提取的物种节点

### 领域特定规则
- 关系类型包括：捕食、寄生、竞争、互利共生、共生
- 捕食关系：捕食者 → 被捕食者
- 竞争关系：竞争同一资源的物种之间
- 互利共生：双方都受益的关系

## 已知物种列表:
{known_nodes}

## 生态学文献:
{source_text}
"""


class SpeciesInteractionWeb(AutoGraph[SpeciesNode, SpeciesRelation]):
    """
    适用文档: 生态学专著、物种描述文献、食物网分析报告

    功能介绍:
    提取物种间的捕食、寄生、竞争、互利共生等关系，构建物种相互作用网络。
    适用于食物网分析、生态关系研究和生物多样性保护。

    Example:
        >>> template = SpeciesInteractionWeb(llm_client=llm, embedder=embedder)
        >>> template.feed_text("湖泊中，鲢鱼滤食浮游植物，翘嘴鲌捕食小型鱼类...")
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
        初始化物种相互作用网模板。

        Args:
            llm_client: LLM 客户端，用于知识提取
            embedder: 嵌入模型，用于语义检索
            extraction_mode: 提取模式，可选 "one_stage"（同时提取节点和边）
                或 "two_stage"（先提取节点，再提取边），默认为 "two_stage"
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """
        super().__init__(
            node_schema=SpeciesNode,
            edge_schema=SpeciesRelation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relation_type}|{x.target}",
            nodes_in_edge_extractor=lambda x: (x.source, x.target),
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
        展示物种相互作用网。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: SpeciesNode) -> str:
            return f"{node.name} ({node.category})"

        def edge_label_extractor(edge: SpeciesRelation) -> str:
            return edge.relation_type

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
