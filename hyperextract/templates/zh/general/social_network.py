"""社交网络图 - 专注于提取人际关系、互动与组织隶属。

适用于传记分析、人物设定研究等。
"""

from typing import Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoGraph


class PersonNode(BaseModel):
    """人物/组织节点"""
    name: str = Field(description="名称")
    type: str = Field(description="节点类型：人物、组织、机构、其他")
    description: str = Field(description="简要描述", default="")
    role: str = Field(description="角色/身份", default="")


class SocialRelation(BaseModel):
    """社会关系边"""
    source: str = Field(description="源节点")
    target: str = Field(description="目标节点")
    relationType: str = Field(description="关系类型：亲属、朋友、同事、师生、上下级、合作、竞争、隶属、其他")
    details: str = Field(description="关系详细说明", default="")


_PROMPT = """你是一位专业的社会关系分析专家。请从文本中提取人物、组织及其相互关系，构建社交网络图。

### 节点提取规则
1. 提取所有人物、组织、机构等
2. 为每个节点指定类型：人物、组织、机构、其他
3. 为每个节点添加简要描述
4. 为每个节点标注角色或身份

### 关系提取规则
1. 仅从提取的节点中创建边
2. 关系类型包括：
   - 亲属：家庭关系（父母、子女、配偶、兄弟姐妹等）
   - 朋友：朋友关系
   - 同事：工作伙伴关系
   - 师生：教育关系
   - 上下级：管理关系
   - 合作：协作关系
   - 竞争：竞争关系
   - 隶属：组织隶属关系
   - 其他：其他关系
3. 每条边必须连接已提取的节点

### 约束条件
- 不要创建未在文本中提及的节点或关系
- 保持客观准确，不添加文本中没有的信息

### 源文本:
"""

_NODE_PROMPT = """你是一位专业的人物和组织识别专家。请从文本中提取所有人物、组织作为节点。

### 提取规则
1. 提取所有人物、组织、机构等
2. 为每个节点指定类型：人物、组织、机构、其他
3. 为每个节点添加简要描述
4. 为每个节点标注角色或身份

### 源文本:
"""

_EDGE_PROMPT = """你是一位专业的社会关系提取专家。请从给定节点列表中提取节点之间的相互关系。

### 关系类型说明
- 亲属：家庭关系（父母、子女、配偶、兄弟姐妹等）
- 朋友：朋友关系
- 同事：工作伙伴关系
- 师生：教育关系
- 上下级：管理关系
- 合作：协作关系
- 竞争：竞争关系
- 隶属：组织隶属关系
- 其他：其他关系

### 约束条件
1. 仅从下方已知节点列表中提取边
2. 不要创建未列出的节点

"""


class SocialNetwork(AutoGraph[PersonNode, SocialRelation]):
    """
    适用文档: 人物传记、回忆录、小说、人物设定文档

    功能介绍:
    专注于提取人际关系、互动与组织隶属。适用于传记分析、人物设定研究等。

    Example:
        >>> template = SocialNetwork(llm_client=llm, embedder=embedder)
        >>> template.feed_text("祖冲之师从何承天，与戴法兴有过辩论...")
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
        初始化社交网络图模板。
        
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
            node_schema=PersonNode,
            edge_schema=SocialRelation,
            node_key_extractor=lambda x: x.name,
            edge_key_extractor=lambda x: f"{x.source}|{x.relationType}|{x.target}",
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
        展示社交网络图。
        
        Args:
            top_k_for_search: 语义检索返回的节点/边数量，默认为 3
            top_k_for_chat: 问答使用的节点/边数量，默认为 3
        """
        def node_label_extractor(node: PersonNode) -> str:
            if node.role:
                return f"{node.name} ({node.role})"
            return f"{node.name} ({node.type})"
        
        def edge_label_extractor(edge: SocialRelation) -> str:
            return edge.relationType
        
        super().show(
            node_label_extractor=node_label_extractor,
            edge_label_extractor=edge_label_extractor,
            top_k_nodes_for_search=top_k_for_search,
            top_k_edges_for_search=top_k_for_search,
            top_k_nodes_for_chat=top_k_for_chat,
            top_k_edges_for_chat=top_k_for_chat,
        )
