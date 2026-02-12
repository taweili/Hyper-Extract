from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from hyperextract.types import AutoSet

# ==============================================================================
# 1. Schema Definitions
# ==============================================================================

class ConstructionResource(BaseModel):
    """
    分配给建筑项目的特定资产、材料或劳动力类别。
    """
    resource_name: str = Field(description="资源名称（例如：'塔吊 TC-01'、'粉煤灰混凝土'）。")
    category: str = Field(description="类别：'重型机械'、'散装材料'、'技工'、'固定设备'、'易耗品'。")
    quantity: Optional[str] = Field(None, description="现场当前数量或容量。")
    supplier_or_team: Optional[str] = Field(None, description="提供或管理此资源的实体。")
    status: str = Field("在用", description="当前运营状态：'在用'、'闲置'、'维护'、'用尽'。")

# ==============================================================================
# 2. Prompts
# ==============================================================================

CONSTRUCTION_RESOURCE_PROMPT = (
    "你是一位建筑物流和采购经理。请从文本中提取所有项目资源和资产。\n\n"
    "提取规则：\n"
    "- 识别机械、材料和劳动力类型。\n"
    "- 捕获提到的具体数量和供应商名称。\n"
    "- 自动合并相似项（例如：'挖掘机 A' 和 '那台主要的挖掘机' 如果指代同一个单元，应合并）。"
)

# ==============================================================================
# 3. Template Class
# ==============================================================================

class ResourceRegistrySet(AutoSet[ConstructionResource]):
    """
    用于管理统一的工地资产和材料清单的模板。
    
    使用 AutoSet 自动去重并合并多段文本中提到的资源信息。

    Example:
        >>> from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        >>> registry = ResourceRegistrySet(llm_client=llm, embedder=embedder)
        >>> registry.feed_text("现场有两台来自利勃海尔的50吨起重机。")
        >>> registry.feed_text("这些利勃海尔起重机目前正在进行维修。")
        >>> print(registry.items)  # 信息将合并到单个起重机资源中
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        embedder: Embeddings,
        *,
        chunk_size: int = 2048,
        chunk_overlap: int = 256,
        max_workers: int = 10,
        verbose: bool = False,
        **kwargs: Any,
    ):
        """
        初始化资源登记表模板。

        Args:
            llm_client (BaseChatModel): 用于资源提取的大模型客户端。
            embedder (Embeddings): 用于资源去重的嵌入模型。
            chunk_size (int, optional): 单个文本块的最大字符数。默认为 2048。
            chunk_overlap (int, optional): 文本块之间的重叠字符数。默认为 256。
            max_workers (int, optional): 并行处理的工作线程数。默认为 10。
            verbose (bool, optional): 是否启用详细日记记录。默认为 False。
            **kwargs (Any): 传递给 AutoSet 基类的其他参数。
        """
        super().__init__(
            item_schema=ConstructionResource,
            key_extractor=lambda x: x.resource_name.strip().lower(),
            llm_client=llm_client,
            embedder=embedder,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_workers=max_workers,
            verbose=verbose,
            prompt=CONSTRUCTION_RESOURCE_PROMPT,
            **kwargs,
        )

    def show(
        self,
        *,
        top_k_for_search: int = 3,
        top_k_for_chat: int = 3,
    ) -> None:
        """
        Visualize the collection using OntoSight.
    
        Args:
            top_k_for_search (int): Number of items to retrieve for search context. Default 3.
            top_k_for_chat (int): Number of items to retrieve for chat context. Default 3.
        """
        def item_label_extractor(item: ConstructionResource) -> str:
            info = f" ({ item.category })" if getattr(item, "category", None) else ""
            return f"{ item.resource_name }{info}"
    
        super().show(
            item_label_extractor=item_label_extractor,
            top_k_for_search=top_k_for_search,
            top_k_for_chat=top_k_for_chat,
        )
