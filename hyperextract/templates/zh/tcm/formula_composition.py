"""君臣佐使结构图 - 将方剂建模为 {君药, 臣药, 佐药, 使药} 的层级化超边结构。

适用于方剂结构解析、组方规律研究。

设计原则：
- 节点（HerbNode）：存储药物的固有属性（性味归经、功效），不随方剂变化
- 边（FormulaHyperedge）：存储方剂信息，以及药物在该方剂中的具体信息（剂量、角色）
"""

from typing import Any, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoHypergraph


class HerbNode(BaseModel):
    """药物节点 - 存储药物的固有属性（不随方剂变化）"""

    name: str = Field(description="药物名称")
    nature: str = Field(description="性味，如：辛温、苦寒、甘平", default="")
    meridian: str = Field(description="归经，如：归肺经、归脾经、归心经", default="")
    effect: str = Field(description="功效，如：发汗解表、温通经脉、补气健脾", default="")


class HerbInFormula(BaseModel):
    """药物在方剂中的信息 - 包含剂量和炮制方法"""

    name: str = Field(description="药物名称")
    dosage: str = Field(description="剂量，如：三两、五钱、10g", default="")
    processing: str = Field(description="炮制方法，如：炙、炒、煅、酒制", default="")


class FormulaHyperedge(BaseModel):
    """方剂超边 - 存储方剂信息和药物在方剂中的具体角色"""

    formulaName: str = Field(description="方剂名称")
    source: str = Field(description="方剂来源，如：伤寒论、金匮要略、方剂学教材", default="")
    junHerbs: List[HerbInFormula] = Field(description="君药列表", default_factory=list)
    chenHerbs: List[HerbInFormula] = Field(description="臣药列表", default_factory=list)
    zuoHerbs: List[HerbInFormula] = Field(description="佐药列表", default_factory=list)
    shiHerbs: List[HerbInFormula] = Field(description="使药列表", default_factory=list)
    functions: List[str] = Field(description="方剂功能，如：解肌发表、调和营卫", default_factory=list)
    indications: List[str] = Field(description="主治证候，如：外感风寒表虚证", default_factory=list)
    decoctionMethod: str = Field(description="煎服法，如：水煎服，日三服", default="")


_PROMPT = """## 角色与任务
你是一位专业的方剂学专家，请从文本中提取方剂的君臣佐使结构。

## 核心概念定义
- **节点 (Node)**：药物实体，存储药物的固有属性（性味归经、功效）
- **边 (Edge)**：方剂超边，存储方剂信息及药物在该方剂中的具体信息

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 药物固有属性：性味、归经、功效（不随方剂变化）
- 药物在方剂中的属性：剂量、炮制方法、角色（君/臣/佐/使）

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取方剂中的药物实体作为节点。

## 核心概念定义
- **节点 (Node)**：药物实体，存储药物的固有属性

## 提取规则
### 核心约束
1. 每个节点只能对应一个独立的实体，禁止将多个实体合并为一个节点
2. 实体名称与原文保持一致

### 领域特定规则
- 药物固有属性：性味、归经、功效

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知药物列表中提取方剂的君臣佐使结构。

## 核心概念定义
- **边 (Edge)**：方剂超边，存储方剂信息及药物在该方剂中的具体信息

## 提取规则
### 核心约束
1. 仅从已知药物列表中提取边，不要创建未列出的药物
2. 关系描述应与原文保持一致

### 领域特定规则
- 药物角色：君药、臣药、佐药、使药

### 已知药物列表:
"""


class FormulaComposition(AutoHypergraph[HerbNode, FormulaHyperedge]):
    """
    适用文档: 方剂规范、伤寒论、金匮要略、方剂学教材等

    功能介绍:
    将方剂建模为 {君药, 臣药, 佐药, 使药} 的层级化超边结构，适用于方剂结构解析、组方规律研究。

    设计说明:
    - 节点（HerbNode）：存储药物的固有属性（性味归经、功效），不随方剂变化
    - 边（FormulaHyperedge）：存储方剂信息，以及药物在该方剂中的具体信息（剂量、角色）

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
        chunk_size: int = 512,
        chunk_overlap: int = 64,
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
            chunk_size: 每个分块的最大字符数，默认为 512（中医文本信息量大，需较小分块）
            chunk_overlap: 分块之间的重叠字符数，默认为 64
            max_workers: 最大工作线程数，默认为 10
            verbose: 是否输出详细日志，默认为 False
            **kwargs: 其他技术参数，传递给基类
        """

        def nodes_in_edge_extractor(edge: FormulaHyperedge) -> set:
            herbs = []
            for herb_list in [
                edge.junHerbs,
                edge.chenHerbs,
                edge.zuoHerbs,
                edge.shiHerbs,
            ]:
                for herb in herb_list:
                    herbs.append(herb.name)
            return set(herbs)

        super().__init__(
            node_schema=HerbNode,
            edge_schema=FormulaHyperedge,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: x.formulaName,
            nodes_in_edge_extractor=nodes_in_edge_extractor,
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
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
            return f"{node.name}"

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
