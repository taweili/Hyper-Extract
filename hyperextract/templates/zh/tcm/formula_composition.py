"""君臣佐使结构图 - 将方剂建模为 {君药, 臣药, 佐药, 使药} 的层级化超边结构。

适用于方剂结构解析、组方规律研究。
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class HerbNode(BaseModel):
    """药物节点"""

    name: str = Field(description="药物名称")
    role: str = Field(description="药物角色：君药、臣药、佐药、使药")
    dosage: str = Field(description="药物剂量", default="")
    effect: str = Field(description="药物功效", default="")


class FormulaHyperedge(BaseModel):
    """方剂超边"""

    formulaName: str = Field(description="方剂名称")
    junHerbs: List[str] = Field(description="君药列表")
    chenHerbs: List[str] = Field(description="臣药列表")
    zuoHerbs: List[str] = Field(description="佐药列表")
    shiHerbs: List[str] = Field(description="使药列表")
    functions: List[str] = Field(description="方剂功能", default_factory=list)
    indications: List[str] = Field(description="主治证候", default_factory=list)
    decoctionMethod: str = Field(description="煎服法", default="")


_PROMPT = """## 角色与任务
你是一位专业的方剂学专家，请从文本中提取方剂的君臣佐使结构。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指方剂中的药物实体，包括药物名称、角色、剂量、功效等信息。
- **边 (Edge)**：本模板中的"边"指方剂超边，包含方剂名称、君药、臣药、佐药、使药列表、方剂功能、主治证候、煎服法等信息。

## 提取规则
### 节点提取规则
1. 提取方剂中的所有药物实体
2. 为每个药物指定角色：君药、臣药、佐药、使药
3. 提取每个药物的剂量和功效

### 边提取规则
1. 提取方剂名称
2. 提取君药、臣药、佐药、使药列表
3. 提取方剂功能和主治证候
4. 提取煎服法

### 术语标准化指导
- **药物名称标准化**：同一药物的不同名称需统一使用规范正名（如"国老"→"甘草"，"仙灵脾"→"淫羊藿"）
- **角色术语统一**：君、臣、佐、使的不同表述需统一为"君药"、"臣药"、"佐药"、"使药"
- **剂量单位保留**：古代剂量单位（两、钱、分、匕、枚等）可保留原文，无需转换
- **同义词处理**：同一概念的不同表述（如"主治"与"主疗"，"功效"与"功用"）应统一提取

### 约束条件
- 每条边必须包含方剂名称和至少一种角色的药物列表
- 不要创建未在文本中提及的实体或关系
- 保持客观准确，符合方剂学专业术语规范

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
你是一位专业的药物识别专家，请从文本中提取方剂中的所有药物实体作为节点。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指方剂中的药物实体，包括药物名称、角色、剂量、功效等信息。

## 提取规则
1. 提取方剂中的所有药物实体
2. 为每个药物指定角色：君药、臣药、佐药、使药
3. 提取每个药物的剂量和功效

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的方剂学专家，请从给定药物列表中提取方剂的君臣佐使结构。

## 核心概念定义
- **节点 (Node)**：本模板中的"节点"指方剂中的药物实体，作为方剂的组成部分。
- **边 (Edge)**：本模板中的"边"指方剂超边，包含方剂名称、君药、臣药、佐药、使药列表、方剂功能、主治证候、煎服法等信息。

## 提取规则
1. 提取方剂名称
2. 从已知药物列表中提取君药、臣药、佐药、使药列表
3. 提取方剂功能和主治证候
4. 提取煎服法

### 约束条件
1. 仅从下方已知药物列表中提取药物
2. 不要创建未列出的药物
3. 每条边必须包含方剂名称和至少一种角色的药物列表

"""


class FormulaComposition(AutoHypergraph[HerbNode, FormulaHyperedge]):
    """
    适用文档: 方剂规范、伤寒论、金匮要略、方剂学教材等

    功能介绍:
    将方剂建模为 {君药, 臣药, 佐药, 使药} 的层级化超边结构，适用于方剂结构解析、组方规律研究。

    Example:
        >>> template = FormulaComposition(llm_client=llm, embedder=embedder)
        >>> template.feed_text("桂枝汤：桂枝三两，芍药三两，甘草二两，生姜三两，大枣十二枚...")
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
        初始化君臣佐使结构图模板。

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
            node_schema=HerbNode,
            edge_schema=FormulaHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: x.formulaName,
            nodes_in_edge_extractor=lambda x: set(
                [
                    *x.junHerbs,
                    *x.chenHerbs,
                    *x.zuoHerbs,
                    *x.shiHerbs,
                ]
            ),
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
        展示君臣佐使结构图。

        Args:
            top_k_nodes_for_search: 语义检索返回的节点数量，默认为 3
            top_k_edges_for_search: 语义检索返回的边数量，默认为 3
            top_k_nodes_for_chat: 问答使用的节点数量，默认为 3
            top_k_edges_for_chat: 问答使用的边数量，默认为 3
        """

        def node_label_extractor(node: HerbNode) -> str:
            return f"{node.name} ({node.role})"

        def edge_label_extractor(edge: FormulaHyperedge) -> str:
            return edge.formulaName

        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_nodes_for_search,
            top_k_edges_for_search=top_k_edges_for_search,
            top_k_nodes_for_chat=top_k_nodes_for_chat,
            top_k_edges_for_chat=top_k_edges_for_chat,
        )
