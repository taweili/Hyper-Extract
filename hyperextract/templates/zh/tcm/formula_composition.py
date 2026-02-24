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

### 节点提取规则
1. 提取方剂中的所有药物实体
2. 提取每个药物的固有属性：
   - 性味：如辛温、苦寒、甘平
   - 归经：如归肺经、归脾经
   - 功效：如发汗解表、温通经脉
3. 注意：性味归经和功效是药物本身的属性，不随方剂变化

### 边提取规则
1. 提取方剂名称和来源
2. 提取君药、臣药、佐药、使药列表，每个药物包含：
   - 名称
   - 剂量（如三两、五钱）
   - 炮制方法（如炙、炒、煅）
3. 提取方剂功能和主治证候
4. 提取煎服法

### 约束条件
- 每条边必须包含方剂名称
- 药物角色（君臣佐使）通过所属列表区分

### 源文本:
"""

_NODE_PROMPT = """## 角色与任务
请从文本中提取方剂中的药物实体作为节点。

## 核心概念定义
- **节点 (Node)**：药物实体，存储药物的固有属性

## 提取规则
1. 提取方剂中的所有药物实体
2. 提取每个药物的固有属性：
   - 性味：如辛温、苦寒、甘平
   - 归经：如归肺经、归脾经
   - 功效：如发汗解表、温通经脉
3. 注意：只提取药物本身的属性，不要提取剂量和角色

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
请从已知药物列表中提取方剂的君臣佐使结构。

## 核心概念定义
- **边 (Edge)**：方剂超边，存储方剂信息及药物在该方剂中的具体信息

## 提取规则
1. 提取方剂名称和来源
2. 提取君药、臣药、佐药、使药列表
3. 每个药物需包含：
   - 名称（必须从已知药物列表中选择）
   - 剂量
   - 炮制方法（如有）
4. 提取方剂功能和主治证候
5. 提取煎服法

## 约束条件
1. 药物名称必须从已知药物列表中选择
2. 每条边必须包含方剂名称
3. 药物角色通过所属列表（君/臣/佐/使）区分
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
