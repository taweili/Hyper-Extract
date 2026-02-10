from typing import List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.graphs.base import AutoGraph

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class TaxonNode(BaseModel):
    """
    表示生命之树中的生物分类单元。
    """
    name: str = Field(description="生物体或群体的学名（拉丁语）或标准俗名。")
    rank: str = Field(description="分类等级：'域'、'界'、'门'、'纲'、'目'、'科'、'属'、'种'。")
    common_name: Optional[str] = Field(None, description="在非科学背景下使用的通用名称。")
    description: Optional[str] = Field(None, description="简要的生物特征、栖息地或区别性性状。")

class TaxonomyRelation(BaseModel):
    """
    两个分类单元之间直接的层级关系。
    """
    source: str = Field(description="父级分类单元（如：'哺乳纲'）。")
    target: str = Field(description="子级分类单元（如：'灵长目'）。")
    type: str = Field("parent_of", description="关系类型：'parent_of'（父级）、'subspecies_of'（亚种）、'classified_under'（归类于）。")
    evidence: Optional[str] = Field(None, description="证明该分类合理的表型或基因组数据引用。")

# ==============================================================================
# 2. Prompts
# ==============================================================================

TAXONOMY_CONSOLIDATED_PROMPT = (
    "你是一位专业的分类学家和系统生物学家。请从文本中提取生物层级（分类学）信息。\n\n"
    "规则：\n"
    "- 识别所有分类阶元（从界到种）及其特定的等级。\n"
    "- 使用 'parent_of' 关系构建严格的树状层级。\n"
    "- 捕捉可用的学名和常用名。"
)

TAXONOMY_NODE_PROMPT = (
    "提取所有生物分类群（节点）。识别它们的等级（例如：科：人科）。"
    "专注于正式分类，排除临时或非标准的分类。"
)

TAXONOMY_EDGE_PROMPT = (
    "映射所提供的分类单元的谱系。创建反映系统发育演化或分类树的边。"
    "确保源节点的等级高于或等于目标节点的等级。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class TaxonomyGraph(AutoGraph[TaxonNode, TaxonomyRelation]):
    """
    生物分类和系统发育层级的高精度提取模板。
    """
    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        extraction_mode: str = "one_stage",
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any
    ):
        super().__init__(
            node_schema=TaxonNode,
            edge_schema=TaxonomyRelation,
            node_key_extractor=lambda x: x.name.strip(),
            edge_key_extractor=lambda x: f"{x.source.strip()}--({x.type})-->{x.target.strip()}",
            nodes_in_edge_extractor=lambda x: (x.source.strip(), x.target.strip()),
            llm_client=llm_client,
            embedder=embedder,
            extraction_mode=extraction_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=TAXONOMY_CONSOLIDATED_PROMPT,
            prompt_for_node_extraction=TAXONOMY_NODE_PROMPT,
            prompt_for_edge_extraction=TAXONOMY_EDGE_PROMPT,
            **kwargs
        )
