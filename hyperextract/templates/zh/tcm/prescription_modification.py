"""处方加减逻辑 - 提取基于特定症状对基础方剂进行的药物加减（如"随证加减"）。

适用于临证用药规律分析。
"""

from typing import Any
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from hyperextract.types import AutoGraph

class PrescriptionEntity(BaseModel):
    """处方实体节点"""
    name: str = Field(description="实体名称，如方剂名、药物名、症状名")
    category: str = Field(description="实体类型：方剂、药物、症状")
    description: str = Field(description="简要描述", default="")

class ModificationRelation(BaseModel):
    """处方加减关系边"""
    source: str = Field(description="源实体，如症状或证型")
    target: str = Field(description="目标实体，如药物")
    modificationType: str = Field(description="加减类型：加、减、替换")
    reason: str = Field(description="加减原因", default="")
    dosage: str = Field(description="药物剂量", default="")
    baseFormula: str = Field(description="基础方剂名称", default="")

_NODE_PROMPT = """## 角色与任务
你是一位专业的中医方剂专家，请从文本中提取所有关键实体作为节点。

## 核心概念定义
- **节点 (Node)**：图谱中的实体
- **边 (Edge)**：节点之间的二元关系

## 提取规则
1. 提取所有方剂、药物、症状等实体
2. 为每个实体指定类型：方剂、药物、症状
3. 保持实体名称与原文一致
4. 方剂应包含完整的方剂名称
5. 药物应包含具体的中药名称
6. 症状应包含具体的临床表现

### 源文本:
"""

_EDGE_PROMPT = """## 角色与任务
你是一位专业的中医方剂专家，请从给定实体列表中提取处方加减逻辑。

## 核心概念定义
- **节点 (Node)**：图谱中的实体
- **边 (Edge)**：节点之间的二元关系

## 提取规则
1. 仅从下方已知实体列表中提取边
2. 不要创建未列出的实体
3. 每条边必须包含 source、target、modificationType
4. source 应为症状或证型
5. target 应为药物
6. modificationType 应为：加、减、替换
7. 提取加减的原因和剂量信息
8. 提取基础方剂名称

"""

_PROMPT = """## 角色与任务
你是一位专业的中医方剂专家，请从文本中提取实体和处方加减逻辑。

## 核心概念定义
- **节点 (Node)**：图谱中的实体，如方剂、药物、症状等
- **边 (Edge)**：节点之间的二元关系，如症状与药物的加减关系

## 提取规则
### 节点提取规则
1. 提取所有方剂、药物、症状等实体
2. 为每个实体指定类型：方剂、药物、症状
3. 保持实体名称与原文一致

### 关系提取规则
1. 提取基于特定症状对基础方剂进行的药物加减
2. 每条边必须包含 source、target、modificationType
3. source 应为症状或证型
4. target 应为药物
5. modificationType 应为：加、减、替换
6. 提取加减的原因和剂量信息
7. 提取基础方剂名称

### 源文本:
"""

# ==============================================================================
# 3. 模板类
# ==============================================================================

class PrescriptionModification(AutoGraph[PrescriptionEntity, ModificationRelation]):
    """
    适用文档: 中医方剂学著作、临床医案
    
    功能介绍:
    从中医文本中提取基于特定症状对基础方剂进行的药物加减逻辑，
    如"随证加减"等临证用药规律。
    
    Example:
        >>> template = PrescriptionModification(llm_client=llm, embedder=embedder)
        >>> template.feed_text("...")
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
        初始化处方加减逻辑模板。
        
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
            node_schema=PrescriptionEntity,
            edge_schema=ModificationRelation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.modificationType}|{x.target}",
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
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ):
        """
        展示处方加减逻辑图。
        
        Args:
            top_k_for_search: 语义检索返回的节点/边数量，默认为 3
            top_k_for_chat: 问答使用的节点/边数量，默认为 3
        """
        def node_label_extractor(node: PrescriptionEntity) -> str:
            return f"{node.name} ({node.category})"
        
        def edge_label_extractor(edge: ModificationRelation) -> str:
            return f"{edge.modificationType}: {edge.target}"
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
